import json


def check_format(cds):
    if isinstance(cds, list):
        for cd in cds:
            if 'parents' not in cd or 'dependencies' not in cd:
                raise TypeError(
                    "Input must be formatted as [{'parents':['a',...], 'dependencies':['b',...]},...]")


def find_dependencies(dependencies, parent):
    for dependency in dependencies:
        if dependency['parents'] == [parent]:
            return dependency["dependencies"]
    return []


def find_circular_dependencies(dependencies, objects=None, iterations=0):
    check_format(dependencies)
    check_format(objects)
    if iterations > len(dependencies):
        return []
    if not objects:
        objects = json.loads(json.dumps(dependencies))
    new_objects = []
    for object_ in objects:
        for parent in object_['parents']:
            for dependency in object_['dependencies']:
                if parent == dependency:
                    return object_['parents'] + [parent]
                new_objects.append({"parents": object_['parents'] + [
                                   dependency], 'dependencies': find_dependencies(dependencies, dependency)})
    return find_circular_dependencies(dependencies, new_objects, iterations+1)
