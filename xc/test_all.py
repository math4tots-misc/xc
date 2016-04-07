from . import lexer_test
from . import ast_test
from . import annotator_test

def main(verbose):
  lexer_test.main(verbose-1)
  ast_test.main(verbose-1)
  annotator_test.main(verbose-1)
  if verbose:
    print('test_all pass')

if __name__ == '__main__':
  main(2)
