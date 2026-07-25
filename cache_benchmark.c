#include <stdint.h>
#include <stdio.h>

#define SMALL_SIZE (12 * 1024)   // 48 KiB
#define LARGE_SIZE (128 * 1024)  // 512 KiB

static int small_array[SMALL_SIZE];
static int large_array[LARGE_SIZE];

int main(void)
{
    volatile uint64_t sum = 0;

    for (int i = 0; i < SMALL_SIZE; i++) {
        small_array[i] = i;
    }

    for (int i = 0; i < LARGE_SIZE; i++) {
        large_array[i] = i;
    }

    for (int pass = 0; pass < 100; pass++) {
        for (int i = 0; i < SMALL_SIZE; i++) {
            sum += small_array[i];
        }
    }

    for (int pass = 0; pass < 10; pass++) {
        for (int i = 0; i < LARGE_SIZE; i++) {
            sum += large_array[i];
        }
    }

    printf("Checksum: %llu\n", (unsigned long long)sum);
    return 0;
}