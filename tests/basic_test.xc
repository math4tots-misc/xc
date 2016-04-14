fn main[] {
  assert[true, 'true']
  assert[not false, 'not false']

  assert[true and true, 'and']
  assert[not (true and false), 'and2']
  assert[not (false and false), 'and3']

  assert[true or true, 'or']
  assert[true or false, 'or2']
  assert[not (false or false), 'or3']

  assert[1 < 2, 'lt']
  assert[2 > 1, 'gt']
  assert[1 <= 1, 'le']
  assert[1 <= 2, 'le2']
  assert[2 >= 1, 'ge']
  assert[2 >= 2, 'ge2']

  var x = new ExampleClass[]
  var y = new ExampleClass[]
  assert[x is x, '"is" operator']
  assert[x is not y, '"is not" operator']

  assert[repr[c'x'] == "c'x'", 'char repr']
  assert[str[c'x'] == "x", 'char str']
  assert[repr['hello world'] == '"hello world"', 'str repr']
  assert[str['hello world'] == 'hello world', 'str str']
  assert[repr[5] == '5', 'int repr']
  assert[repr[5.0] == '5.000000', 'float repr: ' + repr[5.0]]

  assert[float['5.20'] == 5.2, 'str2float']
  assert[int['72'] == 72, 'str2int']

  var xs = $Int[1, 2, 3]
  assert[str[xs] == "[1, 2, 3]", "str list"]

  assert[$String["4", "5", "75"].map[int] == $Int[4, 5, 75]]

  # .map[fn[i Int] Float {
  #   return i + 7
  # }]

  var z String
  var a String
  assert[z is nil]
  assert[not (z is not nil)]
  z = 'hi'
  assert[z is not nil]
  assert[not (z is nil)]
  assert['hi' == z]
  z = nil
  assert[z is nil]
  assert[not (z is not nil)]

  var ec = new ExampleClass[]
  assert[ec.attr is nil]
  ec.attr = 'hello'
  assert[ec.attr is not nil]
  assert[ec.attr == 'hello']
  ec.attr = nil
  assert[ec.attr is nil]

  assert['hello'.size[] == 5]
  assert[$String['a', 'b', 'c'].size[] == 3]
  assert[$Int[45, 64].size[] == 2]

  print['basic_test pass']
}

class ExampleClass {
  var attr String
}
