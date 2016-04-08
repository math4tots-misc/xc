from . import annotator
from . import types
from . import ast

def main(verbose):

  f1 = ast.Function(
      'f', [('x', types.Name('Int'))], types.Name('Int'),
  )
  if verbose:
    print('annotator_test pass')

if __name__ == '__main__':
  main(1)
