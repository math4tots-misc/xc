from . import lexer

class Visitor(object):
  def visit(self, node, *args, **kwargs):
    method_name = 'visit' + type(node).__name__
    if hasattr(self, method_name):
      return getattr(self, method_name)(node, *args, **kwargs)
    else:
      return self.generic_visit(node, *args, **kwargs)

  def generic_visit(self, node, *args, **kwargs):
    return self.visit_children(node, *args, **kwargs)

  def visit_children(self, node, *args, **kwargs):
    for child in node.children():
      self.visit(child, *args, **kwargs)

def type_match(type_, arg):
  if isinstance(type_, type):
    return isinstance(arg, type_)
  elif isinstance(type_, tuple):
    return (
        isinstance(arg, tuple) and
        all(type_match(t, a) for t, a in zip(type_, arg)))
  elif isinstance(type_, list):
    return (
        isinstance(arg, list) and
        all(type_match(type_[0], a) for a in arg))
  raise TypeError('Invalid type %r' % type_)

class Ast(object):
  "special attributes: 'token' and 'sig'"
  def __init__(self, token, *args):
    sig = self.sig
    if len(sig) != len(args):
      raise ValueError(
          ('%s expects %d args (including the first Token argument),' +
          ' but got %d') % (
              type(self).__name__,
              1 + len(sig),
              1 + len(args)))
    if not isinstance(token, lexer.Token):
      raise TypeError(
          'First non-self argument to Ast.__init__' +
          'must be of a Token type')
    self.token = token
    for i, ((name, argtype), arg) in enumerate(zip(sig, args)):
      if not type_match(argtype, arg):
        raise TypeError('Expected %s for "%s" (%d) but got %r' % (
            argtype,
            name, i,
            arg))
      setattr(self, name, arg)

  def children(self):
    for name, type_ in self.sig:
      value = getattr(self, name)
      stack = [(value, type_)]
      while stack:
        value, type_ = stack.pop()
        if isinstance(type_, type) and issubclass(type_, Ast):
          yield value
        elif isinstance(type_, tuple):
          for v, t in reversed(tuple(zip(value, type_))):
            stack.append((v, t))
        elif isinstance(type_, list):
          for v in reversed(value):
            stack.append((v, type_[0]))

  def clone(self):
    return clone(self)

def clone(value):
  if isinstance(value, Ast):
    args = [getattr(value, x) for x, _ in value.sig]
    copy = type(value)(value.token, *args)
    for key in vars(value):
      setattr(copy, key, getattr(value, key))
    return copy
  elif isinstance(value, tuple):
    return tuple(map(clone, value))
  elif isinstance(value, list):
    return list(map(clone, value))
  else:
    return value

######

# 'Type' is a tuple of either 'str' or other 'Type'.
Type = tuple

class Expression(Ast):
  pass

class Bool(Expression):
  sig = [('value', bool)]
  type = ('Bool',)

class Char(Expression):
  sig = [('value', str)]
  type = ('Char',)

class Int(Expression):
  sig = [('value', int)]
  type = ('Int',)

class Float(Expression):
  sig = [('value', float)]
  type = ('Float',)

class String(Expression):
  sig = [('value', str)]
  type = ('String',)

class Name(Expression):
  sig = [('name', str)]

class Or(Expression):
  sig = [('left', Expression), ('right', Expression)]
  type = ('Bool',)

class New(Expression):
  sig = [('type', Type)]

class FunctionCall(Expression):
  sig = [
      ('name', str),
      ('typeargs', [Type]),
      ('args', [Expression]),
  ]

class MethodCall(Expression):
  sig = [
      ('owner', Expression),
      ('name', str),
      ('typeargs', [Type]),
      ('args', [Expression]),
  ]

class Statement(Ast):
  pass

class Block(Statement):
  sig = [('stmts', [Statement])]

class Declaration(Statement):
  sig = [
      ('name', str),
      ('type', object),  # Should be 'Type', but nullable.
      ('expr', object),  # Should be 'Expression', but nullable.
  ]

class Return(Statement):
  sig = [('expr', Expression)]

class ExpressionStatement(Statement):
  sig = [('expr', Expression)]

class Function(Ast):
  sig = [
      ('name', str),
      ('args', [(str, Type)]),
      ('return_type', Type),
      ('body', Statement),
  ]

class Include(Ast):
  sig = [('uri', str)]

class TranslationUnit(Ast):
  sig = [
        ('includes', [Include]),
        ('functions', [Function]),
    ]

class Program(Ast):
  sig = [('functions', [Function])]