
#include <iostream>
#include <fstream>
#include <algorithm>

typedef long long xc_Int;
typedef double xc_Float;
typedef const std::string& xc_String;
typedef void xc_Void;

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

xc_Int xc_blarg(xc_Int xc_a, xc_Int xc_b);
xc_Int xc_main();
xc_Int xc_blarg(xc_Int xc_a, xc_Int xc_b)
{
  return xc_add(xc_a, xc_b);
}
xc_Int xc_main()
{
  xc_print("hello world!");
  xc_print(xc_blarg(4, 5));
  return 0;
}
