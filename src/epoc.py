import time
import uasyncio
import ntptime
import bw
import logger
import sys

timeIsSet = False
startTime = time.time_ns()
finishTime = 0


def getTime():
    try:
        # 946684800000 is miliseconds from 1/1/1970 to 1/1/2000
        # ntptime gives epoc2000 instead of epoc1970
        if timeIsSet:
            return (time.time_ns()//1000000) + 946684800000
        else:
            # if time is not set => add miliseconds from boot and asign that to msg time,
            # then, once time is set, we can do the math to get the correct time
            response = (time.time_ns() - startTime) // (-1000000)
            return response
    except Exception as e:
        logger.logError(e)


def log(log):
    print(log)


async def loopEpoc():
    global timeIsSet
    global finishTime
    n = 0
    while True:
        try:
            await uasyncio.sleep(0.1)
            if timeIsSet is True:
                break
            if bw.internetIsConnected is True:
                n = n + 1
                finishTime = (time.time_ns() - startTime) // 1000000
                ntptime.settime()
                timeIsSet = True
                logger.logInfo("Time is set")
        except Exception as e:
            if n < 4:
                logger.logError(e)
            else:
                logger.logFatal(e)


uasyncio.create_task(loopEpoc())

if __name__ == "__main__":
    var2 = "hello2"
    print(var2 + timeIsSet)
