fn main[args List(String)] {
  print["Hello world!"]
  print["Hello world!".size[]]
  print[5 + 18]
  print[true]
  sample[1234 - 7]
  print[repr["Hello world!"]]
  var m = new AnotherClass[]
  m.i = 12 * 12
  print["m.i = " + repr[m.i]]
  var a = 5
  print[a + 10]
  m.method[]

  var b = new ExampleTemplateClass(Int)[]
  b.print[5]

  print[$Int[1, 2, 3]]
  print[$List(Int)[
      $Int[1, 2, 3],
      $Int[4, 5, 6],
  ]]

  print["Starting for loop"]
  for x in $Int[1, 2, 3] {
    print[x]
  }
  print["Ending for loop"]

  for x in $String["a", "bcd", "ef"] {
    print["item: " + x]
  }

  var i = 0
  while i < 10 {
    print["On item " + str[i]]
    i = i + 3
  }

  print["Final value of i = " + str[i]]
}

fn sample(T)[t T] {
  print["Hi " + str[t]]
}

class ExampleTemplateBase(T) {
  fn print[t T] {
    print['printing inside ExampleTemplateBase: ' + str[t]]
  }
}
class ExampleTemplateClass(T): ExampleTemplateBase(T) {}

class ExampleClass {
  var i Int

  fn[] {
    print['Inside ExampleClass constructor']
  }

  fn method[] {
    print['Inside ExampleClass.method!']
  }
}

class AnotherClass: ExampleClass {}

class OtherClass {}

class MyClass(T) {
  var x Int
  var y String
  var z OtherClass

  fn[x Int] {
    self.x = x
    self.y = "hi"
    self.z = new OtherClass[]
  }

  fn say_hi[] {
    print["Hi!"]
  }
}
