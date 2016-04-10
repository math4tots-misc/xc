from . import lexer_test
from . import translator_test

def main(verbose):
  lexer_test.main(verbose-1)
  translator_test.main(verbose-1)
  if verbose:
    print('xc.test pass')

if __name__ == '__main__':
  main(2)
