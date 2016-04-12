from . import translator
from . import lexer


def main(verbose):
  expression_tests()
  whole_program_tests()
  if verbose:
    print('translator_test pass')


def expression_tests():
  s = lexer.Source('<test>', '43')
  t = translator.Translator(None, s)
  a = t.parse_expression()
  assert a == '43LL', a

  s = lexer.Source('<test>', '43.3')
  t = translator.Translator(None, s)
  a = t.parse_expression()
  assert a == '43.3', a

  s = lexer.Source('<test>', 'xxx')
  t = translator.Translator(None, s)
  a = t.parse_expression()
  assert a == 'xcv_xxx', a

  s = lexer.Source('<test>', 'new X[5]')
  t = translator.Translator(None, s)
  a = t.parse_expression()
  assert a == 'xct_X(new xct_X::Pointee(5LL))', a

  s = lexer.Source('<test>', '$Int[1, 2, 3]')
  t = translator.Translator(None, s)
  a = t.parse_expression()
  assert a == 'xct_List<xct_Int>(new xcs_List<xct_Int>({1LL, 2LL, 3LL}))', a

  s = lexer.Source('<test>', '''$List(Int)[
      $Int[1, 2, 3],
      $Int[4, 5, 6],
  ]''')
  t = translator.Translator(None, s)
  a = t.parse_expression()
  assert a == ('xct_List<xct_List<xct_Int>>(' +
    'new xcs_List<xct_List<xct_Int>>({' +
    'xct_List<xct_Int>(new xcs_List<xct_Int>({1LL, 2LL, 3LL})), ' + 'xct_List<xct_Int>(new xcs_List<xct_Int>({4LL, 5LL, 6LL}))}))'), a


def whole_program_tests():
  s = lexer.Source('<test>', r"""
fn f[] Void {}
fn main[] Void {}
""")
  t = translator.Translator(None, s)
  a, b, c, d = t.parse_program()
  assert a == '', a  # forward type declarations
  assert b == '', b  # type declarations
  assert c == r"""
xct_Void xcf_f();
xct_Void xcf_main();""", c  # function declarations/global var decls
  assert d == r"""
xct_Void xcf_f()
{
}
xct_Void xcf_main()
{
}""", d  # function/method definitions

  s = lexer.Source('<test>', r"""
class C {
  fn m[i Int] Float { return 4.5 }
}
fn main[] {}
""")
  t = translator.Translator(None, s)
  a, b, c, d = t.parse_program()
  assert a == r"""
struct xcs_C;
using xct_C = SharedPtr<xcs_C>;""", a  # forward type declarations
  assert b == r"""
struct xcs_C: xcs_Object
{
  xct_Float xcm_m(xct_Int xcv_i);
};""", b  # type declarations
  assert c == r"""
xct_Void xcf_main();""", c  # function declarations/global var decls
  assert d == r"""
xct_Float xcs_C::xcm_m(xct_Int xcv_i)
{
  return 4.5;
}
xct_Void xcf_main()
{
}""", d  # function/method definitions


if __name__ == '__main__':
  main(1)
