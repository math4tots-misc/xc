var stuff = new List(String)[]

fn main[] {
  var g = fn[] {
    stuff.push[trace[]]
  }
  g[]
  f[]
  var s = new Sample[]
  s.foo[]
  s.rec[0]

  for item in stuff {
    print[item]
  }
}

fn f[] {
  stuff.push[trace[]]
}

class Sample {
  fn[] {
    stuff.push[trace[]]
  }

  fn foo[] {
    stuff.push[trace[]]
  }

  fn rec[i Int] {
    if i == 10 {
      stuff.push[trace[]]
    } else {
      self.rec[i+1]
    }
  }
}

var expected = r"""
Kyumins-MacBook-Pro:xc math4tots$ xc test.xc && ./a.out
Traceback (most recent call last):
  File "test.xc", line 7 in main
  File "test.xc", line 5 in <anonymous>

Traceback (most recent call last):
  File "test.xc", line 8 in main
  File "test.xc", line 19 in f

Traceback (most recent call last):
  File "test.xc", line 9 in main
  File "test.xc", line 24 in Sample.<constructor>

Traceback (most recent call last):
  File "test.xc", line 10 in main
  File "test.xc", line 28 in Sample.foo

Traceback (most recent call last):
  File "test.xc", line 11 in main
  File "test.xc", line 35 in Sample.rec
  File "test.xc", line 35 in Sample.rec
  File "test.xc", line 35 in Sample.rec
  File "test.xc", line 35 in Sample.rec
  File "test.xc", line 35 in Sample.rec
  File "test.xc", line 35 in Sample.rec
  File "test.xc", line 35 in Sample.rec
  File "test.xc", line 35 in Sample.rec
  File "test.xc", line 35 in Sample.rec
  File "test.xc", line 35 in Sample.rec
  File "test.xc", line 33 in Sample.rec
"""
