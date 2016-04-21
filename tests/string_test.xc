fn main[] {
  stdout.write['string_test... ']
  var words List(String)
  var lines List(String)

  words = ''.words[]
  assert[words == $String[], repr[words]]

  words = 'ab c'.words[]
  assert[words == $String['ab', 'c'], repr[words]]

  words = 'def'.words[]
  assert[words == $String['def'], repr[words]]

  words = ' def '.words[]
  assert[words == $String['def'], repr[words]]

  words = 'def '.words[]
  assert[words == $String['def'], repr[words]]

  words = '  wirh 89 .fw'.words[]
  assert[words == $String["wirh", "89", ".fw"], repr[words]]

  words = 'wirh 89 .fw  '.words[]
  assert[words == $String["wirh", "89", ".fw"], repr[words]]

  var text = r"""
a b c d
  asdf fghj
83/uoi.LKFJ 3940
"""

  words = text.words[]
  assert[
      words ==
      $String["a", "b", "c", "d", "asdf", "fghj", "83/uoi.LKFJ", "3940"],
      repr[words]]

  lines = text.lines[]
  assert[
      text.lines[] ==
      $String["a b c d", "  asdf fghj", "83/uoi.LKFJ 3940"],
      repr[lines]]


  {
    var format = "%s %% %s %%"
    var s String = format % $String['hi', 'there']
    assert[s == "hi % there %", '%: ' + s]

    assert['%s%s' % $String['hello', 'world'] == 'helloworld', '%2']
  }

  {
    var s = ', '.join[$String['a', 'b', 'cc']]
    assert[s == 'a, b, cc', repr[s]]
    s = ', '.join[$String[]]
    assert[s == '', repr[s]]
  }

  print['pass']
}
