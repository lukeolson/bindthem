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
