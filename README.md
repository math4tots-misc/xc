# xc

Narrow scope programming language for programming contests.

You can include xc code from lib/

Otherwise, you can just run a program with ./xc <filename>

If you need to generate the C++ code (requires C++14), you can run

  python process.py <filename> > a.cc

## testing

On windows test with:

  windows\\xc.bat test.xc

On OS X test with:

  osx/xc test.xc
