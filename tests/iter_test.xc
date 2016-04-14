fn main[] {
  {
    var i = $Int[1, 2, 3]._iter_[]
    assert[i.more[]]
    assert[i.next[] == 1]
    assert[i.more[]]
    assert[i.next[] == 2]
    assert[i.more[]]
    assert[i.next[] == 3]
    assert[not i.more[]]
  }
  {
    var m = new Map(String, Int)[]
    assert[m.size[] == 0]
    m.set['hi', 55]
    var i = m._iter_[]
    assert[i.more[]]
    assert[i.next[] == 'hi']
    assert[not i.more[]]
  }
  {
    var i = new Map(Int, String)[]
        .set[44, 'a']
        .set[5, 'c']
        .set[7123, 'bbb']
        .set[7123, 'k']
        ._iter_[]
    var keys = $Int[]
    while i.more[] {
      keys.push[i.next[]]
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
  print['iter_test pass']
}
