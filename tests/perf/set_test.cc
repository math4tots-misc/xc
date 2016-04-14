"""
Kyumins-MacBook-Pro:xc math4tots$ g++ --std=c++11 -Wall -Werror -Wpedantic tests/perf/set_test.cc && time ./a.out 
99999220000000

real	0m6.524s
user	0m6.192s
sys	0m0.310s
Kyumins-MacBook-Pro:xc math4tots$ g++ --std=c++11 -Wall -Werror -Wpedantic -O3 tests/perf/set_test.cc && time ./a.out 
99999220000000

real	0m4.783s
user	0m4.484s
sys	0m0.291s
Kyumins-MacBook-Pro:xc math4tots$ 
"""

#include <unordered_set>
#include <iostream>
using namespace std;

constexpr long long TEN_MIL = 10000000;

int main() {
  unordered_set<double> s;
  for (long long i = 0; i < TEN_MIL; i++) {
    s.insert(2 * i - 77);
  }

  long long total = 0;
  for (double i: s) {
    total += i;
  }

  cout << total << endl;
}
