fn main[args List(String)] {
  stdout.print["printing with stdout!!!"]
  stdout.write["writing with stdout --- "]
  stdout.print["again using stdout"]

  # var line = stdin.input[]
  # stdout.print["You typed: " + line]

  var fout = new FileWriter["sample.txt"]
  fout.print["This is some sample text!"]
}
