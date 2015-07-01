import sys
import base64
import StringIO
import json
import cjson
import zlib
import itertools
import requests
import time
import urllib2
from xml.sax.saxutils import escape, quoteattr

import xml2json
import delete
from processing import *

KPS = 42


def produceXML(doc_part):
    out = StringIO.StringIO()
    out.write("<doc_part>\n")
    for sent in doc_part["Sents"]:
        out.write("<sent>\n")
        for word in sent["Words"]:
            out.write("<w")
            out.write(" sz_%s=%s" % ("form", quoteattr(word["Text"])))
            out.write(">")
            subsets = set()
            for ana in word["Anas"]:
                for key, val in ana.items():
                    if key == "gr":
                        vals = val.replace(",", " ").replace("=", " ").split(" ")
                        for i in xrange(1, len(vals) + 1):
                            for comb in itertools.combinations(vals, i):
                                subsets.add(",".join(sorted(comb)))
            for item in subsets:
                out.write("<e sz_%s='%s'/>" % ("gr", item))
            for ana in word["Anas"]:
                for key, val in ana.items():
                     if key != "gr":
                        out.write("<e sz_%s=%s/>" % (key, quoteattr(val)))
            attrs = word.get("Attrs", {})
            for key in attrs:
                for val in attrs[key]:
                    out.write("<e sz_%s=%s/>" % (key, quoteattr(val)))
            out.write("a")
            out.write("</w>")
        out.write("</sent>\n")
    out.write("</doc_part>")
    return out.getvalue().encode("utf-8")


def produceJSON(doc, url, i, kps=KPS):
    p_doc_part = base64.b64encode(zlib.compress(cjson.encode(doc["Parts"][i])))
    obj = {
        "prefix": kps,
        "action": "modify",
        "docs": [{
            "options": {
                "mime_type": "text/xml",
                "charset": "utf8",
                "language": "ru",
                "realtime": "false"
            },
            "url": {"value": url + "#%04d" % i},
            "s_url": {"value": url, "type": "#hl"},
            "p_url": {"value": url, "type": "#p"},
            "s_subindex": {"value": i, "type": "#g"},
            "p_doc_part": {"value": p_doc_part, "type": "#p"},
            "body": {"value": "body_xml"},
        }],
    }
    for name, value in doc["Attrs"]:
        key = "s_" + name.encode("utf-8")
        parent = obj["docs"][0]
        parent[key] = parent.get(key, []) + [{"value": value.encode("utf-8"), "type": "#pl"}]

    return json.dumps(obj, ensure_ascii=False)


def index_requests(inpath, json_message, body_xml, retries=3):
    if retries == 0:
        print >>sys.stderr, inpath, "FAILED"
        return
    url = "http://saas-indexerproxy-prestable.yandex.net:80/service/2b6087d5f79ee63acbbb64c2ebea3223?timeout=30000"
    files = [("json_message", json_message), ("body_xml", body_xml)]
    try:
        r = requests.post(url, files=files, timeout=30000)
        response = r.text.strip()
        if response:
            print >>sys.stderr, response, "retrying..."
            index_requests(inpath, json_message, body_xml, retries - 1)
    except Exception as ex:
        print >>sys.stderr, ex, "retrying..."
        index_requests(inpath, json_message, body_xml, retries - 1)


def process(inpath, kps=KPS):
    doc = xml2json.process(inpath)
    partition.split_long_sentences(doc)
    partition.group_parts_in_blocks(doc)
    normalization.normalize_accents(doc)
    marks.normalize_punct(doc)
    marks.set_marks(doc)
    positions.set_first_last(doc)
    positions.set_capital(doc)
    repetition.set_repetitions(doc)
    reversion.set_reversed(doc)

    #delete.delete(kps, inpath)

    for i, doc_part in enumerate(doc["Parts"]):
        json_message = produceJSON(doc, inpath, i, kps)
        body_xml = produceXML(doc_part)
        #index_requests(inpath, json_message, body_xml)
        with open(inpath + ".%04d.json" % i, "w") as f:
            f.write(json_message)
        with open(inpath + ".%04d.xml" % i, "w") as f:
            f.write(body_xml)
    print "DONE:", inpath, len(doc["Parts"])
    sys.stdout.flush()


def main():
    process(sys.argv[1])


if __name__ == "__main__":
    main()

