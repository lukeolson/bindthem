import myheader
import numpy as np

print(myheader.__doc__)

print(myheader.myfunc.__doc__)

J = np.ones((3,), dtype=np.int32)
x = np.ones((3,), dtype=np.float64)
y = np.ones((3,), dtype=np.float64) + 0*1j
a = 5.5

i = myheader.myfunc(J, x, y, a)

print("output")
print("------")
print("i: ", i)
print("J: ", J)
print("x: ", x)
print("y: ", y)
print("a: ", a)
