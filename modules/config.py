CONFIG = {}

def generate_config(in_options):
    global CONFIG
    CONFIG['out_encoding'] = in_options.out_encoding
    if 'features' in vars(in_options):
        CONFIG['features'] = sorted(in_options.features.split(','))
    CONFIG['jobs_number'] = int(in_options.jobs_number)
