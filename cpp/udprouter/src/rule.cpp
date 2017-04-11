#include "rule.h"
#include <fstream>
#include <sstream>
#include <iostream>





using namespace VSchedule;


Rule::Rule() {
    std::ifstream  istrm("rule", std::ios::in);
    for (std::string line; std::getline(istrm, line);) {
        std::stringstream ss(line);
        std::string key, value;
        ss >> key; ss >> value;
        _map[key].push_back(value);
    }
}



Rule::Array
Rule::parse(const std::string & source) {
    return _map[source];
}


void Rule::show() {
    for (Map::iterator it = _map.begin(); it != _map.end(); ++it) {
        std::cout << it->first << ":";
        for (Array::iterator ait = it->second.begin(); ait != it->second.end(); ++ait) {
            std::cout << *ait << " ";
        }
        std::cout << std::endl;
    }
}
