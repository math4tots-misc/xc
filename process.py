"""process.py
Domain specific language for programming contests.

Generates C++11 source.

Builtin types,

  Any
    Any type can be converted to 'Any'.
    You can try to convert 'Any' to any type, but it will
    throw an exception if you try to cast it to the wrong type.
  Object
    'Object' is a base class of all objects except primitive types.
    There are seven primitive types:
      Void, Bool, Char, Int, Float, Tuple, Function
  Void
  Bool
  Char
  Int
  Float
  String
  Tuple(Args...)
  TupleObject(Args...)
  Vector(T)
  Deque(T)
  Map(K, V)
  Set(T)
  Function(R, Args...)

Only builtin types can be generics. User defined types or functions
may not be generic.

Caveats:

  * Any and Tuple
    Since Any should be a fixed size and since Tuple can be arbitrarily
    large, if you cast a Tuple to Any, it will dynamically allocate
    memory for the Tuple in the heap.

  * Any and primitive types except Tuple
    For all primitive types besides Tuple, if a value is converted to Any,
    the Any object will not allocate any extra memory.

"""

import re
import sys
import os

## Err
class Err(Exception):
  def __init__(self, message, *tokens):
    self.tokens = list(tokens)
    self.message = message

  def add_token(self, token):
    self.tokens.append(token)

  def __str__(self):
    return repr(self)

  def __repr__(self):
    return 'err: %s%s' % (
        self.message,
        ''.join(map(location_message, self.tokens)))

def location_message(token):
  return '\nin file "%s" on line %d %r:\n%s\n%s' % (
      token.source.filespec,
      token.lineno(),
      token,
      token.line(),
      (token.colno()-1) * ' ' + '*')

## Lexer
def compile_re(pattern):
  return re.compile(pattern, re.DOTALL|re.MULTILINE)

class Source(object):
  def __init__(self, filespec, data):
    self.filespec = filespec
    self.data = data

symbols = tuple(reversed(sorted((
    '(', ')', '[', ']', '{', '}', '.', ',', ';', '=', '==', '!=', ':',
    '+', '-', '*', '/', '%', '$', '<', '>', '<=', '>=',
    '+=', '-=', '*=', '/=', '%='))))
keywords = (
    'fn', 'return', 'if', 'else', 'while', 'break', 'continue',
    'var', 'include', 'extern', 'new',
    'class', 'for', 'in', 'is', 'not', 'and', 'or')
whitespace_pattern = compile_re(r'(?:\s|#.*?$)*')
err_pattern = compile_re(r'\S+')
token_table = tuple((type_, compile_re(pattern)) for type_, pattern in
    [
      ('STR', r'"""(?:\\|(?!\"\"\").)*"""'),
      ('STR', r"'''(?:\\|(?!\'\'\').)*'''"),
      ('STR', r'"(?:\\|(?!\").)*"'),
      ('STR', r"'(?:\\|(?!\').)*'"),
      ('STR', r'r""".*?"""'),
      ('STR', r"r'''.*?'''"),
      ('STR', r'r".*?"'),
      ('STR', r"r'.*?'"),
      ('CHR', r'c"(?:\\|(?!\").)*"'),
      ('CHR', r"c'(?:\\|(?!\').)*'"),
      ('FLT', r'\d+\.\d*'),
      ('FLT', r'\d*\.\d+'),
      ('INT', r'\d+'),
    ] +
    [(kw, r'\b%s\b' % kw) for kw in keywords] +
    [(sym, re.escape(sym)) for sym in symbols] +
    [('ID', r'\w+')])

class Token(object):
  def __init__(self, type_, value, i, source):
    self.type = type_
    self.value = value
    self.i = i
    self.source = source

  def __repr__(self):
    return '(%s, %r)@%d' % (self.type, self.value, self.i)

  def lineno(self):
    return 1 + self.source.data.count('\n', 0, self.i)

  def colno(self):
    return self.i - self.source.data.rfind('\n', 0, self.i)

  def line(self):
    a = self.source.data.rfind('\n', 0, self.i) + 1
    b = self.source.data.find('\n', self.i)
    if b == -1:
      b = len(self.source.data)
    return self.source.data[a:b]

def lex(source):
  s = source.data
  tokens = []
  i = whitespace_pattern.match(s).end()
  while i < len(s):
    for type_, pattern in token_table:
      m = pattern.match(s, i)
      if m:
        tokens.append(Token(type_, m.group(), i, source))
        i = m.end()
        break
    else:
      raise Err(
          'Unrecognized token',
          Token('ERR', err_pattern.match(s, i).group(), i, source))
    i = whitespace_pattern.match(s, i).end()
  tokens.append(Token('EOF', None, i, source))
  return tokens

## Parser
string_literals = dict()

def register_string(s):
  if s in string_literals:
    id_ = string_literals[s]
  else:
    id_ = len(string_literals)
    string_literals[s] = id_

  return 'kkstrlit%d' % id_

class Parser(object):

  def __init__(self, source):
    self.source = source
    self.tokens = lex(source)
    self.i = 0

    # Output vars
    self.includes = set()
    self.forward_decls = ''
    self.decls = ''
    self.vardecls = ''
    self.defs = ''

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
      raise Err(
          'Expected token of type %r but found %r' % (
              type_, self.peek()),
          self.peek())

  ##############

  def parse(self):
    while not self.at('EOF'):
      if self.consume('include'):
        self.includes.add(self.expect('STR'))
      elif self.at('fn'):
        self.parse_function()
      elif self.at('class'):
        self.parse_class()
      elif self.at('interface'):
        self.parse_interface()
      elif self.at('using'):
        self.decls += self.parse_using()
      elif self.consume('var'):
        name = 'vv' + self.expect('ID').value
        type_ = 'auto'
        if self.at('ID'):
          type_ = self.parse_type()
        value = ''
        if self.consume('='):
          value = ' = ' + self.parse_expression()
        if type_ != 'auto':
          self.decls += '\nextern %s %s;' % (type_, name)
        self.vardecls += '\n%s %s%s;' % (type_, name, value)
      else:
        raise Err('Top level, found %r' % (
            type_, self.peek()))

  def parse_function(self):
    self.expect('fn')
    name = 'vv' + self.expect('ID').value
    args = self.parse_argsigs()
    rettype = 'auto'
    if self.at('ID'):
      rettype = self.parse_type()
    elif name == 'vvmain':
      rettype = 'PPVoid'
    decl = '\n%s %s%s;' % (rettype, name, args)
    self.decls += decl
    body = self.parse_block()
    self.defs += '\n%s %s%s%s' % (rettype, name, args, body)

  def parse_argsigs(self):
    self.expect('[')
    args = []
    while not self.consume(']'):
      name = 'vv' + self.expect('ID').value
      type_ = self.parse_type()
      args.append('%s %s' % (type_, name))
      self.consume(',')
    return '(%s)' % ', '.join(args)

  def parse_type(self):
    name = 'PP' + self.expect('ID').value
    if self.consume('('):
      args = []
      while not self.consume(')'):
        args.append(self.parse_type())
        self.consume(',')
      return '%s<%s>' % (name, ', '.join(args))
    else:
      return name

  def parse_statement(self):
    if self.at('{'):  # }
      return self.parse_block()
    elif self.consume('return'):
      return '\nreturn %s;' % self.parse_expression()
    elif self.consume('var'):
      name = 'vv' + self.expect('ID').value
      type_ = 'auto'
      if self.at('ID'):
        type_ = self.parse_type()
      val = ''
      if self.consume('='):
        val = ' = ' + self.parse_expression()
      return '\n%s %s%s;' % (type_, name, val)
    elif self.at('if'):
      return self.parse_if()
    elif self.consume('while'):
      cond = self.parse_expression()
      body = self.parse_block()
      return '\nwhile (%s)%s' % (cond, body)
    elif self.consume('for'):
      n = 'vv' + self.expect('ID').value
      self.expect('in')
      cont = self.parse_expression()
      body = self.parse_block()
      return '\nfor (auto %s: %s)%s' % (n, cont, body)
    elif self.consume('break'):
      return '\nbreak;'
    elif self.consume('continue'):
      return '\ncontinue;'
    else:
      return '\n%s;' % self.parse_expression()

  def parse_if(self):
    self.expect('if')
    cond = self.parse_expression()
    body = self.parse_block()
    other = ''
    if self.consume('else'):
      if self.at('if'):
        other = '\nelse ' + self.parse_if().lstrip()
      else:
        other = '\nelse' + self.parse_block()
    return '\nif (%s)%s%s' % (cond, body, other)

  def parse_expression(self):
    return self.parse_relation_expression()

  def parse_relation_expression(self):
    e = self.parse_additive_expression()
    if self.consume('=='):
      return '(%s==%s)' % (e, self.parse_additive_expression())
    if self.consume('!='):
      return '(%s!=%s)' % (e, self.parse_additive_expression())
    if self.consume('<'):
      return '(%s<%s)' % (e, self.parse_additive_expression())
    if self.consume('<='):
      return '(%s<=%s)' % (e, self.parse_additive_expression())
    if self.consume('>'):
      return '(%s>%s)' % (e, self.parse_additive_expression())
    if self.consume('>='):
      return '(%s>=%s)' % (e, self.parse_additive_expression())
    return e

  def parse_additive_expression(self):
    e = self.parse_multiplicative_expression()
    while True:
      if self.consume('+'):
        e = '(%s+%s)' % (e, self.parse_multiplicative_expression())
        continue
      if self.consume('-'):
        e = '(%s-%s)' % (e, self.parse_multiplicative_expression())
        continue
      break
    return e

  def parse_multiplicative_expression(self):
    e = self.parse_prefix_expression()
    while True:
      if self.consume('*'):
        e = '(%s*%s)' % (e, self.parse_prefix_expression())
        continue
      if self.consume('/'):
        e = '(%s/%s)' % (e, self.parse_prefix_expression())
        continue
      if self.consume('%'):
        e = '(%s%%%s)' % (e, self.parse_prefix_expression())
        continue
      break
    return e

  def parse_prefix_expression(self):
    if self.at('-'):
      return '(-%s)' % self.parse_postfix_expression()
    else:
      return self.parse_postfix_expression()

  def parse_postfix_expression(self):
    e = self.parse_primary_expression()
    while True:
      if self.at('(') or self.at('['):  # ] )
        e = '%s%s' % (e, self.parse_args())
        continue
      if self.consume('.'):
        n = self.expect('ID').value
        if self.at('(') or self.at('['):  # ] )
          e = '%s->mm%s%s' % (e, n, self.parse_args())
        elif self.consume('='):
          e = '(%s->aa%s = %s)' % (e, n, self.parse_expression())
        elif self.consume('+='):
          e = '(%s->aa%s += %s)' % (e, n, self.parse_expression())
        elif self.consume('-='):
          e = '(%s->aa%s -= %s)' % (e, n, self.parse_expression())
        elif self.consume('*='):
          e = '(%s->aa%s *= %s)' % (e, n, self.parse_expression())
        elif self.consume('/='):
          e = '(%s->aa%s /= %s)' % (e, n, self.parse_expression())
        elif self.consume('%='):
          e = '(%s->aa%s %= %s)' % (e, n, self.parse_expression())
        else:
          e = '%s->aa%s' % (e, n)
        continue
      break
    return e

  def parse_args(self, inps='[]', outs='()'):
    self.expect(inps[0])
    args = []
    while not self.consume(inps[1]):
      args.append(self.parse_expression())
      self.consume(',')
    return '%s%s%s' % (outs[0], ', '.join(args), outs[1])

  def parse_primary_expression(self):
    if self.at('('):
      e = self.parse_expression()
      self.expect(')')
      return e
    elif self.at('ID'):
      name = 'vv' + self.expect('ID').value
      if self.consume('='):
        e = self.parse_expression()
        return '(%s = %s)' % (name, e)
      if self.consume('='):
        return '(%s = %s)'  % (name, self.parse_expression())
      if self.consume('+='):
        return '(%s += %s) ' % (name, self.parse_expression())
      if self.consume('-='):
        return '(%s -= %s) ' % (name, self.parse_expression())
      if self.consume('*='):
        return '(%s *= %s) ' % (name, self.parse_expression())
      if self.consume('/='):
        return '(%s /= %s) ' % (name, self.parse_expression())
      if self.consume('%='):
        return '(%s %= %s) ' % (name, self.parse_expression())
      else:
        return name
    elif self.at('INT'):
      return '((PPInt) %s)' % self.expect('INT').value
    elif self.at('FLT'):
      return self.expect('FLT').value
    elif self.at('STR'):
      return register_string(sanitize_string(eval(self.expect('STR').value)))
    elif self.at('CHR'):
      return "'%s'" % sanitize_string(eval(self.expect('CHR').value[1:]))
    elif self.consume('$'):
      t = ''
      if self.at('ID'):
        t = '<%s>' % self.parse_type()
      if self.at('['):  # ]
        return 'V%s(%s)' % (t, self.parse_args(outs='{}'))
      elif self.at('{'):  # }
        return 'M%s(%s)' % (t, self.parse_args(inps='{}', outs='{}'))
      else:
        return Err('Invalid aggregate literal', self.peek())
    raise Err('Expected expression', self.peek())

  def parse_block(self):
    self.expect('{')
    stmts = []
    while not self.consume('}'):
      stmts.append(self.parse_statement())
    return '\n{%s\n}' % ''.join(stmts).replace('\n', '\n  ')

  def parse_class(self):
    self.expect('class')
    name = 'CC' + self.expect('ID').value
    bases = {'CCObject'}
    if self.consume('['):
      while not self.consume(']'):
        bases.append('CC' + self.expect('ID').value)
    baselist = ', '.join('public virtual ' + b for b in bases)
    self.forward_decls += '\nclass %s;' % name
    decl = '\nclass %s: %s {\npublic:' % (name, baselist)
    self.expect('{')
    while not self.consume('}'):
      if self.consume('fn'):
        if self.at('ID'):
          methname = 'mm' + self.expect('ID').value
          virt = 'virtual '
        else:
          methname = name
          virt = ''
        argsigs = self.parse_argsigs()
        if methname != name:
          rettype = 'auto '
          if self.at('ID'):
            rettype = self.parse_type() + ' '
        else:
          rettype = ''
        decl += '\n  %s%s%s%s;' % (virt, rettype, methname, argsigs)
        body = self.parse_block()
        self.defs += '\n%s%s::%s%s%s' % (
            rettype, name, methname, argsigs, body)
      elif self.consume('var'):
        attrname = 'aa' + self.expect('ID').value
        type_ = self.parse_type()
        decl += '\n  %s %s;' % (type_, attrname)
      else:
        raise Err('class def', self.peek())
    decl += '\n};'
    self.forward_decls += '\nclass %s;' % name
    self.forward_decls += '\ntypedef P<class %s> PP%s;' % (name, name[2:])
    self.decls += decl
    self.decls += r"""
template <class... Args>
inline P<%s> vv%s(Args&&... args) {
  return new %s(std::forward<Args>(args)...);
}""" % (name, name[2:], name)

def sanitize_string(s):
  return (s
      .replace('\n', '\\n')
      .replace('\t', '\\t')
      .replace('"', '\\"')
      .replace("'", "\\'"))

## Main
# TODO: include
rdir = os.path.dirname(os.path.realpath(__file__))

def load(path, prefix):
  with open(os.path.join(prefix, path)) as f:
    data = f.read()
  parser = Parser(Source(path, data))
  parser.parse()
  return parser

def include(path):
  """returns a list of unique processed parsers (let's call it parsers)
  such that if parsers[i] depends on parsers[j], j < i."""
  parsers = [load(path, '.')]
  table = {path: parsers[0]}
  todo = set(parsers[0].includes)|{'prelude.xc'}
  while todo:
    item = todo.pop()
    if item not in table:
      parsers.append(load(item, os.path.join(rdir, 'lib')))
      todo.update(parsers[-1].includes)
      table[item] = parsers[-1]
    else:
      parsers.append(table[item])
  seen = set()
  uniques = []
  for p in reversed(parsers):
    if p not in seen:
      seen.add(p)
      uniques.append(p)
  return uniques

def combine(parsers):
  with open(os.path.join(rdir, 'rt.cc')) as f:
    prelude = ''
    for line in f:
      if line == 'using namespace std;\n':
        break
      else:
        prelude += line
  strs = ''.join(
      '\nPPString kkstrlit%d(new CCString("%s"));' % (
          id_, sanitize_string(key)) for key, id_ in string_literals.items())
  fwd = ''
  decls = ''
  vardecls = ''
  defs = ''
  for p in parsers:
    fwd += p.forward_decls
    decls += p.decls
    vardecls += p.vardecls
    defs += p.defs
  return ''.join((prelude, strs, fwd, decls, vardecls, defs))

def main(path):
  print(combine(include(path)))

if __name__ == '__main__':
  main(sys.argv[1])

