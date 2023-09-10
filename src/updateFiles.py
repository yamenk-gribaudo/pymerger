import json
import logger
import bw


def updateConfig(msg):
    try:
        if bw.globalConfigFilepath is None:
            logger.logError(
                "You must use a configFilepath to update the config")
        elif msg is not None:
            updateFile(bw.globalConfigFilepath, msg)
        else:
            logger.logWarn("Content is None")
    except Exception as e:
        logger.logFatal(e)


def updateFileByPath(rawMsg):
    try:
        if rawMsg is not None:
            msg = json.loads(rawMsg)
            filename = msg['filename']
            content = msg['content']
            updateFile(filename, content)
        else:
            logger.logWarn("Content is None")
    except Exception as e:
        logger.logError(e)


def updateModule(rawMsg):
    try:
        if rawMsg is not None:
            msg = json.loads(rawMsg)
            filename = 'modules/' + msg['filename']
            content = msg['content']
            updateFile(filename, content)
        else:
            logger.logWarn("Content is None")
    except Exception as e:
        logger.logError(e)


def updateBw(msg):
    try:
        if msg is not None:
            updateFile('bw.py', msg)
        else:
            logger.logWarn("Content is None")
    except Exception as e:
        logger.logFatal(e)


def updateFile(fileName, content):
    try:
        logger.logInfo("Updating file: " + fileName)
        file = open(fileName, 'w')
        file.flush()
        file.write(content)
        file.close()
        logger.logInfo("File '%s' updated" % fileName)
    except Exception as e:
        logger.logFatal(e)
