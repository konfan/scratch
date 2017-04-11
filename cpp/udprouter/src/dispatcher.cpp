#include "dispatcher.h"
#include <string.h>
#include <Poco/Net/DatagramSocket.h>
#include <Poco/Net/SocketAddress.h>
#include <Poco/Logger.h>
#include <cassert>



using namespace VSchedule;




Dispatcher::Dispatcher() {
}

Dispatcher::~Dispatcher() {
}



void Dispatcher::apply(
        const std::string & source,
        void * buffer, size_t len) {

    Rule::Array dests = _rule.parse(source);
    Poco::Net::DatagramSocket sender;
    Poco::Logger & logger = Poco::Logger::get("TestLogger");


    for (Rule::Array::iterator it = dests.begin();
            it != dests.end(); ++it) {
        Poco::Net::SocketAddress addr(*it);
        int l = sender.sendTo(buffer, len, addr);
        assert(l == (int)len);
        logger.information("from %s to %s %d", source, addr.toString(), l);
    }


    // write to file

}
