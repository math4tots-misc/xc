
#include <iostream>
#include <fstream>
#include <algorithm>
#include <vector>

typedef long long xc_Int;
typedef double xc_Float;
typedef char xc_Char;
typedef const std::string xc_String;
typedef void xc_Void;

// 'T' must derive from 'Root'
template <class T>
struct SharedPtr {
  SharedPtr(): ptr(nullptr) {}
  SharedPtr(T* p): ptr(p) { ptr->increment_refcnt(); }
  SharedPtr(const SharedPtr<T>& p): ptr(p.ptr) { ptr->increment_refcnt(); }
  ~SharedPtr() { ptr->decrement_refcnt(); }
  SharedPtr& operator=(const SharedPtr& p) {
    if (ptr != p.ptr) {
      if (ptr != nullptr)
        ptr->decrement_refcnt();
      ptr = p.ptr;
      ptr->increment_refcnt();
    }
    return *this;
  }
  T* operator->() { return ptr; }

private:
  T* ptr;
};

struct Root {
  int refcnt = 0;
  virtual ~Root() {}
  void increment_refcnt() { refcnt++; }
  void decrement_refcnt() {
    refcnt--;
    if (refcnt <= 0)
      delete this;
  }
};

template <class T> struct xcc_List;
template <class T> using xc_List = SharedPtr<xcc_List<T>>;
template <class T> struct xcc_List: Root {
  std::vector<T> data;

  xc_List<T> xc_add(T t) {
    data.push_back(t);
    return xc_List<T>(this);
  }

  xc_Int xc_size() const {
    return data.size();
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
xc_Int xc_bar();
xc_Int xc_main();
xc_Void xc_foo(xc_List<xc_Int> xc_xs)
{
  xc_print("inside foo");
  xc_xs->xc_add(5);
  xc_print("About to leave foo");
}
xc_Int xc_blarg(xc_Int xc_a, xc_Int xc_b)
{
  return xc_add(xc_a, xc_b);
}
xc_Int xc_bar()
{
  xc_print("hello world!");
  xc_print(xc_blarg(4, 5));
  xc_foo(xc_getlist());
  return 0;
}
xc_Int xc_main()
{
  xc_bar();
  xc_print("Finished bar");
  return 0;
}
