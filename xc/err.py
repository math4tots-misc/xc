class Err(Exception):
  def __init__(self, token, message):
    self.token = token
    self.message = message

  def __str__(self):
    return '%s in file "%s" on line %d:\n%s\n%s' % (
        self.message,
        self.token.source.filespec,
        self.token.lineno(),
        self.token.line(),
        (self.token.colno()-1) * ' ' + '*')
