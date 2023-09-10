import logger
import epoc
import json
import bw as bwe
import modulesHandler
import uasyncio

messengerReady = False
msgQueue = []


def addState(msg):
    try:
        if(len(msgQueue) <= 50):
            msg['method'] = "addState"
            msgQueue.append(msg)
        else:
            logger.logWarn(
                "State not added to queue, len(msgQueue) > 50")
    except Exception as e:
        logger.logError(e)


def sendFirstMessageInQueue():
    try:
        if(len(msgQueue) > 0):
            msg = msgQueue.pop(0)
            # if time was defined before epoc time is set => do the math to get the correct msg time
            if 'time' in msg and msg['time'] < 0:
                msg['time'] = epoc.getTime() - epoc.finishTime - msg['time']
            # modules['mqtt'].sendMessage( json.dumps(msg))
            uasyncio.create_task(bwe.modules['ws'].sendMessage(json.dumps(msg)))
    except Exception as e:
        logger.logError(e)


def addFirstMessage():
    device = modulesHandler.getDevice()
    msg = msg = {'method': 'addDevice',
                 'time': epoc.getTime(), 'data': json.dumps(device)}
    msgQueue.append(msg)


async def startSender():
    while True:
        await uasyncio.sleep(0.1)
        # Send first message in queue
        if messengerReady == True:
            sendFirstMessageInQueue()
