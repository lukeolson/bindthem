#! /usr/bin/env python3
from __future__ import print_function
import yaml

PYBINDHEADER = """\
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/complex.h>

#include "{}"

namespace py = pybind11;
"""


def find_comments(fname, ch):
    """
    Find the comments for a function.

    fname: filename
    ch: CppHeaderParser parse tree

    The function must look like
    /*
     * comments
     * comments
     */
     template<class I, ...>
     void somefunc(...){

     -or-

    /*
     * comments
     * comments
     */
     void somefunc(...){

     -or-

    with // style comments

    Then, take off the first three spaces
    """
    with open(fname, 'r') as inf:
        fdata = inf.readlines()

    comments = {}
    for f in ch.functions:
        lineno = f['line_number'] - 1  # zero based indexing

        # set starting position
        lineptr = lineno - 1
        if f['template']:
            lineptr -= 1
        start = lineptr

        # find the top of the comment block
        while fdata[lineptr].startswith('//') or\
            fdata[lineptr].startswith('/*') or\
                fdata[lineptr].startswith(' *'):
            lineptr -= 1
        lineptr += 1
        comment = fdata[lineptr:(start + 1)]
        comment = [c[3:].rstrip() for c in comment]
        comments[f['name']] = '\n'.join(comment).strip()

    return comments


def build_function(func):
    """
    Build a function from a templated function.  The function must look like
    template<class I, class T, ...>
    void func(const p[], p_size, ...)

    rules:
        - a pointer or array p is followed by int p_size
        - all arrays are templated
        - non arrays are basic types: int, double, complex, etc
        - all functions are straight up c++
    """

    indent = '    '

    # temlpate and function name

    if func['template']:
        fdef = func['template'] + '\n'
    else:
        fdef = ''

    newcall = func['returns'] + ' _' + func['name'] + '('
    fdef += newcall + '\n'

    # function parameters

    # for each parameter
    # if it's an array
    #   - replace with py::array_t
    #   - skip the next _size argument
    #   - save in a list of arrays
    # else replicate

    i = 0
    arraylist = []
    while i < len(func['parameters']):
        p = func['parameters'][i]

        # check if pointer/array
        if p['pointer'] or p['array']:
            paramtype = p['raw_type']
            const = ''
            if p['constant']:
                const = 'const '

            param = 'py::array_t<{}> &'.format(paramtype) + ' ' + p['name']
            arraylist.append((const, paramtype, p['name']))

            # skip "_size" parameter
            i += 1
            p = func['parameters'][i]
            if '_size' not in p['name']:
                raise ValueError('Expecting a _size parameter for {}'.format(p['name']))
        # if not a pointer, just copy it
        else:
            param = p['type'] + ' ' + p['name']

        i += 1

        fdef += '{:>25}'.format(param) + ',\n'    # set width to 25

    fdef = fdef.strip()[:-1]  # trim comma and newline
    fdef += '\n' + ' ' * len(newcall) + ')'
    fdef += '\n{\n'

    # make a list of python objects
    for a in arraylist:
        if 'const' in a[0]:
            unchecked = '.unchecked();\n'
        else:
            unchecked = '.mutable_unchecked();\n'

        fdef += indent
        fdef += "auto py_" + a[2] + ' = ' + a[2] + unchecked

    # make a list of pointers to the arrays
    for a in arraylist:
        if 'const' in a[0]:
            data = '.data();\n'
        else:
            data = '.mutable_data();\n'
        fdef += indent
        fdef += a[0] + a[1] + ' *_' + a[2] + ' = py_' + a[2] + data

    # get the template signature
    if len(arraylist) > 0:
        fdef += '\n'
    if func['template']:
        template = func['template']
        template = template.replace('template', '').replace('class ', '')   # template <class T> ----> <T>
    else:
        template = ''
    newcall = '    return ' + func['name'] + template + '('
    fdef += newcall + '\n'

    # function parameters
    for p in func['parameters']:
        if '_size' in p['name']:
            fdef = fdef.strip()
            fdef += ' ' + p['name'].replace('_size', '.size()')
        else:
            if p['pointer'] or p['array']:
                name = '_' + p['name']
            else:
                name = p['name']
            fdef += '{:>25}'.format(name)
        fdef += ',\n'
    fdef = fdef.strip()[:-1]
    fdef += '\n' + ' ' * len(newcall) + ');\n}'
    return fdef


def build_plugin(headerfile, ch, comments, inst, remaps):
    """
    Take a header file (headerfile) and a parse tree (ch)
    and build the pybind11 plugin

    headerfile: somefile.h

    ch: parse tree from CppHeaderParser

    comments: a dictionary of comments

    inst: files to instantiate

    remaps: list of remaps
    """
    headerfilename = headerfile.replace('.h', '')

    indent = '    '
    plugin = ''

    # plugin += '#define NC py::arg().noconvert()\n'
    # plugin += '#define YC py::arg()\n'
    plugin += 'PYBIND11_MODULE({}, m) {{\n'.format(headerfilename)
    plugin += indent + 'm.doc() = R"pbdoc(\n'
    plugin += indent + 'Pybind11 bindings for {}\n\n'.format(headerfile)
    plugin += indent + 'Methods\n'
    plugin += indent + '-------\n'
    for f in ch.functions:
        for func in inst:
            if f['name'] in func['functions']:
                plugin += indent + f['name'] + '\n'
    plugin += indent + ')pbdoc";\n\n'

    plugin += indent + 'py::options options;\n'
    plugin += indent + 'options.disable_function_signatures();\n\n'

    unbound = []
    bound = []
    for f in ch.functions:
        # for each function:
        #   - find the entry in the instantiation list
        #   - note any array parameters to the function
        #   - for each type, instantiate
        found = False
        for func in inst:
            if f['name'] in func['functions']:
                found = True
                types = func['types']

        if not found:
            # print('Could not find {}'.format(f['name']))
            unbound.append(f['name'])
            continue
        else:
            bound.append(f['name'])

        # find all parameter names and mark if array
        argnames = []
        for p in f['parameters']:

            array = False
            if p['pointer'] or p['array']:
                array = True

            # skip "_size" parameters
            if '_size' in p['name']:
                continue
            else:
                argnames.append((p['name'], array))

        ntypes = len(types)
        for i, t in enumerate(types):

            # add the function call with each template
            instname = f['name']

            # check the remaps
            for remap in remaps:
                if f['name'] in remap:
                    instname = remap[f['name']]

            if t is not None:
                # templated function
                typestr = '<' + ', '.join(t) + '>'
            else:
                # not a templated function
                typestr = ''

            plugin += indent + 'm.def("{}", &_{}{},\n'.format(instname, f['name'], typestr)

            # name the arguments
            pyargnames = []
            for p, array in argnames:
                convert = ''
                if array:
                    convert = '.noconvert()'
                pyargnames.append('py::arg("{}"){}'.format(p, convert))

            argstring = indent + ', '.join(pyargnames)
            plugin += indent + argstring

            # add the docstring to the last
            if i == ntypes - 1:
                plugin += ',\nR"pbdoc(\n{})pbdoc");\n'.format(comments[f['name']])
            else:
                plugin += ');\n'
        plugin += '\n'

    plugin += '}\n'
    # plugin += '#undef NC\n'
    # plugin += '#undef YC\n'
    return plugin, bound, unbound


def main():
    import argparse
    import CppHeaderParser

    parser = argparse.ArgumentParser(description='Wrap a C++ header with Pybind11')

    parser.add_argument("-o", "--output-file", metavar="FILE",
                        help="(default output name for header.h is header_bind.cpp)")

    parser.add_argument("input_file", metavar="FILE")

    args = parser.parse_args()

    print('[Generating {} from {}]'.format(args.input_file.replace('.h', '_bind.cpp'), args.input_file))
    ch = CppHeaderParser.CppHeader(args.input_file)
    comments = find_comments(args.input_file, ch)

    if args.input_file == 'bind_examples.h':
        data = yaml.load(open('instantiate-test.yml', 'r'))
    else:
        data = yaml.load(open('instantiate.yml', 'r'))

    inst = data['instantiate']
    if 'remaps' in data:
        remaps = data['remaps']
    else:
        remaps = []
    plugin, bound, unbound = build_plugin(args.input_file, ch, comments, inst, remaps)

    chfuncs = {f['name']: f for f in ch.functions}
    print('\t[unbound functions: {}]'.format(' '.join(unbound)))
    flist = []
    for fname in bound:
        print('\t[building {}]'.format(fname))
        fdef = build_function(chfuncs[fname])
        flist.append(fdef)

    if args.output_file is not None:
        outf = args.output_file
    else:
        outf = args.input_file.replace('.h', '_bind.cpp')

    with open(outf, 'wt') as outf:

        print('// DO NOT EDIT: this file is generated\n', file=outf)
        print(PYBINDHEADER.format(args.input_file), file=outf)

        for f in flist:
            print(f, '\n', file=outf, sep="")

        print(plugin, file=outf)


if __name__ == '__main__':
    main()
