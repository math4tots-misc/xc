from xc import Source, lex, parse

assert repr(lex(Source('<test>', 'hi there 5 5.5 "hi" """hoi there"""'))) == r'''[(ID, 'hi')@0, (ID, 'there')@3, (INT, '5')@9, (FLT, '5.5')@11, (STR, '"hi"')@15, (STR, '"""hoi there"""')@20, (EOF, None)@35]'''

text = repr(parse(Source('<test>', r"""include 'lib'
include 'blarg'

fn gcd[a Int, b Int] Int {
  print[];
  print[a];
  print[(add_Int_Int[a, b])];
  print[add_Int_Int[a, 5]];
}
""")))

assert text == r"""
include'lib'
include'blarg'
fn'gcd'[('a', Type'Int'),('b', Type'Int')]
{
  Call'print'[];
  Call'print'[Name'a'];
  Call'print'[Call'add_Int_Int'[Name'a',Name'b']];
  Call'print'[Call'add_Int_Int'[Name'a',Int5]];
}""", text
