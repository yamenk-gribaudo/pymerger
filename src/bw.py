import logger as log, json as js
from automationsTest import loopAuto as aut
import uasyncio
from messenger import addFirstMessage as mes
from messenger import startSender as mes2
import modulesHandler

version = 1

internetIsConnected = False

token = None
host = None
tenant = None
username = None
password = None

config = None
globalConfigFilepath = None
automations = None
modulesConfig = None
modules = []


async def automationsLoop():
    moduleStates = {}
    for _, module in modules.items():
        # moduleStates is a dictionary with pointers, so now moduleStates 'knows' every time a value is updated. Be careful,
        # if you 'update' the whole value of an inmutable type, a new variable is created instead of updating the old one,
        # so you must change state values accesing keys inside the value instead of updating the whole value.
        moduleStates[module.id] = module.value
    await aut(automations, moduleStates)


def asyncExceptionHandler(_, context):
    log.logFatal(context["exception"])


def start(tokenString=None, tokenFilepath=None, configObject=None, configFilepath=None):
    global modules
    global token, host, tenant, username, password
    global config, automations, modulesConfig, globalConfigFilepath

    # Chekc and add token
    if tokenString != None:
        token = tokenString
    elif tokenFilepath != None:
        token = open(tokenFilepath).read().strip().split(':')
    else:
        raise Exception(
            "Either tokenString or tokenFilepath must be passed as arguments!")
    host = token[0]
    tenant = token[1]
    username = token[2]
    password = token[3]

    # Check and add config
    if configObject != None:
        config = configObject
    elif configFilepath != None:
        config = js.load(open(configFilepath))
        globalConfigFilepath = configFilepath
    else:
        raise Exception(
            "Either configObject or configFilepath must be passed as arguments!")
    automations = config['automations']
    modulesConfig = config['modules']

    modules = modulesHandler.generateModuleInstances(modulesConfig)
    mes()
    uasyncio.create_task(automationsLoop())
    uasyncio.create_task(mes2())
    uasyncio.get_event_loop().set_exception_handler(asyncExceptionHandler)
    uasyncio.get_event_loop().run_forever()

if __name__=="__main__":
    var ="hello"
    print(var + version)