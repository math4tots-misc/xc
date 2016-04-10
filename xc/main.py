import sys

from . import lexer
from . import translator

def main(filespec, outfilespec=None):
  with open(filespec) as f:
    data = f.read()
  source = lexer.Source(filespec, data)
  result = translator.translate(source)
  if outfilespec is None:
    print(result)
  else:
    with open(outfilespec, 'w') as f:
      f.write(result)
      f.write('\n')

if __name__ == '__main__':
  main(sys.argv[1], sys.argv[2] if len(sys.argv) >= 3 else None)
