PREFIX_1 = r"""// <Autogenerated from xc source>
// requires C++11
// xcs_* -> xc struct type
// xct_* -> xc type
// xcm* -> xc method (no underscore, want to avoid double underscore)
// xca_* -> xc attribute (member variable)
// xcv_* -> xc variable
// xcc_* -> xc constant
#include <algorithm>
#include <fstream>
#include <initializer_list>
#include <iostream>
#include <sstream>
#include <stdlib.h>
#include <string>
#include <tuple>
#include <type_traits>
#include <unordered_set>
#include <unordered_map>
#include <vector>
"""

"""Without trace"""
PREFIX_2A = r"""
typedef void xct_Void;
#define RETURN_VOID

std::string make_trace_message() {
  return "<Trace is off>\n";
}
"""

"""With Trace"""
PREFIX_2B = r"""
typedef std::nullptr_t xct_Void;
#define RETURN_VOID return nullptr

// Code for manual stack trace.
// This code is only used if the 'trace' option is turned on.
// when turned on, a Frame object is inserted into every statement with
// an expression and declaration's expressions.
// Also, note, this is kind of a fragile approach. Coroutines, asynchronous
// code could potentially mess this all up.
// TODO: Figure out a better solution.
struct Frame;
static std::vector<Frame*> trace;
struct Frame {
  const char* message;
  int lineno;
  Frame(const char* message): Frame(message, 0) {}
  Frame(const char* message, int lineno): message(message), lineno(lineno) {
    trace.push_back(this);
  }
  ~Frame() {
    trace.pop_back();
  }
  template <class T>
  T with(T expr) {
    return expr;
  }
};
std::string make_trace_message() {
  std::stringstream ss;
  for (auto frame: trace) {
    if (frame->lineno)
      ss << "  *** " << frame->message <<
          " on line " << frame->lineno << std::endl;
    else
      ss << "  *** " << frame->message << std::endl;
  }
  return ss.str();
}
"""

PREFIX_3 = r"""
typedef bool xct_Bool;
typedef char xct_Char;
typedef long long xct_Int;
typedef double xct_Float;
struct Root;
template <class T> struct SharedPtr;
template <class T> struct IterableSharedPtr;
struct xcs_String;

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

void die(std::string message);

template <class T>
struct SharedPtr {
  static_assert(
      std::is_base_of<Root, T>::value,
      "Template argument to SharedPtr must be derived from struct 'Root'");

  typedef T Pointee;

  SharedPtr(): ptr(nullptr) {}
  SharedPtr(T* p): ptr(p) { ptr->increment_refcnt(); }

  //// TODO: Consider whether the following template constructor is
  //// worth having.
  // template <class K> SharedPtr(SharedPtr<K> p): SharedPtr(p->ptr) {}

  SharedPtr(const SharedPtr<T>& p): ptr(p.ptr) { incr(); }
  ~SharedPtr() { decr(); }
  SharedPtr& operator=(const SharedPtr& p) {
    if (ptr != p.ptr) {
      decr();
      ptr = p.ptr;
      incr();
    }
    return *this;
  }

  T* operator->() const {
    // TODO: Consider whether this check is worth it.
    // TODO: If I'm going to keep this check maybe include the
    // pointer's type to make this more helpful. Although, I think it'd
    // be best if stack traces could be annotated with line numbers.
    if (ptr == nullptr)
      die("Tried to call a method on a nil pointer");
    return ptr;
  }

  SharedPtr<T> operator+(SharedPtr<T> other) {
    return ptr->xcm_add_(other);
  }

  xct_Int hash() const {
    return ptr->xcm_hash_();
  }

  IterableSharedPtr<T> iterptr() const;

  // TODO: Understand how this works even when 'T' is a type that does
  // not implement 'xcm_eq_'.
  // An alternative solution would be to have an 'equals' template function
  // that always directly calls 'xcm_eq_' on SharedPtr<T>,
  // and specialize for builtin types.
  xct_Bool operator==(SharedPtr<T> p) const {
    return ptr == p.ptr || ptr->xcm_eq_(p);
  }

  xct_Bool operator!=(SharedPtr<T> p) const {
    return !(*this == p);
  }

  xct_Bool operator<(SharedPtr<T> p) const {
    return ptr->xcm_lt_(p);
  }

  template <class K>
  SharedPtr<T> operator+=(K k) {
    return *this = ptr->xcm_iadd_(k);
  }

  template <class K>
  SharedPtr<T> operator-=(K k) {
    return *this = ptr->xcm_isub_(k);
  }

  template <class K>
  SharedPtr<T> operator*=(K k) {
    return *this = ptr->xcm_imul_(k);
  }

  template <class K>
  SharedPtr<T> operator/=(K k) {
    return *this = ptr->xcm_idiv_(k);
  }

  template <class K>
  SharedPtr<T> operator%=(K k) {
    return *this = ptr->xcm_imod_(k);
  }

  xct_Bool is(SharedPtr<T> p) const {
    return ptr == p.ptr;
  }

  xct_Bool is_not(SharedPtr<T> p) const {
    return ptr != p.ptr;
  }

  xct_Bool is_nil() const {
    return ptr == nullptr;
  }

  xct_Bool is_not_nil() const {
    return ptr != nullptr;
  }

  SharedPtr<T>& set_nil() {
    decr();
    ptr = nullptr;
    return *this;
  }

protected:
  T* ptr;

private:
  void incr() {
    if (ptr != nullptr)
      ptr->increment_refcnt();
  }

  void decr() {
    if (ptr != nullptr)
      ptr->decrement_refcnt();
  }
};

// A separate IterableSharedPtr is necessary because if you just
// return e.g. ptr->data for List, the shared pointer to the List object
// will go out of scope, potentially causing the object to be deleted.
// The C++11 standard specifies that only the range expression result
// will have its lifetime extended. So we need the SharedPtr itself to
// be iterable.
// However, we can't add this functionality to SharedPtr itself, because
// that would cause compile errors when trying to use the pointer for
// non-iterable objects.
template <class T>
struct IterableSharedPtr: SharedPtr<T> {
  using I = decltype(std::declval<T>().xcm_iter_());
  using V = decltype(std::declval<T>().xcm_iter_()->xcm_next_());
  bool more;
  I iter;
  V item;
  IterableSharedPtr(T* p):
      SharedPtr<T>(p),
      iter(p->xcm_iter_()) {
    if (iter->xcm_more_()) {
      more = true;
      item = iter->xcm_next_();
    } else {
      more = false;
    }
  }

  IterableSharedPtr& begin() {
    return *this;
  }

  IterableSharedPtr& end() {
    return *this;
  }

  IterableSharedPtr& operator++() {
    if (iter->xcm_more_()) {
      more = true;
      item = iter->xcm_next_();
    } else {
      more = false;
    }
    return *this;
  }

  V operator*() {
    return item;
  }

  bool operator!=(const IterableSharedPtr& p) const {
    return more;
  }
};

template <class T>
IterableSharedPtr<T> SharedPtr<T>::iterptr() const {
  return IterableSharedPtr<T>(ptr);
}

namespace std {
  template<class T>
  struct hash<SharedPtr<T>> {
    std::size_t operator()(SharedPtr<T> p) const {
      return p->xcm_hash_();
    }
  };
}

///////////////////////

struct xcs_String;
using xct_String = SharedPtr<xcs_String>;
template <class T> struct xcs_List;
template <class T> using xct_List = SharedPtr<xcs_List<T>>;
template <class K, class V> struct xcs_Map;
template <class K, class V> using xct_Map = SharedPtr<xcs_Map<K, V>>;

template <class T> xct_String xcv_repr(T t);

struct xcs_Object: Root {
  // TODO: repr and str.
};

struct xcs_String: xcs_Object {
  const std::string data;
  xcs_String() {}
  xcs_String(const std::string& d): data(d) {}

  xct_String xcm_add_(xct_String other) {
    return new xcs_String(data + other->data);
  }

  xct_Int xcmsize() const {
    return data.size();
  }

  xct_Int xcm_hash_() {
    std::hash<std::string> hasher;
    return hasher(data);
  }

  xct_String xcm_repr_() {
    std::string s("\"");
    for (char c: data) {
      switch (c) {
      case '\"': s.append("\\\"");
      case '\n': s.append("\\n");
      default: s.push_back(c);
      }
    }
    s.push_back('\"');
    return new xcs_String(s);
  }

  xct_Bool xcm_eq_(xct_String s) const {
    return data == s->data;
  }

  xct_Bool xcm_lt_(xct_String s) const {
    return data < s->data;
  }

  xct_String xcm_iadd_(xct_String s) const {
    return new xcs_String(data + s->data);
  }

  // TODO
  // xct_List<xct_String> xcmwords() const {
  // }
};

template <class T> struct xcs_ListIterator;
template <class T> using xct_ListIterator = SharedPtr<xcs_ListIterator<T>>;
template <class T> struct xcs_ListIterator: xcs_Object {
  xct_List<T> owner;
  typename std::vector<T>::iterator iter;
  xcs_ListIterator(xct_List<T> xs): owner(xs), iter(xs->data.begin()) {}
  xct_Bool xcm_more_() {
    return iter != owner->data.end();
  }
  T xcm_next_() {
    T t = *iter;
    ++iter;
    return t;
  }
};

template <class T> struct xcs_List: xcs_Object {
  using Iterator = typename std::vector<T>::iterator;
  std::vector<T> data;

  xcs_List(){}
  xcs_List(std::initializer_list<T> args): data(args) {}

  xct_List<T> xcmadd(T t) {
    data.push_back(t);
    return xct_List<T>(this);
  }

  xct_Int xcmsize() const {
    return data.size();
  }

  xct_Void xcmpush(T t) {
    data.push_back(t);
    RETURN_VOID;
  }

  T xcmpop() {
    T d = data.back();
    data.pop_back();
    return d;
  }

  T xcmget(xct_Int i) {
    return data[i];
  }

  xct_Void xcmset(xct_Int i, T t) {
    data[i] = t;
    RETURN_VOID;
  }

  xct_String xcm_repr_() {
    std::string s("[");
    bool first = true;
    for (auto x: data) {
      if (!first)
        s.append(", ");
      s.append(xcv_repr(x)->data);
      first = false;
    }
    s.push_back(']');
    return new xcs_String(s);
  }

  Iterator begin() {
    return data.begin();
  }

  Iterator end() {
    return data.end();
  }

  xct_Bool xcm_eq_(xct_List<T> p) const {
    return data == p->data;
  }

  template <class F>
  auto xcmmap(F f) -> xct_List<decltype(f(T()))> {
    using K = decltype(f(T()));
    xct_List<K> result(new xcs_List<K>());
    for (T t: data) {
      result->xcmpush(f(t));
    }
    return result;
  }

  xct_List<T> xcmsort() {
    std::sort(data.begin(), data.end());
    return this;
  }

  xct_Bool xcm_lt_(xct_List<T> s) {
    return data < s->data;
  }

  xct_ListIterator<T> xcm_iter_() {
    return new xcs_ListIterator<T>(this);
  }
};

template <class K, class V> struct xcs_MapIterator;
template <class K, class V> using xct_MapIterator =
    SharedPtr<xcs_MapIterator<K,V>>;
template <class K, class V> struct xcs_MapIterator: xcs_Object {
  xct_Map<K,V> owner;
  typename std::unordered_map<K,V>::iterator iter;
  xcs_MapIterator(xct_Map<K,V> xs): owner(xs), iter(xs->data.begin()) {}
  xct_Bool xcm_more_() {
    return iter != owner->data.end();
  }
  K xcm_next_() {
    K t = iter->first;
    ++iter;
    return t;
  }
};

template <class K, class V> struct xcs_Map: xcs_Object {
  struct Iterator {
    typedef typename std::unordered_map<K,V>::const_iterator Iter;
    Iter iter;
    Iterator(const Iter& i): iter(i)  {}
    Iterator& operator++() {
      ++iter;
      return *this;
    }
    K operator*() const {
      return iter->first;
    }
    bool operator!=(const Iterator& i) const {
      return iter != i.iter;
    }
  };

  std::unordered_map<K,V> data;

  xcs_Map() {}

  Iterator begin() const {
    return Iterator(data.begin());
  }

  Iterator end() const {
    return Iterator(data.end());
  }

  xct_Int xcmsize() const {
    return data.size();
  }

  V xcmget(K key) const {
    auto it = data.find(key);
    if (it == data.end())
      die("Could not find in Map, key = " + xcv_repr(key)->data);
    return it->second;
  }

  xct_Map<K,V> xcmset(K key, V value) {
    data[key] = value;
    return this;
  }

  xct_Bool xcmhas(K key) {
    return data.find(key) != data.end();
  }

  xct_Bool xcmrm(K key) {
    auto it = data.find(key);
    if (it != data.end()) {
      data.erase(it);
      return true;
    }
    return false;
  }

  xct_MapIterator<K,V> xcm_iter_() {
    return new xcs_MapIterator<K,V>(this);
  }

  xct_Bool xcm_eq_(xct_Map<K,V> m) {
    return data == m->data;
  }
};

template <class T>
xct_String xcv_repr(T t) {
  return t->xcm_repr_();
}

template <>
xct_String xcv_repr(xct_Char t) {
  std::stringstream ss;
  ss << "c'";
  switch (t) {
  case '\n': ss << "\n";
  case '\t': ss << "\t";
  case '\"': ss << "\"";
  default: ss << t;
  }
  ss << "'";
  return new xcs_String(ss.str());
}

template <>
xct_String xcv_repr(xct_Int t) {
  return new xcs_String(std::to_string(t));
}

template <>
xct_String xcv_repr(xct_Float t) {
  return new xcs_String(std::to_string(t));
}

template <>
xct_String xcv_repr(xct_Bool t) {
  return new xcs_String(t ? "true" : "false");
}

// TODO: The default impl of 'str' should call method '_str_'.
// And every value type should have a template specialization.
// All value type specialization besides 'Char' should just
// redirect to 'repr'. Also, template specialization for 'String'
// should no longer be needed.
template <class T>
xct_String xcv_str(T t) {
  return xcv_repr(t);
}

template <>
xct_String xcv_str(xct_Char t) {
  std::stringstream ss;
  ss << t;
  return new xcs_String(ss.str());
}

template <>
xct_String xcv_str(xct_String t) {
  return t;
}

xct_Int xcv_parse_int(xct_String s, xct_Int base) {
  return stoll(s->data, 0, base);
}

xct_Int xcv_int(xct_String s) {
  return stoll(s->data, 0, 10);
}

xct_Float xcv_float(xct_String s) {
  return stod(s->data);
}

///////////////////////

struct xcs_Reader;
using xct_Reader = SharedPtr<xcs_Reader>;
struct xcs_Reader: xcs_Object {
  virtual std::istream& ins()=0;
  xct_String xcminput() {  // read a line of input.
    std::string buf;
    std::getline(ins(), buf);
    return new xcs_String(buf);
  }
};

struct xcs_StdinReader;
using xct_StdinReader = SharedPtr<xcs_StdinReader>;
struct xcs_StdinReader: xcs_Reader {
  std::istream& ins() {
    return std::cin;
  }
};

xct_StdinReader xcv_stdin(new xcs_StdinReader());

struct xcs_FileReader;
using xct_FileReader = SharedPtr<xcs_FileReader>;
struct xcs_FileReader: xcs_Reader {
  std::ifstream fin;
  xcs_FileReader(xct_String path): fin(path->data) {}
  std::istream& ins() {
    return fin;
  }
  xct_String xcmread() {  // read entire contents of file.
    std::stringstream sstr;
    sstr << fin.rdbuf();
    return new xcs_String(sstr.str());
  }
};

struct xcs_Writer;
using xct_Writer = SharedPtr<xcs_Writer>;
struct xcs_Writer: xcs_Object {
  virtual std::ostream& out()=0;
  template <class T>
  xct_Void xcmwrite(T t) {
    out() << xcv_str(t)->data;
    RETURN_VOID;
  }
  template <class T>
  xct_Void xcmprint(T t) {
    xcmwrite(t);
    out() << std::endl;
    RETURN_VOID;
  }
};

struct xcs_FileWriter;
using xct_FileWriter = SharedPtr<xcs_FileWriter>;
struct xcs_FileWriter: xcs_Writer {
  std::ofstream fout;
  xcs_FileWriter(xct_String path): fout(path->data) {}
  std::ostream& out() {
    return fout;
  }
};

struct xcs_StdoutWriter;
using xct_StdoutWriter = SharedPtr<xcs_StdoutWriter>;
struct xcs_StdoutWriter: xcs_Writer {
  std::ostream& out() {
    return std::cout;
  }
};

xct_StdoutWriter xcv_stdout(new xcs_StdoutWriter);

///////////////////////

void print_trace() {
  std::cout << make_trace_message();
}
xct_Void xcv_assert(xct_Bool cond, xct_String message) {
  if (!cond) {
    std::cout << "--------------------" << std::endl;
    std::cout << "^^^ assertion failure: " << message->data << std::endl;
    print_trace();
    exit(1);
  }
  RETURN_VOID;
}
xct_String assert_message(new xcs_String("assertion failed"));
xct_Void xcv_assert(xct_Bool cond) {
  xcv_assert(cond, assert_message);
  RETURN_VOID;
}
xct_String xcv_trace() {
  return new xcs_String(make_trace_message());
}

void die(std::string message) {
  std::cout << message << std::endl;
  print_trace();
  exit(1);
}

///////////////////////

// TODO: Hmm. Is using a global var the best way to do this?
xct_List<xct_String> xcv_ARGS(new xcs_List<xct_String>());

xct_Void xcv_main();
int main(int argc, char **argv) {
  for (int i = 0; i < argc; i++) {
    xcv_ARGS->xcmpush(new xcs_String(argv[i]));
  }
  xcv_main();
}"""
