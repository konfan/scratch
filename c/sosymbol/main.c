#include "call.h"
#include <stdio.h>
#include <sys/select.h>

int gdata = 20;


int main() {
    gdata = 33;
    printf("%d\n", call());
    select(0, NULL, NULL, NULL, NULL);
    return 0;
}
