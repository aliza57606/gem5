#include <stdio.h>

#define SIZE 8

int main() {
    int A[SIZE]={1,2,3,4,5,6,7,8};
    int B[SIZE]={8,7,6,5,4,3,2,1};
    int C[SIZE];

    for(int i=0;i<SIZE;i++)
        C[i]=A[i]+B[i];

    printf("Result:\n");

    for(int i=0;i<SIZE;i++)
        printf("%d ",C[i]);

    printf("\n");

    return 0;
}