var x = 424

var s String

var ss = 'hello world!'

fn main[] {
  stdout.write['globalvars_test... ']
  assert[x == 424, 'before local assignment ' + repr[x]]
  x = 77
  assert[x == 77, 'after local assignment ' + repr[x]]
  assert[ss == 'hello world!', 'globally assigned string ' + repr[ss]]
  assert[s is nil, 'global unassigned string should be nil ']
  s = 'hi'
  assert[s == 'hi', 'local assigned string ' + repr[s]]
  print['pass']
}
