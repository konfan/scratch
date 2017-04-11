#ifndef _VS_RTPSERVER_H__2312323
#define _VS_RTPSERVER_H__2312323
#include "udpreceiver.h"
#include <Poco/ThreadPool.h>

/*
 * receive 
 */

namespace VSchedule {

    class RtpServer 
    {
    public:
        RtpServer();

    private:
        UdpReceiver *    _receiver;
        Poco::ThreadPool *     _pool;
        
        // dispatcher connect udpreceiver and buffer
        Dispatcher *    _dispatcher;
    };
}

#endif
