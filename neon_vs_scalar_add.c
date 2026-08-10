// neon_vs_scalar_add.c
//
// Fair scalar-versus-NEON benchmark for Apple Silicon.
//
// Compile:
//   clang -O2 -o neon_vs_scalar_add neon_vs_scalar_add.c
//
// Run:
//   ./neon_vs_scalar_add
//
// The scalar loop keeps normal -O2 optimization, but Clang vectorization
// and interleaving are disabled only for that loop. The NEON version uses
// explicit 128-bit int32x4_t vectors and processes four integers at a time.

#include <arm_neon.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N (1 << 24)   // 16,777,216 integers
#define REPS 5

static double now_seconds(void) {
    struct timespec timestamp;

    if (clock_gettime(CLOCK_MONOTONIC, &timestamp) != 0) {
        perror("clock_gettime");
        exit(EXIT_FAILURE);
    }

    return (double)timestamp.tv_sec +
           (double)timestamp.tv_nsec / 1.0e9;
}

__attribute__((noinline))
static void scalar_add(
    const int32_t *restrict a,
    const int32_t *restrict b,
    int32_t *restrict c,
    size_t count
) {
#pragma clang loop vectorize(disable)
#pragma clang loop interleave(disable)
    for (size_t i = 0; i < count; ++i) {
        c[i] = a[i] + b[i];
    }
}

__attribute__((noinline))
static void neon_add(
    const int32_t *restrict a,
    const int32_t *restrict b,
    int32_t *restrict c,
    size_t count
) {
    size_t i = 0;

    for (; i + 4 <= count; i += 4) {
        const int32x4_t vector_a = vld1q_s32(&a[i]);
        const int32x4_t vector_b = vld1q_s32(&b[i]);
        const int32x4_t vector_c = vaddq_s32(vector_a, vector_b);

        vst1q_s32(&c[i], vector_c);
    }

    // Handle any remaining elements if count is not divisible by four.
    for (; i < count; ++i) {
        c[i] = a[i] + b[i];
    }
}

static int64_t calculate_checksum(
    const int32_t *values,
    size_t count
) {
    int64_t checksum = 0;

    for (size_t i = 0; i < count; ++i) {
        checksum += values[i];
    }

    return checksum;
}

static double benchmark_scalar(
    const int32_t *a,
    const int32_t *b,
    int32_t *c,
    size_t count
) {
    double best_time = 1.0e30;

    for (int repetition = 0; repetition < REPS; ++repetition) {
        const double start = now_seconds();

        scalar_add(a, b, c, count);

        const double end = now_seconds();
        const double elapsed = end - start;

        if (elapsed < best_time) {
            best_time = elapsed;
        }
    }

    return best_time;
}

static double benchmark_neon(
    const int32_t *a,
    const int32_t *b,
    int32_t *c,
    size_t count
) {
    double best_time = 1.0e30;

    for (int repetition = 0; repetition < REPS; ++repetition) {
        const double start = now_seconds();

        neon_add(a, b, c, count);

        const double end = now_seconds();
        const double elapsed = end - start;

        if (elapsed < best_time) {
            best_time = elapsed;
        }
    }

    return best_time;
}

int main(void) {
    const size_t bytes = N * sizeof(int32_t);

    int32_t *a = malloc(bytes);
    int32_t *b = malloc(bytes);
    int32_t *scalar_result = malloc(bytes);
    int32_t *neon_result = malloc(bytes);

    if (
        a == NULL ||
        b == NULL ||
        scalar_result == NULL ||
        neon_result == NULL
    ) {
        fprintf(stderr, "Memory allocation failed.\n");

        free(a);
        free(b);
        free(scalar_result);
        free(neon_result);

        return EXIT_FAILURE;
    }

    for (size_t i = 0; i < N; ++i) {
        a[i] = (int32_t)i;
        b[i] = (int32_t)(N - i);
    }

    // Warm-up runs
    scalar_add(a, b, scalar_result, N);
    neon_add(a, b, neon_result, N);

    const double scalar_time = benchmark_scalar(
        a,
        b,
        scalar_result,
        N
    );

    const double neon_time = benchmark_neon(
        a,
        b,
        neon_result,
        N
    );

    const int64_t scalar_checksum = calculate_checksum(
        scalar_result,
        N
    );

    const int64_t neon_checksum = calculate_checksum(
        neon_result,
        N
    );

    const double scalar_throughput =
        (double)N / scalar_time / 1.0e6;

    const double neon_throughput =
        (double)N / neon_time / 1.0e6;

    const double speedup = scalar_time / neon_time;

    printf("N = %d elements\n", N);
    printf("Repetitions = %d\n", REPS);

    printf(
        "Scalar: best_time = %.6f s, "
        "throughput = %.2f Melem/s, "
        "checksum = %lld\n",
        scalar_time,
        scalar_throughput,
        (long long)scalar_checksum
    );

    printf(
        "NEON:   best_time = %.6f s, "
        "throughput = %.2f Melem/s, "
        "checksum = %lld\n",
        neon_time,
        neon_throughput,
        (long long)neon_checksum
    );

    printf(
        "Speedup (scalar_time / neon_time): %.2fx\n",
        speedup
    );

    printf(
        "Checksums match: %s\n",
        scalar_checksum == neon_checksum ? "yes" : "NO"
    );

    free(a);
    free(b);
    free(scalar_result);
    free(neon_result);

    return scalar_checksum == neon_checksum
        ? EXIT_SUCCESS
        : EXIT_FAILURE;
}–