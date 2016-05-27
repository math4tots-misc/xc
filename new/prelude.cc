#include <iostream>
#include <deque>
#include <stdexcept>

typedef bool PPbool;
typedef char PPchar;
typedef long long PPint;
typedef double PPfloat;

template <class T>
struct P {
public:
  typedef T value_type;
  constexpr P(): ptr(nullptr) {}
  P(T* p): ptr(p) { incr(); }
  P(const P& p): P(p.ptr) {}
  ~P() { decr(); }
  P& operator=(const P& p) { p.incr(); decr(); ptr = p.ptr; return *this; }
  T* getptr() const { return ptr; }
  T* operator->() const { return ptr; }
  void clear() { decr(); ptr = nullptr; }
  template <class K> auto operator==(K k) const { return ptr->mmxxeq(k); }
  template <class K> auto operator!=(K k) const { return ptr->mmxxne(k); }
  template <class K> auto operator<(K k) const { return ptr->mmxxlt(k); }
  template <class K> auto operator+(K k) const { return ptr->mmxxadd(k); }
  template <class K> auto operator-(K k) const { return ptr->mmxxsub(k); }
  template <class K> auto operator*(K k) const { return ptr->mmxxmul(k); }
  template <class K> auto operator/(K k) const { return ptr->mmxxdiv(k); }
  template <class K> auto operator%(K k) const { return ptr->mmxxmod(k); }
  auto operator++() const { return ptr->mmxxincr(); }
  auto operator*() const { return ptr->mmxxderef(); }
  auto begin() const { return ptr->mmxxbegin(); }
  auto end() const { return ptr->mmxxend(); }
  template <class K>  // 'K' should be an instantiation of 'P'.
  auto as() const {
    if (ptr == nullptr) {
      return K();
    } else {
      auto* k = dynamic_cast<typename K::value_type*>(ptr);
      if (k == nullptr) {
        throw std::runtime_error("cast exception");
      }
      return K(k);
    }
  }
private:
  void incr() const { if (ptr) { ++ptr->refcnt; } }
  void decr() const {
    if (ptr) {
      --ptr->refcnt;
      if (!ptr->refcnt) {
        delete ptr;
      }
    }
  }
  T* ptr;
};

struct CCObject;
typedef P<CCObject> PPObject;
struct CCObject {
  CCObject(): refcnt(0) {}
  virtual ~CCObject() {}
private:
  template <class T> friend struct P;
  int refcnt;
};

struct CCEquatable;
typedef P<CCEquatable> PPEquatable;
struct CCEquatable: virtual CCObject {
  virtual bool mmxxeq(PPEquatable)=0;
};

struct CCComparable;
typedef P<CCComparable> PPComparable;
struct CCComparable: virtual CCEquatable {
  virtual bool mmxxlt(PPComparable)=0;
};

struct CCBool;
typedef P<CCBool> PPBool;
struct CCBool final: virtual CCComparable {
  CCBool(PPbool v): val(v) {}
  PPbool mmgetval() const { return val; }
  bool mmxxeq(PPEquatable x) override {
    return val == x.as<PPBool>()->val;
  }
  bool mmxxlt(PPComparable x) override {
    return val < x.as<PPBool>()->val;
  }
private:
  PPbool val;
};

struct CCChar;
typedef P<CCChar> PPChar;
struct CCChar final: virtual CCObject {
  CCChar(PPchar v): val(v) {}
  PPchar mmgetval() const { return val; }
private:
  PPchar val;
};

struct CCInt;
typedef P<CCInt> PPInt;
struct CCInt final: virtual CCObject {
  CCInt(PPint v): val(v) {}
  PPint mmgetval() const { return val; }
private:
  PPint val;
};

struct CCFloat;
typedef P<CCFloat> PPFloat;
struct CCFloat final: virtual CCObject {
  CCFloat(PPfloat v): val(v) {}
  PPfloat mmgetval() const { return val; }
private:
  PPfloat val;
};

inline PPBool objectify(PPbool x) { return new CCBool(x); }
inline PPChar objectify(PPchar x) { return new CCChar(x); }
inline PPInt objectify(PPint x) { return new CCInt(x); }
inline PPFloat objectify(PPfloat x) { return new CCFloat(x); }
template <class T> inline decltype(auto) objectify(P<T>&& p) { return p; }

struct CCString;
typedef P<CCString> PPString;
struct CCString final: virtual CCObject {
  CCString(const std::string& s): val(s) {}
  const std::string& getval() const { return val; }
private:
  const std::string val;
};

using namespace std;
int main() {
  objectify(((PPint)5));
}
