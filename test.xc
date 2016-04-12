fn main[args List(String)] {
  stdout.print["printing with stdout!!!"]
  stdout.write["writing with stdout --- "]
  stdout.print["again using stdout"]

  # var line = stdin.input[]
  # stdout.print["You typed: " + line]

  var fout = new FileWriter["sample.txt"]
  fout.print["This is some sample text!"]

  assert[true, "'true' should be true"]

  print["This is using print function, not the method"]

  print[""]

  # assert[false, "Failing due to false being false"]

  var f = new Foo[]
}


class Foo {
  fn[] {
    self.method[]
  }

  fn method[] {
    assert[false, "xxx"]
  }
}
