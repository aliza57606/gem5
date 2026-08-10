#include <iostream>
#include <vector>
#include <cstdlib>

int main(int argc, char* argv[])
{
    if (argc != 3) {
        std::cerr << "Usage: daxpy_worker <start> <end>" << std::endl;
        return 1;
    }

    int start = std::atoi(argv[1]);
    int end = std::atoi(argv[2]);

    const int N = 10000;
    const double a = 2.5;

    if (start < 0 || end > N || start >= end) {
        std::cerr << "Invalid range." << std::endl;
        return 1;
    }

    std::vector<double> x(N, 1.0);
    std::vector<double> y(N, 2.0);

    for (int i = start; i < end; i++) {
        y[i] = a * x[i] + y[i];
    }

    std::cout << "Processed range: "
              << start << " to " << end << std::endl;

    std::cout << "Result check: y[" << start
              << "] = " << y[start] << std::endl;

    return 0;
}
