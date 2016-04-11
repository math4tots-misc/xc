// Experimenting with what works in C++

#include <iostream>
using namespace std;

template <class T>
struct C {
  C();
  void method();
  C blarg() { return C(); }
};

template <class T>
void C<T>::method() {
  cout << "Inside C<T>!" << endl;
}

template <class T>
C<T>::C() {
  cout << "Constructing C<T> (i.e. C<T>::C())" << endl;
}

int main() {
  C<int> c;
  c.method();
  C<float> d;
  d.method();
}
