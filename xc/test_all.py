from . import lexer_test

def main(verbose=True):
  lexer_test.main(False)
  if verbose:
    print('test_all pass')

if __name__ == '__main__':
  main()
