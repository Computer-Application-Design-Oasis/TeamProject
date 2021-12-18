import os
import sys
import time
import re
import subprocess

def getHTTPStatusCodeString(url):
    return os.popen('curl -o /dev/null -w %{http_code} ' + url + ' -s -XGET').read()

def getHTTPStatusCode(url):
    statusCodeString = getHTTPStatusCodeString(url)

    if statusCodeString.isdecimal():
        return int(statusCodeString)

    return -1

def hasHTTPStatusCodeError(statusCode : int):
    if statusCode == -1:
        return True

    if statusCode >= 400:
        return True

    return False

class MicroService:
    def __init__(self, containerName = ""):
        self.containerName = containerName

    def restart(self):
        print("[{}]: Error occured, restarting container...".format(self.containerName), file=sys.stderr)
        
        result = os.system("docker restart " + self.containerName)

        if result == 0:
            print("[{}]: Restarted successfully.".format(self.containerName))
        else:
            print("[{}]: Failed to restart container.".format(self.containerName))

    def isAvailable(self):
        return True

    def restartIfNotAvailable(self):
        print("[{}]: Checking If microservice available...".format(self.containerName))

        if not self.isAvailable():
            self.restart()
        else:
            print("[{}]: This microservice is available now.".format(self.containerName))
        
        print("")

class MicroServiceHTTP(MicroService):
    def __init__(self, containerName = "", urls = []):
        super().__init__(containerName)

        self.urls = urls

    def isAvailable(self):
        for url in self.urls:
            httpStatusCode = getHTTPStatusCode(url)
            print("Got a http status code from {} : {}".format(url, httpStatusCode))

            if hasHTTPStatusCodeError(httpStatusCode):
                return False

        return True

class MicroServicePrivate(MicroService):
    def __init__(self, containerName = "", ports = []):
        super().__init__(containerName)

        self.ports = ports

    def isAvailable(self):
        for port in self.ports:
            result = os.system('docker exec {} nc -z localhost {}'.format(self.containerName, port))

            if result != 0:
                return False

        return True

class MicroServiceProcess(MicroService):
    def __init__(self, containerName = "", processNames = []):
        super().__init__(containerName)

        self.processNames = processNames

    def isAvailable(self):
        for processName in self.processNames:
            result = os.system('docker exec {} pgrep {}'.format(self.containerName, processName))
     
            if result != 0:
                return False
        
        return True

rootURL = 'http://localhost/'

edgeRouter = MicroServiceHTTP("docker-compose_edge-router_1", [rootURL])
frontend = MicroServiceHTTP("docker-compose_front-end_1", [rootURL])
catalogue = MicroServiceHTTP("docker-compose_catalogue_1", [rootURL + "catalogue"])
carts = MicroServiceHTTP("docker-compose_carts_1", [rootURL + "cart"])
user = MicroServiceHTTP("docker-compose_user_1", [rootURL + "customers", rootURL + "cards", rootURL + "addresses"])

orders = MicroServicePrivate("docker-compose_orders_1", [80])
shipping = MicroServicePrivate("docker-compose_shipping_1", [80])
payment = MicroServicePrivate("docker-compose_payment_1", [80])
queueMaster = MicroServicePrivate("docker-compose_queue-master_1", [80])

rabbitmq = MicroServiceProcess("docker-compose_rabbitmq_1", ["rabbitmq-server"])
catalogueDB = MicroServiceProcess("docker-compose_catalogue-db_1", ["mysqld"])
cartsDB = MicroServiceProcess("docker-compose_carts-db_1", ["mongod"])
userDB = MicroServiceProcess("docker-compose_user-db_1", ["mongod"])
ordersDB = MicroServiceProcess("docker-compose_orders-db_1", ["mongod"])

autoHealTargets =[
    edgeRouter,
    frontend,
    catalogue,
    carts,
    user,

    orders,
    shipping,
    payment,
    queueMaster,

    rabbitmq,
    catalogueDB,
    cartsDB,
    userDB,
    ordersDB
]

while 1:
    print("--------------------------------------------")
    
    for target in autoHealTargets:
        target.restartIfNotAvailable()

    print("--------------------------------------------")

    time.sleep(10)