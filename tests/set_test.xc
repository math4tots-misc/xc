fn main[] {
  stdout.write['set_test... ']
  var s = new Set(String)[]
  assert[s.size[] == 0]
  s.add['hi']
  assert[s.size[] == 1]
  assert[s.has['hi']]
  s.add['a']
  assert[s.list[].sort[] == $String['a', 'hi']]

  {
    var s = new Set(List(String))[]
    s.add[$String['a', 'b']]
    s.add[$String['a', 'b']]
    s.add[$String['a', 'b', 'c']]
    assert[s.size[] == 2, repr[s.size[]]]
  }

  {
    var s = new Set(Map(String, Int))[]
    s.add[new Map(String, Int)[].set['a', 1]]
    s.add[new Map(String, Int)[].set['a', 1]]
    assert[s.size[] == 1, repr[s.size[]]]
    s.add[new Map(String, Int)[].set['a', 2]]
    assert[s.size[] == 2, repr[s.size[]]]
  }

  print['pass']
}
