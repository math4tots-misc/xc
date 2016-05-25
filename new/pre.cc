#include <iostream>

typedef long long PPInt;

template <class T> struct Pointer;

struct CCObject {
private:
  template <class T> friend struct Pointer;
};

template <class T>
struct Pointer {
  static_assert(std::is_base_of<CCObject, T>::value, "Must subclass Object");
  template <class J> Pointer(const Pointer<J>& p): ptr(p.ptr) { incr(); }
  template <class J> Pointer<T>& operator=(const Pointer<J>& p) {
    p.incr();
    decr();
    ptr = p.ptr;
    return *this;
  }
private:
  constexpr void incr() { if (ptr) { ptr->refcnt++; } }
  constexpr void decr() { if (ptr) { ptr->refcnt--; } }
  T *ptr;
};

struct CCEquatable: virtual CCObject {
};

struct CCInt final: virtual CCObject, virtual CCEquatable {
  constexpr CCInt(PPInt x): val(x) {}
  constexpr CCInt(const CCInt& i): val(i.val) {}
  constexpr PPInt getval() const { return val; }
  constexpr CCInt operator+(CCInt x) const { return val + x.val; }
  constexpr CCInt operator-(CCInt x) const { return val - x.val; }
  constexpr CCInt operator*(CCInt x) const { return val * x.val; }
  constexpr CCInt operator/(CCInt x) const { return val / x.val; }
  constexpr CCInt operator%(CCInt x) const { return val % x.val; }
  constexpr CCInt operator-() const { return -val; }
  constexpr CCInt operator++() { return ++val; }
  constexpr bool asbool() const { return val; }
private:
  PPInt val;
};

int main() {
}
