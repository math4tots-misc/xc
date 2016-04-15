# TODO: Consider supporting ranges going in the negative direction.
class Range {
  var start Int
  var end Int
  var step Int

  fn[start Int, end Int, step Int] {
    self.start = start
    self.end = end
    self.step = step
  }

  fn _iter_[] RangeIterator {
    return new RangeIterator[self]
  }
}

class RangeIterator {
  var range Range
  var i Int

  fn[range Range] {
    self.range = range
    self.i = range.start
  }

  fn _more_[] Bool {
    return self.i < self.range.end
  }

  fn _next_[] Int {
    self.i += 1
    return self.i - 1
  }

  # TODO: Figure out how I need to extend the type system to make
  # 'map' work.
  #fn map(F)[f F] List(%F[Int]) {
  #  var xs = new List(Int)[]
  #  for i in self {
  #    xs.push[]
  #  }
  #}
}

fn range[start Int, end Int] Range {
  return new Range[start, end, 1]
}

fn range[start Int, end Int, step Int] Range {
  return new Range[start, end, step]
}
