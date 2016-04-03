
fn println(T)[t T] Void {
  print[str[t]];
  print['\n'];
}

fn foo[xs List(Int)] Void {
  println["inside foo"];
  println[xs.size[]];
  xs.add[5];
  println[xs.size[]];
  xs.add[1].add[2].add[3];
  println[xs.size[]];
  println["About to leave foo"];
}

fn blarg[a Int, b Int] Int {
  return add[a, b];
}

fn List(T)[] List(T) {
  return new List(T);
}

fn bar[] Int {
  # var xs = new List(Int)[1, 2, 3];
  # var ys: List(Int) = new List(Int).init[].add[1].add[2].add[3];
  # var m = new Map(Int, Int).put[1, 2].put[3, 4];
  # var z = 5.5;
  # var a: Float = 5.5;
  # println[ys.get[0]];
  # ys.set[0, 5];
  # println[ys.get[0]];

  println["hello world!"];
  println[blarg[4, 5]];
  foo[getlist[]];
  return 0;
}

fn main[] Int {
  bar[];
  println["Finished bar"];

  var xs = List(Int)[];
  println[xs.size[]];

  return 0;
}
