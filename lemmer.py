# coding: utf-8

# All rights belong to Non-commercial Partnership "Russian National Corpus"
# http://ruscorpora.ru

import sys
import re
import codecs
from collections import deque
import os

import semantics

import liblemmer_python_binding

to_encoding = codecs.getencoder("utf-8")
from_encoding = codecs.getdecoder("utf-8")

_Translate = {
    u'indet': u'indef',
    u'part': u'gen2',
    u'irreg': u'',
    u'dual': u'du',
    u'predic-1p-sg': u'perf',
    u'inpraes': u'gNotpast',
    u'praed': u'PRAEDIC',
    u'loc': u'loc2',
    u'abl': u'loc',
    u'predic-1p-pl': u'imperf',
    u'det': u'def',
    u'abbr': u'contr',
    u'dist': u'anom',
    u'impers': u'',
    u'geo': u'topon',
    u'obsol': u'oldused',
    u'parenth': u'PARENTH',
}

_good_grams = set([
    u"S", u"A", u"NUM", u"ANUM", u"V", u"ADV", u"PRAEDIC", u"PARENTH",
    u"SPRO", u"APRO", u"PRAEDICPRO", u"ADVPRO", u"PR", u"CONJ", u"PART", u"INTJ",u"COM",
    u"nom", u"voc", u"gen", u"gen2", u"dat", u"acc", u"acc2", u"ins", u"loc", u"loc2", u"adnum",
    u"indic", u"imper", u"imper2", u"inf", u"partcp", u"ger",
    u"poss", u"comp", u"comp2",
    u"supr", u"plen", u"brev",
    u"praes", u"fut", u"praet", u"aor", u"perf", u"imperf",
    u"tran", u"intr",
    u"sg", u"pl",
    u"1p", u"2p", u"3p",
    u"famn", u"persn", u"patrn",
    u"m", u"f", u"n", u"mf",
    u"act", u"pass", u"med",
    u"anim", u"inan",
    u"pf", u"ipf",
    u"d_flex", u"d_type", u"d_refltype", u"d_refl", u"d_part", u"d_contr", u"d_num", u"d_gend", u"d_pref",
    u"norm", u"ciph", u"anom", u"distort", u"bastard",
    u"INIT", u"abbr", u"0",
    u"diallex",
    u"topon",
    u"NONLEX", u"obsc"
])

_CapitalFeatures = set(["famn", "persn", "patrn", "topon"])
_DoNotRemoveDuplicates = set(["famn", "persn", "patrn", "topon"])

class Lemmer:
    def __init__ (self,
                  langs=[],
                  dictionaryPath="",
                  addPath="",
                  delPath="",
                  full=False,
                  addLang=False,
                  reallyAdd = False):
        self.langs = langs

        self.dictionary = semantics.SemanticDictionary(dictionaryPath)
        self.full = full
        self.addLang = addLang
        self.reallyAdd = reallyAdd

        self.Add = {}
        if addPath:
            f = codecs.getreader("windows-1251")(file(addPath, "rb"))
            for l in f:
                x = l.replace(u"<ana", "@") \
                    .replace("lex=", "") \
                    .replace("gr=", "") \
                    .replace("/>", "") \
                    .replace(">", "") \
                    .replace("\"", " ") \
                    .replace("=", ",") \
                    .rstrip() \
                    .split("@")
                form = x[0].lstrip().rstrip()
                if form not in self.Add:
                    self.Add[form] = []
                for el in x[1:]:
                    s = el.lstrip().rstrip().split()
                    lemma = s[0]
                    gramm = s[1]
                    (head, _, tail) = gramm.partition("(")
                    head = head.split(",")
                    category = head[0]
                    head = set(head)
                    head.discard("")
                    tail = (tail.partition(")")[0]).split("|")
                    res = []
                    for tl in tail:
                        s = set(tl.split(","))
                        s.discard("")
                        res.append(self.createAttrs("", lemma, category, head, s))
                    self.Add[form].append((lemma, res, 'ru', 1.0))
            f.close()

        self.Del = set()
        self.DelPatterns = []
        if delPath:
            f = codecs.getreader("windows-1251")(file(delPath, "rb"))
            for l in f:
                x = l.rstrip().split()
                if x[0].endswith("*"):
                    self.DelPatterns.append((x[0][:-1], x[1], set(x[2].split(','))))
                else:
                    self.Del.add(tuple(x[0:3]))
            f.close()

    def Reset(self):
        pass


    def parse(self, word, languageFilter=[]):
        result = (False, {})

        word = word.strip()
        if len(word) > 0:
            lword = word.lower()
            table = {} # (start, end) -> [(lemma, [(gramm, sem, semall)], language)]
            temp = self.Add.get(lword, None) # check if this word has it's own special morphological analysis

            if temp != None:
                if self.reallyAdd:
                    for el in temp:
                        table[(0, 1)] = table.get((0, 1), []) + [(el[0], el[1], 'ru', 1.0)]
                else:
                    return (False, {(0, 1): temp})
            else:
                temp = self.Add.get("+" + lword, None)
                if temp != None:
                    for el in temp:
                        table[(0, 1)] = table.get((0, 1), []) + [(el[0], el[1], 'ru', 1.0)]

            analyses = liblemmer_python_binding.AnalyzeWord(word, langs=self.langs)
            minNormFirst = maxNormLast = None
            for ana in analyses:
                language = ana.Language
                if len(languageFilter) > 0:
                    if language not in languageFilter:
                        continue

                first = ana.First
                last = ana.Last # + first
                lemma = ana.Lemma
                weight = ana.Weight if hasattr(ana, 'Weight') else 0.0
                head = ana.LexicalFeature
                if head == []: head = [u'']
                head = _toLatin(head)
                if word[0].isupper() and not set(head).isdisjoint(_CapitalFeatures):
                    lemma = lemma[0].upper() + lemma[1:]

                if ana.Bastardness in (0, 16):     # QDictionary, QBadRequest
                    head.append("norm")
                elif (ana.Bastardness % 4) in (1,2): # QBastard, QSob
                    head.append("bastard")
                else:
                    continue

                tail = list(ana.FormFeature)
                if tail == []: tail = ['']

                category = head[0]
                llemma = lemma.lower()
                if (word, lemma, category) in self.Del or (lword, llemma, category) in self.Del:
                    continue
                to_delete = False
                lexical_feature_set = set([_Translate[feature] if feature in _Translate else feature \
                                           for feature in ana.LexicalFeature])
                for (del_pattern, del_lemma, del_category) in self.DelPatterns:
                    if del_lemma in (lemma, llemma) and \
                       del_category.issubset(set(lexical_feature_set)) and \
                       (word.startswith(del_pattern) or lword.startswith(del_pattern)):
                        to_delete = True
                        break
                if to_delete:
                    continue

                gramm = [] # all grammatic attributes for this lemma
                for i in xrange(len(tail)):
                    t = _toLatin(tail[i])
                    tail[i] = t
                    gramm.extend(t)

                if language == "ru":
                    if "bastard" in head and "PARENTH" in head:
                        continue
                    if self.full: # m + f => mf
                        m = []
                        f = []
                        rest = []
                        for el in tail:
                            if "m" in el:
                                m.append(frozenset([e for e in el if e != "m"]))
                            elif "f" in el:
                                f.append(frozenset([e for e in el if e != "f"]))
                            else:
                                rest.append(el)
                        if set(m) == set(f):
                            tail = [list(e) + ["mf"] for e in m] + rest

                    add = []
                    gramms = frozenset(gramm)
                    if gramms.issuperset(("nom", "gen", "dat", "acc", "ins", "loc")) and not gramms.issuperset(("m", "f")):
                        if self.full:
                            add.append("0")
                        else:
                            add = None
                            gramm = [self.createAttrs(word, lemma, category, head, ["0"], language)]

                    if add != None:
                        gramm = []
                        for el in tail:
                            gramm.append(self.createAttrs(word, lemma, category, head, el + add, language))

                else: # other language
                    gramm = []
                    for el in tail:
                        gr = set(head[1:] + el)
                        gr.discard("")
                        if language in ("en", "ge"):
                            gr.discard("brev")
                            gr.discard("awkw")
                        if language == "ge":
                            if "PR" in gr:
                                gr.discard("dat")
                                gr.discard("gen")
                                gr.discard("acc")
                        if language == "uk" and "gNotpast" in gr:
                            gr.discard("gNotpast")
                            gr.add("fut")

                        gr = list(gr)
                        gr.sort()
                        gr = [category] + gr
                        gramm.append((",".join(gr), "", ""))

                if first == 0 and last > 1 and ana.Bastardness == 0 and language == "ru":
                    for rng in table.keys():
                        if rng[1] < last:
                            del table[rng]
                if (first, last) in table:
                    table[(first, last)].append((lemma, gramm, language, weight))
                else:
                    table[(first, last)] = [(lemma, gramm, language, weight)]
                if ana.Bastardness == 0 and language == "ru":
                    if minNormFirst == None:
                        minNormFirst, maxNormLast = first, last
                    elif first <= minNormFirst and last >= maxNormLast:
                        minNormFirst = first
                        maxNormLast = last

            if len(table) == 0:
                result = (False, {(0,1): [(word, [("NONLEX", "", "")], "ru", '0.0')]})
            else:
                complete_parse_builder = SegmentCoveringParseBuilder()
                complete_parse = complete_parse_builder.buildCompleteParse(word, table)
                # some parts of a compound word are not parsed (rejected or something),
                # falling back to a single 'NONLEX' part
                if not complete_parse:
                    result = (False, {(0, 1): [(word, [("NONLEX", "", "")], "ru", '0.0')]})
                else:
                    complete_parse = self._removeDuplicates(complete_parse)
                    compound = len(complete_parse) > 1
                    result = (compound, complete_parse)
        return result


    def _grammsSets(self, gramms):
        return [(set(gramm.split(",")), set(sem.split(",")), set(sem2.split(","))) for (gramm, sem, sem2) in gramms]


    def _isSubset(self, gramms1, gramms2):
        gramms1 = self._grammsSets(gramms1)
        gramms2 = self._grammsSets(gramms2)
        for gramm1 in gramms1:
            isIncluded = False
            for gramm2 in gramms2:
                if gramm1[0].issubset(gramm2[0]) and gramm1[1].issubset(gramm2[1]) and gramm1[2].issubset(gramm2[2]):
                    isIncluded = True
                    break
            if not isIncluded:
                return False
        return True


    def _removeDuplicates(self, table):
        newTable = {}
        for rng in table:
            newAnas = []
            discardIndices = set()
            for i in xrange(len(table[rng])):
                lemma_i, gramms_i, language_i, weight_i = table[rng][i]
                toRemove = False
                for j in xrange(len(table[rng])):
                    if i == j or j in discardIndices: continue
                    lemma_j, gramms_j, language_j, weight_j = table[rng][j]
                    if lemma_i == lemma_j and language_i == language_j:
                        if _DoNotRemoveDuplicates.isdisjoint(gramms_j[0]) and self._isSubset(gramms_i, gramms_j):
                            toRemove = True
                            break
                if not toRemove:
                    newAnas.append((lemma_i, gramms_i, language_i, weight_i))
                else:
                    discardIndices.add(i)
            if len(newAnas) > 0:
                newTable[rng] = newAnas
        return newTable


    def prefixCount(word, prefix):
        if words.startswith(prefix):
            return 1 + prefixCount(word[len(prefix):], prefix)
        return 0


    def createAttrs(self, word, lemma, category, head, tail, language=None):
        def prefixCount(word, prefix):
            if word.startswith(prefix):
                return 1 + prefixCount(word[len(prefix):], prefix)
            return 0

        gramm = list(_fixGramm(category, head, tail))
        if language=="ru" and "imper" in gramm and (word.endswith(u"мте") or word.endswith(u"мтесь")):
            gramm[gramm.index("imper")] = "imper2"
        # comp -> comp2 for words with true prefix "по"
        if language=="ru" and "comp" in gramm and prefixCount(word, u"по") > prefixCount(lemma, u"по"):
            subword = word[2:]
            subanalyses = liblemmer_python_binding.AnalyzeWord(subword, langs=["ru"])
            for ana in subanalyses:
                if ana.First == 0 and ana.Last == 1 and ana.Bastardness == 0:
                    subhead = _toLatin(ana.LexicalFeature)
                    subtail = set()
                    for ff in ana.FormFeature:
                        subtail |= set(_toLatin(ff))
                    if "comp" in subhead or "comp" in subtail:
                        gramm[gramm.index("comp")] = "comp2"
                        break

        if self.addLang and language != None:
            gramm.append(language)
        entry = self.dictionary.get((category + ":" + lemma).lower())
        if entry:
            sem = ""
            semall = ""
            primary_semantics = semantics._semantic_filter(entry.primary_features, category, gramm)
            secondary_semantics = semantics._semantic_filter(entry.secondary_features, category, gramm)

            if primary_semantics:
                sem = " ".join(primary_semantics)
            if secondary_semantics:
                semall = " ".join(secondary_semantics)

            return (",".join(gramm), sem, semall)
        else:
            return (",".join(gramm), "", "")

# given a set of parsed word segments, finds a connected sequence
# of segments with maximal individual length
class SegmentCoveringParseBuilder(object):

    def __getSegmentsRelativePosition(self, in_first, in_second):
        # segments are supposed to be sorted at the input
        if in_second[0] > in_first[1]:
            return 'NOT_ADJACENT'
        if in_first[0] == in_second[0] and in_first[1] <= in_second[1]:
            return 'FIRST_ENCLOSED_BY_SECOND'
        if in_first[0] <= in_second[0] and in_second[1] <= in_first[1]:
            return 'SECOND_ENCLOSED_BY_FIRST'
        if in_second[0] == in_first[1] and in_first[1] < in_second[1]:
            return 'ADJACENT'
        if in_first[0] < in_second[0] and in_second[0] < in_first[1] and in_first[1] < in_second[1]:
            return 'INTERSECTED'

    # building a parse for the entire input phrase
    # by combining partial parses
    def buildCompleteParse(self, in_word, in_parse_table):
        atomic_parts_number = len(re.split('\-+|\'', in_word))

        result_parse = {}
        segments = sorted(in_parse_table.keys())
        # adding fake intervals to make sure we have a connected sequence of intervals
        # from the start to the beginning of the word
        segments = [(0, 0)] + segments + [(atomic_parts_number, atomic_parts_number)]

        result_segments = deque([])
        segment_index = 0
        while segment_index != len(segments):
            interval = segments[segment_index]
            if not len(result_segments):
                result_segments.append(interval)
                segment_index += 1
                continue
            last_interval = result_segments[-1]
            relative_position = self.__getSegmentsRelativePosition(last_interval, interval)
            if relative_position == 'FIRST_ENCLOSED_BY_SECOND':
                result_segments.pop()
                result_segments.append(interval)
            elif relative_position == 'ADJACENT' and interval[0] != interval[1]:
                result_segments.append(interval)
            elif relative_position == 'NOT_ADJACENT':
                return None
            segment_index += 1

        for result_segment in result_segments:
            result_parse[result_segment] = in_parse_table[result_segment]
        return result_parse

def _toLatin(gramms):
    res = []
    for el in gramms:
        res.append(_Translate.get(el, el))
    return res

def _fixGramm(category, head, tail):
    gramm = set(head)
    gramm.update(tail)

    if "gNotpast" in gramm:
        if "pf" in gramm and "ger" not in gramm:
            gramm.add("fut")
        else:
            gramm.add("praes")

    if (("A" in gramm) or ("partcp" in gramm)) and not ("brev" in gramm) and not ("supr" in gramm) and not ("comp" in gramm):
        gramm.add("plen")

    if ("V" in gramm) and not ("pass" in gramm):
        gramm.add("act")

    if ("V" in gramm) and not ("imper" in gramm) and not ("inf" in gramm) and not ("partcp" in gramm) and not ("ger" in gramm):
        gramm.add("indic")

    if ("obsc" in gramm) and not ("norm" in gramm):
        gramm.discard("obsc")

    if ("S" in gramm) and ("brev" in gramm):
        gramm.discard("brev")

    if "anom" in gramm:
        gramm.discard("norm")

    if ("ADV" in gramm or category == "ADV") and ("PRAEDIC" in gramm or category == "PRAEDIC"):
        gramm.discard("ADV")
        if category == "ADV":
            category = "PRAEDIC"

    if ("ADV" in gramm or category == "ADV") and ("PARENTH" in gramm or category == "PARENTH"):
        gramm.discard("ADV")
        if category == "ADV":
            category = "PARENTH"

    gramm.discard(category)
    gramm.discard("")
    gramm = list(gramm)
    gramm = list(_good_grams.intersection(gramm))
    gramm.sort()
    gramm = [category] + gramm
    if gramm == ["bastard"] or gramm == []:
        gramm.append("NONLEX")
    return gramm

def _badGramms(path):
    out = codecs.getwriter("utf-8")(file(path, "wb"), 'xmlcharrefreplace')
    for (key, val) in _Translate.items():
        if val not in _good_grams:
            out.write("%s;%s;\n" % (key, val))
    out.close()

def main():
    # debug only
    out = codecs.getwriter("utf-8")(sys.stdout, 'xmlcharrefreplace')

    out.write("...\n")
    lemm = Lemmer(langs=['ru'],
                  addPath=os.path.join('tables', 'add.cfg'),
                  delPath=os.path.join('tables', 'del.cfg'))
    out.write(">\n")

    while True:
        l = sys.stdin.readline()
        if not l:
            break
        ul = codecs.getdecoder("utf-8")(l, "replace")[0]
        (b, x) = lemm.parse(ul)
        out.write("%s %s:\n" % (b, len(x)))
        for (key, val) in x.items():
            out.write("    %s %s:\n" % (key[0], key[1]))
            for el in val:
                out.write("        ")
                for ell in el:
                    out.write("%s " % ell)
                out.write("\n")

if __name__ == "__main__":
    main()

