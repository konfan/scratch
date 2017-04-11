#include "udpreceiver.h"
#include <Poco/Net/SocketAddress.h>
#include <Poco/Logger.h>



using namespace VSchedule;

UdpReceiver::UdpReceiver(const std::string & hostaddress, int port) :
    _threadpool(new Poco::ThreadPool(1))
{

    Poco::Net::SocketAddress addr(hostaddress, port);
    _socket.bind(addr, true);

}

UdpReceiver::~UdpReceiver() {
    _threadpool->stopAll();
    delete _threadpool;
}



void UdpReceiver::start() {
    // bind a socket and listening
    //
    for (int i = 0; i< 1; i++)
        _threadpool->start(*this);
}


void UdpReceiver::run() {
    Poco::Logger & logger = Poco::Logger::get("TestLogger");
    // ip packet max capicity is 64KB
    char buffer[64*1024] = {0}; 
    Dispatcher dispatcher;

    for (;;) {
        Poco::Net::SocketAddress srcaddr;
        int len = _socket.receiveFrom(buffer, sizeof(buffer), srcaddr);
        logger.debug("received %d", len);
        if (len < 0) {
            logger.critical("error when reading sockert");
        }
        dispatcher.apply(srcaddr.toString(), buffer, len);
    }
}
