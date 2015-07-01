from doc_iters import all_sents, all_words

def _insert_flag(word, value):
    if "Attrs" not in word:
        word["Attrs"] = {}
    if "flags" not in word["Attrs"]:
        word["Attrs"]["flags"] = []
    word["Attrs"]["flags"].append(value)


def set_first_last(doc):
    for sent in all_sents(doc):
        if not sent["Words"]:
            continue
        _insert_flag(sent["Words"][0], "first")
        _insert_flag(sent["Words"][-1], "last")


def set_capital(doc):
    for word in all_words(doc):
        if word["Text"] and word["Text"][0].isupper():
            _insert_flag(word, "capital")

