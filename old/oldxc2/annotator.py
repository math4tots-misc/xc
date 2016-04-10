from . import ast
from . import err
from . import types


def annotate(program):
  decorate_classes_with_interfaces(program)

def decorate_classes_with_interfaces(program):
  for c in program.classes:
    itfs = []
    for itf in program.interfaces:
      if class_implements_interface(c, itf):
        itfs.append(itf)
    c.interfaces = itfs

def class_implements_interface(c, itf):
  for im in itf.methods:
    for cm in c.methods:
      if method_signatures_match(im, cm):
        break
    else:
      return False
  return True

def method_signatures_match(a, b):
  return (
      len(a.args) == len(b.args) and
      all(ta == tb for (_, ta), (_, tb) in zip(a.args, b.args)) and
      a.ret == b.ret)

## WIP below this line

class TypeAnnotator(ast.Visitor):

  def __init__(self):
    self.cache = None

  def visitProgram(self, node):
    if not hasattr(node, 'cache'):
      cache = ProgramTypeCache()
      cache.visit(node)
      node.cache = cache
    return self.generic_visit(node, cache)

  def visitTernary(self, node, cache, vartypes):
    self.visit(node.cond, cache, vartypes)
    self.visit(node.left, cache, vartypes)
    self.visit(node.right, cache, vartypes)
    if node.cond.type != types.Name('Bool'):
      raise err.Err(
          'Conditional expression must be Bool (found %s)' % (
              node.cond.type,),
          node.cond.token)
    if node.left.type != node.right.type:
      raise err.Err(
          'Ternary expression type mismatch left=%s, right=%s' % (
              node.left.type, node.right.type),
          node.left.token,
          node.right.token)
    node.type = node.left.type


class ProgramTypeCache(ast.Visitor):

  def __init__(self):
    self.classes = dict()
    self.interfaces = dict()
    self.functions = dict()

  def visitClass(self, node):
    if node.name in self.classes:
      raise err.Err(
          'Duplicate class definition',
          self.classes[node.name].token,
          node.token)
    self.classes[node.name] = node

  def visitInterface(self, node):
    if node.name in self.interfaces:
      raise err.Err(
          'Duplicate interface definition',
          self.interfaces[node.name].token,
          node.token)
    self.interfaces[node.name] = node

  def visitFunction(self, node):
    if node.name in self.functions:
      raise err.Err(
          'Duplicate function definition',
          self.functions[node.name].token,
          node.token)
    self.functions[node.name] = node
