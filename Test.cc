#include <iostream>
using namespace std;

int main() {
  auto f = [=]() -> int { return 5; };
  cout << f() << endl;
}
