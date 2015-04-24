import cachetools
import lemmer
import mystem_wrapper


class LemmerHolder(object):
    LANGUAGE_MAPPING = {
        # identity mappings for 2-letter ids
        'hy': 'hy',
        'be': 'be',
        'bg': 'bg',
        'cs': 'cs',
        'fr': 'fr',
        'de': 'de',
        'it': 'it',
        'kz': 'kz',
        'pl': 'pl',
        'pt': 'pt',
        'ro': 'ro',
        'ru': 'ru',
        'es': 'es',
        'ta': 'ta',
        'uk': 'uk',
        'en': 'en',
        # mappings for 3-letter ids
        'arm': 'hy',
        'bel': 'be',
        'bul': 'bg',
        'cze': 'cs',
        'fre': 'fr',
        'ger': 'de',
        'ita': 'it',
        'kaz': 'kz',
        'pol': 'pl',
        'por': 'pt',
        'rum': 'rm',
        'rus': 'ru',
        'spa': 'es',
        'tat': 'ta',
        'ukr': 'uk'
    }
    MAX_CACHED_LEMMERS_NUMBER = 2

    def __init__(self, in_options, in_default_language):
        self.options = in_options
        self.lemmers_cache =\
            cachetools.LRUCache(maxsize=LemmerHolder.MAX_CACHED_LEMMERS_NUMBER)
        self.default_language = in_default_language
        self.default_lemmer = self.initialize_new_lemmer(self.default_language)

    def get_lemmer(self, in_language):
        if in_language == self.default_language:
            return self.default_lemmer
        if in_language not in self.lemmers_cache:
            self.lemmers_cache[in_language] =\
                self.initialize_new_lemmer(in_language)
        return self.lemmers_cache[in_language]

    def initialize_new_lemmer(self, in_language):
        mystem_language_id = LemmerHolder.LANGUAGE_MAPPING[in_language]
        wrapper = mystem_wrapper.MystemWrapper(language=mystem_language_id)
        return lemmer.Lemmer([in_language],
                             dictionaryPath=self.options.semdict,
                             addPath=self.options.addpath,
                             delPath=self.options.delpath,
                             full=self.options.full,
                             mystem=wrapper)