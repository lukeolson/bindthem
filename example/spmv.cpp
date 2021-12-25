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
