"""
Kyumins-MacBook-Pro:xc math4tots$ xc tests/perf/simple_test.xc && time ./a.out
100000020000000
perf/simple_test pass

real	0m0.803s
user	0m0.714s
sys	0m0.085s
Kyumins-MacBook-Pro:xc math4tots$ xc tests/perf/simple_test.xc -O3 && time ./a.out
100000020000000
perf/simple_test pass

real	0m0.168s
user	0m0.083s
sys	0m0.081s

----

I find this speed pretty impressive.

Unoptimized C++: real	0m0.515s
Optimized C++:   real	0m0.151s

Java:            real	0m2.717s

Unoptimized is ~2x slower than C++, but with -O3, pretty close.
Unoptimized xc is still 2x faster than Java.
Optimized xc is ~18x faster than Java.

"""

fn main[] {
  stdout.write['perf/simple_test... ']
  var TEN_MIL = 10000000
  var i = 0
  var xs = new List(Int)[]
  while i < TEN_MIL {
    xs.push[2 * i + 3]
    i = i + 1
  }

  var total = 0
  for x in xs {
    total = total + x
  }

  print['pass']
}
