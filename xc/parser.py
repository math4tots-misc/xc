from . import lexer
from . import ast
from . import err

def parse(source):
  i = [0]
  toks = lexer.lex(source)

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
      raise err.Err(
          'Expected token of type %r but found %r' % (
              type_, peek()),
          peek())

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
    return ast.TranslationUnit(tok, incs, fns)

  def parse_include():
    tok = expect('include')
    uri = eval(expect('STR').value)
    return Include(tok, uri)

  def parse_function():
    tok = expect('fn')
    name = expect('ID').value
    args = []
    type_args = None
    if consume('('):
      type_args = []
      while not consume(')'):
        type_args.append(expect('ID').value)
        consume(',')
    expect('[')
    while not consume(']'):
      n = expect('ID').value
      t = parse_typename()
      args.append((n, t))
      consume(',')
    return_type = parse_typename()
    body = parse_block_statement()
    return ast.Function(tok, name, args, return_type, body)

  def parse_typename():
    name = expect('ID').value
    if consume('('):
      args = []
      while not consume(')'):
        args.append(parse_typename())
      return (name,) + tuple(args)
    else:
      return (name,)

  def parse_block_statement():
    tok = expect('{')
    stmts = []
    while not consume('}'):
      stmts.append(parse_statement())
    return ast.Block(tok, stmts)

  def parse_statement():
    tok = peek()
    if at('{'):
      return parse_block_statement()
    elif consume('return'):
      expr = parse_expression()
      expect(';')
      return ast.Return(tok, expr)
    elif consume('var'):
      name = expect('ID').value
      type_ = None
      if not at('='):
        type_ = parse_typename()
      expr = None
      if consume('='):
        expr = parse_expression()
      expect(';')
      if type_ is None and expr is None:
        raise err.Err(
            'Variable declaration must specify either type or ' +
            'expression or both', tok)
      return ast.Declaration(tok, name, type_, expr)
    else:
      expr = parse_expression()
      expect(';')
      return ast.ExpressionStatement(tok, expr)

  def parse_expression():
    return parse_postfix_expression()

  def parse_postfix_expression():
    expr = parse_primary_expression()
    while at('.'):
      tok = expect('.')
      name = expect('ID').value
      # TODO: attribute access
      typeargs = []
      if at('('):
        typeargs = parse_type_args()
      args = parse_args()
      expr = ast.MethodCall(tok, expr, name, typeargs, args)
    return expr

  def parse_primary_expression():
    tok = peek()
    if consume('('):
      expr = parse_expression()
      expect(')')
      return expr
    elif consume('new'):
      type_ = parse_typename()
      return ast.New(tok, type_)
    elif at('ID'):
      name = expect('ID').value
      if at('(') or at('['):
        typeargs = []
        if at('('):
          typeargs = parse_type_args()
        args = parse_args()
        return ast.FunctionCall(tok, name, typeargs, args)
      else:
        return ast.Name(tok, name)
    elif at('INT'):
      return ast.Int(tok, int(expect('INT').value))
    elif at('FLT'):
      return ast.Float(tok, float(expect('FLT').value))
    elif at('STR'):
      return ast.String(tok, eval(expect('STR').value))
    elif at('CHR'):
      return ast.Char(tok, eval(expect('CHR').value))
    else:
      raise SyntaxError('Expected expression but found %r' % peek())

  def parse_args():
    expect('[')
    args = []
    while not consume(']'):
      args.append(parse_expression())
      consume(',')
    return args

  def parse_type_args():
    expect('(')
    args = []
    while not consume(')'):
      args.append(parse_typename())
      consume(',')
    return args

  return parse_program()
