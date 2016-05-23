fn g[i Int] Int {
  return f[i - 1]
}

fn f[i Int] Int {
  if i == 1 {
    return g[i]
  } else {
    return i
  }
}

fn h[] {
  print['hi!']
}

class Sample {

  fn[] {
    print['Inside Sample constructor!']
  }

  fn method[] Int {
    return 5
  }

  fn mmstr[] String {
    return '<Sample>'
  }
}

var x Int = 5

fn outer[] {
  print["hello\nworld"]
  var i = 5532
  print[i]
  var s = Sample[]
  # print[s.method[]]
  print['end outer']
}

fn main[] {
  outer[]
  print['end main']
  h[]
  print[x]
  x += 1
  print[x]
  for i in range[10, 20] {
    print[i]
  }

  for i in $[5, 7, 22] {
    print[i]
  }

  var t = T[57, "hi", Sample[]]
  print[t]

  print[$[1, 2, 3, 77]]

  print[ARGS]
}
