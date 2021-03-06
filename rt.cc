// Autogenerated from <xc> programming language.
// Needs C++14 features
////// BEGIN prelude
#include <iostream>
#include <fstream>
#include <functional>
#include <type_traits>
#include <initializer_list>
#include <string>
#include <sstream>
#include <vector>
#include <map>
#include <set>
#include <algorithm>
#include <tuple>
#include <exception>
#include <stdexcept>

//-- Section 00: defines
#define vvnil nullptr
#define vvself this
#define vvtrue true
#define vvfalse false

// Standard Xcode tools do not seem to support thread_local yet.
// THREAD_LOCAL is used to keep a manual stack trace.
// So as long as there is there's no multithreading in the program,
// things should still run ok.
#define THREAD_LOCAL

//-- Section 01: Error handling/assert
THREAD_LOCAL std::vector<std::tuple<const char*, int, const char*>> trace;

inline void push_trace(const char *filespec, int lineno, const char *f) {
  trace.push_back(std::make_tuple(filespec, lineno, f));
}

inline void pop_trace() {
  trace.pop_back();
}

template <class T>
inline T pop_trace_with_value(T t) {
  pop_trace();
  return t;
}

std::string make_trace() {
  std::stringstream ss;
  ss << "Traceback (most recent call last):" << std::endl;
  for (auto& triple: trace) {
    ss << "  File \"" << std::get<0>(triple)
       << "\", line " << std::get<1>(triple)
       << ", in " << std::get<2>(triple) << std::endl;
  }
  return ss.str();
}

[[noreturn]] void err(const std::string& message) {
  throw std::runtime_error(make_trace() + message + "\n");
}

//-- Section 02: P
class CCObject;
template <class T>
class P {
public:
  static_assert(std::is_base_of<CCObject, T>::value, "Must subclass Object");
  typedef T value_type;
  constexpr P(): ptr(nullptr) {}
  P(T* p): ptr(p) { incr(); }
  P(const P& p): P(p.ptr) {}
  ~P() { decr(); }
  P& operator=(const P& p) { p.incr(); decr(); ptr = p.ptr; return *this; }
  T* getptr() const { return ptr; }
  T* operator->() const { return ptr; }
  void clear() { decr(); ptr = nullptr; }
  template <class K> auto operator==(K k) const { return ptr->mmmmeq(k); }
  template <class K> auto operator!=(K k) const { return ptr->mmmmne(k); }
  template <class K> auto operator<(K k) const { return ptr->mmmmlt(k); }
  template <class K> auto operator+(K k) const { return ptr->mmmmadd(k); }
  template <class K> auto operator-(K k) const { return ptr->mmmmsub(k); }
  template <class K> auto operator*(K k) const { return ptr->mmmmmul(k); }
  template <class K> auto operator/(K k) const { return ptr->mmmmdiv(k); }
  template <class K> auto operator%(K k) const { return ptr->mmmmmod(k); }
  auto operator++() const { return ptr->mmmmincr(); }
  auto operator*() const { return ptr->mmmmderef(); }
  auto begin() const { return ptr->mmmmbegin(); }
  auto end() const { return ptr->mmmmend(); }
private:
  void incr() const { if (ptr) { ptr->increment(); } }
  void decr() const { if (ptr) { ptr->decrement(); } }
  T* ptr;
};

//-- Section 03: CCObject
class CCObject {
public:
  constexpr CCObject(): refcnt(0) {}
  virtual ~CCObject() {}
private:
  int refcnt;
  void increment() { refcnt++; }
  void decrement() { refcnt--; if (!refcnt) { delete this; } }
  template <class T> friend class P;
};

class CCEquatable: public virtual CCObject {
public:
  virtual bool mmmmeq(P<CCEquatable> pe)=0;
};
typedef P<CCEquatable> PPEquatable;

//-- Section 04: Primitive type aliases
typedef void PPVoid;
typedef bool PPBool;
typedef char PPChar;
typedef long long PPInt;
typedef double PPFloat;
template <class... T> using PPTuple = std::tuple<T...>;
template <class R, class... A> using PPFunction = std::function<R(A...)>;

//-- Section 05: Tupleobject
template <class... T>
class CCTupleObject final: public CCObject {
public:
  CCTupleObject(const PPTuple<T...>& v): value(v) {}
  CCTupleObject(const CCTupleObject<T...>& v): value(v.value) {}
  const PPTuple<T...> value;
};
template <class... T> using PPTupleObject = CCTupleObject<T...>;
// make Tuple
template <class... A>
PPTuple<A...> vvT(A... args) {
  return PPTuple<A...>(args...);
}

//-- Section 06: Any
class PPAny final {
public:
  static constexpr int POINTER = 0;
  static constexpr int BOOL = 1;
  static constexpr int CHAR = 2;
  static constexpr int INT = 3;
  static constexpr int FLOAT = 4;
  constexpr PPAny(): type(POINTER), boolean(false) {}
  constexpr PPAny(PPBool b): type(BOOL), boolean(b) {}
  constexpr PPAny(PPChar b): type(CHAR), character(b) {}
  constexpr PPAny(PPInt b): type(INT), integer(b) {}
  constexpr PPAny(PPFloat b): type(FLOAT), floating(b) {}
  template <class T> PPAny(P<T> value):
      type(POINTER), pointer(value.getptr()), boolean(false) {}
  PPAny& operator=(PPBool b) { type = BOOL; boolean = b; return *this; }
  PPAny& operator=(PPChar b) { type = CHAR; character = b; return *this; }
  PPAny& operator=(PPInt b) { type = INT; integer = b; return *this; }
  PPAny& operator=(PPFloat b) { type = FLOAT; floating = b; return *this; }
  template <class... T>
  PPAny& operator=(PPTuple<T...> t) {
    type = POINTER;
    pointer = new CCTupleObject<T...>(t);
    return *this;
  }
  template <class T>
  PPAny& operator=(P<T> p) {
    type = POINTER;
    pointer = p.getptr();
    return *this;
  }
  PPBool as_bool() const {
    if (type != BOOL) {
      err("Not a bool");
    }
    return boolean;
  }
  PPChar as_char() const {
    if (type != CHAR) {
      err("Not a char");
    }
    return character;
  }
  PPInt as_int() const {
    if (type != INT) {
      err("Not an int");
    }
    return integer;
  }
  PPFloat as_float() const {
    if (type != FLOAT) {
      err("Not a float");
    }
    return floating;
  }
private:
  int type;
  P<CCObject> pointer;
  union {
    PPBool boolean;
    PPChar character;
    PPInt integer;
    PPFloat floating;
  };
};

//-- Section 07: String
class CCString;
typedef P<CCString> PPString;
class CCString final: public CCObject {
public:
  CCString(const std::string& v): s(v) {}
  CCString(char c): s(1, c) {}
  const std::string& str() const { return s; }
  PPInt mmsize() const { return s.size(); }
  PPChar mmmmdiv(PPInt i) const { return s[i]; }
  auto mmmmbegin() { return s.begin(); }
  auto mmmmend() { return s.end(); }
  bool mmmmeq(const PPString& ps) const {
    return s == ps->s;
  }
  PPString mmmmadd(const PPString& ps) const {
    return new CCString(s + ps->s);
  }
private:
  const std::string s;
};
PPString vvtrace() {
  return new CCString(make_trace());
}
[[noreturn]] void vverr(PPString message) {
  err(message->str());
}
void vvassert(PPBool cond) {
  if (!cond) {
    err("Assertion Err");
  }
}
template <class T>
void vvassert(PPBool cond, T t) {
  if (!cond) {
    std::stringstream ss;
    ss << "Assertion Err: " << t;
    err(ss.str());
  }
}

//-- Section 08: repr
template <class T>
std::string repr(T t) {
  std::stringstream ss;
  ss << t;
  return ss.str();
}

inline std::string sanitize_char(char c) {
  switch (c) {
  case '\n': return "\\n";
  case '\t': return "\\t";
  case '"': return "\\\"";
  case '\'': return "\\'";
  default: return std::string(1, c);
  }
}

template <>
std::string repr<PPString>(PPString pps) {
  const std::string& s = pps->str();
  std::stringstream ss;
  ss << '"';
  for (unsigned i = 0; i < s.size(); i++) {
    ss << sanitize_char(s[i]);
  }
  ss << '"';
  return ss.str();
}

template <>
std::string repr<PPChar>(PPChar ppc) {
  return "'" + sanitize_char(ppc) + "'";
}

template <class T>
PPString vvrepr(T t) {
  return new CCString(repr(t));
}

//-- Section 09: Containers: Vector/Deque/Map/Set
template <class T> class CCVector;
template <class T> using PPVector = P<CCVector<T>>;
template <class T>
class CCVector final: public CCObject {
public:
  CCVector(std::initializer_list<T> args): v(args) {}
  PPInt mmsize() const { return v.size(); }
  T mmmmdiv(PPInt i) const { return v[i]; }
  void mmmmsetitem(PPInt i, T v) { v[i] = v; }
  void mmpush(T t) { v.push_back(t); }
  auto mmmmbegin() { return v.begin(); }
  auto mmmmend() { return v.end(); }
  PPString mmmmstr() {
    std::stringstream ss;
    ss << "$[";
    bool first = true;
    for (auto i: v) {
      if (!first) {
        ss << ", ";
      }
      ss << repr(i);
      first = false;
    }
    ss << "]";
    return new CCString(ss.str());
  }
  bool mmmmeq(const PPVector<T>& pv) const { return v == pv->v; }
  bool mmmmne(const PPVector<T>& pv) const { return v != pv->v; }
  bool mmmmlt(const PPVector<T>& pv) const { return v <  pv->v; }
  bool mmmmle(const PPVector<T>& pv) const { return v <= pv->v; }
  bool mmmmgt(const PPVector<T>& pv) const { return v >  pv->v; }
  bool mmmmge(const PPVector<T>& pv) const { return v >= pv->v; }
private:
  std::vector<T> v;
};

template <class T>
PPVector<T> make_vector(std::initializer_list<T> args) {
  return new CCVector<T>(args);
}

//-- Section 10: stream out overloads/str.
template <class Tuple, int I>
struct TupleWriteHelper {
  static void write(std::ostream& out, const Tuple& t) {
    out << repr(std::get<std::tuple_size<Tuple>::value-I>(t)) << ", ";
    TupleWriteHelper<Tuple, I-1>::write(out, t);
  }
};

template <class Tuple>
struct TupleWriteHelper<Tuple, 1> {
  static void write(std::ostream& out, const Tuple& t) {
    out << repr(std::get<std::tuple_size<Tuple>::value-1>(t));
  }
};

template <class... A>
std::ostream& operator<<(std::ostream& out, const PPTuple<A...>& t) {
  out << "T[";
  TupleWriteHelper<
      PPTuple<A...>,
      std::tuple_size<PPTuple<A...>>::value
  >::write(out, t);
  return out << "]";
}

std::ostream& operator<<(std::ostream& out, const PPString& s) {
  return out << s->str();
}

template <class T>
std::ostream& operator<<(std::ostream& out, const P<T>& t) {
  return out << t->mmmmstr();
}

template <class T>
PPString vvstr(T t) {
  return new CCString(t);
}

//-- Section 11: FileWriter/FileReader and input/print
class CCFileWriter final: public CCObject {
public:
  CCFileWriter(const std::string& filename):
      destroy(true), out(new std::ofstream(filename)) {}
  CCFileWriter(): destroy(false), out(&std::cout) {}
  ~CCFileWriter() { if (destroy) { delete out; } }
  CCFileWriter(const CCFileWriter& w) = delete;
  CCFileWriter& operator=(const CCFileWriter& w) = delete;
  template <class T> void mmwrite(T t) { (*out) << t; }
  template <class T> void mmprint(T t) { mmwrite(t); (*out) << std::endl; }
private:
  const bool destroy;  // indicates whether we should destory the ostream.
  std::ostream* out;
};
typedef P<CCFileWriter> PPFileWriter;
PPFileWriter vvstdout(new CCFileWriter());
inline PPFileWriter vvFileWriter(PPString filename) {
  return new CCFileWriter(filename->str());
}
class CCFileReader final: public CCObject {
public:
  CCFileReader(const std::string& filename):
    destroy(true), fin(new std::ifstream(filename)) {}
  CCFileReader(): destroy(false), fin(&std::cin) {}
  ~CCFileReader() { if (destroy) { delete fin; } }
  PPString mminput() {
    std::string s;
    std::getline(*fin, s);
    return new CCString(s);
  }
  PPString mmread() {
    return new CCString(std::string(
        (std::istreambuf_iterator<char>(*fin)),
        (std::istreambuf_iterator<char>())));
  }
private:
  const bool destroy;  // indicates whether we should destroy the istream.
  std::istream* fin;
};
typedef P<CCFileReader> PPFileReader;
PPFileReader vvstdin(new CCFileReader());
inline PPFileReader vvFileReader(PPString filename) {
  return new CCFileReader(filename->str());
}

template <class T> void vvprint(const T& t) { vvstdout->mmprint(t); }
PPString vvinput() { return vvstdin->mminput(); }

//-- Section 12: ARGS and main.
PPVector<PPString> vvARGS(new CCVector<PPString>({}));

void vvmain();

int main(int argc, char **argv) {
  for (int i = 0; i < argc; i++) {
    vvARGS->mmpush(new CCString(argv[i]));
  }
  try {
    vvmain();
  } catch (const std::runtime_error& err) {
    std::cerr << err.what();
  }
}

////// END prelude
using namespace std;

int main() {
  auto v = V({1, 2, 3});
  cout << v->mmsize() << endl;
}
