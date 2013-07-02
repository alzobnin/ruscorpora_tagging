import StringIO
import codecs
import os
import sys
from modules import fs_walk, common
import morpho_tagger
import tokenizer


def convert(inpath, outpath):
    intermediate_buffer = codecs.getwriter(common.OUTPUT_ENCODING)(StringIO.StringIO(),
                                                                   'xmlcharrefreplace')
    outfile = codecs.getwriter(common.OUTPUT_ENCODING)(file(outpath, 'wb'), 'xmlcharrefreplace')

    sys.stdout.write('Tokenizing')
    tokenizer.convert(inpath, intermediate_buffer)
    intermediate_buffer.seek(0)
    sys.stdout.write('Morpho tagging')
    morpho_tagger.convert(intermediate_buffer, outfile)

def main():

    usage_string = 'Usage: annotate_texts.py --input <input path> --output <output path> [options]'
    parser = morpho_tagger.configure_option_parser(usage_string)
    (options, args) = parser.parse_args()

    if not options.input or not options.output:
        parser.print_help()
        exit(0)

    inpath = os.path.abspath(options.input)
    outpath = os.path.abspath(options.output)

    morpho_tagger.initialize_lemmers(options)

    if os.path.isdir(inpath):
        fs_walk.process_directory(inpath, outpath, convert)
    else:
        convert(inpath, outpath)


if __name__ == '__main__':
    main()
