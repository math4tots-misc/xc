from .parse import Visitor

PREFIX = r"""
#include <iostream>
#include <fstream>
#include <algorithm>

typedef long long xc_Int;
typedef double xc_Float;
typedef const std::string& xc_String;
typedef void xc_Void;

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
  def __init__(self):
    self.hdr = []
    self.src = []

  def get(self):
    hh = ''.join(''.join(h) for h in self.hdr)
    self.hdr = [[hh]]
    ss = ''.join(''.join(s) for s in self.src)
    self.src = [[ss]]
    return PREFIX + hh + ss

  def make_hdr_stream(self):
    self.hdr.append([])
    return self.hdr[-1]

  def make_src_stream(self):
    self.src.append([])
    return self.src[-1]

  def translate(self, program):
    return self.visit(program)

  def visitProgram(self, program):
    for function in program.functions:
      self.visit(function)
    return self.get()

  def visitFunction(self, function):
    hs = self.make_hdr_stream()
    ss = self.make_src_stream()
    sig = '%s xc_%s(%s)' % (
        self.visit(function.return_type),
        function.name,
        ', '.join('%s xc_%s' % (self.visit(type_), name)
            for name, type_ in function.args))
    hs.append('\n%s;' % sig)
    ss.append('\n%s%s' % (sig, self.visit(function.body)))

  def visitTypename(self, typename):
    return 'xc_' + typename.name

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
