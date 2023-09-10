import json
import uasyncio
import modulesHandler
import logger


def get_values(raw_values, previous_states, current_states):
    values = []
    for raw_value in raw_values:
        if raw_value['type'] == 'fixed':
            values.append(raw_value['value'])
        elif raw_value['type'] == 'previous':
            values.append(
                previous_states[raw_value['moduleId']][raw_value['index']])
        elif raw_value['type'] == 'current':
            values.append(
                current_states[raw_value['moduleId']][raw_value['index']])
    return values


def check_conditions(conditions, previous_states, current_states):
    for condition in conditions:
        values = get_values(condition['values'],
                            previous_states, current_states)
        if condition['operator'] == '=':
            if values[0] != values[1]:
                return False
        elif condition['operator'] == '!=':
            if values[0] == values[1]:
                return False
        else:
            return False
    return True


def execute_action(actions, current_states):
    for action in actions:
        if action['type'] == 'updateState':
            module_id = action['moduleId']
            index = action['index']
            newValue = action['value']
            if newValue != current_states[module_id][index]:
                logger.logInfo("Automation triggered for %s" % module_id)
                new_state = json.dumps({index: newValue})
                msg = json.dumps(
                    {'module_id': module_id, 'new_state': new_state})
                modulesHandler.updateState(msg)


# Return true if states are the same
def compare_states(first_state, second_state):
    for module in first_state:
        if type(first_state) == list and type(second_state) == list:
            for key in first_state[module]:
                if str(first_state[module][key]) != str(second_state[module][key]):
                    return False
        else:
            if first_state != second_state:
                return False
    return True


async def loopAuto(automations, current_states):
    previous_states = json.loads(json.dumps(current_states))
    while True:
        try:
            await uasyncio.sleep(0.01)
            if compare_states(current_states, previous_states) == False:
                for automation in automations:
                    result = check_conditions(
                        automation['conditions'], previous_states, current_states)
                    if result == True:
                        execute_action(automation['actions'], current_states)
                # .copy() do not work for create a deepcopy because the value of the
                # states are dictionaries (mutable types), so they act as 'pointers'
                previous_states = json.loads(json.dumps(current_states))
        except Exception as e:
            logger.logFatal(e)
