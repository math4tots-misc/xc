
#include <iostream>
#include <fstream>
#include <algorithm>
#include <vector>
#include <type_traits>
#include <sstream>

// xcs_* -> xc struct type
// xct_* -> xc type
// xcf_* -> xc function
// xcm_* -> xc method
// xcv_* -> xc variable

typedef long long xct_Int;
typedef double xct_Float;
typedef char xct_Char;
typedef bool xct_Bool;
typedef const std::string xct_String;
typedef void xct_Void;

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

template <class T>
struct SharedPtr {
  static_assert(
      std::is_base_of<Root, T>::value,
      "Template argument to SharedPtr must be derived from struct 'Root'");

  typedef T Pointee;

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

template <class T> struct xcs_List;
template <class T> using xct_List = SharedPtr<xcs_List<T>>;
template <class T> struct xcs_List: Root {
  std::vector<T> data;

  xct_List<T> xcm_add(T t) {
    data.push_back(t);
    return xct_List<T>(this);
  }

  xct_Int xcm_size() const {
    return data.size();
  }
};

xct_List<xct_Int> xcf_getlist() {
  return xct_List<xct_Int>(new xcs_List<xct_Int>());
}

xct_Int xcf_add(xct_Int a, xct_Int b) {
  return a + b;
}

xct_String xcf_str(xct_String x) {
  return x;
}

xct_String xcf_str(xct_Int x) {
  std::stringstream ss;
  ss << x;
  return ss.str();
}

xct_String xcf_str(xct_Float x) {
  std::stringstream ss;
  ss << x;
  return ss.str();
}

xct_String xcf_str(xct_Char x) {
  std::stringstream ss;
  ss << x;
  return ss.str();
}

template <class T>
xct_Void xcf_print(T s) {
  std::cout << xcf_str(s);
}

xct_Int xcf_main();
int main() {
  xcf_main();
}

////////////////////////////////////////

template <class xct_T> xct_Void xcf_println(xct_T xcv_t);
xct_Void xcf_foo(xct_List<xct_Int> xcv_xs);
xct_Int xcf_blarg(xct_Int xcv_a, xct_Int xcv_b);
template <class xct_T> xct_List<xct_T> xcf_List();
xct_Int xcf_bar();
xct_Int xcf_main();
template <class xct_T> xct_Void xcf_println(xct_T xcv_t)
{
  xcf_print(xcf_str(xcv_t));
  xcf_print('\n');
}
xct_Void xcf_foo(xct_List<xct_Int> xcv_xs)
{
  xcf_println("inside foo");
  xcf_println(xcv_xs->xcm_size());
  xcv_xs->xcm_add(5LL);
  xcf_println(xcv_xs->xcm_size());
  xcv_xs->xcm_add(1LL)->xcm_add(2LL)->xcm_add(3LL);
  xcf_println(xcv_xs->xcm_size());
  xcf_println("About to leave foo");
}
xct_Int xcf_blarg(xct_Int xcv_a, xct_Int xcv_b)
{
  return xcf_add(xcv_a, xcv_b);
}
template <class xct_T> xct_List<xct_T> xcf_List()
{
  return xct_List<xct_T>(new typename xct_List<xct_T>::Pointee);
}
xct_Int xcf_bar()
{
  xcf_println("hello world!");
  xcf_println(xcf_blarg(4LL, 5LL));
  xcf_foo(xcf_getlist());
  return 0LL;
}
xct_Int xcf_main()
{
  xcf_bar();
  xcf_println("Finished bar");auto xcv_xs = xcf_List<xct_Int>();
  xcf_println(xcv_xs->xcm_size());
  return 0LL;
}
