import vectorfunc
import numpy as np
import time
from memory_profiler import profile

@profile
def vectorfuncprof(mb):

    nbytes = 1024 * 1024 * mb
    n = int(nbytes / 8)

    a = np.ones((n,), dtype=np.double)
    a[0] = 88

    a = vectorfunc.VectorDouble(a)

    vectorfunc.f1(a, 0)

    vectorfunc.f2(a, 0)

if __name__ == '__main__':
    prof()
