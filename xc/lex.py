import re

def compile_re(pattern):
  return re.compile(pattern, re.DOTALL|re.MULTILINE)

class Source(object):
  def __init__(self, filespec, data):
    self.filespec = filespec
    self.data = data

symbols = ('(', ')', '[', ']', '{', '}', '.', ',', ';')
keywords = (
    'fn', 'return', 'if', 'else', 'while', 'break', 'continue',
    'var', 'include', 'extern')
whitespace_pattern = compile_re(r'(?:\s|#.*?$)*')
err_pattern = compile_re(r'\S+')
token_table = tuple((type_, compile_re(pattern)) for type_, pattern in
    [
      ('STR', r'"""(?:\\|(?!\"\"\").)*"""'),
      ('STR', r"'''(?:\\|(?!\'\'\').)*'''"),
      ('STR', r'"(?:\\|(?!\").)*"'),
      ('STR', r"'(?:\\|(?!\').)*'"),
      ('STR', r'r""".*?"""'),
      ('STR', r"r'''.*?'''"),
      ('STR', r'r".*?"'),
      ('STR', r"r'.*?'"),
      ('FLT', r'\d+\.\d*'),
      ('FLT', r'\d*\.\d+'),
      ('INT', r'\d+'),
    ] +
    [(kw, r'\b%s\b' % kw) for kw in keywords] +
    [(sym, re.escape(sym)) for sym in symbols] +
    [('ID', r'\w+')])

class Token(object):
  def __init__(self, type_, value, i, source):
    self.type = type_
    self.value = value
    self.i = i
    self.source = source

  def __repr__(self):
    return '(%s, %r)@%d' % (self.type, self.value, self.i)

def lex(source):
  s = source.data
  i = 0
  tokens = []
  i = whitespace_pattern.match(s).end()
  while i < len(s):
    for type_, pattern in token_table:
      m = pattern.match(s, i)
      if m:
        tokens.append(Token(type_, m.group(), i, source))
        i = m.end()
        break
    else:
      raise SyntaxError(
          "Unrecognized token %r" % err_pattern.match(s, i).group())
    i = whitespace_pattern.match(s, i).end()
  tokens.append(Token('EOF', None, i, source))
  return tokens
