from optparse import OptionParser

import sys
import os.path
import xml.sax
import multiprocessing

import index_multipart

VALID_FILE_EXTENSIONS = ['.xml', '.xhtml']
KPS = 42
FILE_LIST = []

def prepare_file_list(indir, in_handler):
    filelist = os.listdir(indir)
    subdirs = [f for f in filelist if os.path.isdir(os.path.join(indir, f))]
    files = [f for f in filelist if not os.path.isdir(os.path.join(indir, f))]
    for subdir in subdirs:
        inpath = os.path.join(indir, subdir)
        prepare_file_list(inpath, in_handler)
    for f in files:
        if os.path.splitext(f)[1] not in VALID_FILE_EXTENSIONS:
            continue
        inpath = os.path.join(indir, f)
        in_handler(inpath)


def process(path):
    try:
        return index_multipart.process(path, KPS)
    except Exception as ex:
        print >>sys.stderr, path, ex

def main():
    parser = configure_option_parser()
    options, args = parser.parse_args()
    if len(args) < 1:
        print 'Usage: python index_folder.py FOLDER [--jobs <jobs number>] [--kps <kps number> (default: 42)]'
        exit(0)
    global KPS
    KPS = options.kps
    if os.path.isdir(args[0]):
        prepare_file_list(args[0], in_handler=lambda path: FILE_LIST.append(path))
        if options.jobs_number == 1:
            for item in FILE_LIST:
                process(item)
        else:
            pool = multiprocessing.Pool(processes=int(options.jobs_number))
            pool.map(process, FILE_LIST)
    else:
        process(args[0])


def configure_option_parser():
    parser = OptionParser()
    parser.add_option('--jobs',
                      dest='jobs_number',
                      help='parallel jobs number',
                      default=1)
    parser.add_option('--kps',
                      dest='kps',
                      help='kps',
                      default=42)
    return parser


if __name__ == '__main__':
    main()
