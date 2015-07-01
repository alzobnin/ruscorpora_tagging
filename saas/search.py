import base64
import zlib
import sys
import urllib
import urllib2
import cjson
from meta_pb2 import TReport
import rendering
import parser

SAAS_HOST = "http://saas-searchproxy-prestable.yandex.net:17000/ruscorpora?"
KPS = "42"

DEFAULT_SERP_PARAMS = {
    "p": 0,
    "dpp": 10,
    "spd": 10,
    "radius": 0,
}

def total_stat(kps=KPS):
    params = urllib.urlencode((
        ("kps", kps),
        ("relev", "attr_limit=1000000"),
        ("text", 'url:"*"'),
        ("g", "1.s_url.1.0"),
        ("ms", "proto"),
        #("info", "doccount"),
    ))
    url = SAAS_HOST + params
    print url
    response = urllib2.urlopen(url)
    obj = TReport()
    obj.ParseFromString(response.read())
    if not obj.Grouping or not obj.Grouping[0].NumGroups:
        total_docs = 0
    else:
        total_docs = obj.Grouping[0].NumGroups[0]
    return total_docs


def extract_doc(blob):
    return cjson.decode(zlib.decompress(base64.b64decode(blob)))


def extract_url(group):
    for doc in group.Document:
        for attr in doc.ArchiveInfo.GtaRelatedAttribute:
            if attr.Key == "p_url":
                return attr.Value
    return ""


def process_doc(doc):
    arch_info = doc.ArchiveInfo
    for attr in arch_info.GtaRelatedAttribute:
        if attr.Key == "p_doc_part":
            doc = extract_doc(attr.Value)
        elif attr.Key == "__HitsInfo":
            hits_info = cjson.decode(attr.Value)
    hits = dict()
    for item in hits_info:
        s = int(item["sent"]) - 1
        w = int(item["word"]) - 1
        if s not in hits:
            hits[s] = set()
        hits[s].add(w)
    return {"Hits": hits, "Doc": doc, "Url": arch_info.Url}


def process_attrs(group):
    attrs = {}
    for doc in group.Document:
        arch_info = doc.ArchiveInfo
        for attr in arch_info.GtaRelatedAttribute:
            if attr.Key.startswith("s_"):
                key = attr.Key.decode("utf-8")[2:]
                value = attr.Value.decode("utf-8")
                attrs[key] = attrs.get(key, []) + [value]
        break
    return attrs


def process_snippets(result, spd, radius):
    doc = result["Doc"]
    hits = result["Hits"]
    url = result["Url"]
    part_index = url.rsplit("#")[-1]
    snippets = []
    sents = set()
    for s in sorted(hits.keys()):
        left = max(0, s - radius)
        right = min(len(doc["Sents"]) - 1, s + radius)
        for i in xrange(left, right + 1):
            sents.add(i)
    last_s = -2
    for s in sorted(sents):
        if s - last_s > 1:
            if len(snippets) >= spd:
                break
            snippets.append([])
        last_s = s
        sent = doc["Sents"][s]
        snippet = snippets[-1]
        for i, word in enumerate(sent["Words"]):
            has_hit = s in hits and i in hits[s]
            snippet.append(("Punct", word["Punct"]))
            snippet.append(("Word", word["Text"], map(str, (url, s, i)), has_hit))
        snippet.append(("Punct", sent["Punct"]))
    return snippets


def process_group(group, serp_params):
    snippets = []
    url = ""
    for doc in group.Document:
        result = process_doc(doc)
        snippets += process_snippets(result, serp_params["spd"] - len(snippets), serp_params["radius"])
    return snippets


def process(response, query_len, serp_params):
    obj = TReport()
    obj.ParseFromString(response)
    results = []
    stat = {"Docs": 0, "Hits": 0}
    total_docs = total_stat()
    stat["TotalDocs"] = total_docs
    if not obj.Grouping:
        return results, stat
    min_doc = serp_params["p"] * serp_params["dpp"]
    max_doc = min_doc + serp_params["dpp"] - 1
    for i, group in enumerate(obj.Grouping[0].Group):
        if not (min_doc <= i <= max_doc): continue
        #if len(results) >= serp_params["dpp"]:
        #    break
        snippets = process_group(group, serp_params)
        attrs = process_attrs(group)
        url = extract_url(group)
        results.append({"Attrs": attrs, "Snippets": snippets, "Url": url})
    stat["Docs"] = int(obj.Grouping[0].NumGroups[0])
    for prop in obj.SearcherProp:
        if prop.Key == "rty_hits_count_full":
            stat["Hits"] = int(prop.Value) / query_len
            break
    return results, stat


def search(query, wfile):
    query_len = 1
    text = query["text"][0]
    if text == "word-info":
        return word_info(query, wfile)
    elif text == "document-info":
        return doc_info(query, wfile)
    elif text == "lexgramm":
        saas_query, query_len = parse_lexgramm_cgi(query)
    elif text == "lexform":
        saas_query, query_len = parse_lexform_cgi(query)
    else:
        saas_query = text

    serp_params = dict(DEFAULT_SERP_PARAMS)
    serp_params["p"] = p = int(query.get("p", [0])[0])
    serp_params["dpp"] = dpp = int(query.get("dpp", [10])[0])
    min_doc = p * dpp
    max_doc = (p + 1) * dpp - 1

    params = urllib.urlencode((
        ("text", saas_query),
        ("kps", KPS),
        ("relev", "attr_limit=1000000"),
        ("rty_hits_detail", "da"),
        ("qi", "rty_hits_count"),
        ("qi", "rty_hits_count_full"),
        ("fsgta", "__HitsInfo"),
        ("fsgta", "s_url"),
        ("ms", "proto"),
        ("g", "1.s_url.%d.10.....s_subindex.1" % (max_doc + 1)),
        ("how", "p_sort"),
        ("asc", "1"),
    ))
    url = SAAS_HOST + params
    response = urllib2.urlopen(url)
    results, stat = process(response.read(), query_len, serp_params)
    rendering.render_xml(results, stat, serp_params, wfile)


def doc_info(query, wfile):
    docid = base64.b64decode(query["docid"][0])
    params = urllib.urlencode((
        ("text", 'p_url:"%s"' % docid),
        ("kps", KPS),
        ("ms", "proto"),
        ("numdoc", "1"),
    ))
    url = SAAS_HOST + params
    response = urllib2.urlopen(url)
    obj = TReport()
    obj.ParseFromString(response.read())
    if not obj.Grouping or not obj.Grouping[0].Group:
        return
    attrs = process_attrs(obj.Grouping[0].Group[0])
    results = [{"Attrs": attrs, "Snippets": [], "Url": docid}]
    stat = {"Docs": 1, "Hits": 0}
    rendering.render_xml(results, stat, DEFAULT_SERP_PARAMS, wfile, query_type="document-info", search_type="document-info")


def word_info(query, wfile):
    url, sent, word = base64.b64decode(query["source"][0]).rsplit("\t", 2)
    sent = int(sent)
    word = int(word)
    params = urllib.urlencode((
        ("text", 'url:"%s"' % url),
        ("kps", KPS),
        ("ms", "proto"),
        ("numdoc", "1"),
    ))
    url = SAAS_HOST + params
    response = urllib2.urlopen(url)
    obj = TReport()
    obj.ParseFromString(response.read())
    arch_info = obj.Grouping[0].Group[0].Document[0].ArchiveInfo
    for attr in arch_info.GtaRelatedAttribute:
        if attr.Key == "p_doc_part":
            doc = cjson.decode(zlib.decompress(base64.b64decode(attr.Value)))
    result = doc["Sents"][sent]["Words"][word]
    rendering.render_word_info_xml(result, wfile)


def all_urls(kps):
    max_int = 2**10
    params = urllib.urlencode((
        ("text", 'url:"*"'),
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


def extract_numerated_params(query):
    nodes = {}
    special = {}
    for param in query:
        value = query[param][0]
        if not value:
            continue
        num = ""
        while param and param[-1] in "0123456789":
            num = param[-1] + num
            param = param[:-1]
        if not param or not num:
            continue
        if param in ("min", "max", "sem-mod", "parent", "level"):
            if num not in special:
                special[num] = {}
            special[num][param] = value
        else:
            if num not in nodes:
                nodes[num] = {}
            nodes[num][param] = value
    return nodes, special


def build_node_query(param, value):
    value = value.replace(" ", "&")
    value = value.replace(",", "&")
    tree = parser.parse(value)
    if param == "gramm":
        param = "gr"
        tree = parser.dnf(tree)
        tree = parser.join_disjuncts(tree)
    result = parser.subs(tree, param)
    return result


def parse_lexgramm_cgi(query):
    nodes, special = extract_numerated_params(query)
    full_query = ""
    nodes_count = len(nodes)
    for i, ind in enumerate(sorted(nodes.keys())):
        params = nodes[ind]
        spec_params = special[ind]
        min_dist = spec_params.get("min", "+1")
        max_dist = spec_params.get("max", "+1")
        if min_dist[0] not in "+-0":
            min_dist = "+" + min_dist
        if max_dist[0] not in "+-0":
            max_dist = "+" + max_dist
        node_query = []
        query_len = 0
        for param, value in params.items():
            value = value.decode("cp1251").encode("utf-8")
            if param not in ("min", "max", "sem-mod", "parent", "level"):
                subnodes, subquery_len = build_node_query(param, value)
                query_len += subquery_len
                node_query.append(subnodes)
        node_query = " /0 ".join(node_query)
        full_query += "(%s)" % node_query
        if i < nodes_count - 1:
            full_query += " /(%s %s) " % (min_dist, max_dist)
    if nodes_count > 1:
        query_len = nodes_count
    print full_query
    return full_query, query_len


def parse_lexform_cgi(query):
    words = query.get("req", [""])[0].decode("cp1251").encode("utf-8").split(" ")
    query_len = len(words)
    nodes = []
    for word in words:
        nodes.append('sz_form:"%s"' % word)
    full_query = " /+1 ".join(nodes)
    return full_query, query_len


def main():
    if "--all_urls" in sys.argv:
        print "\n".join(all_urls(sys.argv[-1]))
        return
    l = sys.stdin.readline()
    l = l.rstrip()
    search(l)

if __name__ == "__main__":
    total_stat()
    #main()
