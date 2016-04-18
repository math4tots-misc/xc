"""set_test.xc

'Set' is written in xs, wrapping around 'Map'.

See how this implementation holds up against other languages.

---

Kyumins-MacBook-Pro:xc math4tots$ xc tests/perf/set_test.xc && time ./a.out
99999220000000

real	0m7.924s
user	0m7.616s
sys	0m0.300s
Kyumins-MacBook-Pro:xc math4tots$ xc tests/perf/set_test.xc -O3 && time ./a.out
99999220000000

real	0m5.065s
user	0m4.763s
sys	0m0.295s
"""

fn main[] {
  stdout.write['perf/set_test... ']
  var TEN_MIL = 10000000
  var s = new Set(Float)[]

  var i = 0
  while i < TEN_MIL {
    s.add[2 * i - 77]
    i = i + 1
  }

  var total = 0
  for x in s {
    total = total + x
  }

  print['pass']
}
