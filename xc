#!/bin/sh
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Split args
# all the ones before '--' go to g++, and the rest go to ./a.out
SPLIT="${#@}"
for ((i=1; i < ${#@}; ++i)); do
  if [ "--" = "${!i}" ]; then
    SPLIT="$i"
    break
  fi
done

if [ "$SPLIT" -lt 2 ]; then
  SPLIT=2
fi

python "$DIR"/process.py "$1" > "$DIR"/a.cc && \
g++ -std=c++14 \
    -Wall -Werror -Wpedantic \
    -Wno-parentheses-equality \
    "$DIR"/a.cc -o "$DIR"/a.out \
    "${@:2:$((SPLIT - 2))}" && \
"$DIR"/a.out "${@:$((SPLIT + 1))}" <&0
