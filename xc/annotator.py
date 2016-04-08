from . import ast
from . import err


builtin_type_data = {
    'println': 'Void',
}


def annotate(program):
  cache = TypeCache(program)
  return Annotator(cache).visit(program)

class Annotator(ast.Visitor):
  def __init__(self, cache):
    self.cache = cache

  def visitFunction(self, node):
    self.visit_children(node, {n:t for n, t in node.args})

  def visitDeclaration(self, node, vartypes):
    self.visit_children(node, vartypes)
    vartypes[node.name] = node.expr.type
    if node.type is not None:
      if node.type != node.expr.type:
        raise err.Err(
            'Type mismatch: expected %r but got %r' % (
                node.type,
                node.expr.type),
            node.token)
    else:
      node.type = node.expr.type

  def visitName(self, node, vartypes):
    if node.name not in vartypes:
      raise err.Err(
          'Variable %r used without being declared' % node.name,
          node.token)
    node.type = vartypes[node.name]

  def visitFunctionCall(self, node, vartypes):
    self.visit_children(node, vartypes)
    node.type = self.cache.get_function_type(node.name, node.token)

  def visitMethodCall(self, node, vartypes):
    self.visit_children(node, vartypes)
    node.type = self.cache.get_method_type(
        node.owner.type, node.name, node.token)

# TODO: Take into consideration genefric arguments.
class TypeCache(object):
  def __init__(self, program):
    data = dict(builtin_type_data)
    ## TODO
    # for c in program.classes:
    #   cn = (c.name,)
    #   for m in c.methods:
    #     data[cn, m.name] = m.return_type
    for f in program.functions:
      data[f.name] = f.return_type
    self.data = data

  def get_method_type(self, owner_type, name, token):
    # TODO: Take into consideration genefric arguments.
    key = (owner_type[0], name)
    if key not in self.data:
      e = err.Err('Method %r not defined' % (key,))
      if token is not None:
        e.add_token(token)
      raise e
    return self.data[key]

  def get_function_type(self, name, token):
    if name not in self.data:
      e = err.Err('Function %r not defined' % name)
      if token is not None:
        e.add_token(token)
      raise e
    return self.data[name]


