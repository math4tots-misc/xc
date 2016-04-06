import sys

from .program import ProgramBuilder, SimpleSourceLoader
from . import cc

translator_map = {
  'cc': cc.Translator(),
}

def translate(language, source_root, main_filespec):
  if language not in translator_map:
    raise ValueError(
        'language %r is not supported (must be one of {%s})' % (
            language, ', '.join(translator_map)))
  loader = SimpleSourceLoader(source_root)
  builder = ProgramBuilder(loader)
  builder.load(main_filespec)
  program = builder.get_program()
  translator = translator_map[language]
  return translator.translate(program)

def main():
  if len(sys.argv) != 4:
    print('Usage: %s <language> <source_root> <main_filespec>' % sys.argv[0])
  else:
    print(translate(sys.argv[1], sys.argv[2], sys.argv[3]))

if __name__ == '__main__':
  main()
