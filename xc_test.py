from xc import Source, lex, parse, whitespace_pattern

assert whitespace_pattern.match('#  ')
s = '\n   # abc \n  xyz '
m = whitespace_pattern.match(s)
assert s[m.end():] == 'xyz ', repr(s[m.end():])

t = repr(lex(Source(
    '<test>', 'hi there 5 5.5 "hi" """hoi there""" # comments')))
assert t == (
    r'''[(ID, 'hi')@0, (ID, 'there')@3, (INT, '5')@9, ''' +
    r'''(FLT, '5.5')@11, (STR, '"hi"')@15, ''' +
    r'''(STR, '"""hoi there"""')@20, ''' +
    r'''(EOF, None)@46]'''), t

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

print('xc_test passes')
