class Type(object):
  pass

class Name(Type):
  def __init__(self, name):
    self.name = name

  def __eq__(self, other):
    return type(self) == type(other) and self.name == other.name

  def __hash__(self):
    return hash(self.name)

class Compound(Type):
  def __init__(self, name, args):
    assert isinstance(name, str), (name, type(name))
    self.name = name
    self.args = tuple(args)

  def __eq__(self, other):
    return (
        type(self) == type(other) and
        self.name == other.name and
        self.args == other.args)

  def __hash__(self):
    return hash((self.name, self.args))
