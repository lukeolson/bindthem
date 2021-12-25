void spmv(const int n,
          const int Ap[], const int Ap_size,
          const int Aj[], const int Aj_size,
          const double Ax[], const int Ax_size,
          const double Xx[], const int Xx_size,
                double Yx[], const int Yx_size)
{
    for(int i = 0; i < n; i++){
        double sum = Yx[i];
        for(int jj = Ap[i]; jj < Ap[i+1]; jj++){
            sum += Ax[jj] * Xx[Aj[jj]];
        }
        Yx[i] = sum;
    }
}


//
// Reference SpMV from scipy
//
// y <- A * x
//
// Parameters
// ----------
// n_row, n_col : int
//    dimensions of the n_row x n_col matrix A
// Ap, Aj, Ax : array
//    CSR pointer, index, and data vectors for matrix A
// Xx : array
//    input vector
// Yy : array
//    output vector (modified in-place)
//
// See Also
// --------
// csr_matvec_omp
//
// Notes
// -----
// Requires GCC 4.9 for ivdep
// Requires a compiler with OMP
// https://github.com/scipy/scipy/blob/master/scipy/sparse/sparsetools/csr.h#L1122
template <class I, class T>
void csr_matvec(const I n_row,
                const I n_col,
                const I Ap[], const int Ap_size,
                const I Aj[], const int Aj_size,
                const T Ax[], const int Ax_size,
                const T Xx[], const int Xx_size,
                      T Yx[], const int Yx_size)
{
    for(I i = 0; i < n_row; i++){
        T sum = Yx[i];
        for(I jj = Ap[i]; jj < Ap[i+1]; jj++){
            sum += Ax[jj] * Xx[Aj[jj]];
        }
        Yx[i] = sum;
    }
}
