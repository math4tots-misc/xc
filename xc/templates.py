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
#include <functional>
#include <initializer_list>
#include <iostream>
#include <sstream>
#include <stdlib.h>
#include <string>
#include <tuple>
#include <type_traits>
#include <unordered_map>
#include <unordered_set>
#include <vector>
"""

"""Without trace"""
PREFIX_2A = r"""
// Trace is turned off -- embed message and line number in the source,
// but ignore them using the macro.
typedef void xct_Void;
#define RETURN_VOID
#define WITH_FRAME(msg, ln, msg2, expr) (expr)
std::string make_trace_message() {
  return "<Trace is off>\n";
}
"""

"""With Trace"""
PREFIX_2B = r"""
// Code for manual stack trace.
// This code is only used if the 'trace' option is turned on.
// when turned on, a Frame object is inserted into every statement with
// an expression and declaration's expressions.
// Also, note, this is kind of a fragile approach. Coroutines, asynchronous
// code could potentially mess this all up.
// TODO: Figure out a better solution.
typedef std::nullptr_t xct_Void;
#define RETURN_VOID return nullptr
#define WITH_FRAME(msg, ln, msg2, expr) (Frame(msg, ln, msg2).with(expr))
struct Frame;
static std::vector<Frame*> trace;
struct Frame {
  const char* msg;
  int lineno;
  const char* msg2;
  Frame(const char* msg, int lineno, const char* msg2):
      msg(msg), lineno(lineno), msg2(msg2) {
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
  ss << "Traceback (most recent call last):" << std::endl;
  for (auto frame: trace) {
    ss << "  " << frame->msg << frame->lineno << frame->msg2 << std::endl;
  }
  return ss.str();
}
"""

PREFIX_3 = r"""

template <class F, class... Args>
using ResultOf = typename std::result_of<F(Args...)>::type;

template <class T>
inline void hash_combine(std::size_t& seed, const T& v) {
    std::hash<T> hasher;
    seed ^= hasher(v) + 0x9e3779b9 + (seed<<6) + (seed>>2);
}

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

  template <class K>
  SharedPtr(SharedPtr<K> p): SharedPtr(p.ptr) {}

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

  template <class K>
  SharedPtr<K> cast() const {
    return SharedPtr<K>(dynamic_cast<K*>(ptr));
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

  template <class K>
  SharedPtr<T> operator+(SharedPtr<K> other) {
    return ptr->xcm_add_(other);
  }

  template <class K>
  SharedPtr<T> operator-(SharedPtr<K> other) {
    return ptr->xcm_sub_(other);
  }

  template <class K>
  SharedPtr<T> operator*(SharedPtr<K> other) {
    return ptr->xcm_mul_(other);
  }

  template <class K>
  SharedPtr<T> operator/(SharedPtr<K> other) {
    return ptr->xcm_div_(other);
  }

  template <class K>
  SharedPtr<T> operator%(SharedPtr<K> other) {
    return ptr->xcm_mod_(other);
  }

  xct_Int hash() const {
    return ptr->xcm_hash_();
  }

  IterableSharedPtr<T> iterptr() const;

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

  template <class K>
  friend struct SharedPtr;

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
template <class K, class V> using xct_Map = SharedPtr<xcs_Map<K,V>>;
template <class T> struct xcs_Iterable;
template <class T> using xct_Iterable = SharedPtr<xcs_Iterable<T>>;
template <class T> struct xcs_Iterator;
template <class T> using xct_Iterator = SharedPtr<xcs_Iterator<T>>;

template <class T> xct_String xcv_repr(T t);

struct xcs_Object: Root {
  // TODO: repr and str.
};

template <class T>
struct xcs_Iterable: virtual xcs_Object {
  virtual xct_Iterator<T> xcm_iter_()=0;

  template <class F>
  xct_Iterator<ResultOf<F, T>> xcmmap(F f);

  xct_Iterator<T> xcmfilter(std::function<xct_Bool(T)> f);

  xct_List<T> xcmlist();
};

template <class T>
struct xcs_Iterator: virtual xcs_Iterable<T> {
  virtual xct_Bool xcm_more_()=0;
  virtual T xcm_next_()=0;
  xct_Iterator<T> xcm_iter_() final {
    return this;
  }
};

template<class T, class F>
struct MapResult final: virtual xcs_Iterator<ResultOf<F,T>> {
  xct_Iterator<T> iter;
  F f;

  MapResult(xct_Iterator<T> iter, F f):
      iter(iter), f(f) {}

  xct_Bool xcm_more_() override {
    return iter->xcm_more_();
  }

  ResultOf<F,T> xcm_next_() override {
    return f(iter->xcm_next_());
  }
};

template <class T>
struct FilterResult final: virtual xcs_Iterator<T> {
  xct_Iterator<T> iter;
  std::function<xct_Bool(T)> f;
  xct_Bool more;
  T next;

  FilterResult(xct_Iterator<T> iter, std::function<xct_Bool(T)> f):
      iter(iter), f(f), more(false) {
    readynext();
  }

  xct_Bool xcm_more_() override {
    return more;
  }

  T xcm_next_() override {
    T n = next;
    readynext();
    return n;
  }

private:
  void readynext() {
    more = false;
    while (iter->xcm_more_() && !more) {
      next = iter->xcm_next_();
      if (f(next))
        more = true;
    }
  }
};

template <class T>
template <class F>
xct_Iterator<ResultOf<F, T>> xcs_Iterable<T>::xcmmap(F f) {
  return new MapResult<T, F>(xcm_iter_(), f);
}

template <class T>
xct_Iterator<T> xcs_Iterable<T>::xcmfilter(std::function<xct_Bool(T)> f) {
  return new FilterResult<T>(xcm_iter_(), f);
}

struct xcs_String final: xcs_Object {
  const std::string data;

  xcs_String() {}
  xcs_String(const std::string& d): data(d) {}

  xct_String xcm_add_(xct_String other) {
    return new xcs_String(data + other->data);
  }

  xct_Int xcmsize() const {
    return data.size();
  }

  xct_Int xcm_hash_() const {
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

  xct_String xcmjoin(xct_Iterable<xct_String> xs) const {
    auto iter = xs->xcm_iter_();
    if (!iter->xcm_more_())
      return new xcs_String("");

    std::string s;
    s.append(iter->xcm_next_()->data);

    while (iter->xcm_more_()) {
      s.append(data);
      s.append(iter->xcm_next_()->data);
    }
    return new xcs_String(s);
  }

  xct_String xcm_mod_(xct_Iterable<xct_String> xs) const {
    std::string s;
    char last = 'x';
    auto iter = xs->xcm_iter_();
    for (char c: data) {
      if (last == '%') {
        if (c == '%') {
          s.push_back('%');
        } else if (c == 's') {
          if (!iter->xcm_more_()) {
            die("Not enough arguments to string format");
          }
          s.append(iter->xcm_next_()->data);
        } else {
          die(std::string("Invalid format char: ") + c);
        }
      } else {
        if (c != '%') {
          s.push_back(c);
        }
      }

      if (last == '%' && c == '%')
        last = 'x';
      else
        last = c;
    }
    if (iter->xcm_more_()) {
      die("Too many arguments to string format");
    }
    return new xcs_String(s);
  }

  xct_List<xct_String> xcmwords() const;
  xct_List<xct_String> xcmlines() const;
};

template <class T> struct xcs_ListIterator;
template <class T> using xct_ListIterator = SharedPtr<xcs_ListIterator<T>>;
template <class T> struct xcs_ListIterator final: xcs_Iterator<T> {
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

template <class T>
struct xcs_List final: xcs_Iterable<T> {
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

  xct_List<T> xcmsort() {
    std::sort(data.begin(), data.end());
    return this;
  }

  xct_Bool xcm_lt_(xct_List<T> s) {
    return data < s->data;
  }

  xct_Iterator<T> xcm_iter_() final {
    return new xcs_ListIterator<T>(this);
  }

  xct_Int xcm_hash_() {
    size_t seed = 0;
    for (auto item: data)
      hash_combine(seed, item);
    return seed;
  }
};

template <class T>
xct_List<T> xcs_Iterable<T>::xcmlist() {
  xct_List<T> list(new xcs_List<T>());
  for (T t: IterableSharedPtr<xcs_Iterable<T>>(this)) {
    list->xcmpush(t);
  }
  return list;
}

xct_List<xct_String> xcs_String::xcmwords() const {
  xct_List<xct_String> words(new xcs_List<xct_String>({}));
  std::string word;
  for (char c: data) {
    if (isspace(c)) {
      if (!word.empty()) {
        words->xcmpush(new xcs_String(word));
        word.clear();
      }
    } else {
      word.push_back(c);
    }
  }
  if (!word.empty()) {
    words->xcmpush(new xcs_String(word));
  }
  return words;
}

xct_List<xct_String> xcs_String::xcmlines() const {
  xct_List<xct_String> words(new xcs_List<xct_String>({}));
  std::string word;
  for (char c: data) {
    if (c == '\n') {
      if (!word.empty()) {
        words->xcmpush(new xcs_String(word));
        word.clear();
      }
    } else {
      word.push_back(c);
    }
  }
  if (!word.empty()) {
    words->xcmpush(new xcs_String(word));
  }
  return words;
}

template <class K, class V> struct xcs_MapIterator;
template <class K, class V> using xct_MapIterator =
    SharedPtr<xcs_MapIterator<K,V>>;
template <class K, class V>
struct xcs_MapIterator final: xcs_Iterator<K> {
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

template <class K, class V>
struct xcs_Map final: xcs_Iterable<K> {
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

  xct_Iterator<K> xcm_iter_() final {
    return new xcs_MapIterator<K,V>(this);
  }

  xct_Bool xcm_eq_(xct_Map<K,V> m) {
    return data == m->data;
  }

  xct_Int xcm_hash_() {
    size_t seed = 0;
    for (auto& pair: data) {
      hash_combine(seed, pair.first);
      hash_combine(seed, pair.second);
    }
    return seed;
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
struct xcs_StdinReader final: xcs_Reader {
  std::istream& ins() {
    return std::cin;
  }
};

xct_StdinReader xcv_stdin(new xcs_StdinReader());

struct xcs_FileReader;
using xct_FileReader = SharedPtr<xcs_FileReader>;
struct xcs_FileReader final: xcs_Reader {
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
struct xcs_FileWriter final: xcs_Writer {
  std::ofstream fout;
  xcs_FileWriter(xct_String path): fout(path->data) {}
  std::ostream& out() {
    return fout;
  }
};

struct xcs_StdoutWriter;
using xct_StdoutWriter = SharedPtr<xcs_StdoutWriter>;
struct xcs_StdoutWriter final: xcs_Writer {
  std::ostream& out() {
    return std::cout;
  }
};

xct_StdoutWriter xcv_stdout(new xcs_StdoutWriter);

///////////////////////

void print_trace() {
  std::cout << make_trace_message();
}

template <class T>
xct_Void xcv_assert(xct_Bool cond, T message) {
  if (!cond) {
    print_trace();
    std::cout << "AssertionError: " << xcv_repr(message)->data << std::endl;
    exit(1);
  }
  RETURN_VOID;
}
xct_String assert_message(new xcs_String("(*_*)"));
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
