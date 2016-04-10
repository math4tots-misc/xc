public class XcProgram {
  
  public static void main(java.lang.String[] args) {
    main();
  }
  
  public static void println(Stringable s) {
    System.out.println(s.to_String().data);
  }
  
  public static interface Stringable {
    public String to_String();
  }
  
  public static class Int implements Stringable {
    public int data;
  
    public Int(int data) {
      this.data = data;
    }
  
    public String to_String() {
      return new String(java.lang.Integer.toString(data));
    }
  }
  
  public static class String implements Stringable {
    public java.lang.String data;
  
    public String(java.lang.String data) {
      this.data = data;
    }
  
    public String to_String() {
      return this;
    }
  }
  
  ///////////////////
  
  public static void main()
  {
    println(new String("Hi!"));
    String x = new String("Hi again!");
    println(x);
    Int a = new Int(5);
    println(a);
  }
}
