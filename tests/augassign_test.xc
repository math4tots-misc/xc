fn main[] {
  var i = 10
  i += 12
  assert[i == 22, '+=' + repr[i]]

  i -= 7
  assert[i == 15, '-=' + repr[i]]

  var ec = new ExampleClass[]
  ec.i = 5
  ec.i += 10
  assert[ec.i == 15, 'attr += ' + repr[ec.i]]

  ec.i *= 10
  assert[ec.i == 150, 'attr *= ' + repr[ec.i]]

  ec.i /= 6
  assert[ec.i == 25, 'attr /= ' + repr[ec.i]]

  ec.i %= 4
  assert[ec.i == 1, 'attr %= ' + repr[ec.i]]

  ec.attr = 'hi'
  ec.attr += ' there'
  assert[ec.attr == 'hi there', 'str attr += ' + repr[ec.attr]]
}

class ExampleClass {
  var attr String
  var i Int
}

