CONFIG = {}

def generate_config(in_options, in_arguments):
    global CONFIG
    CONFIG['out_encoding'] = in_options.out_encoding
