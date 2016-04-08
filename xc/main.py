import sys
import os

from . import java
from . import lexer
from . import parser
from . import ast
from . import annotator

translator_map = {
  'java': java.Translator(),
}

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


def build_program(source_loader, main_filespec):
  functions = []
  loaded = dict()

  def load(filespec):
    if filespec not in loaded:
      data = source_loader.load(filespec)
      translation_unit = parser.parse(lexer.Source(filespec, data))
      for include in translation_unit.includes:
        load(filespec)
      for function in translation_unit.functions:
        functions.append(function)
      loaded[filespec] = ast.Program(translation_unit.token, functions)
    return loaded[filespec]

  return load(main_filespec)


def translate(language, source_root, main_filespec):
  if language not in translator_map:
    raise ValueError(
        'language %r is not supported (must be one of {%s})' % (
            language, ', '.join(translator_map)))
  loader = SimpleSourceLoader(source_root)
  program = build_program(loader, main_filespec)
  annotator.annotate(program)
  translator = translator_map[language]
  return translator.translate(program)


def main():
  if len(sys.argv) != 4:
    print('Usage: %s <language> <source_root> <main_filespec>' % sys.argv[0])
  else:
    print(translate(sys.argv[1], sys.argv[2], sys.argv[3]))

if __name__ == '__main__':
  main()
