import threading
from socket import *
import time
s=socket(AF_INET, SOCK_DGRAM)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

HELLO_MSG = 'HI'

def heartbeat():
    print 'Domain Hearbeat Started'
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        print 'sending hello'
        s.sendto(HELLO_MSG,('', 12345))
        time.sleep(1)

def recv():
    print 'Domain Receiver Started'
    t = threading.currentThread()
    while getattr(t, "do_run", True):
         data, rcvr = s.recvfrom(1024)
         if data == HELLO_MSG:
             identification(rcvr)
         else:
             print 'Client Discovered'
             print 'Acquisition URL: ' + data
             print 'Client IP: ' + rcvr[0]
             checkAcquisition(data)

def identification(server_ip):
    print 'Hello received'
    print 'Client Sen1ding Identification'
    FUNCTION_URL = 'https://github.com/mgarriga/example-lambda'
    s.sendto(FUNCTION_URL,(CLIENT_IP, 12345))

def checkAcquisition(repo_url):
    print 'Checking Acquisition of ' + repo_url
    


CLIENT_IP = '127.0.0.1'
s.bind((CLIENT_IP,12345))

hrtb_t = threading.Thread(target=heartbeat)
hrtb_t.start()

recv_t = threading.Thread(target=recv)
recv_t.start()

time.sleep(2)

recv_t.do_run = False
recv_t.join()

hrtb_t.do_run = False
hrtb_t.join()
