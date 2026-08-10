#include <iostream>
#include <vector>
#include <thread>
#include <cstdlib>
#include <functional>

void daxpy_worker(
    const std::vector<double>& x,
    std::vector<double>& y,
    double a,
    int start,
    int end
) {
    for (int i = start; i < end; i++) {
        y[i] = a * x[i] + y[i];
    }
}

int main(int argc, char* argv[]) {

    int num_threads = 1;

    if (argc > 1) {
        num_threads = std::atoi(argv[1]);
    }

    if (num_threads < 1) {
        std::cerr << "Number of threads must be at least 1." << std::endl;
        return 1;
    }

    const int N = 10000;
    const double a = 2.5;

    std::vector<double> x(N, 1.0);
    std::vector<double> y(N, 2.0);

    int chunk_size = N / num_threads;

    std::vector<std::thread> threads;

    /*
     * Create num_threads - 1 worker threads.
     *
     * The main thread performs the final portion of the work.
     * Therefore:
     *
     * 1 requested thread = main thread only
     * 2 requested threads = 1 worker + main
     * 4 requested threads = 3 workers + main
     * 8 requested threads = 7 workers + main
     */

    for (int t = 0; t < num_threads - 1; t++) {

        int start = t * chunk_size;
        int end = start + chunk_size;

        threads.emplace_back(
            daxpy_worker,
            std::cref(x),
            std::ref(y),
            a,
            start,
            end
        );
    }

    /*
     * Main thread processes the final chunk.
     */
    int main_start = (num_threads - 1) * chunk_size;

    daxpy_worker(
        x,
        y,
        a,
        main_start,
        N
    );

    /*
     * Wait for worker threads.
     */
    for (auto& thread : threads) {
        thread.join();
    }

    std::cout << "Threads: " << num_threads << std::endl;
    std::cout << "Result check: y[0] = " << y[0] << std::endl;

    return 0;
}