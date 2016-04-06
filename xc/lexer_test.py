from . import lexer

def match(tokens, patterns):
  for tok, (type_, value) in zip(tokens, patterns):
    assert tok.type == type_, (type_, tok)
    assert tok.value == value, (value, tok)

def main(verbose=False):
  toks = lexer.lex(lexer.Source('<test>', '''while ab "c" 'd' 3\nf'''))
  match(toks, [
      ('while', 'while'),
      ('ID', 'ab'),
      ('STR', '"c"'),
      ('CHR', "'d'"),
      ('INT', '3'),
      ('ID', 'f'),
      ('EOF', None),
  ])
  assert toks[0].lineno() == 1, toks[0].lineno()  # while
  assert toks[-1].lineno() == 2, toks[-1].lineo()  # ID(f)

  if verbose:
    print('lexer_test pass')

if __name__ == '__main__':
  main(True)
