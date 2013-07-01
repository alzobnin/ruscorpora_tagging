# All rights belong to Non-commercial Partnership "Russian National Corpus"
# http://ruscorpora.ru

import codecs
import os
import re
import xml.sax
import sys
import lemmer
from modules import common, element_stack, fs_walk

OUTPUT_ENCODING = 'cp1251'
LEMMERS = {}
default_lang = ''

langs_without_lemmer = frozenset(
    ("hr", "hsb", "la", "lt", "lv", "mk", "nl", "sk", "sl", "sr", "sv")
)
manual_tagging_langs = frozenset(("pl"))

number_re = re.compile(ur'[0-9,.-]+$')

class MorphoTaggerHandler(xml.sax.handler.ContentHandler):
    def __init__(self, outfile):
        self.out = outfile
        self.element_stack = element_stack.ElementStack()
        self.within_word = False
        self.distForm = '' # normal form of the distinct word
        self.lang = ''
        self.lemmer = LEMMERS[default_lang]
        self.do_not_parse_word = False
        self.do_not_parse_sentence = False

    def startDocument(self):
        self.out.write('<?xml version="1.0" encoding="%s"?>\n' % OUTPUT_ENCODING)

    def endDocument(self):
        self.collapse_element_stack()
        self.out.write('\n')

    def startElement(self, tag, attrs):
        self.element_stack.startTag(tag, attrs)

        if tag == 'ana':
            self.word_tagged = True
        if tag == 'w':
            self.within_word = True
        elif tag == 'se':
            self.lang = attrs.get('lang', default_lang)
            if len(self.lang) > 2 and self.lang[-2] == "_":
                self.lang = self.lang[:-2]
            if self.lang in langs_without_lemmer:
                self.lemmer = None
            elif not self.lang in LEMMERS:
                self.lemmer = LEMMERS['']
            else:
                self.lemmer = LEMMERS[self.lang]
            if self.lang in manual_tagging_langs:
                self.do_not_parse_sentence = True

    def endElement(self, tag):
        self.element_stack.endTag(tag)
        if tag == 'se':
            self.do_not_parse_sentence = False
        if tag == 'w':
            self.within_word = False
            if not self.do_not_parse_sentence and not self.do_not_parse_word:
                self.tag_last_word()
            self.do_not_parse_word = False
            self.collapse_element_stack()

    def characters(self, content):
        self.element_stack.addChars(content)

    def ignorableWhitespace(self, whitespace):
        self.characters(whitespace)

    def collapse_element_stack(self):
        self.out.write(self.element_stack.collapse())

    def build_parsed_segment(self, in_segment, in_word_parts, in_delimiters):
        result = ''
        for atomic_index in xrange(in_segment[0], in_segment[1]):
            result += in_word_parts[atomic_index]
            if atomic_index != in_segment[1] - 1:
                result += ''.join(in_delimiters[atomic_index: atomic_index + 1])
        return result

    # determining the tag region of the last word
    def tag_last_word(self):
        PLUS_INFINITY = 99999
        MINUS_INFINITY = -99999
        tag_indices = [len(self.element_stack.storage) - 1, len(self.element_stack.storage) - 1]
        plaintext = ''
        content_coordinates = [PLUS_INFINITY, MINUS_INFINITY]
        # searching for <w> tag open
        keep_searching = True
        index = tag_indices[0]
        while keep_searching:
            element = self.element_stack.storage[index]
            if element[0] == 'content':
                plaintext = element[1] + plaintext
                content_coordinates[0] = min(content_coordinates[0], element[2])
                content_coordinates[1] = max(content_coordinates[1], element[3])
            if element[0] == 'tag_open' and element[1] == 'w':
                tag_indices[0] = index
                keep_searching = False
            index -= 1
            if index < 0:
                keep_searching = False
        self.parse_word(plaintext, content_coordinates, tag_indices)

    # annotating the content within the tag region with <ana>'s
    # and splitting compounds into multiple <w>'s
    def parse_word(self, word, in_coordinates, in_tag_indices):
        pretty_apostrophe = u'\u2019'
        apostrophe = '\''.decode('utf-8')
        clearword = word.replace(u'\u0300', '').replace(u'\u0301', '').replace(pretty_apostrophe,
                                                                               apostrophe).strip()
        if number_re.match(clearword):
            tag = ('tag_open', 'ana', 'lex="%s" gr="NUM,ciph"' % common.quoteattr(clearword))
        elif not clearword or self.lemmer == None:
            tag = ('tag_open', 'ana', 'lex="?" gr="NONLEX"')
        else:
            word_for_parse = clearword
            COMPOUND_WORD_DELIMITER = '\-+|\'|%s' % pretty_apostrophe
            for bracket in common.editor_brackets:
                word_for_parse = word_for_parse.replace(bracket, '')
            (compound, analysis) = self.lemmer.parse(word_for_parse)
            word_parts = re.split(COMPOUND_WORD_DELIMITER, word)
            delimiters = re.findall(COMPOUND_WORD_DELIMITER, word)

            analysis_segments = sorted(analysis.keys())
            parsed_tokens = []

            token_begin = in_coordinates[0]
            for segment in analysis_segments:
                if segment[0] != 0 and segment[0] <= len(delimiters):
                    delimiter = delimiters[segment[0] - 1]
                    parsed_tokens.append(('delim', token_begin, token_begin + len(delimiter)))
                    token_begin += len(delimiter)
                atomic_word = self.build_parsed_segment(segment, word_parts, delimiters)
                parsed_tokens.append(('word',
                                      token_begin,
                                      token_begin + len(atomic_word),
                                      segment))
                token_begin += len(atomic_word)

            target_element_index = in_tag_indices[0]
            last_word_open_index = target_element_index
            (content_begin, content_end) = in_coordinates
            for index in xrange(len(parsed_tokens)):
                token = parsed_tokens[index]
                if token[0] == 'word':
                    ana_tags = self.build_tags_for_parse(analysis[token[3]])
                    for tag in ana_tags:
                        target_element_index += 1
                        self.element_stack.storage.insert(target_element_index, tag)
                # token[0] == 'delim'
                else:
                    target_element_index = self.find_next_content_element(target_element_index)
                    target_element_index = \
                        self.element_stack.insert_tag_into_content(target_element_index,
                                                                   token[1],
                                                                   ('tag_close', 'w', ''))
                    # fixing tag structure and updating <w>, </w> element indices
                    (last_word_open_index, target_element_index) = \
                        self.element_stack.fix_intersected_tags(last_word_open_index,
                                                                target_element_index)
                    target_element_index = self.find_next_content_element(target_element_index)
                    target_element_index = \
                        self.element_stack.insert_tag_into_content(target_element_index,
                                                                   token[2],
                                                                   ('tag_open', 'w', ''))
                    last_word_open_index = target_element_index

    def find_next_content_element(self, in_element_index):
        storage = self.element_stack.storage
        while in_element_index < len(storage):
            if storage[in_element_index][0] == 'content':
                return in_element_index
            else:
                in_element_index += 1
        return -1


    def build_tags_for_parse(self, in_ambiguous_parse):
        tags = []
        for parse in in_ambiguous_parse:
            lemma = parse[0]
            for (gramm, sem, semall) in parse[1]:
                features = 'lex="%s" gr="%s" sem="%s" sem2="%s"' % (
                    common.quoteattr(lemma),
                    common.quoteattr(gramm),
                    common.quoteattr(sem),
                    common.quoteattr(semall)
                )
                tags.append(('tag_open_close', 'ana', features))
        return tags



def convert(inpath, outpath, indent=''):
    print '%s%s' % (indent, os.path.basename(inpath)),
    out = codecs.getwriter(OUTPUT_ENCODING)(file(outpath, 'wb'), 'xmlcharrefreplace')

    for key in LEMMERS.keys():
        if LEMMERS[key] != None:
            LEMMERS[key].Reset()

    try:
        tagger = MorphoTaggerHandler(out)
        xml.sax.parse(inpath, tagger)
        print ' - OK'
    except xml.sax.SAXException:
        print ' - FAILED'


def main():
    from optparse import OptionParser

    usage_string = 'Usage: morpho_tagger.py --input <input path> --output <output path>'
    parser = OptionParser(usage=usage_string)

    parser.add_option("--input", dest="input", help="input path")
    parser.add_option("--output", dest="output", help="output path")
    parser.add_option("--lang", dest="lang", help="default language")
    parser.add_option("--semdict", dest="semdict", help="semantic dictionary path")
    parser.add_option("--add", dest="addpath", help="add.cfg path")
    parser.add_option("--del", dest="delpath", help="del.cfg path")
    parser.add_option("--full", action="store_true", dest="full", default=False,
                      help="use full morphology")
    parser.add_option("--addFixList", action="store_true", dest="addFixList", default=False,
                      help="add fix list analyses instead of replacing analyses from lemmer")

    (options, args) = parser.parse_args()

    global errwriter
    errwriter = codecs.getwriter("utf-8")(sys.stderr, "xmlcharrefreplace")

    if not options.input or not options.output:
        parser.print_help()
        exit(0)

    inpath = os.path.abspath(options.input)
    outpath = os.path.abspath(options.output)

    print 'Initializing...',
    global LEMMERS

    # first parameter options.lemmer deleted
    LEMMERS = {
        "ru": lemmer.Lemmer(["ru"], options.semdict, options.addpath, options.delpath,
                            full=options.full, reallyAdd=options.addFixList),
        "en": lemmer.Lemmer(["en"], full=options.full),
        "de": lemmer.Lemmer(["de"], full=options.full),
        "uk": lemmer.Lemmer(["uk"], full=options.full),
        "be": lemmer.Lemmer(["be"], full=options.full),
        "chu": lemmer.Lemmer(["chu"], full=options.full),
        "fr": lemmer.Lemmer(["fr"], full=options.full),
        "es": lemmer.Lemmer(["es"], full=options.full),
        "it": lemmer.Lemmer(["it"], full=options.full),
        "pt": lemmer.Lemmer(["pt"], full=options.full),
        "ro": lemmer.Lemmer(["ro"], full=options.full),
        "cs": lemmer.Lemmer(["cs"], full=options.full),
        "bg": lemmer.Lemmer(["bg"], full=options.full),
        "": lemmer.Lemmer([], full=options.full),
    }
    LEMMERS["rus"] = LEMMERS["ru"]
    LEMMERS["eng"] = LEMMERS["en"]
    LEMMERS["ger"] = LEMMERS["de"]
    LEMMERS["ukr"] = LEMMERS["uk"]
    LEMMERS["bel"] = LEMMERS["be"]

    if options.lang and options.lang in LEMMERS:
        global default_lang
        default_lang = options.lang

    print 'done!'

    if os.path.isdir(inpath):
        fs_walk.process_directory(inpath, outpath, convert)
    else:
        convert(inpath, outpath)


if __name__ == '__main__':
    main()
