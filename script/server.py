import threading
import time
import os
from socket import *
from subprocess import call

HELLO_MSG = 'HI'
CLIENT_IP = '127.0.0.1'

s=socket(AF_INET, SOCK_DGRAM)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
s.bind((CLIENT_IP,12345))

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
             CLIENT_IP = rcvr[0]
             checkAcquisition(data)

def identification(server_ip):
    print 'Hello received'
    print 'Client Sen1ding Identification'
    FUNCTION_URL = 'https://github.com/mgarriga/example-lambda'
    s.sendto(FUNCTION_URL,(CLIENT_IP, 12345))

def checkAcquisition(repo_url):
    print 'Checking Acquisition of ' + repo_url
    repo_name = repo_url.rsplit('/', 1)[-1]
    path_exists = os.path.exists(repo_name)
    if not path_exists:
        print 'Acquisition result: ', cloneRepo(repo_url)
    else:
        print repo_url + ' already acquired, checking for updates'
        print 'Update result: ', updateRepo(repo_url, repo_name)
    checkFunctionsInRepo(repo_name)

def checkFunctionsInRepo(repo_name):
    print 'Checking for JS functions in repo ' + repo_name
    for actionName in os.listdir(repo_name):
        if actionName.endswith("Function.js"):
            # print(os.path.join(directory, filename))
            performInstallation(repo_name, actionName, actionName)
            continue
        else:
            continue

def performInstallation(repo_name, actionName, actionSourceFile):
    print 'Installing function ' + actionName + ' as ' + actionSourceFile
    add_function_cmd = 'wsk action create ' + actionName + ' ' + actionSourceFile + ' --web yes'
    install_cmd = "cd " + repo_name + '; ' + add_function_cmd
    return call(install_cmd, shell=True)

def cloneRepo(repo_url):
    print 'Cloning repo' + repo_url
    return call("git clone " + repo_url, shell=True)

def updateRepo(repo_url, repo_name):
    print 'Updating repo' + repo_url
    return call("cd " + repo_name + ";git pull origin master", shell=True)

hrtb_t = threading.Thread(target=heartbeat)
hrtb_t.start()

recv_t = threading.Thread(target=recv)
recv_t.start()

#comment out in production
time.sleep(2)
recv_t.do_run = False
recv_t.join()
hrtb_t.do_run = False
hrtb_t.join()
