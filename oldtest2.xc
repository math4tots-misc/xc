"""oldtest2.xc

Tests trace message prints properly.

Kyumins-MacBook-Pro:xc math4tots$ python3 -m xc.test && python3 -m xc.main oldtest2.xc > a.cc && g++ --std=c++11 -Wall -Werror -Wpedantic a.cc && ./a.out
lexer_test pass
translator_test pass
xc.test pass
printing with stdout!!!
writing with stdout --- again using stdout
This is using print function, not the method

  *** in file "oldtest2.xc" in function "main" (defined on line 27)
  *** in file "oldtest2.xc" in function "Foo.<constructor>" (defined on line 51)
  *** in file "oldtest2.xc" in function "Foo.method" (defined on line 55)


--------------------
^^^ assertion failure: xxx
  *** in file "oldtest2.xc" in function "main" (defined on line 27)
  *** in file "oldtest2.xc" in function "Foo.<constructor>" (defined on line 51)
  *** in file "oldtest2.xc" in function "Foo.method" (defined on line 55)

"""

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

    print[trace[]]

    print['']

    # print[trace[].lines[].get[0]]

    assert[false, "xxx"]
  }
}
