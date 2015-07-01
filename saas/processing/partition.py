import copy

MAX_PARTS_PER_BLOCK = 10

def split_long_sentences(doc):
    for part in doc["Parts"]:
        sents = part["Sents"]
        i = 0
        while i < len(sents):
            sent = sents[i]
            if len(sent["Words"]) >= 64:
                rest_sent = copy.deepcopy(sent)
                rest_sent["Words"] = rest_sent["Words"][63:]
                sent["Words"] = sent["Words"][:63]
                sent["Punct"] = ""
                sents.insert(i + 1, rest_sent)
            i += 1


def group_parts_in_blocks(doc):
    blocks = []
    block = []
    counter = 0
    for part in doc["Parts"]:
        block += part["Sents"]
        counter += 1
        if counter == MAX_PARTS_PER_BLOCK:
            blocks.append({"Sents": block})
            block = []
            counter = 0
    if block:
        blocks.append({"Sents": block})
    doc["Parts"] = blocks

