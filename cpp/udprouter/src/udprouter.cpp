#include "rtpserver.h"
#include "udpreceiver.h"
#include "rule.h"

#include <Poco/RunnableAdapter.h>
#include <Poco/Logger.h>
#include <Poco/ConsoleChannel.h>
#include <Poco/AutoPtr.h>
#include <iostream>
#include <stdio.h>


int main() {

    // parse option or config file 
    // create rtpserver
    
    Poco::AutoPtr<Poco::ConsoleChannel> pChannel(new Poco::ConsoleChannel(std::cout));
    //Poco::Logger::root().setChannel(pChannel);
    Poco::Logger & log = Poco::Logger::get("TestLogger");
    log.information("start testing");

    VSchedule::Rule rule;

    rule.show();

    VSchedule::UdpReceiver v("0.0.0.0", 2008);
    VSchedule::UdpReceiver a("0.0.0.0", 2010);
    v.start();
    a.start();
    v.join();
    a.join();



    return 0;
}
