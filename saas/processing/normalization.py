from doc_iters import all_words

def normalize_accents_str(s):
    pos = s.find("`")
    while pos >= 0 and pos + 1 < len(s):
        s = s[:pos] + s[pos + 1] + u'\u0301' + s[pos + 2:]
        pos = s.find("`", pos)
    return s

def normalize_accents(doc):
    for word in all_words(doc):
        word["Text"] = normalize_accents_str(word["Text"])

