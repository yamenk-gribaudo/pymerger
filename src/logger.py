import sys
import os
import uasyncio
import json
import machine
import messenger
import epoc

logs = []
logsDirectory = "logs"
warnFilename = logsDirectory + "/warn.log"
errorFilename = logsDirectory + "/error.log"
fatalFilename = logsDirectory + "/fatal.log"


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


def log(log):
    try:
        global logs
        logs.insert(len(logs), log)
        if len(logs) > 5:
            logs.pop(0)
    except Exception as e:
        sys.print_exception(e)


def logInfo(info):
    try:
        print("INFO:", info)
        log(info)
    except Exception as e:
        sys.print_exception(e)


def logWarn(warn):
    try:
        print("WARN:", end=" ")
        sys.print_exception(warn)
        log(warn)
        logsToFile(warnFilename)
        addErrorToQueue(warn, 'warn')
    except Exception as e:
        sys.print_exception(e)


def logError(error):
    try:
        print("ERROR:", end=" ")
        sys.print_exception(error)
        log(error)
        logsToFile(errorFilename)
        addErrorToQueue(error, 'error')
    except Exception as e:
        sys.print_exception(e)


def logFatal(fatal):
    try:
        print("FATAL:", end=" ")
        sys.print_exception(fatal)
        log(fatal)
        logsToFile(fatalFilename)
        addErrorToQueue(fatal, 'fatal')
        uasyncio.sleep(1)
        machine.reset()
    except Exception as e:
        sys.print_exception(e)


def formatTime(t):
    return str(t[0])+"/"+str(t[1])+"/"+str(t[2])+" "+str(t[4])+":"+str(t[5])+":"+str(t[6])


def logsToFile(filename):
    if os.stat(filename)[6] > 50000:
        os.remove(filename)
    with open(filename, "a") as f:
        for log in logs:
            sys.print_exception(log, f)
        f.write("Time: " + formatTime(machine.RTC().datetime()) + '\n')
        f.write("___\n")
        f.close()


def addErrorToQueue(error, level):
    msg = {
        'method': 'addLog',
        'time': epoc.getTime(),
        'data': json.dumps({'level': level, 'error': str(error)})
    }
    messenger.msgQueue.append(msg)


createLogFiles()
