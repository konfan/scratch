#ifndef _VSCHE_DISPATCHER_H__vder3
#define _VSCHE_DISPATCHER_H__vder3


#include "rule.h"
#include <string>
#include <stddef.h>


namespace VSchedule {


    class Dispatcher
    {
    public:
        Dispatcher();
        ~Dispatcher();


        void apply(const std::string & source, void * buffer, size_t len);

    private:

        // modify to map<socket addr, sendqueue>
        // create strategy

        // working thread pool
        

        Rule    _rule;
    };
}



#endif
