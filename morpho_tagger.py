# All rights belong to Non-commercial Partnership "Russian National Corpus"
# http://ruscorpora.ru

import codecs
from optparse import OptionParser
import os
import re
import xml.sax
import lemmer
from modules import common, element_stack, fs_walk, config, lemmer_cache, task_list

LEMMERS = {}
default_lang = 'rus'

langs_without_lemmer = {"hr", "hsb", "la", "lt", "lv", "mk", "nl", "sk", "sl", "sr", "sv"}
manual_tagging_langs = {"pl"}

number_re = re.compile(ur'[0-9,.-]+$')

class MorphoTaggerHandler(xml.sax.handler.ContentHandler):
    def __init__(self, outfile):
        self.out = outfile
        self.element_stack = element_stack.ElementStack()
        self.within_word = False
        self.distForm = '' # normal form of the distinct word
        self.lang = ''
        self.lemmer = LEMMERS[default_lang]
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
            self.do_not_parse_sentence = True
        if tag == 'w':
            self.within_word = True
        if tag == 'se':
            self.sentence_buffer = []
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
            if not self.do_not_parse_sentence:
                self.tag_sentence()
            self.collapse_element_stack()
            self.do_not_parse_sentence = False
        if tag == 'w':
            self.within_word = False
            if not self.do_not_parse_sentence:
                pass

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

    def tag_sentence(self):
        se_close_index = len(self.element_stack) - 1
        se_open_index = self.__find_tag_open_index(se_close_index)
        word_regions = self.__find_all_word_tag_coordinates_in_range(se_open_index, se_close_index)

        coordinates, content = [], []
        for region_begin, region_end in word_regions:
            region_coordinates, region_content = \
                self.__collect_content_between_tags(region_begin, region_end)
            coordinates.append(region_coordinates)
            content.append(region_content)
        parses = self.lemmer.parse_tokens_context_aware(content)

        assert len(content) == len(parses)
        for content, coordinates, tag_indices, parse \
        in reversed(zip(content, coordinates, word_regions, parses)):
            self.tag_word(content, coordinates, tag_indices, parse)

    # searching for the open tag from the end of element stack
    def __find_tag_open_index(self, in_tag_close_index):
        close_element = self.element_stack.storage[in_tag_close_index]
        assert close_element[0] == 'tag_close'
        tag = close_element[1]

        tag_index = in_tag_close_index
        keep_searching = True
        while not tag_index < 0:
            element = self.element_stack.storage[tag_index]
            if element[0] == 'tag_open' and element[1] == 'se':
                keep_searching = False
            tag_index -= 1
        return tag_index

    def __find_all_word_tag_coordinates_in_range(self, in_range_begin, in_range_end):
        tags = []
        for index in xrange(in_range_begin, in_range_end + 1):
            element = self.element_stack.storage[index]
            if element[:2] == ('tag_open', 'w'):
                tags.append([index, None])
            if element[:2] == ('tag_close', 'w'):
                tags[-1][1] = index
        return tags

    def __collect_content_between_tags(self, in_tag_open_index, in_tag_close_index):
        coordinates = [-1, -1]
        content = ''
        for index in xrange(in_tag_open_index + 1, in_tag_close_index):
            element = self.element_stack.storage[index]
            if element[0] == 'content':
                content += element[1]
                if coordinates[0] == -1:
                    coordinates[0] = element[2]
                coordinates[1] = element[3]
        return coordinates, content

    def parse_sentence(self, in_content_with_coordinates, in_tag_indices):
        tokens = [content for content, coordinates in in_content_with_coordinates]
        parses = self.lemmer.parse_tokens_context_aware(tokens)

        for token, parse in reversed(zip(tokens, parses)):
            content_tag_index = in_tag_indices[0] + 1
            while self.element_stack.storage[content_tag_index][0] != 'content'\
                  and content_tag_index < in_tag_indices[1]:
                content_tag_index += 1
            if self.element_stack.storage[content_tag_index][0] != 'content':
                raise RuntimeError('Could not find content element while parsing "%s" %d' %
                                   (word, str(in_coordinates)))

    # annotating the content within the tag region with <ana>'s
    # and splitting compounds into multiple <w>'s
    def tag_word(self, in_word, in_content_coordinates, in_tag_indices, in_parse):
        content_tag_index = in_tag_indices[0] + 1
        while content_tag_index != len(self.element_stack.storage) \
              and self.element_stack.storage[content_tag_index][0] != 'content':
              content_tag_index += 1
        if content_tag_index == len(self.element_stack.storage):
            raise RuntimeError('Could not find content element in the stack!')

        if number_re.match(in_word):
            tag = ('tag_open_close',
                   'ana',
                   self.process_features({'lex': common.quoteattr(in_word),
                                          'gr': 'NUM,ciph',
                                          'disamb': 'yes'}))
            self.element_stack.insert_tag_into_content(content_tag_index,
                                                       in_content_coordinates[0],
                                                       tag)
            return
        elif not in_word or self.lemmer == None:
            tag = ('tag_open_close', 'ana', self.process_features({'lex': '?', 'gr': 'NONLEX'}))
            self.element_stack.insert_tag_into_content(content_tag_index,
                                                       in_content_coordinates[0],
                                                       tag)
        else:
            word_for_parse = in_word
            if not len(word_for_parse):
                tag = ('tag_open_close', 'ana', self.process_features({'lex': '?', 'gr': 'NONLEX'}))
                self.element_stack.insert_tag_into_content(content_tag_index,
                                                           in_content_coordinates[0],
                                                           tag)
                return

            self.__markup_word_parses(in_tag_indices, in_content_coordinates, in_parse)

    def process_features(self, in_features):
        features_filtered = []
        for (feature, value) in in_features.iteritems():
            if feature in config.CONFIG['features']:
                features_filtered.append('%s="%s"' % (feature, value))
        return ' '.join(features_filtered)


    def __markup_word_parses(self, in_tag_indices, in_content_coordinates, in_parse):
        word_open_index, word_close_index = in_tag_indices
        unclosed_w_tag = False
        # processing each subparse from last to first,
        # as in "Saint-Petersburg-Moscow", we'll have these subparses: (Saint-Petersburg)-(Moscow)
        for index in xrange(len(in_parse) - 1, -1, -1):
            parse_coordinates, parse = in_parse[index]
            absolute_begin = in_content_coordinates[0] + parse_coordinates[0]
            absolute_end = in_content_coordinates[0] + parse_coordinates[1]
            print absolute_begin, absolute_end
            content_element_index = self.find_content_element_by_coordinate(absolute_begin)

            # we go from last to first, so we start off each time with </w>
            if unclosed_w_tag:
                word_close_index = self.element_stack.insert_tag_into_content(content_element_index,
                                                                              absolute_end,
                                                                              ('tag_close', 'w', ''))
                unclosed_w_tag = False
                content_element_index = word_close_index - 1
            # for each "tail" subparse, we have to insert an additional <w> tag
            if index != 0:
                word_open_index = self.element_stack.insert_tag_into_content(content_element_index,
                                                                             absolute_begin,
                                                                             ('tag_open', 'w', ''))
                unclosed_w_tag = True
                word_close_index += 1 + word_open_index - content_element_index
            else:
                word_open_index = in_tag_indices[0]
            ana_tags = self.build_tags_for_parse(parse)
            word_close_index += len(ana_tags)
            for tag in reversed(ana_tags):
                self.element_stack.storage.insert(word_open_index + 1, tag)
            for el in self.element_stack.storage:
                print el
            print word_open_index, word_close_index
            print '\n\n\n'
            #word_open_index, word_close_index = \
            #    self.element_stack.fix_intersected_tags(word_open_index, word_close_index)

    def find_content_element_by_coordinate(self, in_coordinate):
        storage = self.element_stack.storage
        for element_index in xrange(len(storage)):
            if storage[element_index][0] == 'content':
                coordinates = storage[element_index][2:]
                if coordinates[0] <= in_coordinate and in_coordinate < coordinates[1]:
                    return element_index
        return -1

    def build_tags_for_parse(self, in_ambiguous_parse):
        tags = []
        for parse in in_ambiguous_parse:
            assert len(parse) == 4
            lemma, parse_variants, language, disamb = parse
            for gramm, sem, semall in parse_variants:
                features = {
                    'lex': common.quoteattr(lemma),
                    'gr': common.quoteattr(gramm),
                    'sem': common.quoteattr(sem),
                    'sem2': common.quoteattr(semall),
                }
                if disamb == 'disamb':
                    features['disamb'] = 'yes'
                tags.append(('tag_open_close', 'ana', self.process_features(features)))
        return tags

def convert_and_log(in_paths):
    retcode = convert(in_paths)
    print '"%s" morpho tagged - %s' % (in_paths[0], 'OK' if retcode == 0 else 'FAIL')

def convert_wrapper(in_input, in_output):
    return convert((in_input, in_output))

def convert(in_paths):
    (inpath, outpath) = in_paths
    out = outpath
    if isinstance(outpath, str):
        out = codecs.getwriter(config.CONFIG['out_encoding'])(file(outpath, 'wb'), 'xmlcharrefreplace')
    for key in LEMMERS.keys():
        if LEMMERS[key] != None:
            LEMMERS[key].Reset()

    retcode = 0
    try:
        tagger_handler = MorphoTaggerHandler(out)
        parser = xml.sax.make_parser()
        parser.setContentHandler(tagger_handler)
        parser.parse(inpath)
    except xml.sax.SAXException:
        retcode = 1
    return retcode

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
                      help='what features to output: any \',\'-separated combination of [gr, lex, sem, sem2, disamb]',
                      default='lex,gr,sem,sem2,disamb')
    parser.add_option('--jobs', dest='jobs_number', help='parallel jobs number', default='1')
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
        fs_walk.process_directory(inpath, outpath, task_list.add_task)
        return_codes = task_list.execute_tasks(convert_and_log)
        retcode = sum([1 if code is not None else 0 for code in return_codes])
    else:
        retcode = convert_and_log((inpath, outpath))
    return retcode


if __name__ == '__main__':
    retcode = main()
    exit(retcode)
