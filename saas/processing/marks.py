from doc_iters import all_sents, all_words

_MARKS = {
    '.': "dot",
    ',': "comma",
    '!': "excl",
    '?': "ques",
    ':': "colon",
    ';': "semicolon",
    '/': "slash",
    '-': "dash",
    '"': "quot",
    "'": "apos",
    '(': "lparenth",
    ')': "rparenth",
    '[': "lbracket",
    ']': "rbracket",
    '<': "langle",
    '>': "rangle",
    '{': "lbrace",
    '}': "rbrace",
    '\\': "backslash",
    u'\u2015': "dash",
    u'\u2026': "dots",
}

def _insert_flags(word, prefix, values):
    if "Attrs" not in word:
        word["Attrs"] = {}
    if "flags" not in word["Attrs"]:
        word["Attrs"]["flags"] = []
    for value in values:
        word["Attrs"]["flags"].append(prefix + value)


def _inspect_marks(punct):
    values = set()
    for c in punct:
        if c in _MARKS:
            values.add(_MARKS[c])
    if "..." in punct:
        values.add("dots")
    if values:
        values.add("mark")
    return values


def set_marks(doc):
    for sent in all_sents(doc):
        words = sent["Words"]
        for i in xrange(len(words)):
            values = _inspect_marks(words[i]["Punct"])
            if values:
                _insert_flags(words[i], "a", values)
                if i > 0:
                    _insert_flags(words[i-1], "b", values)
        values = _inspect_marks(sent["Punct"])
        if values and words:
            _insert_flags(words[-1], "b", values)


def _normalize_punct_str(punct):
    punct = punct.replace("---", u"\u2015").replace("--", u"\u2015").replace(" - ", u"\u2015")
    punct = punct.replace("...", u"\u2026")
    return punct


def normalize_punct(doc):
    for word in all_words(doc):
        word["Punct"] = _normalize_punct_str(word["Punct"])
    for sent in all_sents(doc):
        sent["Punct"] = _normalize_punct_str(sent["Punct"])

