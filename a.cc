
#include <iostream>
#include <fstream>
#include <algorithm>
#include <vector>
#include <memory>

typedef long long xc_Int;
typedef double xc_Float;
typedef const std::string& xc_String;
typedef void xc_Void;

template <class T> struct xcc_List;
template <class T> using xc_List = std::shared_ptr<xcc_List<T>>;
template <class T> struct xcc_List {
  std::vector<T> data;

  xc_List<T> add(T t) {
    data.push_back(t);
    return xc_List<T>(this);
  }
};

xc_List<xc_Int> xc_getlist() {
  return xc_List<xc_Int>(new xcc_List<xc_Int>());
}

xc_Int xc_add(xc_Int a, xc_Int b) {
  return a + b;
}

xc_Void xc_print(xc_String s) {
  std::cout << s << std::endl;
}

xc_Void xc_print(xc_Int x) {
  std::cout << x << std::endl;
}

xc_Int xc_main();
int main() {
  xc_main();
}

////////////////////////////////////////

xc_Void xc_foo(xc_List<xc_Int> xc_xs);
xc_Int xc_blarg(xc_Int xc_a, xc_Int xc_b);
xc_Int xc_main();
xc_Void xc_foo(xc_List<xc_Int> xc_xs)
{
}
xc_Int xc_blarg(xc_Int xc_a, xc_Int xc_b)
{
  return xc_add(xc_a, xc_b);
}
xc_Int xc_main()
{
  xc_print("hello world!");
  xc_print(xc_blarg(4, 5));
  xc_foo(xc_getlist());
  return 0;
}
