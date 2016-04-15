fn main[] {
  stdout.write['range_test... ']
  var xs = $Int[]
  for i in range[0, 4] {
    xs.push[i]
  }
  assert[xs == $Int[0, 1, 2, 3], 'xs$1 = ' + repr[xs]]
  print['pass']
}
