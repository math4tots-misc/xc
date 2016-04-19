from . import templates
from . import lexer
from . import err


def translate(source, loader=None, trace=False, additional_includes=None):
  return Translator(
      source=source,
      loader=loader,
      trace=trace,
      included=set(),
      additional_includes=additional_includes or []).translate()

class Translator(object):

  def __init__(self, source, loader, included, trace, additional_includes):
    self.loader = loader
    self.source = source
    self.tokens = lexer.lex(source)
    self.i = 0
    self.additional_includes = additional_includes
    self.included = included
    self.trace = trace

    # TODO: Use context managers with these, instead of
    # manually assigning to them everywhere.
    self.class_name_prefix = ''
    self.function_name_prefix = ''
    self.base_class_name = ''

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

  def prefix(self):
    if self.trace:
      return templates.PREFIX_1 + templates.PREFIX_2B + templates.PREFIX_3
    else:
      return templates.PREFIX_1 + templates.PREFIX_2A + templates.PREFIX_3

  def translate(self):
    return '\n//////////////'.join((
        self.prefix(), self.translate_without_prefix()))

  def translate_without_prefix(self):
    return '\n'.join(self.parse_program())

  def parse_program(self):
    incs = a = b = c = d = ''
    for inc in self.additional_includes:
      incs += self.process_include(inc)
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
      elif self.at('using'):
        a += self.parse_using()
      elif self.at('include'):
        incs += self.parse_include()
      elif self.consume('STR') or self.consume('CHR'):
        # TODO: Consider inserting these comments into generated source.
        pass  # string or char style comments
      else:
        raise err.Err('Expected function or class', self.peek())
    a = incs + a
    # a = includes and forward type declarations
    # b = type declarations
    # c = function declarations and global variable definitions
    # d = function and method definitions
    return a, b, c, d

  def parse_include(self):
    self.expect('include')
    uri = eval((self.consume('STR') or self.consume('CHR')).value)
    return self.process_include(uri)

  def process_include(self, uri):
    if uri in self.included:
      return ''
    self.included.add(uri)
    data = self.loader.load(uri)
    source = lexer.Source(uri, data)
    return '\n// uri = %s%s' % (uri, Translator(
        source=source,
        loader=self.loader,
        included=self.included,
        trace=self.trace,
        additional_includes=[])
        .translate_without_prefix())

  def parse_global_declaration(self):
    return self.parse_declaration()

  def parse_class(self):
    self.expect('class')
    name = self.expect('ID').value
    self.class_name_prefix = name + '.'
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
    if self.consume('<'):
      base = self.parse_type() + '::Pointee'
    else:
      base = 'xcs_Object'
    self.base_class_name = base
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
    self.class_name_prefix = ''
    self.base_class_name = ''
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
    self.function_name_prefix = name = self.expect('ID').value
    # TODO: Think about whether I want to allow template methods.
    argsig = self.parse_arg_sig()
    if not self.at('{'):
      ret = self.parse_type()
    else:
      ret = 'xct_Void'
    body = self.parse_block()

    if ret == 'xct_Void':
      body = patch_block_with_nil_return(body)

    decl = '\nvirtual %s xcm%s(%s);' % (ret, name, argsig)
    if typeargs is None:
      defn = '\n%s xcs_%s::xcm%s(%s)%s' % (
          ret, class_name, name, argsig, body)
    else:
      # TODO: Don't do this hack. Figure out a cleaner solution.
      # TODO: Stop duplicating this evil hack.
      typeargnames = ', '.join(
          name for name in typeargs.replace(',', ' ').split()
          if name != 'class')
      defn = '\ntemplate <%s>\n%s xcs_%s<%s>::xcm%s(%s)%s' % (
          typeargs, ret, class_name, typeargnames, name, argsig, body)
    self.function_name_prefix = ''
    return decl, defn

  def parse_rest_of_constructor(self, class_name, typeargs, token):
    self.function_name_prefix = '<constructor>'
    argsig = self.parse_arg_sig()
    body = self.parse_block()

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
    self.function_name_prefix = ''
    return decl, defn

  def parse_function(self):
    token = self.expect('fn')
    raw_name = self.expect('ID').value
    self.function_name_prefix = raw_name
    name = 'xcv_' + raw_name
    if self.at('('):
      typeargs = self.parse_typearg_sig()
    else:
      typeargs = None
    args = self.parse_arg_sig()
    type_ = 'xct_Void' if self.at('{') else self.parse_type()
    body = self.parse_block()

    if type_ == 'xct_Void':
      body = patch_block_with_nil_return(body)

    if typeargs is None:
      sig = '%s %s(%s)' % (type_, name, args)
    else:
      sig = 'template <%s>\n%s %s(%s)' % (typeargs, type_, name, args)
    self.function_name_prefix = ''
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
      cond = self.parse_top_level_expression()
      body = self.parse_block()
      return '\nwhile (%s)%s' % (cond, body)
    elif self.consume('for'):
      name = self.expect('ID').value
      self.expect('in')
      container = self.parse_top_level_expression()
      body = self.parse_block()
      return '\nfor (auto xcv_%s: %s.iterptr())%s' % (name, container, body)
    elif self.consume('if'):
      cond = self.parse_top_level_expression()
      body = self.parse_block()
      other = ''
      if self.consume('else'):
        if self.at('if'):
          other = '\nelse' + self.parse_statement()
        else:
          other = '\nelse' + self.parse_block()
      return 'if (%s)%s%s' % (cond, body, other)
    elif self.consume('return'):
      return '\nreturn %s;' % self.parse_top_level_expression()
    elif self.at('{'):
      return self.parse_block()
    elif self.at('var'):
      return self.parse_declaration()
    elif self.at('using'):
      return self.parse_using()
    else:
      return '\n%s;' % self.parse_top_level_expression()

  def parse_using(self):
    self.expect('using')
    name = self.expect('ID').value
    args = None
    if self.at('('):
      args = self.parse_typearg_sig()
    self.expect('=')
    type_ = self.parse_type()
    if args is None:
      return '\nusing xct_%s = %s;' % (name, type_)
    else:
      return '\ntemplate <%s> using xct_%s = %s;' % (args, name, type_)


  def parse_declaration(self):
    self.expect('var')
    name = self.expect('ID').value
    if not self.at('='):
      type_ = self.parse_type()
    else:
      type_ = 'auto'
    if self.consume('='):
      value = ' = ' + self.parse_top_level_expression()
    else:
      value = ''
    return '\n%s xcv_%s%s;' % (type_, name, value)

  def parse_expression(self):
    return self.parse_or_expression()

  def parse_or_expression(self):
    e = self.parse_and_expression()
    while True:
      if self.consume('or'):
        r = self.parse_and_expression()
        e = '%s || %s' % (e, r)
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
      elif self.consume('is'):
        if self.consume('not'):
          if self.consume('nil'):
            e = '%s.is_not_nil()' % e
          else:
            r = self.parse_inequality_expression()
            e = '%s.is_not(%s)' % (e, r)
        elif self.consume('nil'):
          e = '%s.is_nil()' % e
        else:
          r = self.parse_inequality_expression()
          e = '%s.is(%s)' % (e, r)
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
    if self.consume('-'):
      return '-' + self.parse_postfix_expression()
    elif self.consume('not'):
      return '!' + self.parse_postfix_expression()
    else:
      return self.parse_postfix_expression()

  def parse_postfix_expression(self):
    e = self.parse_primary_expression()
    while self.at('.'):
      if self.consume('.'):
        name = self.expect('ID').value
        if self.at('(') or self.at('['):
          e = '%s->xcm%s%s' % (e, name, self.parse_fullarg())
        elif self.consume('+='):
          v = self.parse_expression()
          e = '%s->xca_%s += %s' % (e, name, v)
        elif self.consume('-='):
          v = self.parse_expression()
          e = '%s->xca_%s -= %s' % (e, name, v)
        elif self.consume('*='):
          v = self.parse_expression()
          e = '%s->xca_%s *= %s' % (e, name, v)
        elif self.consume('/='):
          v = self.parse_expression()
          e = '%s->xca_%s /= %s' % (e, name, v)
        elif self.consume('%='):
          v = self.parse_expression()
          e = '%s->xca_%s %%= %s' % (e, name, v)
        elif self.consume('='):
          if self.consume('nil'):
            e = '%s->xca_%s.set_nil()' % (e, name)
          else:
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
      return '(%s)' % e
    elif self.at('ID'):
      name = self.expect('ID').value
      if self.at('(') or self.at('['):
        return 'xcv_%s%s' % (name, self.parse_fullarg())
      elif self.consume('+='):
        return 'xcv_%s += %s' % (name, self.parse_expression())
      elif self.consume('-='):
        return 'xcv_%s -= %s' % (name, self.parse_expression())
      elif self.consume('*='):
        return 'xcv_%s *= %s' % (name, self.parse_expression())
      elif self.consume('/='):
        return 'xcv_%s /= %s' % (name, self.parse_expression())
      elif self.consume('%='):
        return 'xcv_%s %%= %s' % (name, self.parse_expression())
      elif self.consume('='):
        if self.consume('nil'):
          return 'xcv_%s.set_nil()' % name
        else:
          return 'xcv_%s = %s' % (name, self.parse_expression())
      else:
        return 'xcv_' + name
    elif self.consume('new'):
      type_ = self.parse_type()
      args = self.parse_args()
      return '%s(new typename %s::Pointee(%s))' % (type_, type_, args)
    elif self.consume('fn'):
      old_prefix = self.function_name_prefix
      self.function_name_prefix = '<anonymous>'
      args = self.parse_arg_sig()
      if self.at('{'):
        ret = 'xct_Void'
      else:
        ret = self.parse_type()
      body = self.parse_block()
      if ret == 'xct_Void':
        body = patch_block_with_nil_return(body)
      self.function_name_prefix = old_prefix
      return '[=](%s)->%s%s' % (args, ret, body)
    elif self.consume('self'):
      if self.class_name_prefix == '':
        raise err.Err('Used "self" outside of class definition', token)
      return 'this'
    elif self.consume('super'):
      if self.base_class_name == '':
        raise err.Err('Used "super" outside of class definition', token)
      self.expect('.')
      method_name = self.expect('ID').value
      return '%s::xcm%s%s' % (
          self.base_class_name, method_name, self.parse_fullarg())
    elif self.consume('true'):
      return 'true'
    elif self.consume('false'):
      return 'false'
    elif self.at('INT'):
      return self.expect('INT').value + 'LL'
    elif self.at('FLT'):
      return self.expect('FLT').value
    elif self.at('CHR'):
      return "'%s'" % sanitize_string(eval(self.expect('CHR').value[1:]))
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
    typeargs = None
    if self.at('('):
      typeargs = self.parse_typearg_sig()
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

  def parse_fullarg(self):
    targs = None
    if self.at('('):
      targs = self.parse_typeargs()
    args = self.parse_args()
    if targs is None:
      return '(%s)' % args
    else:
      return '<%s>(%s)' % (targs, args)

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

  def parse_top_level_expression(self):
    token = self.peek()
    filespec = token.source.filespec
    lineno = token.lineno()
    return self.patch_expression_with_frame(
        self.parse_expression(), filespec, lineno)

  def patch_expression_with_frame(self, expr, filespec, lineno):
    return r'WITH_FRAME("File \"%s\", line ", %d, " in %s", (%s))' % (
        filespec, lineno,
        self.class_name_prefix + self.function_name_prefix, expr)

def sanitize_string(s):
  return (s
      .replace('\n', '\\n')
      .replace('\t', '\\t')
      .replace('"', '\\"')
      .replace("'", "\\'"))

def patch_block_with_nil_return(block):
  """Depends on block always ending with close brace"""
  return "%s\n  RETURN_VOID;%s" % (block[:-1], block[-1:])

