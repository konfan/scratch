#include "call.h"
#include <stdio.h>

int gdata = 20;


int main() {
    gdata = 33;
    printf("%d\n", call());
    return 0;
}
