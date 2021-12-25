#include <algorithm>
#include <vector>

/*
 *  Perform one iteration of Jacobi relaxation on the linear
 *  system Ax = b, where A is stored in CSR format and x and b
 *  are column vectors.  Damping is controlled by the omega
 *  parameter.
 *
 *  Refer to gauss_seidel for additional information regarding
 *  row_start, row_stop, and row_step.
 *
 *  Parameters
 *      Ap[]       - CSR row pointer
 *      Aj[]       - CSR index array
 *      Ax[]       - CSR data array
 *      x[]        - approximate solution
 *      b[]        - right hand side
 *      temp[]     - temporary vector the same size as x
 *      row_start  - beginning of the sweep
 *      row_stop   - end of the sweep (i.e. one past the last unknown)
 *      row_step   - stride used during the sweep (may be negative)
 *      omega      - damping parameter
 *
 *  Returns:
 *      Nothing, x will be modified in place
 *
 */
template<class I, class T>
void jacobi(const I Ap[], const int Ap_size,
            const I Aj[], const int Aj_size,
            const T Ax[], const int Ax_size,
                  T  x[], const int  x_size,
            const T  b[], const int  b_size,
                  T temp[], const int temp_size,
            const I row_start,
            const I row_stop,
            const I row_step,
            const T omega[], const int omega_size)
{
    T one = 1.0;
    T omega2 = omega[0];

    for(I i = row_start; i != row_stop; i += row_step) {
        temp[i] = x[i];
    }

    for(I i = row_start; i != row_stop; i += row_step) {
        I start = Ap[i];
        I end   = Ap[i+1];
        T rsum = 0;
        T diag = 0;

        for(I jj = start; jj < end; jj++){
            I j = Aj[jj];
            if (i == j)
                diag  = Ax[jj];
            else
                rsum += Ax[jj]*temp[j];
        }

        if (diag != (T) 0.0){
            x[i] = (one - omega2) * temp[i] + omega2 * ((b[i] - rsum)/diag);
        }
    }
}

/*
 *  Multiple RHS Jacobi
 */
template<class I, class T>
void jacobi_m(const I Ap[], const int Ap_size,
            const I Aj[], const int Aj_size,
            const T Ax[], const int Ax_size,
                  T  x[], const int  x_size0, const int x_size1,
            const T  b[], const int  b_size0, const int b_size1,
                  T temp[], const int temp_size0, const int temp_size1,
            const I row_start,
            const I row_stop,
            const I row_step,
            const T omega[], const int omega_size)
{
    T one = 1.0;
    T omega2 = omega[0];
    I s = x_size1;
    std::vector<T> rsum(s);

    // copy each vector
    for(I i = row_start; i != row_stop; i += row_step) {
        for(I si = 0; si < s; si++) {
            temp[i*s + si] = x[i*s + si];
        }
    }

    for(I i = row_start; i != row_stop; i += row_step) {
        I start = Ap[i];
        I end   = Ap[i+1];
        T diag = 0;
        std::fill(rsum.begin(), rsum.end(), 0);

        for(I jj = start; jj < end; jj++){
            I j = Aj[jj];
            if (i == j) {
                diag  = Ax[jj];
            }
            else {
                for(I si=0; si < s; si++){
                    rsum[si] += Ax[jj]*temp[j*s + si];
                }
            }
        }

        if (diag != (T) 0.0){
            for(I si=0; si < s; si++){
                x[i*s + si] = (one - omega2) * temp[i*s + si] + omega2 * ((b[i*s + si] - rsum[si])/diag);
            }
        }
    }
}
