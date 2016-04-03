from .parse import Visitor

PREFIX = r"""
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
"""

class Translator(Visitor):
  def translate(self, program):
    return self.visit(program)

  def visitProgram(self, program):
    hh = []
    ss = []
    for function in program.functions:
      hdr, src = self.visitFunction(function)
      hh.append(hdr)
      ss.append(src)
    return PREFIX + ''.join(hh) + ''.join(ss)

  def visitFunction(self, function):
    sig = '%s xcf_%s(%s)' % (
        self.visit(function.return_type),
        function.name,
        ', '.join('%s xcv_%s' % (self.visit(type_), name)
            for name, type_ in function.args))
    if function.type_args is not None:
      sig = 'template <%s> %s' % (
          ', '.join('class xct_' + t for t in function.type_args),
          sig)
    return ('\n%s;' % sig, '\n%s%s' % (sig, self.visit(function.body)))

  def visitTypename(self, typename):
    return translate_type(typename.type)

  def visitBlockStatement(self, block):
    inside = ''.join(self.visit(statement) for statement in block.statements)
    return '\n{%s\n}' % inside.replace('\n', '\n  ')

  def visitDeclarationStatement(self, statement):
    if statement.type is None and statement.expression is None:
      raise ValueError(
          'The type and expression of a declaration statement cannot '
          'both be None')
    t = (
        'auto' if statement.type is None else
        translate_type(statement.type.type))
    v = (
        '' if statement.expression is None else
        ' = ' + self.visit(statement.expression))
    return '%s xcv_%s%s;' % (t, statement.name, v)

  def visitReturnStatement(self, statement):
    return '\nreturn %s;' % self.visit(statement.expression)

  def visitExpressionStatement(self, statement):
    return '\n%s;' % self.visit(statement.expression)

  def visitFunctionCallExpression(self, fcall):
    return 'xcf_%s%s(%s)' % (
        fcall.name,
        '' if fcall.type_args is None else (
            '<%s>' % ', '.join(translate_type(t.type)
            for t in fcall.type_args)),
        ', '.join(self.visit(arg) for arg in fcall.args))

  def visitMethodCallExpression(self, mcall):
    return '%s->xcm_%s(%s)' % (
        self.visit(mcall.owner),
        mcall.name,
        ', '.join(self.visit(arg) for arg in mcall.args))

  def visitNewExpression(self, expr):
    t = translate_type(expr.type.type)
    return '%s(new typename %s::Pointee)' % (t, t)

  def visitNameExpression(self, expr):
    return 'xcv_' + expr.name

  def visitStringExpression(self, expr):
    return '"' + sanitize_string(expr.value) + '"'

  def visitCharExpression(self, expr):
    return "'" + sanitize_string(expr.value) + "'"

  def visitIntExpression(self, expr):
    return str(expr.value) + 'LL'

def translate_type(type_):
  if isinstance(type_, str):
    return 'xct_' + type_
  else:
    return 'xct_%s<%s>' % (type_[0], ','.join(map(translate_type, type_[1:])))

def sanitize_string(s):
  return (s
      .replace('\n', '\\n')
      .replace('\t', '\\t')
      .replace('"', '\\"')
      .replace("'", "\\'"))
