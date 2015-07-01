import sys
import json
import xml.sax

class XMLHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.doc = {"Attrs": [], "Parts": []}
        self.buf = ""
        self.part_counter = 0

    def LastPart(self):
        if not self.doc["Parts"]:
            self.doc["Parts"].append({"Sents": []})
        return self.doc["Parts"][-1]

    def LastSent(self):
        return self.LastPart()["Sents"][-1]

    def LastWord(self):
        return self.LastSent()["Words"][-1]

    def LastAna(self):
        return self.LastWord()["Anas"][-1]

    def AddPunct(self, node):
        if self.buf.endswith("\n"):
            self.buf = self.buf[:-1]
            if not self.buf:
                self.buf = " "
        node["Punct"] = self.buf
        self.buf = ""

    def startElement(self, name, attrs):
        if name == "meta":
            self.doc["Attrs"].append((attrs["name"], attrs["content"]))
        elif name == "p":
            self.doc["Parts"].append({"Sents": []})
        elif name == "se":
            self.LastPart()["Sents"].append({"Words": []})
            self.buf = ""
        elif name == "w":
            self.LastSent()["Words"].append({"Anas": []})
            self.AddPunct(self.LastWord())
            self.form = ""
        elif name == "ana":
            self.LastWord()["Anas"].append({})
            for key, val in attrs.items():
                self.LastAna()[key] = val

    def endElement(self, name):
        if name == "w":
            self.LastWord()["Text"] = self.buf
            self.buf = ""
        elif name == "se":
            self.AddPunct(self.LastSent())
            if not self.LastSent()["Words"]:
                self.LastPart()["Sents"].pop()

    def characters(self, buf):
        self.buf += buf


def process(inpath):
    handler = XMLHandler()
    xml.sax.parse(inpath, handler)
    return handler.doc


def dumps(inpath):
    doc = process(inpath)
    return json.dumps(doc, ensure_ascii=False, indent=0)


def main():
    inpath = sys.argv[1]
    result = dumps(inpath)
    with open(inpath + ".json", "w") as f:
        f.write(result.encode("utf-8"))

if __name__ == "__main__":
    main()
