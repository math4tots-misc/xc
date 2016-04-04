import os.path

from .lex import Source
from .parse import parse

class Program(object):
  def __init__(self, functions):
    self.functions = functions

class SimpleSourceLoader(object):
  def __init__(self, source_root):
    self.root = source_root

  def load(self, filespec):
    # It doesn't seem very Pythonic to manually check if a file exists
    # before trying to open it, but which exception is thrown when a file
    # is not found seems to be platform dependent.
    # Taking that into consideration, this seems like the better solution.
    if os.path.isfile(filespec):
      with open(filespec) as f:
        return f.read()
    elif os.path.isfile(os.path.join(self.root, filespec)):
      with open(os.path.join(self.root, filespec)) as f:
        return f.read()
    else:
      raise OSError('Source file not found %r' % filespec)

class ProgramBuilder(object):
  def __init__(self, source_loader):
    self.loader = source_loader
    self.functions = []
    self.loaded = set()

  def load(self, filespec):
    if filespec in self.loaded:
      return
    self.loaded.add(filespec)
    data = self.loader.load(filespec)
    translation_unit = parse(Source(filespec, data))
    for include in translation_unit.includes:
      self.load(filespec)
    for function in translation_unit.functions:
      self.functions.append(function)

  def get_program(self):
    return Program(list(self.functions))
