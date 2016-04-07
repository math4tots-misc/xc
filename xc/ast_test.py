from . import lexer
from . import ast

class Counter(ast.Visitor):
  def __init__(self):
    self.count = 0

  def visit(self, *args, **kwargs):
    self.count += 1
    return super(Counter, self).visit(*args, **kwargs)

def main(verbose=True):
  t = lexer.lex(lexer.Source('<test>', ''))[-1]

  n = ast.Int(t, 5)
  c = Counter()
  c.visit(n)
  assert c.count == 1, c.count

  n = ast.Or(t, ast.Name(t, 'a'), ast.String(t, "hi"))
  c = Counter()
  c.visit(n)
  assert c.count == 3, c.count

  n = ast.clone(ast.Name(t, 'x'))
  assert type(n) == ast.Name, type(n)
  assert n.name == 'x', n.name

  if verbose:
    print('ast_test pass')

if __name__ == '__main__':
  main()

