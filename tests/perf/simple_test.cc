/*
Kyumins-MacBook-Pro:xc math4tots$ g++ --std=c++11 -Wall -Werror -Wpedantic simple_test.cc && time ./a.out 
100000020000000

real	0m0.515s
user	0m0.424s
sys	0m0.086s
Kyumins-MacBook-Pro:xc math4tots$ g++ --std=c++11 -Wall -Werror -Wpedantic -O3 simple_test.cc && time ./a.out 
100000020000000

real	0m0.151s
user	0m0.071s
sys	0m0.075s
*/
#include <iostream>
#include <vector>
using namespace std;

int main() {
  vector<long long> xs;
  for (long long i = 0; i < 10000000; i++) {
    xs.push_back(2 * i + 3);
  }

  long long total = 0;
  for (long long i: xs) {
    total += i;
  }

  cout << total << endl;
}
