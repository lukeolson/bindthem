#!/bin/bash

if [[ "$OSTYPE" == 'darwin'* ]]; then
    mycpp='c++ -O3 -Wall -shared -std=c++11 -undefined dynamic_lookup'
fi

if [[ "$OSTYPE" == 'linux'* ]]; then
    mycpp='c++ -O3 -Wall -shared -std=c++11 -fPIC'
fi

f=$@
echo "[Building ${f%.*}_bind.cpp]"
$mycpp $(python3 -m pybind11 --includes) ${f%.*}_bind.cpp -o ${f%.*}$(python3-config --extension-suffix)
