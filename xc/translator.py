from . import lexer
from . import err

PREFIX = r"""// <Autogenerated from xc source>
// requires C++11
// xcs_* -> xc struct type
// xct_* -> xc type
// xcf_* -> xc function
// xcm_* -> xc method
// xca_* -> xc attribute (member variable)
// xcv_* -> xc variable
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
#include <vector>

typedef void xct_Void;
typedef bool xct_Bool;
typedef char xct_Char;
typedef long long xct_Int;
typedef double xct_Float;
struct Root;
template <class T> struct SharedPtr;
template <class T> struct IterableSharedPtr;

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

  //// TODO: Consider whether the following template constructor is
  //// worth having.
  // template <class K> SharedPtr(SharedPtr<K> p): SharedPtr(p->ptr) {}

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

  SharedPtr<T> operator+(SharedPtr<T> other) {
    return ptr->xcm_operator_add(other);
  }

  xct_Int hash() const {
    return ptr->xcm_operator_hash();
  }

  IterableSharedPtr<T> iterptr() const;

protected:
  T* ptr;
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
struct IterableSharedPtr: public SharedPtr<T> {
  IterableSharedPtr(T* p): SharedPtr<T>(p) {}
  typename T::Iterator begin() {
    return SharedPtr<T>::ptr->begin();
  }
  typename T::Iterator end() {
    return SharedPtr<T>::ptr->end();
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
      return p->hash();
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

template <class T> xct_String xcf_repr(T t);

struct xcs_Object: Root {
  // TODO: repr and str.
};

struct xcs_String: xcs_Object {
  const std::string data;
  xcs_String() {}
  xcs_String(const std::string& d): data(d) {}

  xct_String xcm_operator_add(xct_String other) {
    return new xcs_String(data + other->data);
  }

  xct_Int xcm_size() {
    return data.size();
  }

  xct_Int xcm_operator_hash() {
    std::hash<std::string> hasher;
    return hasher(data);
  }

  xct_String xcm_operator_repr() {
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
};

template <class T> struct xcs_List: xcs_Object {
  using Iterator = typename std::vector<T>::iterator;
  std::vector<T> data;

  xcs_List(){}
  xcs_List(std::initializer_list<T> args): data(args) {}

  xct_List<T> xcm_add(T t) {
    data.push_back(t);
    return xct_List<T>(this);
  }

  xct_Int xcm_size() const {
    return data.size();
  }

  xct_Void xcm_push(T t) {
    data.push_back(t);
  }

  T xcm_pop() {
    T d = data.back();
    data.pop_back();
    return d;
  }

  xct_String xcm_operator_repr() {
    std::string s("[");
    bool first = true;
    for (auto x: data) {
      if (!first)
        s.append(", ");
      s.append(xcf_repr(x)->data);
      first = false;
    }
    s.push_back(']');
    return new xcs_String(s);
  }

  decltype(data.begin()) begin() {
    return data.begin();
  }

  decltype(data.end()) end() {
    return data.end();
  }
};

template <class T>
xct_String xcf_repr(T t) {
  return t->xcm_operator_repr();
}

template <>
xct_String xcf_repr(xct_Int t) {
  return new xcs_String(std::to_string(t));
}

template <>
xct_String xcf_repr(xct_Float t) {
  return new xcs_String(std::to_string(t));
}

template <>
xct_String xcf_repr(xct_Bool t) {
  return new xcs_String(t ? "true" : "false");
}

template <class T>
xct_String xcf_str(T t) {
  return xcf_repr(t);
}

template <>
xct_String xcf_str(xct_String t) {
  return t;
}

///////////////////////

struct xcs_Reader;
using xct_Reader = SharedPtr<xcs_Reader>;
struct xcs_Reader: xcs_Object {
  virtual std::istream& ins()=0;
  xct_String xcm_input() {  // read a line of input.
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
  xct_String xcm_read() {  // read entire contents of file.
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
  xct_Void xcm_write(T t) {
    out() << xcf_str(t)->data;
  }
  template <class T>
  xct_Void xcm_print(T t) {
    xcm_write(t);
    out() << std::endl;
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

// Code for manual stack trace.
// This code is only used if the 'trace' option is turned on.
// when turned on, a Frame object is inserted into every function body.
// Also, note, this is kind of a fragile approach. Coroutines, asynchronous
// code could potentially mess this all up.
// TODO: Figure out a better solution.
static std::vector<const char*> trace;
struct Frame {
  Frame(const char* message) {
    trace.push_back(message);
  }
  ~Frame() {
    trace.pop_back();
  }
};
std::string make_trace_message() {
  std::stringstream ss;
  for (auto message: trace) {
    ss << "  *** " << message << std::endl;
  }
  return ss.str();
}
void print_trace() {
  std::cout << make_trace_message();
}
xct_Void xcf_assert(xct_Bool cond, xct_String message) {
  if (!cond) {
    std::cout << "--------------------" << std::endl;
    std::cout << "^^^ assertion failure: " << message->data << std::endl;
    print_trace();
    exit(1);
  }
}
xct_String xcf_trace() {
  return new xcs_String(make_trace_message());
}

///////////////////////

// TODO: Hmm. Is using a global var the best way to do this?
xct_List<xct_String> xcv_ARGS(new xcs_List<xct_String>());

xct_Void xcf_main();
int main(int argc, char **argv) {
  for (int i = 0; i < argc; i++) {
    xcv_ARGS->xcm_push(new xcs_String(argv[i]));
  }
  xcf_main();
}"""

def translate(source, loader=None, trace=False):
  return Translator(source, loader=loader, trace=trace).translate()

class Translator(object):

  def __init__(self, source, loader=None, included=None, trace=False):
    self.loader = loader
    self.source = source
    self.tokens = lexer.lex(source)
    self.i = 0
    self.additional_includes = []
    self.included = included or set()
    self.trace = trace

  def peek(self):
    return self.tokens[self.i]

  def gettok(self):
    self.i += 1
    return self.tokens[self.i-1]

  def at(self, type_):
    return self.peek().type == type_

  def consume(self, type_):
    if self.at(type_):
      return self.gettok()

  def expect(self, type_):
    if self.at(type_):
      return self.gettok()
    else:
      raise err.Err(
          'Expected token of type %r but found %r' % (
              type_, self.peek()),
          self.peek())

  ##############

  def translate(self):
    return '\n//////////////'.join((PREFIX, self.translate_without_prefix()))

  def translate_without_prefix(self):
    return '\n'.join(self.parse_program())

  def parse_program(self):
    a = b = c = d = ''
    for inc in self.additional_includes:
      a += self.process_include(inc)
    while not self.at('EOF'):
      if self.at('fn'):
        y, z = self.parse_function()
        c += y
        d += z
      elif self.at('class'):
        x, y, z = self.parse_class()
        a += x
        b += y
        d += z
      elif self.at('var'):
        c += self.parse_global_declaration()
      elif self.at('include'):
        a += self.parse_include() + a
      elif self.consume('STR') or self.consume('CHR'):
        # TODO: Consider inserting these comments into generated source.
        pass  # string or char style comments
      else:
        raise err.Err('Expected function or class', self.peek())
    # a = includes and forward type declarations
    # b = type declarations
    # c = function declarations and global variable definitions
    # d = function and method definitions
    return a, b, c, d

  def parse_include(self):
    self.expect('include')
    uri = eval((self.consume('STR') or self.consume('CHR').value))
    return self.process_include(uri)

  def process_include(self, uri):
    data = self.loader.load(uri)
    source = lexer.Source(uri, data)
    self.included.add(uri)
    return (Translator(
        source, loader=self.loader, included=self.included)
        .translate_without_prefix())

  def parse_class(self):
    self.expect('class')
    name = self.expect('ID').value
    if self.at('('):
      typeargs = self.parse_typearg_sig()
      # TODO: Don't do this hack. Figure out a cleaner solution.
      # TODO: Stop duplicating this evil hack.
      typeargnames = ', '.join(
          name for name in typeargs.replace(',', ' ').split()
          if name != 'class')
      a = ((
          '\ntemplate <%s> struct xcs_%s;' +
          '\ntemplate <%s> using xct_%s = SharedPtr<xcs_%s<%s>>;') % (
              typeargs, name,
              typeargs, name, name, typeargnames))
    else:
      typeargs = None
      a = '\nstruct xcs_%s;\nusing xct_%s = SharedPtr<xcs_%s>;' % (
          name, name, name)
    if self.consume(':'):
      base = self.parse_type() + '::Pointee'
    else:
      base = 'xcs_Object'
    attrs = []
    decls = []
    defns = []
    self.expect('{')
    while not self.consume('}'):
      if self.at('var'):
        attrs.append(self.parse_attribute())
      elif self.at('fn'):
        decl, defn = self.parse_method(name, typeargs)
        decls.append(decl)
        defns.append(defn)
      else:
        raise err.Err('Expected attribute or method', self.peek())
    if typeargs is None:
      b = '\nstruct xcs_%s: %s\n{%s%s\n};' % (
          name, base,
          ''.join(attrs).replace('\n', '\n  '),
          ''.join(decls).replace('\n', '\n  '))
    else:
      b = '\ntemplate <%s>\nstruct xcs_%s: %s\n{%s%s\n};' % (
          typeargs,
          name, base,
          ''.join(attrs).replace('\n', '\n  '),
          ''.join(decls).replace('\n', '\n  '))
    c = ''.join(defns)
    return a, b, c

  def parse_attribute(self):
    self.expect('var')
    name = self.expect('ID').value
    type_ = self.parse_type()
    return '\n%s xca_%s;' % (type_, name)

  def parse_method(self, class_name, typeargs):
    token = self.expect('fn')
    if self.at('['):  # NOTE: constructors cannot have template args
      return self.parse_rest_of_constructor(class_name, typeargs, token)
    name = self.expect('ID').value
    # TODO: Think about whether I want to allow template methods.
    argsig = self.parse_arg_sig()
    if not self.at('{'):
      ret = self.parse_type()
    else:
      ret = 'xct_Void'
    body = self.parse_block()

    if self.trace:
      body = patch_block_with_stack_frame(
          body, self.source.filespec, '%s.%s' % (class_name, name),
          token.lineno())

    decl = '\n%s xcm_%s(%s);' % (ret, name, argsig)
    if typeargs is None:
      defn = '\n%s xcs_%s::xcm_%s(%s)%s' % (
          ret, class_name, name, argsig, body)
    else:
      # TODO: Don't do this hack. Figure out a cleaner solution.
      # TODO: Stop duplicating this evil hack.
      typeargnames = ', '.join(
          name for name in typeargs.replace(',', ' ').split()
          if name != 'class')
      defn = '\ntemplate <%s>\n%s xcs_%s<%s>::xcm_%s(%s)%s' % (
          typeargs, ret, class_name, typeargnames, name, argsig, body)

    return decl, defn

  def parse_rest_of_constructor(self, class_name, typeargs, token):
    argsig = self.parse_arg_sig()
    body = self.parse_block()

    if self.trace:
      body = patch_block_with_stack_frame(
          body, self.source.filespec,
          '%s.<constructor>' % class_name,
          token.lineno())

    decl = '\nxcs_%s(%s);' % (class_name, argsig)
    if typeargs is None:
      defn = '\nxcs_%s::xcs_%s(%s)%s' % (
          class_name, class_name, argsig, body)
    else:
      # TODO: Don't do this hack. Figure out a cleaner solution.
      # TODO: Stop duplicating this evil hack.
      typeargnames = ', '.join(
          name for name in typeargs.replace(',', ' ').split()
          if name != 'class')
      defn = '\ntemplate <%s>\nxcs_%s<%s>::xcs_%s(%s)%s' % (
          typeargs, class_name, typeargnames, class_name, argsig, body)
    return decl, defn

  def parse_function(self):
    token = self.expect('fn')
    raw_name = self.expect('ID').value
    name = 'xcf_' + raw_name
    if self.at('('):
      typeargs = self.parse_typearg_sig()
    else:
      typeargs = None
    args = self.parse_arg_sig()
    type_ = 'xct_Void' if self.at('{') else self.parse_type()
    body = self.parse_block()

    if self.trace:
      body = patch_block_with_stack_frame(
          body, self.source.filespec, raw_name,
          token.lineno())

    if typeargs is None:
      sig = '%s %s(%s)' % (type_, name, args)
    else:
      sig = 'template <%s>\n%s %s(%s)' % (typeargs, type_, name, args)
    return '\n%s;' % sig, '\n%s%s' % (sig, body)

  def parse_type(self):
    name = 'xct_' + self.expect('ID').value
    if self.at('('):
      return '%s<%s>' % (name, self.parse_typeargs())
    else:
      return name

  def parse_statement(self):
    if self.consume('break'):
      return '\nbreak;'
    elif self.consume('continue'):
      return '\ncontinue;'
    elif self.consume('while'):
      cond = self.parse_expression()
      body = self.parse_block()
      return '\nwhile (%s)%s' % (cond, body)
    elif self.consume('for'):
      name = self.expect('ID').value
      self.expect('in')
      container = self.parse_expression()
      body = self.parse_block()
      return '\nfor (auto xcv_%s: %s.iterptr())%s' % (name, container, body)
    elif self.consume('return'):
      return '\nreturn %s;' % self.parse_expression()
    elif self.at('{'):
      return self.parse_block()
    elif self.at('var'):
      return self.parse_declaration()
    else:
      return '\n%s;' % self.parse_expression()

  def parse_declaration(self):
    self.expect('var')
    name = self.expect('ID').value
    if not self.at('='):
      type_ = self.parse_type()
    else:
      type_ = 'auto'
    if self.consume('='):
      value = ' = ' + self.parse_expression()
    else:
      value = ''
    return '\n%s xcv_%s%s;' % (type_, name, value)

  def parse_expression(self):
    return self.parse_or_expression()

  def parse_or_expression(self):
    e = self.parse_and_expression()
    while True:
      if self.consume('and'):
        r = self.parse_and_expression()
        e = '%s && %s' % (e, r)
      else:
        break
    return e

  def parse_and_expression(self):
    e = self.parse_equality_expression()
    while True:
      if self.consume('and'):
        r = self.parse_equality_expression()
        e = '%s && %s' % (e, r)
      else:
        break
    return e

  def parse_equality_expression(self):
    e = self.parse_inequality_expression()
    while True:
      if self.consume('=='):
        r = self.parse_inequality_expression()
        e = '%s == %s' % (e, r)
      elif self.consume('!='):
        r = self.parse_inequality_expression()
        e = '%s != %s' % (e, r)
      else:
        break
    return e

  def parse_inequality_expression(self):
    e = self.parse_additive_expression()
    while True:
      if self.consume('<'):
        r = self.parse_additive_expression()
        e = '%s < %s' % (e, r)
      elif self.consume('<='):
        r = self.parse_additive_expression()
        e = '%s <= %s' % (e, r)
      elif self.consume('>'):
        r = self.parse_additive_expression()
        e = '%s > %s' % (e, r)
      elif self.consume('>='):
        r = self.parse_additive_expression()
        e = '%s >= %s' % (e, r)
      else:
        break
    return e

  def parse_additive_expression(self):
    e = self.parse_multiplicative_expression()
    while True:
      if self.consume('+'):
        r = self.parse_multiplicative_expression()
        e = '%s + %s' % (e, r)
      elif self.consume('-'):
        r = self.parse_multiplicative_expression()
        e = '%s - %s' % (e, r)
      else:
        break
    return e

  def parse_multiplicative_expression(self):
    e = self.parse_prefix_expression()
    while True:
      if self.consume('*'):
        r = self.parse_prefix_expression()
        e = '%s * %s' % (e, r)
      elif self.consume('/'):
        r = self.parse_prefix_expression()
        e = '%s / %s' % (e, r)
      elif self.consume('%'):
        r = self.parse_prefix_expression()
        e = '%s %% %s' % (e, r)
      else:
        break
    return e

  def parse_prefix_expression(self):
    if self.at('-'):
      return '-' + self.parse_postfix_expression()
    else:
      return self.parse_postfix_expression()

  def parse_postfix_expression(self):
    e = self.parse_primary_expression()
    while self.at('.'):
      if self.consume('.'):
        name = self.expect('ID').value
        if self.at('('):
          typeargs = self.parse_typeargs()
          args = self.parse_args()
          e = '%s->xcm_%s<%s>(%s)' % (e, name, typeargs, args)
        elif self.at('['):
          args = self.parse_args()
          e = '%s->xcm_%s(%s)' % (e, name, args)
        elif self.consume('='):
          v = self.parse_expression()
          e = '%s->xca_%s = %s' % (e, name, v)
        else:
          e = '%s->xca_%s' % (e, name)
      else:
        break
    return e

  def parse_primary_expression(self):
    token = self.peek()
    if self.consume('('):
      e = self.parse_expression()
      self.expect(')')
      return e
    elif self.at('ID'):
      name = self.expect('ID').value
      if self.at('('):
        typeargs = self.parse_typeargs()
        args = self.parse_args()
        return 'xcf_%s<%s>(%s)' % (name, typeargs, args)
      elif self.at('['):
        args = self.parse_args()
        return 'xcf_%s(%s)' % (name, args)
      elif self.consume('='):
        return 'xcv_%s = %s' % (name, self.parse_expression())
      else:
        return 'xcv_' + name
    elif self.consume('new'):
      type_ = self.parse_type()
      args = self.parse_args()
      return '%s(new %s::Pointee(%s))' % (type_, type_, args)
    elif self.consume('self'):
      return 'this'
    elif self.consume('true'):
      return 'true'
    elif self.consume('false'):
      return 'false'
    elif self.at('INT'):
      return self.expect('INT').value + 'LL'
    elif self.at('FLT'):
      return self.expect('FLT').value
    elif self.at('CHR'):
      return "'%s'" % sanitize_string(eval(self.expect('CHR').value))
    elif self.at('STR'):
      return 'xct_String(new xcs_String("%s"))' % (
          sanitize_string(eval(self.expect('STR').value)),)
    elif self.consume('$'):
      if self.at('('):
        pass  # TODO: Make tuple
      else:
        k = self.parse_type()
        if self.consume(','):
          pass  # TODO: Make Map
        else:
          return 'xct_List<%s>(new xcs_List<%s>({%s}))' % (
              k, k, self.parse_args())
    else:
      raise err.Err('Expected expression', token)

  def parse_block(self):
    self.expect('{')
    stmts = []
    while not self.consume('}'):
      stmts.append(self.parse_statement())
      while self.consume(';'):
        pass
    return '\n{%s\n}' % ''.join(stmts).replace('\n', '\n  ')

  def parse_fullarg_sig(self):
    if self.at('('):
      typeargs = self.parse_typearg_sig()
    else:
      typeargs = None
    args = self.parse_arg_sig()
    return typeargs, args

  def parse_arg_sig(self):
    self.expect('[')
    args = []
    while not self.consume(']'):
      name = 'xcv_' + self.expect('ID').value
      type_ = self.parse_type()
      args.append('%s %s' % (type_, name))
      self.consume(',')
    return ', '.join(args)

  def parse_typearg_sig(self):
    self.expect('(')
    args = []
    while not self.consume(')'):
      name = 'xct_' + self.expect('ID').value
      args.append('class ' + name)
      self.consume(',')
    return ', '.join(args)

  def parse_typeargs(self):
    self.expect('(')
    args = []
    while not self.consume(')'):
      args.append(self.parse_type())
      self.consume(',')
    return ', '.join(args)

  def parse_args(self):
    self.expect('[')
    args = []
    while not self.consume(']'):
      args.append(self.parse_expression())
      self.consume(',')
    return ', '.join(args)


def sanitize_string(s):
  return (s
      .replace('\n', '\\n')
      .replace('\t', '\\t')
      .replace('"', '\\"')
      .replace("'", "\\'"))


def patch_block_with_stack_frame(block, filespec, funcname, lineno):
  fexpr = (
      r'Frame frame("in file \"%s\" in function \"%s\" ' +
      r'(defined on line %d)");') % (
        sanitize_string(filespec),
        sanitize_string(funcname),
        lineno)

  """Depends on block always starting with a newline and open brace"""
  return '%s\n  %s%s' % (block[:2], fexpr, block[2:])
