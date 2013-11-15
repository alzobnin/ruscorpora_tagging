import StringIO
import codecs
import os
from modules import fs_walk, config, task_list
import morpho_tagger
import tokenizer

def convert(paths):
    (inpath, outpath) = paths
    encoding = config.CONFIG['out_encoding']
    intermediate_buffer = codecs.getwriter(encoding)(StringIO.StringIO(), 'xmlcharrefreplace')
    outfile = codecs.getwriter(encoding)(file(outpath, 'wb'), 'xmlcharrefreplace')

    retcode = None
    try:
        tokenization_retcode = tokenizer.convert((inpath, intermediate_buffer))
        print '"%s" tokenized - %s' % (inpath, 'OK' if tokenization_retcode == 0 else 'FAIL')

        intermediate_buffer.seek(0)
        tagging_retcode = morpho_tagger.convert((intermediate_buffer, outfile))
        print '"%s" morpho tagged - %s' % (inpath, 'OK' if tagging_retcode == 0 else 'FAIL')
    except Exception as e:
        print e.message
        retcode = inpath
    return retcode

def main():

    usage_string = 'Usage: annotate_texts.py --input <input path> --output <output path> [options]'
    parser = morpho_tagger.configure_option_parser(usage_string)
    (options, args) = parser.parse_args()

    config.generate_config(options)
    if not options.input or not options.output:
        parser.print_help()
        exit(0)

    inpath = os.path.abspath(options.input)
    outpath = os.path.abspath(options.output)

    morpho_tagger.initialize_lemmers(options)

    retcode = 0
    if os.path.isdir(inpath):
        fs_walk.process_directory(inpath, outpath, task_list.add_task)
        return_codes = task_list.execute_tasks(convert)
        retcode = sum([1 if code is not None else 0 for code in return_codes])
    else:
        retcode = convert((inpath, outpath)) is not None
    return retcode


if __name__ == '__main__':
    retcode = main()
    exit(retcode)
