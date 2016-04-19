# xc

Narrower in scope than before.

Only translate to C++11.

Relatively dumb translator that doesn't annotate types or anything.

Once I find this language to be useful, I might do work to
do more code analysis and translate to other languages.

I'll try to keep language features limited such that translating
to Java/C#/Python/Ruby can also be done in a reasonably natural
way. No promises though.

    ./test && xc oldtest.xc && ./a.out && xc oldtest2.xc && ./a.out

    python3 -m xc.test && python3 -m xc.main test.xc > a.cc && \
        g++ --std=c++11 -Wall -Werror -Wpedantic a.cc && ./a.out

## Setup

Dependencies:
  * Python3 (Python2 is probably ok to, but then 'bin/xc' should be modified)
  * g++ (probably clang is ok too if 'g++' is aliased to it)

Add the 'bin' directory to path.

You must pass exactly 1 filename to 'xc', and rest of the arguments are
passed to g++ as options.

Usage:

  xc test.xc -o test

Will create a 'test' executable.

All library code (i.e. stuff pulled in through 'include') should be in
'xcsrc' directory.

## Objective

Create a programming language that's pretty awesome for programming contests.

That means
  * the resulting code must run 'fast enough' as to pass even the most
    resource intense contest challenges. (i.e. be X times less performant and
    memory wasteful compared to C/C++)
  * it should be easy (and fun!) to prototype and quickly hack in.
    So, it should be less verbose than say, often what you see with Java.

Secondary objective: keep the language relatively simple.

I picked this objective because I think I should pick a domain that I'm
at least reasonably familiar with already so that I can test for myself
whether my language is serving its purpose, and be able to judge reasonably
well whether it actually is an improvement to existing solutions.

Once I've satisfied the above objective to my satisfaction, I do want to
expand to other domains, e.g. make games, make websites, mobile dev.

I'm hoping that in developing my own language and by keeping it simple,
I'll be able to transpile into other environments with minimal effort.

I'll be able to keep in mind what the assumptions are about the environments.

I think this is the language that I kinda wished Java was.

## Builtins

Primitive types
  * Bool
  * Char
  * Int
  * Float

Classes
  * Object (super of all classes)
    * operator_str  # TODO
  * String
    * \_repr\_
    * \_add\_
    * \_mod\_
    * lines
    * words
    * map
  * List(T) < Iterable(T)
    * \_repr\_
    * \_add\_
    * \_iter\_
    * push
    * pop
    * get
    * set
  * Map(K, V) < Iterable(K)
    * \_repr\_
    * \_iter\_
    * contains
    * get
    * set
  * Iterable(T)
    * \_iter\_
  * Iterator(T) < Iterable(T)
    * \_iter\_
    * \_more\_
    * \_next\_

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

Non-language core stuff

Classes
  * Reader
    * input - read a line of input
  * StdinReader: Reader
  * FileReader: Reader
    * read - read entire file.
  * Writer
    * write
    * print
  * FileWriter: Writer
  * StdoutWriter: Writer

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

  * 'nil' is kind of a pseudo-concept.
    You can test for nil with 'is nil'/'is not nil', and
    uninitialized pointer variables start out as nil.
    But all the above are special syntactic rules.
    'nil' is not a true expression.

  * Anonymous functions always capture by value.
    Capturing by reference can be useful, but the sorts of mistakes you
    can make with it I feel are worse. And in general depending on mutations
    in more places seems like a bad idea.
    And if you really must mutate a value in the surrounding scope, you
    can mutate e.g. List or Map. This is similar to workarounds in Python 2.x
    when you have nested functions and want to mutate surrounding scope.

  * 'repr' and 'str' and arithmetic operators are the only cases where
    polymorphism is handled without methods (and even so, only for primitive
    types). All other forms of polymorphisms should rely on method calls.
    This is because builtin types don't support methods in C++.
    In Java, I'll just wrap even primitive types in objects everywhere.

## TODO

  * Prioritize these TODOs.

  * Right now, the C++ compiler is responsible for catching many of the
    static errors.
    It's going to take a lot more work, since right now the transpiler
    is pretty dumb, but eventually I want to catch all compile time
    errors at transpile time.

  * Right now, new string objects are created every time a string literal is
    referenced. If it becomes an issue, might be worth allocating string
    literals in global scope and just reusing them.
    Strings must be immutable, so this seems basically safe.

  * Implement a 'super' syntax that lets you call super methods.

  * Some level of reflection e.g. Get the name of an object's type.

  * Better coverage with tests.

  * User defined iterable (for for loops)
    Think of elegant solution.
    A Java/Python-like 'iterator' class is kind of heavyweight.
    Requiring 'begin' and 'end' methods seem kind of ok, except
    it'll be weird to be able to create a non-primitive value type
    by calling 'begin' and 'end' of certain builtin objects.

  * Consider implementing some sort of aug assignment.

  * Seriously, clean up all the code debt I've been racking up...

  * Add line numbers to stack trace (i.e. line numbers of where
    functions are invoked).

  * Would be nice to print stack trace on segfault.

  * Allow 'include' directives to refer to multiple source roots as well
    as from remote git repositories.

  * Use a proper temporary file instead of "$ROOT"/a.cc

  * Consider Windows support.

  * Stop using double underscores in generated C++ source.
    double underscore names are technically reserved for C++ implementation.

  * Allow template constructors

  * Consider including 'decltype' in the language.

  * Something like Python 'with' statements.
    i.e. context manager, something that does something when entering a block
    then does another thing when exiting.
    Seems like it'd be straight forward with C++ local variables.
    But this is lower on my priorities right now.

  * Something like C++11's 'using' or typedef where types can be aliased.
    Also, aliasing templates should be supported as well, e.g.
    'using Things(T) = Map(Int, T)'
