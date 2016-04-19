class Set(T) {
  var data Map(T, Bool)

  fn[] {
    self.data = new Map(T, Bool)[]
  }

  fn[items List(T)] {
    self.data = new Map(T, Bool)[]
    for item in items {
      self.data.set[item, true]
    }
  }

  fn list[] List(T) {
    var ks = new List(T)[]
    for k in self.data {
      ks.push[k]
    }
    return ks
  }

  fn add[t T] Set(T) {
    self.data.set[t, true]
    return self
  }

  # Returns 'true' if the item was found and removed from the set.
  # Otherwise, 't' was already not in this set, and returns false.
  fn rm[t T] Bool {
    return self.data.rm[t]
  }

  # 'true' iff this set contains the element 't'
  fn has[t T] Bool {
    return self.data.has[t]
  }

  fn size[] Int {
    return self.data.size[]
  }

  fn _iter_[] Iterator(T) {
    return self.data._iter_[]
  }
}
