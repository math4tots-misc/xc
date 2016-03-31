"""xc.py

fn gcd[a Int, b Int] Int {
  // ...
}

"""

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
    'var', 'include')
whitepsace_pattern = compile_re(r'\s*')
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
  i = whitepsace_pattern.match(s).end()
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
    i = whitepsace_pattern.match(s, i).end()
  tokens.append(Token('EOF', None, i, source))
  return tokens

class TranslationUnit(object):
  def __init__(self, token, includes, functions):
    self.token = token
    self.includes = includes
    self.functions = functions

  def __repr__(self):
    return (
        ''.join(map(str, self.includes)) +
        ''.join(map(str, self.functions)))

class Include(object):
  def __init__(self, token, uri):
    self.token = token
    self.uri = uri

  def __repr__(self):
    return '\ninclude%r' % self.uri

class Function(object):
  def __init__(self, token, name, args, return_type, body):
    self.token = token
    self.name = name
    self.args = args
    self.return_type = return_type
    self.body = body

  def __repr__(self):
    return '\nfn%r[%s]%s' % (
        self.name, ','.join(map(str, self.args)),
        self.body)

class Typename(object):
  def __init__(self, token, name):
    self.token = token
    self.name = name

  def __repr__(self):
    return 'Type%r' % self.name

class BlockStatement(object):
  def __init__(self, token, statements):
    self.token = token
    self.statements = statements

  def __repr__(self):
    return ('\n{%s\n}' % ''.join(map(str, self.statements))
        .replace('\n', '\n  '))

class ReturnStatement(object):
  def __init__(self, token, expression):
    self.token = token
    self.expression = expression

  def __repr__(self):
    return '\nreturn %s;' % self.expression

class ExpressionStatement(object):
  def __init__(self, token, expression):
    self.token = token
    self.expression = expression

  def __repr__(self):
    return '\n%r;' % self.expression

class FunctionCallExpression(object):
  def __init__(self, token, name, args):
    self.token = token
    self.name = name
    self.args = args

  def __repr__(self):
    return 'Call%r[%s]' % (self.name, ','.join(map(str, self.args)))

class NameExpression(object):
  def __init__(self, token, name):
    self.token = token
    self.name = name

  def __repr__(self):
    return 'Name%r' % self.name

class IntExpression(object):
  def __init__(self, token, value):
    self.token = token
    self.value = value

  def __repr__(self):
    return 'Int%d' % self.value

class FloatExpression(object):
  def __init__(self, token, value):
    self.token = token
    self.value = value

  def __repr__(self):
    return 'Float%f' % self.value

class StringExpression(object):
  def __init__(self, token, value):
    self.token = token
    self.value = value

  def __repr__(self):
    return 'String%r' % self.value

def parse(source):
  i = [0]
  toks = lex(source)

  def peek():
    return toks[i[0]]

  def gettok():
    i[0] += 1
    return toks[i[0]-1]

  def at(type_):
    return peek().type == type_

  def consume(type_):
    if at(type_):
      return gettok()

  def expect(type_):
    if at(type_):
      return gettok()
    else:
      raise SyntaxError('Expected token of type %r but found %r' % (
          type_, peek()))

  ############

  def parse_program():
    tok = peek()
    incs = []
    fns = []
    while not at('EOF'):
      if at('include'):
        incs.append(parse_include())
      elif at('fn'):
        fns.append(parse_function())
      else:
        raise SyntaxError('Failed to parse at %r' % peek())
    return TranslationUnit(tok, incs, fns)

  def parse_include():
    tok = expect('include')
    uri = eval(expect('STR').value)
    return Include(tok, uri)

  def parse_function():
    tok = expect('fn')
    name = expect('ID').value
    args = []
    expect('[')
    while not consume(']'):
      n = expect('ID').value
      t = parse_typename()
      args.append((n, t))
      consume(',')
    return_type = parse_typename()
    body = parse_block_statement()
    return Function(tok, name, args, return_type, body)

  def parse_typename():
    # TODO: Parametric types.
    tok = peek()
    name = expect('ID').value
    return Typename(tok, name)

  def parse_block_statement():
    tok = expect('{')
    stmts = []
    while not consume('}'):
      stmts.append(parse_statement())
    return BlockStatement(tok, stmts)

  def parse_statement():
    tok = peek()
    if at('{'):
      return parse_block_statement()
    elif consume('return'):
      expr = parse_expression()
      expect(';')
      return ReturnStatement(tok, expr)
    else:
      expr = parse_expression()
      expect(';')
      return ExpressionStatement(tok, expr)

  def parse_expression():
    return parse_primary_expression()

  def parse_primary_expression():
    tok = peek()
    if consume('('):
      expr = parse_expression()
      expect(')')
      return expr
    elif at('ID'):
      name = expect('ID').value
      if consume('['):
        args = []
        while not consume(']'):
          args.append(parse_expression())
          consume(',')
        return FunctionCallExpression(tok, name, args)
      else:
        return NameExpression(tok, name)
    elif at('INT'):
      return IntExpression(tok, int(expect('INT').value))
    elif at('FLT'):
      return FloatExpression(tok, float(expect('FLT').value))
    elif at('STR'):
      return StringExpression(tok, eval(expect('STR').value))
    else:
      raise SyntaxError('Expected expression but found %r' % peek())

  return parse_program()
