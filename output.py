import json, uasyncio, json as js, time, ntptime, sys, os, machine
def get_values(raw_values, previous_states, current_states):
    values = []
    for raw_value in raw_values:
        if (raw_value['type'] == 'fixed'):
            values.append(raw_value['value'])
        elif (raw_value['type'] == 'previous'):
            values.append(previous_states[raw_value['moduleId']][raw_value['index']])
        elif (raw_value['type'] == 'current'):
            values.append(current_states[raw_value['moduleId']][raw_value['index']])
    return values
def compare_states(first_state, second_state):
    for module in first_state:
        if ((type(first_state) == list) and (type(second_state) == list)):
            for key in first_state[module]:
                if (str(first_state[module][key]) != str(second_state[module][key])):
                    return False
        elif (first_state != second_state):
            return False
    return True
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
timeIsSet = False
startTime = time.time_ns()
finishTime = 0
logs = []
logsDirectory = 'logs'
def formatTime(t):
    return ((((((((((str(t[0]) + '/') + str(t[1])) + '/') + str(t[2])) + ' ') + str(t[4])) + ':') + str(t[5])) + ':') + str(t[6]))
messengerReady = False
msgQueue = []
def check_conditions(conditions, previous_states, current_states):
    for condition in conditions:
        values = get_values(condition['values'], previous_states, current_states)
        if (condition['operator'] == '='):
            if (values[0] != values[1]):
                return False
        elif (condition['operator'] == '!='):
            if (values[0] == values[1]):
                return False
        else:
            return False
    return True
warnFilename = (logsDirectory + '/warn.log')
errorFilename = (logsDirectory + '/error.log')
fatalFilename = (logsDirectory + '/fatal.log')
def log(log):
    try:
        global logs
        logs.insert(len(logs), log)
        if (len(logs) > 5):
            logs.pop(0)
    except Exception as e:
        sys.print_exception(e)
def logsToFile(filename):
    if (os.stat(filename)[6] > 50000):
        os.remove(filename)
    with open(filename, 'a') as f:
        for log in logs:
            sys.print_exception(log, f)
        f.write((('Time: ' + formatTime(machine.RTC().datetime())) + '\n'))
        f.write('___\n')
        f.close()
def createLogFiles():
    try:
        os.mkdir(logsDirectory)
    except:
        pass
    f = open(warnFilename, 'a')
    f.close
    f = open(errorFilename, 'a')
    f.close
    f = open(fatalFilename, 'a')
    f.close
def logInfo(info):
    try:
        print('INFO:', info)
        log(info)
    except Exception as e:
        sys.print_exception(e)
createLogFiles()
def execute_action(actions, current_states):
    for action in actions:
        if (action['type'] == 'updateState'):
            module_id = action['moduleId']
            index = action['index']
            newValue = action['value']
            if (newValue != current_states[module_id][index]):
                logInfo(('Automation triggered for %s' % module_id))
                new_state = json.dumps({index: newValue})
                msg = json.dumps({'module_id': module_id, 'new_state': new_state})
                updateState(msg)
async def loopAuto(automations, current_states):
    previous_states = json.loads(json.dumps(current_states))
    while True:
        try:
            (await uasyncio.sleep(0.01))
            if (compare_states(current_states, previous_states) == False):
                for automation in automations:
                    result = check_conditions(automation['conditions'], previous_states, current_states)
                    if (result == True):
                        execute_action(automation['actions'], current_states)
                previous_states = json.loads(json.dumps(current_states))
        except Exception as e:
            logFatal(e)
async def automationsLoop():
    moduleStates = {}
    for (_, module) in modules.items():
        moduleStates[module.id] = module.value
    (await loopAuto(automations, moduleStates))
def asyncExceptionHandler(_, context):
    logFatal(context['exception'])
def start(tokenString=None, tokenFilepath=None, configObject=None, configFilepath=None):
    global modules
    global token, host, tenant, username, password
    global config, automations, modulesConfig, globalConfigFilepath
    if (tokenString != None):
        token = tokenString
    elif (tokenFilepath != None):
        token = open(tokenFilepath).read().strip().split(':')
    else:
        raise Exception('Either tokenString or tokenFilepath must be passed as arguments!')
    host = token[0]
    tenant = token[1]
    username = token[2]
    password = token[3]
    if (configObject != None):
        config = configObject
    elif (configFilepath != None):
        config = js.load(open(configFilepath))
        globalConfigFilepath = configFilepath
    else:
        raise Exception('Either configObject or configFilepath must be passed as arguments!')
    automations = config['automations']
    modulesConfig = config['modules']
    modules = generateModuleInstances(modulesConfig)
    addFirstMessage()
    uasyncio.create_task(automationsLoop())
    uasyncio.create_task(startSender())
    uasyncio.get_event_loop().set_exception_handler(asyncExceptionHandler)
    uasyncio.get_event_loop().run_forever()
def getTime():
    try:
        if timeIsSet:
            return ((time.time_ns() // 1000000) + 946684800000)
        else:
            response = ((time.time_ns() - startTime) // (- 1000000))
            return response
    except Exception as e:
        logError(e)
async def loopEpoc():
    global timeIsSet
    global finishTime
    n = 0
    while True:
        try:
            (await uasyncio.sleep(0.1))
            if (timeIsSet is True):
                break
            if (internetIsConnected is True):
                n = (n + 1)
                finishTime = ((time.time_ns() - startTime) // 1000000)
                ntptime.settime()
                timeIsSet = True
                logInfo('Time is set')
        except Exception as e:
            if (n < 4):
                logError(e)
            else:
                logFatal(e)
uasyncio.create_task(loopEpoc())
def logWarn(warn):
    try:
        print('WARN:', end=' ')
        sys.print_exception(warn)
        log(warn)
        logsToFile(warnFilename)
        addErrorToQueue(warn, 'warn')
    except Exception as e:
        sys.print_exception(e)
def logError(error):
    try:
        print('ERROR:', end=' ')
        sys.print_exception(error)
        log(error)
        logsToFile(errorFilename)
        addErrorToQueue(error, 'error')
    except Exception as e:
        sys.print_exception(e)
def logFatal(fatal):
    try:
        print('FATAL:', end=' ')
        sys.print_exception(fatal)
        log(fatal)
        logsToFile(fatalFilename)
        addErrorToQueue(fatal, 'fatal')
        uasyncio.sleep(1)
        machine.reset()
    except Exception as e:
        sys.print_exception(e)
def addErrorToQueue(error, level):
    msg = {'method': 'addLog', 'time': getTime(), 'data': json.dumps({'level': level, 'error': str(error)})}
    msgQueue.append(msg)
def addState(msg):
    try:
        if (len(msgQueue) <= 50):
            msg['method'] = 'addState'
            msgQueue.append(msg)
        else:
            logWarn('State not added to queue, len(msgQueue) > 50')
    except Exception as e:
        logError(e)
def sendFirstMessageInQueue():
    try:
        if (len(msgQueue) > 0):
            msg = msgQueue.pop(0)
            if (('time' in msg) and (msg['time'] < 0)):
                msg['time'] = ((getTime() - finishTime) - msg['time'])
            uasyncio.create_task(modules['ws'].sendMessage(json.dumps(msg)))
    except Exception as e:
        logError(e)
def addFirstMessage():
    device = getDevice()
    msg = msg = {'method': 'addDevice', 'time': getTime(), 'data': json.dumps(device)}
    msgQueue.append(msg)
async def startSender():
    while True:
        (await uasyncio.sleep(0.1))
        if (messengerReady == True):
            sendFirstMessageInQueue()
def generateModuleInstances(modulesConfig):
    Modules = {}
    for file in os.listdir('modules'):
        moduleName = ''.join(file.split('.')[:(- 1)])
        Modules[moduleName] = __import__(('modules/' + moduleName)).Module
    moduleInstances = {}
    for module in modulesConfig:
        try:
            moduleInstances[module['id']] = Modules[module['type']](module)
        except Exception as e:
            logWarn(e)
    return moduleInstances
def getDevice():
    device = {}
    system = os.uname()
    device['config'] = config
    device['board'] = system[0]
    device['mp'] = system[2]
    device['apiVersion'] = version
    device['moduleVersions'] = getModuleVersions()
    return device
def getModuleVersions():
    versions = {}
    for file in os.listdir('modules'):
        moduleName = ''.join(file.split('.')[:(- 1)])
        if hasattr(__import__(('modules/' + moduleName)), 'version'):
            versions[moduleName] = __import__(('modules/' + moduleName)).version
        else:
            logWarn((moduleName + ' module has no version'))
            versions[moduleName] = 'undefined'
    return versions
def updateState(msg):
    try:
        msg = json.loads(msg)
        module_id = msg['module_id']
        new_state = json.loads(msg['new_state'])
        log(('Updating %s state with %s' % (module_id, new_state)))
        modules[module_id].updateState(new_state)
    except Exception as e:
        logError(e)
def updateConfig(msg):
    try:
        if (globalConfigFilepath is None):
            logError('You must use a configFilepath to update the config')
        elif (msg is not None):
            updateFile(globalConfigFilepath, msg)
        else:
            logWarn('Content is None')
    except Exception as e:
        logFatal(e)
def updateFileByPath(rawMsg):
    try:
        if (rawMsg is not None):
            msg = json.loads(rawMsg)
            filename = msg['filename']
            content = msg['content']
            updateFile(filename, content)
        else:
            logWarn('Content is None')
    except Exception as e:
        logError(e)
def updateModule(rawMsg):
    try:
        if (rawMsg is not None):
            msg = json.loads(rawMsg)
            filename = ('modules/' + msg['filename'])
            content = msg['content']
            updateFile(filename, content)
        else:
            logWarn('Content is None')
    except Exception as e:
        logError(e)
def updateBw(msg):
    try:
        if (msg is not None):
            updateFile('bw.py', msg)
        else:
            logWarn('Content is None')
    except Exception as e:
        logFatal(e)
def updateFile(fileName, content):
    try:
        logInfo(('Updating file: ' + fileName))
        file = open(fileName, 'w')
        file.flush()
        file.write(content)
        file.close()
        logInfo(("File '%s' updated" % fileName))
    except Exception as e:
        logFatal(e)
if (__name__ == '__main__'):
    var = 'hello'
    print((var + version))
    var2 = 'hello2'
    print((var2 + timeIsSet))
