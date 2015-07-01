def all_sents(doc):
    for part in doc["Parts"]:
        for sent in part["Sents"]:
            yield sent


def all_words(doc):
    for sent in all_sents(doc):
        for word in sent["Words"]:
            yield word

