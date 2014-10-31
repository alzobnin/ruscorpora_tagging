import StringIO
from subprocess import Popen, PIPE, STDOUT
import os
import sys
import json

MYSTEM_BINARY_NAME = os.path.join('bin', 'mystem_ruscorpora')


def print_parse(in_parsed_tokens_list):
    for token in in_parsed_tokens_list:
        print token['text']
        for analysis in token['analysis']:
            print '%s: %s' % ('lex', analysis['lex'])
            print '%s: %s' % ('gr', analysis['gr'])


class MystemWrapper(object):
    MYSTEM_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), MYSTEM_BINARY_NAME)

    def __init__(self, in_add_cfg=None):
        self.options = [
            '--format=json', # plaintext at input, json at output
            '-i', # print grammar
            '-d', # use disamb
            '-c', # print every single input symbol at output
            '-g', # glue FlexGrams for the same YandexLemmas
            '--eng-gr' # grammar tags in English
        ]
        if in_add_cfg:
            self.options += [
            '--fixlist',
            in_add_cfg
        ]
        self.mystem_process = Popen([MystemWrapper.MYSTEM_PATH] + self.options,
                                     stdout=PIPE,
                                     stdin=PIPE,
                                     stderr=sys.stderr)

    def analyze_tokens(self, in_tokens):
        plaintext_in = ' '.join(in_tokens)
        print >>self.mystem_process.stdin, plaintext_in.encode('utf-8')
        json_out = json.loads(self.mystem_process.stdout.readline().strip())
        return json_out

    def analyze_token(self, in_token):
        plaintext_in = in_token
        print >>self.mystem_process.stdin, plaintext_in.encode('utf-8')
        json_out = json.loads(self.mystem_process.stdout.readline().strip())
        return json_out[0]

    def __token_list_as_json(self, in_tokens):
        return json.dumps([{'analysis': [], 'text': token} for token in in_tokens])


if __name__ == '__main__':
    wrapper = MystemWrapper()
    for line in sys.stdin:
        for token in wrapper.analyze_tokens(line.strip().split()):
            print json.dumps(token)
