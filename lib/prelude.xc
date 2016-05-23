class Range {
  var begin Int
  var end Int
  var step Int

  fn[begin Int, end Int, step Int] {
    self.begin = begin
    self.end = end
    self.step = step
  }

  fn mmbegin[] IntegerIterator {
    return IntegerIterator[self.begin, self.step]
  }

  fn mmend[] IntegerIterator {
    return IntegerIterator[self.end, self.step]
  }
}

class IntegerIterator {
  var i Int
  var step Int
  fn[i Int, step Int] {
    self.i = i
    self.step = step
  }

  fn mmincr[] Void {
    self.i += self.step
  }

  fn mmne[ri IntegerIterator] Bool {
    return self.i != ri.i
  }

  fn mmeq[ri IntegerIterator] Bool {
    return self.i == ri.i
  }

  fn mmderef[] Int {
    return self.i
  }
}

fn range[begin Int, end Int] Range {
  return range[begin, end, 1]
}

fn range[begin Int, end Int, step Int] Range {
  return Range[begin, end, step]
}