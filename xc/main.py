import os
import sys

from . import loader
from . import lexer
from . import translator

PYTHON_SRC_ROOT = os.path.realpath(os.path.join(__file__, os.pardir))
ROOT = os.path.realpath(os.path.join(PYTHON_SRC_ROOT, os.pardir))
XC_SRC_ROOT = os.path.join(ROOT, 'xcsrc')

def main(filespec, outfilespec, trace):
  with open(filespec) as f:
    data = f.read()
  source = lexer.Source(filespec, data)
  result = translator.translate(
      source=source,
      loader=loader.Loader(XC_SRC_ROOT),
      trace=trace,
      additional_includes=['core/prelude.xc'])
  if outfilespec is None:
    print(result)
  else:
    with open(outfilespec, 'w') as f:
      f.write(result)
      f.write('\n')

if __name__ == '__main__':
  # The usage here isn't super pleasant -- use bin/xc for everyday usage.
  # <trace> should be an integer, 0 for no trace, any other int to turn
  # on trace.
  if len(sys.argv) != 4:
    print('Usage: python3 -m xc.main <infile> <outfile> <trace>')
    exit(1)
  main(sys.argv[1], sys.argv[2], int(sys.argv[3]))
