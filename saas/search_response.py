# -*- Encoding: utf-8

import base64
#import cjson
import json
import urllib
import urllib2
import zlib

SAAS_HOST = "https://saas-searchproxy-outgone.yandex.net/yandsearch?service=ruscorpora&format=json&"

def read_json(blob):
    return json.loads(blob)
    #return cjson.decode(blob)

def read_json_from_url(url):
    return read_json(urllib2.urlopen(url).read())


# Найденный документ
class Document(object):
    def __init__(self, obj):
        self.obj = obj
        self.directIndex = None
        self.hits = None
        self.attrs = None

    def Properties(self):
        try:
            return self.obj["properties"]
        finally:
            pass
        #except:
        #    return {}

    def Property(self, propName):
        return self.Properties().get(propName, "")

    def DirectIndex(self):
        if self.directIndex == None:
            try:
                blob = self.obj["properties"]["p_doc_part"]
                self.directIndex = read_json(zlib.decompress(base64.b64decode(blob)))
            finally:
                pass
            #except:
            #    self.directIndex = {}
        return self.directIndex

    def Hits(self):
        if self.hits == None:
            try:
                hits_info = read_json(self.obj["properties"]["__HitsInfo"][0])
                self.hits = {}
                for item in hits_info:
                    s = int(item["sent"]) - 1
                    w = int(item["word"]) - 1
                    if s not in self.hits:
                        self.hits[s] = set()
                    self.hits[s].add(w)
            finally:
                pass
            #except:
            #    self.hits = {}
        return self.hits

    def Attrs(self):
        if self.attrs == None:
            try:
                self.attrs = {}
                for key, value in self.Properties().items():
                    if key.startswith("s_"):
                        key = key[2:]
                        if type(value) is list:
                            value = value[0]
                        self.attrs[key] = self.attrs.get(key, []) + [value]
            finally:
                pass
            #except:
            #    self.attrs = {}
        return self.attrs


    def Url(self):
        return self.obj.get("url", "")


# Найденная группа документов
class Group(object):
    def __init__(self, obj):
        self.obj = obj

    def Docs(self):
        try:
            for doc in self.obj["documents"]:
                yield Document(doc)
        finally:
            pass
        #except:
        #    return

    # Возвращает атрибуты первого документа в группе
    def Attrs(self):
        for doc in self.Docs():
            return doc.Attrs()
        return {}

    def Property(self, propName):
        for doc in self.Docs():
            return doc.Property(propName)
        return ""


# Результат поискового запроса в SaaS
class SearchResponse(object):
    def __init__(
        self,
        query,
        kps,
        grouping=True,
        group_attr="s_url",
        max_docs=10,
        docs_per_group=10,
        hits_count=False,
        hits_info=False,
        sort=None,
        asc=True
    ):
        params = [
            ("text", query),
            ("kps", str(kps)),
            ("relev", "attr_limit=1000000"),
            ("fsgta", "s_url"),
        ]
        if grouping:
            params += [
                ("g", "1.%s.%d.%d.....s_subindex.1" % (group_attr, max_docs, docs_per_group)),
            ]
        else:
            params += [
                ("numdoc", str(max_docs))
            ]
        if hits_count:
            params += [
                ("rty_hits_detail", "da"),
                ("qi", "rty_hits_count"),
                ("qi", "rty_hits_count_full"),
            ]
        if hits_info:
            params += [
                ("fsgta", "__HitsInfo"),
            ]
        if sort:
            params += [
                ("how", sort),
                ("asc", "1" if asc else "0"),
            ]
        url = SAAS_HOST + urllib.urlencode(params)
        try:
            self.obj = read_json_from_url(url)
        finally:
            pass
        #except:
        #    self.obj = {}


    def IsEmpty(self):
        return "results" not in self.obj.get("response", [])

    def DocsCount(self):
        try:
            return int(self.obj["response"]["results"][0]["found"]["all"])
        finally:
            pass
        #except:
        #    return 0

    def HitsCount(self):
        try:
            return int(self.obj["response"]["searcher_properties"]["rty_hits_count_full"])
        finally:
            pass
        #except:
        #    return 0

    def Groups(self):
        try:
            for group in self.obj["response"]["results"][0]["groups"]:
                yield Group(group)
        finally:
            pass
        #except:
        #    return

