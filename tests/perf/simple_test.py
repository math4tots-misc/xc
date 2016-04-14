"""
Kyumins-MacBook-Pro:xc math4tots$ time python simple_test.py 
100000020000000

real	0m3.530s
user	0m3.202s
sys	0m0.303s
"""

xs = []
for i in range(10000000):
  xs.append(2 * i + 3)

total = 0
for x in xs:
  total += x

print(total)
