# xc

Narrower in scope than before.

Only translate to C++11.

Relatively dumb translator that doesn't annotate types or anything.

Once I find this language to be useful, I might do work to
do more code analysis and translate to other languages.

I'll try to keep language features limited such that translating
to Java/C#/Python/Ruby can also be done in a reasonably natural
way. No promises though.

python3 -m xc.main test.xc > test.cc && g++ --std=c++11 -Wall -Werror -Wpedantic test.cc && ./a.out


## Builtins

Primitive types (Can't subclass these, C++ enforces this)
  * Bool
  * Char
  * Int
  * Float

Classes (Subclassing these is illegal, but not yet enforced)
  * String
    * operator_repr
    * operator_add
  * List(T)
    * operator_repr
    * operator_add
  * Map(K, V)

Functions
  * repr(T)
    * repr(Bool)
    * repr(Char)
    * repr(Int)
    * repr(Float)
    * default calls 'operator_repr' method.
  * str(T)
    * default requires repr(T)
      * TDOO: change this to call 'operator_str' instead.
        and have 'Object' class implement a default 'operator_str'
        that calls 'operator_repr'.
        Specialize for builtin types.
  * print(T)
    * default requires str(T)

## NOTES

  * I think template specialization is kind of awk.
    Right now certain kinds of template specialization is not blocked,
    e.g. if you try to define a template function with zero type args,
    and the specialization types are deducible from function argument types.
    However, in general I want to only use template specialization for
    compatibility with builtin types.
    Otherwise, prefer calling methods.

  * Without const/final, member access control, or anal super constructors,
    I don't really see the use for special syntax for constructors.
    On the other hand, at least for me, it seems to be kind of annoying to
    implement a nice syntax that allows initializing as soon as allocating.
    In order to have Python-like syntax, I need to know which names are
    classes and which are functions.
    Seems like it's just simpler to have a some sort of constructor syntax.
    However, note that if you do not have a default argument constructor,
    it's not subclassable, since constructor initializer lists are not
    supported.

## TODO

  * Right now, new string objects are created every time a string literal is
    referenced. If it becomes an issue, might be worth allocating string
    literals in global scope and just reusing them.
    Strings must be immutable, so this seems basically safe.

  * Implement a 'super' syntax that lets you call super methods.
