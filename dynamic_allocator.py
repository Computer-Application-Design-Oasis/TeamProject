import os
import sys
import time
import re
import subprocess

class MicroService:
    def __init__(self, containerName):
        self.containerName = containerName

    def updateStats(self):
        for line in os.popen("docker stats --no-stream {}".format(self.containerName)).readlines()[1:]:
            id, name, cpuPercentage, memoryUsage, _, memoryLimit, memoryPercentage, netIn, _, netOut, blockIn, _, blockOut, pids = line.split()

            print("Id: {}".format(id))
            print("Name: {}".format(name))
            print("CPU % : {}".format(cpuPercentage))
            print("Memory : {}/{} {}".format(memoryUsage, memoryLimit, memoryPercentage))
            print("")

    def updateStats(self, id, cpuPercentage, memoryUsage, memoryLimit, memoryPercentage):
        print("Name: {}".format(name))
        print("id: {}".format(id))
        print("CPU % : {}".format(cpuPercentage))
        print("Memory : {}/{} {}".format(memoryUsage, memoryLimit, memoryPercentage))
        print("")

edgeRouter = MicroService("docker-compose_edge-router_1")
frontend = MicroService("docker-compose_front-end_1")
catalogue = MicroService("docker-compose_catalogue_1")
carts = MicroService("docker-compose_carts_1")
user = MicroService("docker-compose_user_1")

orders = MicroService("docker-compose_orders_1")
shipping = MicroService("docker-compose_shipping_1")
payment = MicroService("docker-compose_payment_1")
queueMaster = MicroService("docker-compose_queue-master_1")

rabbitmq = MicroService("docker-compose_rabbitmq_1")
catalogueDB = MicroService("docker-compose_catalogue-db_1")
cartsDB = MicroService("docker-compose_carts-db_1")
userDB = MicroService("docker-compose_user-db_1")
ordersDB = MicroService("docker-compose_orders-db_1")

dynamicAllocationTargets =[
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

    lines = os.popen("docker stats --no-stream").readlines()[1:]

    infos = {}
    for line in lines:
        id, name, cpuPercentage, memoryUsage, _, memoryLimit, memoryPercentage, netIn, _, netOut, blockIn, _, blockOut, pids = line.split()
        infos[name] = {
            "id": id,
            "name": name,
            "cpuPercentage": cpuPercentage,
            "memoryUsage": memoryUsage,
            "memoryLimit": memoryLimit,
            "memoryPercentage": memoryPercentage
        }
    
    for target in dynamicAllocationTargets:
        name = target.containerName
        id = infos[name]["id"]
        cpuPercentage = infos[name]["cpuPercentage"]
        memoryUsage = infos[name]["memoryUsage"]
        memoryLimit = infos[name]["memoryLimit"]
        memoryPercentage = infos[name]["memoryPercentage"]

        target.updateStats(id, cpuPercentage, memoryUsage, memoryLimit, memoryPercentage)

    print("--------------------------------------------")


    time.sleep(5)