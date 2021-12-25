#include <iostream>

// 2d array
void printit(int *x, int x_size, int s)
{
	int i, j;
	for(i=0; i<x_size; i++)
	{
		for(j=0; j<s; j++)
		{
            std::cout << x[i + j*x_size] << " ";
		}
        std::cout << std::endl;
	}
}

void printit0(int x[], int x_size, int s)
{
	int i;
	for(i=0; i<x_size; i++)
	{
        std::cout << x[i] << " ";
	}
    std::cout << std::endl;
}
