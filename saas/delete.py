import sys
import json
import requests
import urllib
import urllib2
from meta_pb2 import TReport

SAAS_HOST = "http://saas-searchproxy-prestable.yandex.net:17000/ruscorpora?"

def produceJSON(kps, url):
    obj = {
        "prefix": int(kps),
        "action": "delete",
        "docs": [{
            "options": {
                "mime_type": "text/xml",
                "charset": "utf8",
                "language": "ru"
            },
            "url": {"value": url},
        }],
    }
    return json.dumps(obj, ensure_ascii=False)


def index_requests(json_message):
    url = "http://saas-indexerproxy-prestable.yandex.net:80/service/2b6087d5f79ee63acbbb64c2ebea3223?timeout=20000"
    files = [("json_message", json_message),]
    r = requests.post(url, files=files, timeout=20000)
    print r.text


def all_parts(kps, common_url):
    max_int = 2**10
    params = urllib.urlencode((
        ("text", 's_url:"%s"' % common_url),
        ("kps", kps),
        ("ms", "proto"),
        ("numdoc", max_int),
    ))
    url = SAAS_HOST + params
    response = urllib2.urlopen(url)
    obj = TReport()
    obj.ParseFromString(response.read())
    result = []
    for grouping in obj.Grouping:
        for group in grouping.Group:
            for doc in group.Document:
                arch_info = doc.ArchiveInfo
                result.append(arch_info.Url)
    return result


def delete(kps, common_url):
    parts = all_parts(kps, common_url)
    for part in parts:
        print part
        json_message = produceJSON(kps, part)
        index_requests(json_message)


if __name__ == "__main__":
    kps = sys.argv[1]
    common_url = sys.argv[2]
    delete(kps, common_url)

