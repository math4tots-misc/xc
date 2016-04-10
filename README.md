# xc

Narrower in scope than before.

Only translate to C++11.

Once I find this language to be useful, I might do work to
translate to other languages.

I'll try to keep language features limited such that translating
to Java/C#/Python/Ruby can also be done in a reasonably natural
way. No promises though.

python3 -m xc.main test.xc > test.cc && g++ --std=c++11 -Wall -Werror -Wpedantic test.cc && ./a.out
