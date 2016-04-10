from . import ast
from . import err

PREFIX = r"""

public static void main(java.lang.String[] args) {
  main();
}

public static void println(Stringable s) {
  System.out.println(s.to_String().data);
}

public static interface Stringable {
  public String to_String();
}

public static class Int implements Stringable {
  public int data;

  public Int(int data) {
    this.data = data;
  }

  public String to_String() {
    return new String(java.lang.Integer.toString(data));
  }

  public Int op_add() {
    return 
  }
}

public static class String implements Stringable {
  public java.lang.String data;

  public String(java.lang.String data) {
    this.data = data;
  }

  public String to_String() {
    return this;
  }
}

///////////////////
"""

class Translator(ast.Visitor):
  def generic_visit(self, node, *args, **kwargs):
    raise err.Err(str(type(node)), node.token)  # FUBAR

  def translate(self, node):
    return "public class XcProgram {%s%s\n}" % (
        PREFIX.replace('\n', '\n  '),
        self.visit(node).replace('\n', '\n  '),)

  def visitProgram(self, node):
    return ''.join(self.visit(function) for function in node.functions)

  def visitFunction(self, node):
    vartypes = dict()
    for name, type_ in node.args:
      vartypes[name] = type_
    return '\npublic static %s %s(%s)%s' % (
        translate_type(node.return_type),
        translate_name(node.name),
        ', '.join('%s %s' % (
            translate_type(type_),
            translate_name(name))
            for name, type_ in node.args),
        self.visit(node.body))

  def visitBlock(self, node):
    return '\n{%s\n}' % (
        ''.join(self.visit(s) for s in node.stmts)
            .replace('\n', '\n  '))

  def visitDeclaration(self, node):
    return '\n%s %s = %s;' % (
        translate_type(node.type),
        translate_name(node.name),
        self.visit(node.expr))

  def visitReturn(self, node):
    return '\nreturn %s;' % self.visit(node.expr)

  def visitExpressionStatement(self, node):
    return '\n%s;' % self.visit(node.expr)

  def visitChar(self, node):
    return "new Char('%s')" % sanitize_string(node.value)

  def visitInt(self, node):
    return 'new Int(%d)' % node.value

  def visitFloat(self, node):
    return 'new Float(%f)' % node.value

  def visitString(self, node):
    return 'new String("%s")' % sanitize_string(node.value)

  def visitName(self, node):
    return translate_name(node.name)

  def visitNew(self, node):
    return 'new %s()' % translate_type(node.type)

  def visitFunctionCall(self, node):
    # TODO: Call functions with generic parameters.
    return '%s(%s)' % (
        translate_name(node.name),
        ', '.join(map(self.visit, node.args)))

  def visitMethodCall(self, node):
    # TODO: Call methods with generic parameters.
    return '%s.%s(%s)' % (
        self.visit(node.owner),
        translate_name(node.name),
        ', '.join(map(self.visit, node.args)))

def translate_type(t):
  return (
      translate_name(t[0]) if len(t) == 1 else
      '%s<%s>' % (
          translate_name(t[0]), ', '.join(map(translate_type, t[1:]))))

def translate_name(name):
  return {
      'goto': 'goto_',
      'goto_': 'goto__',
      'Void': 'void',
  }.get(name, name)

def sanitize_string(s):
  return (s
      .replace('\n', '\\n')
      .replace('\t', '\\t')
      .replace('"', '\\"')
      .replace("'", "\\'"))
