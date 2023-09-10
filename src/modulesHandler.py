
import bw
import os
import logger
import json


def generateModuleInstances(modulesConfig):
    # Get module classes
    Modules = {}
    for file in os.listdir("modules"):
        moduleName = ''.join(file.split(".")[: -1])  # Removes file extension
        Modules[moduleName] = __import__("modules/" + moduleName).Module

    # Create module intances
    moduleInstances = {}
    for module in modulesConfig:
        try:
            moduleInstances[module['id']] = Modules[module['type']](module)
        except Exception as e:
            logger.logWarn(e)
    return moduleInstances


def addState(msg):
    print("yah")


def getDevice():
    device = {}
    system = os.uname()
    device["config"] = bw.config
    device["board"] = system[0]
    device["mp"] = system[2]
    device["apiVersion"] = bw.version
    device["moduleVersions"] = getModuleVersions()
    return device


def getModuleVersions():
    versions = {}
    for file in os.listdir("modules"):
        moduleName = ''.join(file.split(".")[: -1])  # Removes file extension
        if hasattr(__import__("modules/" + moduleName), 'version'):
            versions[moduleName] = __import__("modules/" + moduleName).version
        else:
            logger.logWarn(moduleName + " module has no version")
            versions[moduleName] = "undefined"
    return versions


def updateState(msg):
    try:
        msg = json.loads(msg)
        module_id = msg['module_id']
        new_state = json.loads(msg['new_state'])
        logger.log("Updating %s state with %s" % (module_id, new_state))
        bw.modules[module_id].updateState(new_state)
    except Exception as e:
        logger.logError(e)
