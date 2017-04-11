#ifndef _VSCHE_UDPRECEIVER_H__2342342
#define _VSCHE_UDPRECEIVER_H__2342342

#include "dispatcher.h"
#include <Poco/ThreadPool.h>
#include <Poco/Runnable.h>
#include <Poco/Net/DatagramSocket.h>


namespace VSchedule {

    // UdpReceiver has its own thread to receive input
    class UdpReceiver: Poco::Runnable
    {
    public:
        UdpReceiver(const std::string & hostaddress, int port);


        ~UdpReceiver();

        // start udp receive thread
        void start();

        void join() {
            _threadpool->joinAll();
        }

        virtual void run();

    private:
        UdpReceiver(const UdpReceiver &);
        UdpReceiver & operator=(const UdpReceiver &);
        Poco::ThreadPool *          _threadpool;
        Poco::Net::DatagramSocket   _socket;

    };

}

#endif
