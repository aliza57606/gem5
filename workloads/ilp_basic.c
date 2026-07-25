#include <stdio.h>

int main(void)
{
    volatile int a = 5;
    volatile int b = 10;
    volatile int c = 0;

    for (int i = 0; i < 1000; i++) {
        c = a + b;
        a = c % 100;
        b = (a + 2) % 100;
    }

    printf("Result: %d\n", c);
    return 0;
}