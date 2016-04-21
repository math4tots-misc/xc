fn main[] {
  stdout.write['iter_test... ']
  {
    var i = $Int[1, 2, 3]._iter_[]
    assert[i._more_[]]
    assert[i._next_[] == 1]
    assert[i._more_[]]
    assert[i._next_[] == 2]
    assert[i._more_[]]
    assert[i._next_[] == 3]
    assert[not i._more_[]]
  }
  {
    var m = new Map(String, Int)[]
    assert[m.size[] == 0]
    m.set['hi', 55]
    var i = m._iter_[]
    assert[i._more_[]]
    assert[i._next_[] == 'hi']
    assert[not i._more_[]]
  }
  {
    var i = new Map(Int, String)[]
        .set[44, 'a']
        .set[5, 'c']
        .set[7123, 'bbb']
        .set[7123, 'k']
        ._iter_[]
    var keys = $Int[]
    while i._more_[] {
      keys.push[i._next_[]]
    }
    keys.sort[]
    assert[keys == $Int[5, 44, 7123], repr[keys]]
  }
  {
    var set = new Set(String)[]
        .add['a']
        .add['c']
        .add['d']
        .add['b']
    var items = new List(String)[]
    for k in set {
      items.push[k]
    }
    items.sort[]
    assert[items == $String['a', 'b', 'c', 'd'], repr[items]]
  }
  {
    var list = $Int[5, 6, 7, 8]
    var result = list._iter_[].map[fn[i Int] Int { return 7 * i }]
    assert[result._more_[]]
    assert[result._next_[] == 35]
    assert[result._more_[]]
    assert[result._next_[] == 42]
    assert[result._more_[]]
    assert[result._next_[] == 49]
    assert[result._more_[]]
    assert[result._next_[] == 56]
    assert[not result._more_[]]
  }
  {
    var list = $Int[5, 6, 7, 8]
    var result = list._iter_[].map[fn[i Int] Int { return 7 * i }]
    assert[result.list[] == $Int[35, 42, 49, 56]]
  }
  print['pass']
}
