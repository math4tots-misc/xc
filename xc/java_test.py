from . import java
from . import ast
from . import lexer

def main(verbose):
  tr = java.Translator()

  t = lexer.lex(lexer.Source('<test>', ''))[-1]
  n = ast.Function(t, 'main', [], ('Int',), ast.Block(t, []))
  s = tr.visit(n)
  assert s == r"""
public static Int main()
{
}""", s

  if verbose:
    print('java_test pass')

if __name__ == '__main__':
  main(True)

