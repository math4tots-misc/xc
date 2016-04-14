fn main[] {
  var s = new Set(String)[]
  assert[s.size[] == 0]
  s.add['hi']
  assert[s.size[] == 1]
  assert[s.has['hi']]
  s.add['a']
  assert[s.list[].sort[] == $String['a', 'hi']]
  print['core_set_test pass']
}
