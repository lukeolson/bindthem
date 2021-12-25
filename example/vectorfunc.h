#include <iostream>
#include <vector>

// testing a vector
template <class T>
void f(std::vector<T> &v) {
    for(std::vector<int>::size_type i=0; i<v.size(); i++){
        std::cout << "v[i] = " << v[i] << std::endl;
    }
}
