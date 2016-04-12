import os

from . import err

# TODO: In the future, include from e.g. repositories on github.
class Loader(object):

  def __init__(self, root):
    self.root = root

  def load(self, uri):
    path = os.path.join(self.root, uri)
    if os.path.exists(path):
      with open(path) as f:
        return f.read()
    else:
      raise err.Err('Could not find %r (%r)' % (uri, path))
