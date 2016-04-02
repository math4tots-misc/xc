from .parse import Visitor

PREFIX = r"""
#include <iostream>
#include <fstream>
#include <algorithm>
#include <vector>
#include <memory>

typedef long long xc_Int;
typedef double xc_Float;
typedef const std::string& xc_String;
typedef void xc_Void;

template <class T> struct xcc_List;
template <class T> using xc_List = std::shared_ptr<xcc_List<T>>;
template <class T> struct xcc_List {
  std::vector<T> data;

  xc_List<T> add(T t) {
    data.push_back(t);
    return xc_List<T>(this);
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
"""

class Translator(Visitor):
  def translate(self, program):
    return self.visit(program)

  def visitProgram(self, program):
    hh = []
    ss = []
    for function in program.functions:
      hdr, src = self.visit(function)
      hh.append(hdr)
      ss.append(src)
    return PREFIX + ''.join(hh) + ''.join(ss)

  def visitFunction(self, function):
    sig = '%s xc_%s(%s)' % (
        self.visit(function.return_type),
        function.name,
        ', '.join('%s xc_%s' % (self.visit(type_), name)
            for name, type_ in function.args))
    return ('\n%s;' % sig, '\n%s%s' % (sig, self.visit(function.body)))

  def visitTypename(self, typename):
    return translate_type(typename.type)

  def visitBlockStatement(self, block):
    inside = ''.join(self.visit(statement) for statement in block.statements)
    return '\n{%s\n}' % inside.replace('\n', '\n  ')

  def visitExpressionStatement(self, statement):
    return '\n%s;' % self.visit(statement.expression)

  def visitReturnStatement(self, statement):
    return '\nreturn %s;' % self.visit(statement.expression)

  def visitFunctionCallExpression(self, fcall):
    return 'xc_%s(%s)' % (
        fcall.name,
        ', '.join(self.visit(arg) for arg in fcall.args))

  def visitStringExpression(self, expr):
    return '"' + expr.value + '"'

  def visitIntExpression(self, expr):
    return str(expr.value)

  def visitNameExpression(self, expr):
    return 'xc_' + expr.name

def translate_type(type_):
  if isinstance(type_, str):
    return 'xc_' + type_
  else:
    return 'xc_%s<%s>' % (type_[0], ','.join(map(translate_type, type_[1:])))
