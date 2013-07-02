# All rights belong to Non-commercial Partnership "Russian National Corpus"
# http://ruscorpora.ru

# editor marks inside a word
editor_brackets = ur'\[\]\<\>'

OUTPUT_ENCODING = 'cp1251'

def quotetext(s):
  if not s:
    return u""
  return s.replace(u'&', u'&amp;').replace(u'<', u'&lt;').replace(u'>', u'&gt;')

def quoteattr(s):
  return quotetext(s).replace(u"'", u'&#39;').replace(u'"', u'&#34;').replace(u'\n', u'&#xA;').replace(u'\r', u'&#xD;').replace(u'\t', u'&#x9;')