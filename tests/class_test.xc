fn main[] {
  var etc = new ExampleTemplateClass(Int)[]
  assert[etc.print[5] == 'inside ExampleTemplateBase: 5']
  var ac = new AnotherClass[]
  ac.i = 5
  assert[ac.i == 5, repr[ac.i]]
  assert[
      ac.method[] ==
      'Inside ExampleClass constructor -- and now in ExampleClass.method!']
  print['class_test pass']
}

class ExampleTemplateBase(T) {
  fn print[t T] String {
    return 'inside ExampleTemplateBase: ' + str[t]
  }
}
class ExampleTemplateClass(T): ExampleTemplateBase(T) {}

class ExampleClass {
  var i Int
  var message String

  fn[] {
    self.message = 'Inside ExampleClass constructor'
  }

  fn method[] String {
    return self.message + ' -- and now in ExampleClass.method!'
  }
}

class AnotherClass: ExampleClass {}
