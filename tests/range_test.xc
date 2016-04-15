fn main[] {
  var xs = $Int[]
  for i in range[0, 4] {
    xs.push[i]
  }
  assert[xs == $Int[0, 1, 2, 3], 'xs$1 = ' + repr[xs]]
  print['range_test pass']
}
