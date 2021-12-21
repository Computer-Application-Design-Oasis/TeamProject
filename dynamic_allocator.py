import os
import sys
import time
import re
import subprocess

class Container:
    def __init__(self, name):
        self.name = name

        self.id = ""
        self.weight = 1024
        self.memory = 4

    def updateStats(self, id, cpuPercentage, memoryUsage, memoryLimit, memoryPercentage, weight):
        self.id = id
        self.cpuPercentage = cpuPercentage
        self.memoryUsage = memoryUsage
        self.memoryLimit = memoryLimit
        self.memoryPercentage = memoryPercentage       
        self.weight = weight

        print("Name: {}".format(self.name))
        # print("id: {}".format(id)) 
        print("CPU % : {}%".format(cpuPercentage))
        # print("Memory : {}/{} {}%".format(memoryUsage, memoryLimit, memoryPercentage))
        print("CPU Weight : {}".format(self.weight))
        print("")

        self.updateWeight()

    def updateWeight(self):
        subprocess.check_output("docker update {} --cpu-shares={}".format(self.name, int(self.weight)), shell=False)

edgeRouter = Container("docker-compose_edge-router_1")
frontend = Container("docker-compose_front-end_1")
catalogue = Container("docker-compose_catalogue_1")
carts = Container("docker-compose_carts_1")
user = Container("docker-compose_user_1")

orders = Container("docker-compose_orders_1")
shipping = Container("docker-compose_shipping_1")
payment = Container("docker-compose_payment_1")
queueMaster = Container("docker-compose_queue-master_1")

rabbitmq = Container("docker-compose_rabbitmq_1")
catalogueDB = Container("docker-compose_catalogue-db_1")
cartsDB = Container("docker-compose_carts-db_1")
userDB = Container("docker-compose_user-db_1")
ordersDB = Container("docker-compose_orders-db_1")

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

cpuMinWeight = 64
cpuMaxWeight = 4096

while 1:
    print("--------------------------------------------")

    lines = os.popen("docker stats --no-stream").readlines()[1:]

    infos = {}

    cpuPercentageSum = 0
    cpuWeightSum = 0
    for line in lines:
        id, name, cpuPercentage, memoryUsage, _, memoryLimit, memoryPercentage, netIn, _, netOut, blockIn, _, blockOut, pids = line.split()

        cpuPercentage = float(cpuPercentage[:-1])
        memoryPercentage = float(memoryPercentage[:-1])

        infos[name] = {
            "id": id,
            "name": name,
            "cpuPercentage": cpuPercentage,
            "memoryUsage": memoryUsage,
            "memoryLimit": memoryLimit,
            "memoryPercentage": memoryPercentage
        }

        cpuPercentageSum += cpuPercentage
        cpuWeightSum += 1024
    
    for target in dynamicAllocationTargets:
        name = target.name
        id = infos[name]["id"]
        cpuPercentage = infos[name]["cpuPercentage"]
        memoryUsage = infos[name]["memoryUsage"]
        memoryLimit = infos[name]["memoryLimit"]
        memoryPercentage = infos[name]["memoryPercentage"]
        weight = max(min((cpuPercentage / cpuPercentageSum) * cpuWeightSum, cpuMaxWeight), cpuMinWeight)

        target.updateStats(id, cpuPercentage, memoryUsage, memoryLimit, memoryPercentage, weight)

    print("--------------------------------------------")


    time.sleep(5)