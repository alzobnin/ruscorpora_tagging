# -*- Encoding: utf-8

import base64
import sys

import parser
import rendering
from search_response import SearchResponse

KPS = "2"

DEFAULT_SERP_PARAMS = {
    "p": 0,
    "dpp": 10,
    "spd": 10,
    "radius": 0,
}

def total_stat(kps=KPS):
    response = SearchResponse(query='url:"*"', kps=kps, max_docs=1, docs_per_group=0)
    return response.DocsCount()


def process_snippets(doc, spd, radius):
    directIndex = doc.DirectIndex()
    hits = doc.Hits()
    url = doc.Url()
    part_index = url.rsplit("#", 1)[-1]
    snippets = []
    sents = set()
    for s in sorted(hits.keys()):
        left = max(0, s - radius)
        right = min(len(directIndex["Sents"]) - 1, s + radius)
        for i in xrange(left, right + 1):
            sents.add(i)
    last_s = -2
    for s in sorted(sents):
        if s - last_s > 1:
            if len(snippets) >= spd:
                break
            snippets.append([])
        last_s = s
        sent = directIndex["Sents"][s]
        snippet = snippets[-1]
        for i, word in enumerate(sent["Words"]):
            has_hit = s in hits and i in hits[s]
            snippet.append(("Punct", word["Punct"]))
            snippet.append(("Word", word["Text"], map(str, (url, s, i)), has_hit))
        snippet.append(("Punct", sent["Punct"]))
    return snippets


def process_group(group, serp_params):
    snippets = []
    for doc in group.Docs():
        snippets += process_snippets(doc, serp_params["spd"] - len(snippets), serp_params["radius"])
    return snippets


def process(response, query_len, serp_params):
    results = []
    min_doc = serp_params["p"] * serp_params["dpp"]
    max_doc = min_doc + serp_params["dpp"] - 1
    for i, group in enumerate(response.Groups()):
        if not (min_doc <= i <= max_doc):
            continue
        snippets = process_group(group, serp_params)
        attrs = group.Attrs()
        url = group.Property("p_url")
        results.append({"Attrs": attrs, "Snippets": snippets, "Url": url})
    stat = {}
    stat["Docs"] = response.DocsCount()
    stat["Hits"] = response.HitsCount() / query_len
    stat["TotalDocs"] = total_stat()
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
    serp_params["spd"] = spd = int(query.get("spd", [10])[0])

    response = SearchResponse(
        query=saas_query,
        kps=KPS,
        max_docs=(p + 1) * dpp,
        docs_per_group=spd,
        hits_count=True,
        hits_info=True,
    )

    results, stat = process(response, query_len, serp_params)
    rendering.render_xml(results, stat, serp_params, wfile)


def doc_info(query, wfile):
    docid = base64.b64decode(query["docid"][0])
    response = SearchResponse(
        query='p_url:"%s"' % docid,
        kps=KPS,
        grouping=False,
        max_docs=1,
    )
    if response.IsEmpty():
        return
    attrs = tuple(response.Groups())[0].Attrs()
    results = [{"Attrs": attrs, "Snippets": [], "Url": docid}]
    stat = {"Docs": 1, "Hits": 0}
    rendering.render_xml(results, stat, DEFAULT_SERP_PARAMS, wfile, query_type="document-info", search_type="document-info")


def word_info(query, wfile):
    url, sent, word = base64.b64decode(query["source"][0]).rsplit("\t", 2)
    sent = int(sent)
    word = int(word)
    response = SearchResponse(
        query='url:"%s"' % url,
        kps=KPS,
        grouping=False,
        max_docs=1,
    )
    if response.IsEmpty():
        return
    directIndex = tuple(tuple(response.Groups())[0].Docs())[0].DirectIndex()
    result = directIndex["Sents"][sent]["Words"][word]
    rendering.render_word_info_xml(result, wfile)


def all_urls(kps):
    response = SearchResponse(
        query='url:"*"',
        kps=kps,
        grouping=False,
        max_docs=2**10,
    )
    result = []
    for group in response.Groups():
        for doc in group.Docs():
            result.append(doc.Url())
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
    #print full_query
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
    #total_stat()
    main()
