from . import translator
from . import lexer

def main(verbose):
  s = lexer.Source('<test>', r"""
fn f[] Void {}
fn main[] Void {}
""")
  t = translator.Translator(s)
  a, b, c = t.parse_program()
  assert a == '', a
  assert b == r"""
xct_Void xcf_f();
xct_Void xcf_main();""", b
  assert c == r"""
xct_Void xcf_f()
{
}
xct_Void xcf_main()
{
}""", c

  s = lexer.Source('<test>', '43')
  t = translator.Translator(s)
  a = t.parse_expression()
  assert a == '43LL', a

  s = lexer.Source('<test>', '43.3')
  t = translator.Translator(s)
  a = t.parse_expression()
  assert a == '43.3', a

  s = lexer.Source('<test>', 'xxx')
  t = translator.Translator(s)
  a = t.parse_expression()
  assert a == 'xcv_xxx', a

  if verbose:
    print('translator_test pass')

if __name__ == '__main__':
  main(1)
