#include <stdio.h>

template <typename T>
class T1 {
public:
    T1() {
        printf("T1 created\n");
    }
};


template <typename T>
class T2 {
public:
    T2() {
        printf("T2 created\n");
    }
};

template <class C, class P = C *>
class TClass {
public:
    void show() {
        printf("c & c* \n");
    }

};

template <class C>
class TClass <C, T1<C> > 
{
public:
    void show() {
        printf("c & T1\n");
    }
};

template <class C>
class TClass <C, T2<C> > 
{
public:
    void show() {
        printf("c & T2\n");
    }
};

template <class C>
class TClass <C, C * > 
{
public:
    void show() {
        printf("c yoyo\n");
    }
};

int main() {
    int i;
    //TClass<int, T1<int> > o;
    TClass<int> o;
    //o.show();
    unsigned char c = 0x00;
    printf("%hx\n", 1 << c);
    return 0;
}
