
fn blarg[a Int, b Int] Int {
  return add[a, b];
}

fn main[] Int {
  # var xs = new List(Int)[1, 2, 3];
  # var ys: List(Int) = new List(Int).add[1].add[2].add[3];
  # var m = new Map(Int, Int).put[1, 2].put[3, 4];
  # var z = 5.5;
  # var a: Float = 5.5;
  # print[ys.get[0]];
  # ys.set[0, 5];
  # print[ys.get[0]];

  print["hello world!"];
  print[blarg[4, 5]];
  return 0;
}
