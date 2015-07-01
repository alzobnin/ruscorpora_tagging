from doc_iters import all_sents, all_words

def _insert_attr(word, attr, value):
    if "Attrs" not in word:
        word["Attrs"] = {}
    if attr not in word["Attrs"]:
        word["Attrs"][attr] = []
    word["Attrs"][attr].append(value)


def _reverse(doc, attr, rev_attr):
    for word in all_words(doc):
        if attr == "lex":
            for ana in word["Anas"]:
                val = ana["lex"]
                if val:
                    _insert_attr(word, rev_attr, val[::-1])
        elif attr == "form":
            val = word["Text"]
            if val:
                 _insert_attr(word, rev_attr, val[::-1])


def set_reversed(doc):
    _reverse(doc, "lex", "rlex")
    _reverse(doc, "form", "rform")

