#ifndef _VS_RULE_H__lwke3
#define _VS_RULE_H__lwke3

#include <vector>
#include <string>
#include <map>


namespace VSchedule {

    class Rule
    {
    public:
        typedef std::vector<std::string> Array;
        typedef std::map<std::string, Array> Map;
        Rule();
        ~Rule(){}


        Array parse(const std::string & source);
    

        void show() ;


    private:
    
        Map     _map;
    };

}



#endif
