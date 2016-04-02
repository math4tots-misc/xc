from .lex import Source, lex

class Visitor(object):
  """Parse tree visitor"""
  def visit(self, node, *args, **kwargs):
    method_name = 'visit' + type(node).__name__
    return getattr(self, method_name)(node, *args, **kwargs)

## Ast classes

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

  def signature(self):
    """This is what determines whether a function is duplicated"""
    return '%s(%s)' % (
        self.name, ','.join(t.signature() for _, t in self.args))

class Typename(object):
  def __init__(self, token, type_):
    self.token = token
    self.type = type_

  def signature(self):
    return str(self.type)

  def __repr__(self):
    return 'Type%r' % self.type

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
    tok = peek()
    name = type_ = expect('ID').value
    if consume('('):
      args = []
      while not consume(')'):
        args.append(parse_typename().type)
      type_ = (name,) + tuple(args)
    return Typename(tok, type_)

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
