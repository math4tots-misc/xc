class Err(Exception):
  def __init__(self, message, *tokens):
    self.tokens = list(tokens)
    self.message = message

  def add_token(self, token):
    self.tokens.append(token)

  def __str__(self):
    return self.message + ''.join(map(location_message, self.tokens))

def location_message(token):
  return '\nin file "%s" on line %d:\n%s\n%s' % (
      self.token.source.filespec,
      self.token.lineno(),
      self.token.line(),
      (self.token.colno()-1) * ' ' + '*')
