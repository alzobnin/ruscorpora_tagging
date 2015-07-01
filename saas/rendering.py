import base64
import sys
from string import Template
from xml.sax.saxutils import escape, quoteattr

def render_xml(results, stat, serp_params, wfile, query_type="lexgramm", search_type="all-documents"):
    """<corp-stat>
      <words total="229968798"/>
      <sentences total="19362746"/>
      <documents total="85996"/>
    </corp-stat>"""

    out = []
    out.append('<body>')
    out.append('<request page="%d">' % serp_params.get("p", 0))
    out.append('<format documents-per-page="10" snippets-per-document="10" snippets-per-page="50"/>')
    out.append('<query request="123" type="%s">' % query_type)
    out.append('<word lex="abc" gramm="" flags=""/>')
    out.append('</query>')
    out.append('</request>')
    out.append('<result documents="%d" contexts="%d" search-type="%s">' % (stat["Docs"], stat["Hits"], search_type))
    out.append('<corp-stat>')
    out.append('<documents total="%s"/>' % stat.get("TotalDocs", 0))
    out.append('</corp-stat>')
    for doc in results:
        attrs = doc["Attrs"]
        docid = base64.b64encode(doc["Url"])
        title = ". ".join(attrs.get("header",[]))
        tagging = "manual" if "manual" in attrs.get("tagging", []) else "none"
        out.append('<document id=%s title=%s tagging=%s>' % tuple(map(quoteattr, (docid, title, tagging))))
        out.append('<attributes>')
        for name in attrs:
            for value in attrs[name]:
                out.append('<attr name=%s value=%s/>' % (quoteattr(name), quoteattr(value)))
        out.append('</attributes>')
        for snippet in doc["Snippets"]:
            out.append('<snippet>')
            for item in snippet:
                if item[0] == "Punct":
                    out.append('<text>%s</text>' % escape(item[1]))
                elif item[0] == "Word":
                    text, coords, has_hit = item[1:]
                    out.append('<word text=%s source=%s %s/>' % (quoteattr(text), quoteattr(base64.b64encode("\t".join(coords))), 'target="1"' if has_hit else ''))
            out.append('</snippet>')
        out.append('</document>')
    out.append('</result>')
    out.append('</body>')
    wfile.write("".join(out).encode("utf-8"))


def render_text(results):
    out = []
    for doc in results:
        for name, value in doc["Attrs"].items():
            out.append("%s: %s\n" % (name, value))
        for snippet in doc["Snippets"]:
            for item in snippet:
                if item[0] == "Punct":
                    out.append(item[1])
                elif item[0] == "Word":
                    text, coords, has_hit = item[1:]
                    if has_hit:
                        out.append("**%s**" % text)
                    else:
                        out.append(text)
            out.append("\n------------\n")
        out.append("=============\n")
    sys.stdout.write("".join(out).encode("utf-8"))


def render_html(doc):
    out = []
    hits = {}
    out.append("<table>\n")
    out.append("<tr>\n")
    out.append("<td>\n")
    out.append("<ul>\n")
    for s in sorted(hits.keys()):
        sent = doc["Sents"][s]
        out.append("<li>\n")
        for word in sent["Words"]:
            out.append(word["Punct"])
            t = Template('$punct<span class="${style_class}b-wrd-expl">$word</span>')
            out.append(t.substitute(punct=word["Punct"], style_class="g_em " if "Hit" in word else "", word=word["Text"]))
        out.append(sent["Punct"])
        out.append("\n</li>\n")
    out.append("</ul>\n")
    out.append("</td>\n")
    out.append("</tr>\n")
    out.append("</table>\n")


def render_word_info_xml(word, wfile):
    text = word["Text"]
    anas = word["Anas"]
    attrs = word.get("Attrs", {})
    out = []
    out.append('<body>')
    out.append('<result search-type="word-info">')
    out.append('<word text=%s>' % quoteattr(text))
    for ana in anas:
        out.append('<ana>')
        for key in ana:
            key2 = "gramm" if key == "gr" else key
            out.append('<el name=%s>' % quoteattr(key2))
            out.append('<el-group><el-atom>%s</el-atom></el-group>' % escape(ana[key]))
            out.append('</el>')
        out.append('</ana>')
    for key in attrs:
        out.append('<ana>')
        out.append('<el name=%s>' % quoteattr(key))
        out.append('<el-group><el-atom>%s</el-atom></el-group>' % escape(", ".join(attrs[key])))
        out.append('</el>')
        out.append('</ana>')
    out.append('</word>')
    out.append('</result>')
    out.append('</body>')
    wfile.write("".join(out).encode("utf-8"))

