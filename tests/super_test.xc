fn main[] {
  stdout.write['super_test... ']
  var obj = new Derived[]
  assert[obj.method[] == 'derived_method', 'method: ' + obj.method[]]
  assert[obj.method2[] == 'base_method', 'method2: ' + obj.method2[]]
  assert[obj.method3[] == 'derived_method', 'method3: ' + obj.method3[]]

  var b Base = obj
  assert[b.method[] == 'derived_method']
  var c = b as Derived
  assert[c.method[] == 'derived_method']

  print['pass']
}

class Base {

  fn method[] String {
    return 'base_method'
  }
}

class Derived < Base {
  fn method[] String {
    return 'derived_method'
  }

  fn method2[] String {
    return super.method[]
  }

  fn method3[] String {
    return self.method[]
  }
}
