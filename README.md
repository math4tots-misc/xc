# xc

python3 -m xc cc src/ main.xc > a.cc && g++ -Wall -Werror -Wpedantic --std=c++11 a.cc && ./a.out

Thoughts:

  In order to translate to dynamic languages, and at the same time, not do the
  work of expanding generics, I cannot rely on function overloading.

  As such, in order to have proper polymorphic behavior, I need to call methods

  However for languages like C++ and Java, I can't call custom methods on
  primitive types.

  So C++ and Java, use overloading to implement polymorphic functions like
  'print', 'str', or 'add'. In dynamic languages like Python, use method calls
  or other native means of getting the same effect.

  But use of overloading must be narrow and can't be a first class feature
  in the xc language (in order to both keep my implementation simple and also
  be easily portable to many popular languages).

  Idea is to hide this sort of polymorphism behind 'special' functions.

  For special builtin types, these special functions can dispatch them
  appropriately (e.g. by overloading or making a method call).

  The reason for builtin value types is performance. So I think overloading
  should be preferred over creating wrapper types over primitives.

  Also creating wrapper types around primitives might complicate matters.
  e.g. '+=' operator.

Thoughts2:

  Need a few things in target language to make translation easy:

    1. GC or ref counting, or something that makes ref counting easy.
      e.g. in C++, whenever a variable goes out of scope, or
      certain interesting values change, I can react to it easily.

    2. Dynamic typing, or if statically typed, operator overloading.
      To make 'special functions' easier to implement.
      If dynamically typed, even primitives are dynamic.
      Not really important for core features.

    3. Classes. Otherwise, you'd have to implement the class mechanism
      yourself.

    4. Some basic utility objects. E.g. lists, hashmaps, etc.
      I'm thinking of C right now. Basically every other language I can
      think of has that sort of thing covered.

Of course, it is still difficult to map 'xc' naturally into e.g. Haskell.
You could probably do something that naturally maps to monad
style programming in Haskell.

Implementing a 'satisfying' prime sieve in Haskell is nontrivial.

If 'xc' could map naturally to Haskell, I feel like either
  1. prime sieve would be nontrivial in 'xc', or
  2. prime sieve would need to be part of some library implemented externally.

Both of which suck. So I'm ok with poor support for Haskell backend.

TODO:
  * Add a feature for doing generic programming
  * Related: List, Map, and other container types
  * classes
  * method calls
  * borrow types
  * type analysis/annotation
  * Check consistency (i.e. types are correct, used functions exist, etc).
  * Better testing.
  * Better error messages.

Builtin special type
  * Void

Builtin value types
  * Int
  * Float
  * Char
  * Byte
  * Bool

Builtin class types
  * String
  * List(?)
  * Table(?, ?)

