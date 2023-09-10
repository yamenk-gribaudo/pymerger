# pylint: disable=no-member
# pylint: disable=too-complex
# pylint: disable=too-many-nested-blocks
import ast
import re
from glob import glob
import json
import astunparse
from .file_parser import parse
from .circular_dependencies import find_circular_dependencies

SUCCESS = '\033[32m'
WARNING = '\033[33m'
ENDC = '\033[0m'


def get_file_paths(args):
    if not isinstance(args, list):
        print("\n" + WARNING + "Input must be a list rather than a string" + ENDC)
        return []
    file_paths = set()
    for arg in args:
        for file in glob(arg, recursive=True):
            if file.split(".")[len(file.split("."))-1] == 'py':
                file_paths.add(file)
    return sorted(list(file_paths))


def handle_from_import_dependencies(parsed_files):
    for file in parsed_files:
        for import_ in file['from_imports']:
            for node in file['nodes']:
                for parsed_file in parsed_files:
                    if import_['module'] == parsed_file['name']:
                        if import_['asname'] == "*":
                            for other_file_definition in parsed_file['definitions']:
                                for node_dependency in node['dependencies']:
                                    if other_file_definition == node_dependency and node_dependency not in file['definitions']:
                                        node['dependencies'].remove(
                                            node_dependency)
                                        node['dependencies'].add(
                                            parsed_file['name'] + "." + node_dependency)
                        elif import_['asname'] in node['dependencies']:
                            string = astunparse.unparse(node['node'])
                            regex = "(?<![a-zA-Z0-9_.])" + \
                                import_['asname'] + "(?![a-zA-Z0-9_])"
                            node['node'] = ast.parse(
                                re.sub(regex, import_['name'], string))
                            for dependency in node['dependencies']:
                                if dependency == import_['asname']:
                                    node['dependencies'].remove(dependency)
                                    node['dependencies'].add(
                                        import_['module'] + "." + import_['name'])


def handle_imports_from_other_files(parsed_files):
    for file in parsed_files:
        for file2 in parsed_files:
            if file['filepath'] != file2['filepath']:
                for import_ in file['imports']:
                    if import_['name'] == file2['name']:
                        for node in file['nodes']:
                            accumulator = set()
                            for dependency in node['dependencies']:
                                if dependency == import_['asname']:
                                    for imported_definition in file2['definitions']:
                                        string = astunparse.unparse(
                                            node['node'])
                                        regex = "(?<![a-zA-Z_.])" + import_['asname'] + \
                                            "." + imported_definition + \
                                                "(?![a-zA-Z_])"
                                        result = re.search(regex, string)
                                        if result:
                                            node['node'] = ast.parse(
                                                re.sub(regex, imported_definition, string))
                                            for dep in node['dependencies']:
                                                if dep == import_['asname']:
                                                    accumulator.add(
                                                        import_['name'] + "." + imported_definition)
                            node['dependencies'] = node['dependencies'].union(
                                accumulator)
                            if import_['asname'] in node['dependencies']:
                                node['dependencies'].remove(import_['asname'])


def replace_dependencies_from_same_file(parsed_files):
    for file in parsed_files:
        for node in file['nodes']:
            for dependency in node['dependencies']:
                if len(dependency.split('.')) == 1:
                    node['dependencies'].remove(dependency)
                    node['dependencies'].add(file['name'] + "." + dependency)
            for definition in node['definitions']:
                if len(definition.split('.')) == 1:
                    node['definitions'].remove(definition)
                    node['definitions'].add(file['name'] + "." + definition)


def add_imports(nodes, parsed_files):
    final_string = ""
    used_blocks = set()
    removed_nodes = []
    from_future_import_node = ast.ImportFrom()
    setattr(from_future_import_node, 'module', '__future__')
    setattr(from_future_import_node, 'names', [])
    setattr(from_future_import_node, 'level', 0)
    from_import_string = ""
    import_node = ast.Import()
    setattr(import_node, 'names', [])
    for node in nodes:
        if isinstance(node['node'], ast.ImportFrom):
            removed_nodes.append(node)
            should_add_node = True
            for parsed_file in parsed_files:
                if parsed_file['name'] == node['node'].module:
                    should_add_node = False
            if should_add_node:
                if node['node'].module == "__future__":
                    for name in node['node'].names:
                        name_already_in = False
                        for name_in_import_node in from_future_import_node.names:
                            if name.name == name_in_import_node.name and name.asname == name_in_import_node.asname:
                                name_already_in = True
                        if not name_already_in:
                            from_future_import_node.names.append(name)
                else:
                    string = astunparse.unparse(node['node']).strip()
                    if string not in used_blocks:
                        used_blocks.add(string)
                        from_import_string += string + "\n"
        if isinstance(node['node'], ast.Import):
            removed_nodes.append(node)
            import_nodes_to_be_removed = []
            for name in node['node'].names:
                for parsed_file in parsed_files:
                    if parsed_file['name'] == name.name:
                        import_nodes_to_be_removed.append(name)
            for import_node_to_be_removed in import_nodes_to_be_removed:
                node['node'].names.remove(import_node_to_be_removed)
            if len(node['node'].names) > 0:
                for name in node['node'].names:
                    name_already_in = False
                    for name_in_import_node in import_node.names:
                        if name.name == name_in_import_node.name and name.asname == name_in_import_node.asname:
                            name_already_in = True
                    if not name_already_in:
                        import_node.names.append(name)
    if len(from_future_import_node.names) > 0:
        final_string += astunparse.unparse(
            from_future_import_node).strip() + "\n"
    final_string += from_import_string
    if len(import_node.names) > 0:
        final_string += astunparse.unparse(import_node).strip() + "\n"
    for node in removed_nodes:
        nodes.remove(node)
    return final_string


def get_main_block(nodes):
    removed_nodes = []
    main_block = ast.If()
    setattr(main_block, 'test', None)
    setattr(main_block, 'body', [])
    setattr(main_block, 'orelse', None)
    for node in nodes:
        if isinstance(node['node'], ast.If):
            if astunparse.unparse(node['node'].test).strip() == "(__name__ == '__main__')":
                if main_block.test is None:
                    main_block.test = node['node'].test
                removed_nodes.append(node)
                main_block.body += node['node'].body
    for node in removed_nodes:
        nodes.remove(node)
    return main_block if len(main_block.body) > 0 else None


def nodes_to_string(nodes):
    final_string = ""
    removed_nodes = []
    used_blocks = set()
    last_nodes_len = len(nodes)
    while True:
        # Check if a all dependencies of a blocked and stisfied (not in any definition), and,
        # in that case, add it to the final string and remove the node from the nodes to be merged
        for node in nodes:
            depedencies_stisfied = True
            for dependency in node['dependencies']:
                for node2 in nodes:
                    if dependency in node2['definitions']:
                        depedencies_stisfied = False
            if depedencies_stisfied:
                string = astunparse.unparse(node['node']).strip()
                removed_nodes.append(node)
                if string not in used_blocks:
                    used_blocks.add(string)
                    final_string += string + "\n"
        for node in removed_nodes:
            nodes.remove(node)
        removed_nodes = []
        if len(nodes) == last_nodes_len:
            break
        last_nodes_len = len(nodes)
    return final_string


def problematic_nodes_to_string(nodes):
    final_string = ""
    removed_nodes = []
    used_blocks = set()
    if len(nodes) > 0:
        circular_dependencies_object = []
        for node in nodes:
            for dependency in node['definitions']:
                circular_dependencies_object.append(
                    {'parents': [dependency], 'dependencies': list(node['dependencies'])})
        print(WARNING + "\n" + "CIRCULAR DEPENDENCIES: There are circular dependencies in some of the blocks to be merged, the first one is:\n" +
              "   - " + " -> ".join(find_circular_dependencies(circular_dependencies_object)) + ENDC)
        # Merge block with circular dependencies anyway
        for node in nodes:
            if node not in removed_nodes:
                string = astunparse.unparse(node['node']).strip()
                if string not in used_blocks:
                    used_blocks.add(string)
                    final_string += string + "\n"
    return final_string


def check_collitions(nodes):
    collitions = set()
    for node in nodes:
        for node2 in nodes:
            for definition in node['definitions']:
                for definition2 in node2['definitions']:
                    if (definition.split(".")[0] != definition2.split(".")[0]) and (definition.split(".")[1] == definition2.split(".")[1]):
                        collitions.add(json.dumps(
                            sorted((definition, definition2))))
    if len(collitions) > 0:
        print(WARNING + "\n" + "DEFINITION COLLITIONS: There are definition collitions in your files, you should change the naem of the conflicting definitions:" + ENDC)
        for raw_collition in collitions:
            collition = json.loads(raw_collition)
            first_module = collition[0].split(".")[0]
            second_module = collition[1].split(".")[0]
            collition_name = collition[0].split(".")[1]
            print(WARNING + "   - '" + collition_name + "' is used as definition name by " +
                  first_module + " and " + second_module + ENDC)


def merge(raw_filepaths, output=None):
    file_paths = get_file_paths(raw_filepaths)
    if len(file_paths) == 0:
        print(WARNING + "No python files to be merged" + ENDC)
        return ""

    # Parse files
    parsed_files = []
    for file_path in file_paths:
        parsed_files.append(parse(file_path))

    # Replace dependencies from 'from X import Y'
    handle_from_import_dependencies(parsed_files)

    # Replace dependencies from other files: <dependency> -> <imported_name>.<dependency>
    handle_imports_from_other_files(parsed_files)

    # Replace dependencies from same file: <dependency> -> <name>.<dependency>
    replace_dependencies_from_same_file(parsed_files)

    # Combine all nodes
    nodes = []
    for file in parsed_files:
        for node in file['nodes']:
            nodes.append(node)

    # Extract main blocks to merge them and put them at the end
    main_block = get_main_block(nodes)

    # Add imports to final_string
    final_string = add_imports(nodes, parsed_files)

    # Check collitions
    check_collitions(nodes)

    # Add everything else to final_string
    final_string += nodes_to_string(nodes)

    # Add problematic nodes to final string
    final_string += problematic_nodes_to_string(nodes)

    # Add main block
    if main_block is not None:
        final_string += astunparse.unparse(main_block).strip() + "\n"

    if final_string != "":
        if output is not None:
            with open(output, "w", encoding='UTF-8') as file:
                file.write(final_string)
                file.close()
                print("\n" + SUCCESS +
                      "MERGED!!! Output was saved in " + output + ENDC)
    else:
        print("\n" + WARNING + "Output string is null" + ENDC)

    return final_string
