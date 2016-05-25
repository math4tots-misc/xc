"""Top level comments
Simple sanity check to see everything is working.
"""

class Example {
  "Class body comments"

  fn tr[] String {
    return trace[]
  }
}

fn calltr[s Example] String {
  return s.tr[]
}

fn main[] {
  "Function body comments"

  var tr = calltr[Example[]]
  var m = """Traceback (most recent call last):
  File "test.xc", line 20, in main
  File "test.xc", line 14, in calltr
  File "test.xc", line 9, in Example::tr
"""
  assert[tr == m, tr]

  ## string literals test
  assert['hi' == 'hi', 'foobar']
  assert['"' == "\""]

  ## simple vector operations test
  {
    var xs = $Int[]
    for i in $[4, 5, 6, 7] {
      xs.push[i]
    }
    assert[xs == $[4, 5, 6, 7], xs]
    assert[xs != $[4, 5, 6, 8], xs]
    assert[xs != $[56], xs]
    assert[$[5, 6] < $[5, 7]]
  }

  ## range test
  {
    var xs = $Int[]
    for i in range[3, 7] {
      xs.push[i]
    }
    assert[xs == $[3, 4, 5, 6], xs]
  }

  ## tuple test
  {
    let a, b = T[173, 'hi foobar']
    assert[a == 173, a]
    assert[b == 'hi foobar', b]
  }

  # print[ARGS]
  print['pass']
}
