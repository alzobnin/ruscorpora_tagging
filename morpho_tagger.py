# All rights belong to Non-commercial Partnership "Russian National Corpus"
# http://ruscorpora.ru

import codecs
from optparse import OptionParser
import os
import re
import xml.sax
import lemmer
from modules import common, element_stack, fs_walk, config, lemmer_cache

LEMMERS = {}
default_lang = 'rus'

langs_without_lemmer = frozenset(
    ("hr", "hsb", "la", "lt", "lv", "mk", "nl", "sk", "sl", "sr", "sv")
)
manual_tagging_langs = frozenset(("pl"))

number_re = re.compile(ur'[0-9,.-]+$')

class MorphoTaggerHandler(xml.sax.handler.ContentHandler):
    def __init__(self, outfile):
        self.lemmer_cache = lemmer_cache.LemmerCache()
        self.out = outfile
        self.element_stack = element_stack.ElementStack()
        self.within_word = False
        self.distForm = '' # normal form of the distinct word
        self.lang = ''
        self.lemmer = LEMMERS[default_lang]
        self.do_not_parse_word = False
        self.do_not_parse_sentence = False

    def startDocument(self):
        self.out.write('<?xml version="1.0" encoding="%s"?>\n' % config.CONFIG['out_encoding'])

    def endDocument(self):
        self.collapse_element_stack()
        self.out.write('\n')

    def startElement(self, tag, attrs):
        self.element_stack.startTag(tag, attrs)

        if tag == 'ana':
            self.word_tagged = True
        if tag == 'w':
            self.within_word = True
        if tag == 'se':
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
        tag_indices = [len(self.element_stack) - 1, len(self.element_stack) - 1]
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
            tag = ('tag_open_close',
                   'ana',
                   self.process_features({'lex': common.quoteattr(clearword), 'gr': 'NUM,ciph'})
            )
            self.element_stack.insert_tag_into_content(in_tag_indices[0] + 1,
                                                       in_coordinates[0],
                                                       tag)
            return
        elif not clearword or self.lemmer == None:
            tag = ('tag_open_close', 'ana', self.process_features({'lex': '?', 'gr': 'NONLEX'}))
            self.element_stack.insert_tag_into_content(in_tag_indices[0] + 1,
                                                       in_coordinates[0],
                                                       tag)
        else:
            word_for_parse = clearword
            COMPOUND_WORD_DELIMITER = '\-+|\'|%s' % pretty_apostrophe
            for bracket in common.editor_brackets:
                word_for_parse = word_for_parse.replace(bracket, '')
            if not len(word_for_parse):
                tag = ('tag_open_close', 'ana', self.process_features({'lex': '?', 'gr': 'NONLEX'}))
                self.element_stack.insert_tag_into_content(in_tag_indices[0] + 1,
                                                           in_coordinates[0],
                                                           tag)
                return
            if word_for_parse not in self.lemmer_cache:
                (compound, analysis) = self.lemmer.parse(word_for_parse)
                self.lemmer_cache[word_for_parse] = (compound, analysis)
            else:
                (compound, analysis) = self.lemmer_cache[word_for_parse]

            word_parts = re.split(COMPOUND_WORD_DELIMITER, word)
            delimiters = re.findall(COMPOUND_WORD_DELIMITER, word)

            analysis_segments = sorted(analysis.keys())
            parsed_tokens = []

            # generating element stack entries for all word and delimiter tokens
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

            self.markup_word_parses(in_tag_indices, parsed_tokens, analysis)

    def process_features(self, in_features):
        features_filtered = []
        for (feature, value) in in_features.iteritems():
            if feature in config.CONFIG['features']:
                features_filtered.append('%s="%s"' % (feature, value))
        return ' '.join(features_filtered)


    def markup_word_parses(self, in_tag_indices, in_parsed_tokens, in_analysis):
        target_element_index = in_tag_indices[0]
        last_word_open_index = target_element_index

        # inserting elements into the element stack
        for index in xrange(len(in_parsed_tokens)):
            token = in_parsed_tokens[index]
            if token[0] == 'word':
                if index != 0:
                    content_element_index = self.find_content_element_by_coordinate(token[1])
                    target_element_index = \
                        self.element_stack.insert_tag_into_content(content_element_index,
                                                                   token[1],
                                                                   ('tag_open', 'w', ''))
                    last_word_open_index = target_element_index
                ana_tags = self.build_tags_for_parse(in_analysis[token[3]])
                for tag in ana_tags:
                    target_element_index += 1
                    self.element_stack.storage.insert(target_element_index, tag)
                    content_element_index = self.find_content_element_by_coordinate(token[2])
                if index != len(in_parsed_tokens) - 1:
                    target_element_index = \
                        self.element_stack.insert_tag_into_content(content_element_index,
                                                                   token[2],
                                                                   ('tag_close', 'w', ''))
                else:
                    for word_close_index in xrange(target_element_index, len(self.element_stack)):
                        if self.element_stack.storage[word_close_index][:2] == ('tag_close', 'w'):
                            target_element_index = word_close_index
                            break
                (last_word_open_index, target_element_index) = \
                    self.element_stack.fix_intersected_tags(last_word_open_index,
                                                            target_element_index)

    def find_content_element_by_coordinate(self, in_coordinate):
        storage = self.element_stack.storage
        for element_index in xrange(len(storage)):
            if storage[element_index][0] == 'content':
                coordinates = storage[element_index][2:]
                if in_coordinate >= coordinates[0] and in_coordinate <= coordinates[1]:
                    return element_index
        return -1

    def build_tags_for_parse(self, in_ambiguous_parse):
        tags = []
        for parse in in_ambiguous_parse:
            lemma = parse[0]
            for (gramm, sem, semall) in parse[1]:
                features = {
                    'lex': common.quoteattr(lemma),
                    'gr': common.quoteattr(gramm),
                    'sem': common.quoteattr(sem),
                    'sem2': common.quoteattr(semall)
                }
                tags.append(('tag_open_close', 'ana', self.process_features(features)))
        return tags

def convert(inpath, outpath):
    out = outpath
    if isinstance(outpath, str):
        out = codecs.getwriter(config.CONFIG['out_encoding'])(file(outpath, 'wb'), 'xmlcharrefreplace')
    for key in LEMMERS.keys():
        if LEMMERS[key] != None:
            LEMMERS[key].Reset()

    try:
        tagger_handler = MorphoTaggerHandler(out)
        parser = xml.sax.make_parser()
        parser.setContentHandler(tagger_handler)
        parser.parse(inpath)
        print ' - OK'
    except xml.sax.SAXException:
        print ' - FAILED'

def initialize_lemmers(in_options):
    print 'Initializing...',
    global LEMMERS

    # first parameter options.lemmer deleted
    LEMMERS = {
        "ru": lemmer.Lemmer(["ru"], in_options.semdict, in_options.addpath, in_options.delpath,
                            full=in_options.full, reallyAdd=in_options.addFixList),
        "en": lemmer.Lemmer(["en"], full=in_options.full),
        "de": lemmer.Lemmer(["de"], full=in_options.full),
        "uk": lemmer.Lemmer(["uk"], full=in_options.full),
        "be": lemmer.Lemmer(["be"], full=in_options.full),
        "chu": lemmer.Lemmer(["chu"], full=in_options.full),
        "fr": lemmer.Lemmer(["fr"], full=in_options.full),
        "es": lemmer.Lemmer(["es"], full=in_options.full),
        "it": lemmer.Lemmer(["it"], full=in_options.full),
        "pt": lemmer.Lemmer(["pt"], full=in_options.full),
        "ro": lemmer.Lemmer(["ro"], full=in_options.full),
        "cs": lemmer.Lemmer(["cs"], full=in_options.full),
        "bg": lemmer.Lemmer(["bg"], full=in_options.full),
        "": lemmer.Lemmer([], full=in_options.full),
    }
    LEMMERS["rus"] = LEMMERS["ru"]
    LEMMERS["eng"] = LEMMERS["en"]
    LEMMERS["ger"] = LEMMERS["de"]
    LEMMERS["ukr"] = LEMMERS["uk"]
    LEMMERS["bel"] = LEMMERS["be"]

    if in_options.lang and in_options.lang in LEMMERS:
        global default_lang
        default_lang = in_options.lang

    print 'done!'

def configure_option_parser(in_usage_string=''):
    parser = OptionParser(usage=in_usage_string)

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
    parser.add_option('--output_encoding', dest='out_encoding', help='encoding of the output files', default='cp1251')
    parser.add_option('--features',
                      dest='features',
                      help='what features to output: any \',\'-separated combination of [gr, lex, sem, sem2]',
                      default='lex,gr,sem,sem2')
    return parser

def main():
    usage_string = 'Usage: morpho_tagger.py --input <input path> --output <output path> [options]'
    parser = configure_option_parser(usage_string)
    (options, args) = parser.parse_args()

    config.generate_config(options)
    if not options.input or not options.output:
        parser.print_help()
        exit(0)

    initialize_lemmers(options)

    inpath = os.path.abspath(options.input)
    outpath = os.path.abspath(options.output)

    if os.path.isdir(inpath):
        fs_walk.process_directory(inpath, outpath, convert)
    else:
        convert(inpath, outpath)


if __name__ == '__main__':
    main()
