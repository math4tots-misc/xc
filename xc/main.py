import os
import sys

from . import loader
from . import lexer
from . import translator

DEFAULT_LOADER_PATH = os.path.expanduser('~/dev/git/xc/src')

def main(filespec, outfilespec=None):
  with open(filespec) as f:
    data = f.read()
  source = lexer.Source(filespec, data)
  tr = translator.Translator(loader.Loader(DEFAULT_LOADER_PATH), source)
  tr.additional_includes.extend(['core/prelude.xc'])
  result = tr.translate()
  if outfilespec is None:
    print(result)
  else:
    with open(outfilespec, 'w') as f:
      f.write(result)
      f.write('\n')

if __name__ == '__main__':
  main(sys.argv[1], sys.argv[2] if len(sys.argv) >= 3 else None)
