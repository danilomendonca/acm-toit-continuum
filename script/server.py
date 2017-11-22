import threading
import time
import os
from socket import *
from subprocess import call

DEFAULT_EXECUTION_TIME = 2 #seconds

HELLO_MSG = 'HI'
SERVICE_OK_MSG = 'OK'
CLIENT_IP = '127.0.0.1'

s=socket(AF_INET, SOCK_DGRAM)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

#comment out after client has been implemented
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
            #comment out this block after client is implemented
            identification(rcvr[0])
        elif data == SERVICE_OK_MSG:
            confirmation(data)
        else:
             print 'Client Discovered'
             print 'Acquisition URL: ' + data
             print 'Client IP: ' + rcvr[0]
             bindClientIp(rcvr[0])
             checkAcquisition(data)

def bindClientIp(received_ip):
    global CLIENT_IP
    CLIENT_IP = received_ip
    #uncomment after client is implemented
    #s.bind((CLIENT_IP,12345))

#comment out after client is implemented
server_discovered = False
def identification(server_ip):
    global server_discovered
    print 'Hello received'
    if not server_discovered:
        print 'Client Sending Identification'
        FUNCTION_URL = 'https://github.com/mgarriga/example-lambda'
        s.sendto(FUNCTION_URL,(server_ip, 12345))
        server_discovered = True

def confirmation(service_name):
    print 'Service confirmation for ' + service_name + ' received'

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
    s.sendto(SERVICE_OK_MSG,(CLIENT_IP, 12345))

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
    install_result = call(install_cmd, shell=True)
    if install_result != 0:
        print 'Updating function ' + actionName + ' as ' + actionSourceFile
        update_function_cmd = 'wsk action update ' + actionName + ' ' + actionSourceFile + ' --web yes'
        update_cmd = "cd " + repo_name + '; ' + update_function_cmd
        return call(update_cmd, shell=True)
    else:
        return install_result

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

time.sleep(DEFAULT_EXECUTION_TIME)

recv_t.do_run = False
recv_t.join()
hrtb_t.do_run = False
hrtb_t.join()
