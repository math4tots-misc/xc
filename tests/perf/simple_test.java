/*
Kyumins-MacBook-Pro:xc math4tots$ javac simple_test.java && time java Test
100000020000000

real	0m2.719s
user	0m12.256s
sys	0m0.390s
*/
import java.util.ArrayList;

public class simple_test {
  public static void main(String[] args) {
    ArrayList<Long> xs = new ArrayList<Long>();
    for (long i = 0; i < 10000000; i++) {
      xs.add(2 * i + 3);
    }

    long total = 0;
    for (long i: xs) {
      total += i;
    }

    System.out.println(total);
  }
}
