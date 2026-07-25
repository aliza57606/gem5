#include <stdio.h>

int main(void)
{
    volatile long long sum = 0;
    int x = 1;

    for (int i = 0; i < 1000000; i++) {
        x = (x * 1103515245 + 12345) & 0x7fffffff;

        if ((x & 1) == 0) {
            sum += i;
        } else {
            sum -= i;
        }

        if ((x % 4) < 2) {
            sum += x;
        } else {
            sum -= x;
        }

        if (((i & 1) == 0) == ((x & 1) == 0)) {
            sum += 3;
        } else {
            sum -= 3;
        }
    }

    printf("Result: %lld\n", sum);
    return 0;
}