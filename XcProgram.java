public class XcProgram {
  
  public static void main(java.lang.String[] args) {
    main();
  }
  
  public static void println(String s) {
    System.out.println(s.data);
  }
  
  public static class String {
    public java.lang.String data;
  
    public String(java.lang.String data) {
      this.data = data;
    }
  }
  
  ///////////////////
  
  public static void main()
  {
    println(new String("Hi!"));
    String x = new String("Hi again!");
    println(x);
  }
}
