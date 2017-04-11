#include <map>
#include <stdio.h>
#include <functional>



class MapType 
{
public:
    MapType(int a) : _a(a) {}
    // link error if uncommment this line
    //MapType();
    MapType() : _a(0) {}

    int _a;
};


class KeyType 
{
public:
    KeyType(int a) : _a(a) {}


    //bool operator < (const KeyType &rh) const {
    //    return this->_a < rh._a;
    //}

    int _a;
};

template <class T>
struct Cmp 
{
    bool operator()(const T& lh, const T& rh) const {
        return false;
    }
};

template <>
struct Cmp<KeyType> 
{
    bool operator()(const KeyType& lh, const KeyType& rh) const {
        return lh._a > rh._a;
    }

};

namespace std {

    template<>
        struct less<KeyType> {
            bool operator() (const KeyType lh, const KeyType & rh) const {
                return lh._a > rh._a;
            }
        };

}


typedef std::map<int, MapType> Map;
//typedef std::map<KeyType, MapType, Cmp<KeyType> > KeyMap;
typedef std::map<KeyType, MapType > KeyMap;


int main() {
    Map mm;
    mm[2] = MapType(10);

    KeyMap km;
    km[1] = 3;
    km[2] = 3;
    for (KeyMap::iterator it = km.begin() ; it != km.end(); ++it) {
        printf("%d:%d\n", it->first._a, it->second._a);
    }
}
