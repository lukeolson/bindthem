# BindThem

A generating PyBind11 bindings for C++ kernels automatically.

##

The .cpp files in this directory are generated using the script
`generate_bindings.py`.  Pybind11 is used to for the Python bindings.

Run

    bindthem myheader.h

to generate `myheader_bind.cpp`.  See `bindthem.py` for more details.

## C++ kernels

The C++ kernels are limited to basic types and fixed sized arrays.  For example, suppose `myheader.h` contains

```c++
// My Function
// 
// Parameters
// ----------
// J : array
//     some array 
// x : array (in-place)
//     some array 
// y : array (in-place)
//     some array 
// a : float
//     some parameter
//
// Returns
// -------
// i : int
//     return value
//
template <class I, class T, class F>
int myfunc(const I J[], const int J_size,
                 T x[], const int x_size,
                 F y[], const int y_size,
           double a)
{
    F myval (7.5, 8.25);
    x[0] = (T) a;
    y[0] = myval;
    return J[0];
}
```

Then `myheader_bind.cpp` will be bind the method `myheader.myfunc`.  No type conversion is allowed (in this bind); the types are explicitly defined in `instantiate.yml` as

```yaml
- types:
    - [int, double, "std::complex<double>"]
    - [int, float, std::complex<float>]
  functions:
    - myfunc
```

Here, `I`, `T`, and `F` would be `int`, `double`, and `complex<double` along with `int`, `double`, and `double`.

There are a few rules to the kernels and the format is quite limited:

1. The format is comments + template + function declaration, no newlines.

2. The document string is formatted from the comments directly preceding the template or function call.

3. A pointer or array `p` must be followed by `int p_size`.  This allows for straightforward, copy-free calls without bound checks and fancier containers.

## How it works

The binding of header `myheader.h` follows some simple steps:

1. `CppHeaderParser` parses the header file to deduce structure.

2. For each function, `bindthem.find_comments` searches for a comment/docstring.

3. The instantiation file is read `instantiate.yml`

4. The plugin is generated for the header file in `bindthem.build_plugin`, lookin roughly like

```c++
PYBIND11_MODULE(myheader, m) {
    m.doc() = R"pbdoc(
    Pybind11 bindings for myheader.h

    Methods
    -------
    myfunc
    )pbdoc";

    py::options options;
    options.disable_function_signatures();

    m.def("myfunc", &_myfunc<int, double, std::complex<double>>,
        py::arg("J").noconvert(), py::arg("x").noconvert(), py::arg("y").noconvert(), py::arg("a"));
    m.def("myfunc", &_myfunc<int, float, std::complex<float>>,
        py::arg("J").noconvert(), py::arg("x").noconvert(), py::arg("y").noconvert(), py::arg("a"),
R"pbdoc(
My Function
...
}
```

Notice that each instantiation is generated for the plugin.

5. For each function, `myfunc`, a binding function called `_myfunc` is generatedwhich build pointers to the numpy arrays.  In this case

```c++
template <class I, class T, class F>
int _myfunc(
       py::array_t<I> & J,
       py::array_t<T> & x,
       py::array_t<F> & y,
                 double a
            )
{
    auto py_J = J.unchecked();
    auto py_x = x.mutable_unchecked();
    auto py_y = y.mutable_unchecked();
    const I *_J = py_J.data();
    T *_x = py_x.mutable_data();
    F *_y = py_y.mutable_data();

    return myfunc <I, T, F>(
                       _J, J.size(),
                       _x, x.size(),
                       _y, y.size(),
                        a
                            );
}
```

For function `_myfunc`, the template and function are replicated, and parameters are replicated if not array parameters.  If the parameter is an array, replace with `pybind11::array_t` and *skip* the `_size` parameters.

Then, for each array, grab the numpy object with `.unchecked()` or `.mutable_unchecked()` and set the pointer to the data `with `.data()` or `.mutable_data()`.  This should be copy-free.  These pointers are passed to the C++ kernel.
