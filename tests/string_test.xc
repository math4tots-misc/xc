fn main[] {
  stdout.write['string_test... ']
  var words List(String)
  var lines List(String)

  assert[(words =''.words[]) == $String[], repr[words]]
  assert[(words = 'ab c'.words[]) == $String['ab', 'c'], repr[words]]
  assert[(words = 'def'.words[]) == $String['def'], repr[words]]
  assert[(words = ' def '.words[]) == $String['def'], repr[words]]
  assert[(words = 'def '.words[]) == $String['def'], repr[words]]
  assert[
      (words = '  wirh 89 .fw'.words[]) == $String["wirh", "89", ".fw"],
      repr[words]]
  assert[
      (words = 'wirh 89 .fw  '.words[]) == $String["wirh", "89", ".fw"],
      repr[words]]


  var text = r"""
a b c d
  asdf fghj
83/uoi.LKFJ 3940
"""

  assert[
      (words = text.words[]) ==
      $String["a", "b", "c", "d", "asdf", "fghj", "83/uoi.LKFJ", "3940"],
      repr[words]]

  assert[
      (lines = text.lines[]) ==
      $String["a b c d", "  asdf fghj", "83/uoi.LKFJ 3940"],
      repr[lines]]


  {
    var format = "%s %% %s %%"
    var s String
    assert[
        (s = format % $String['hi', 'there']) ==
        "hi % there %", '%: ' + s]

    assert['%s%s' % $String['hello', 'world'] == 'helloworld', '%2']
  }

  print['pass']
}
