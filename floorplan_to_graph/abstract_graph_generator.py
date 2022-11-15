import json
from graph_class import Node, Internal_Graph

abstract_graph = "full_pipeline_files_test/special_feature_coordinates.json"

def main():
    # read in special features
    with open( abstract_graph, 'r') as out:
        special_features = json.load(out)
    graph = Internal_Graph()
    # create all nodes
        # iterate through all the special features names
    for building_floor in special_features:
        for type in special_features[building_floor][building_floor]:
            # iterate through types
            for coords in special_features[building_floor][building_floor][type]:
                # iterate through coordinates/ids
                building,floor = building_floor.split('_')
                if (floor[0] == 'D'):
                    floor = int(floor[1:]) + 20
                elif (floor[0] == 'G'):
                    floor = int(floor[1:]) + 40
                floor = int(floor)
                coordinates = coords[:2]
                id = coords[-1]
                connection = None
                if (type == 'ee'):
                    connection = coords[2:4]
                node = Node(building, floor, type, coordinates, id, connection)
                graph.nodes[node] = []
                # create node object and add it to graph, with value as []
    outside = Node('0', 0, 'ee', [69,69], '99', connection)
    graph.nodes[outside]= []
    for node1 in graph.nodes:
        for node2 in graph.nodes:
            if node1 == node2:
                continue
            if node2 in graph.nodes[node1]:
                continue
            if (node1.type == 'ea'):
                if (node2.type == 'ea'):
                    if (node1.check_condition_ea_sa(node2)):
                        graph.nodes[node1].append(node2)
                        graph.nodes[node2].append(node1)
                if (node2.type == 'eh'):
                    if (node1.check_condition_eh_sh(node2)):
                        graph.nodes[node1].append(node2)
                        graph.nodes[node2].append(node1)
            
            if (node1.type == 'sa'):
                if (node2.type == 'sa'):
                    if (node1.check_condition_ea_sa(node2)):
                        graph.nodes[node1].append(node2)
                        graph.nodes[node2].append(node1)
                if (node2.type == 'sh'):
                    if (node1.check_condition_eh_sh(node2)):
                        graph.nodes[node1].append(node2)
                        graph.nodes[node2].append(node1)
            
            if (node1.type == 'ee' and node2.type == 'ee'):
                    if (node1.check_condition_ee(node2)):
                        graph.nodes[node1].append(node2)
                        graph.nodes[node2].append(node1)
            
            if (node1.type == 'ee' or node2.type == 'ee'):
                    if (node1.check_condition_ee_sh_eh(node2)):
                        graph.nodes[node1].append(node2)
                        graph.nodes[node2].append(node1)
    

    supernodes = []
    nodes = graph.nodes.copy()
    for node in nodes:
        if [node.building, node.floor] not in supernodes:
            supernode = Node(node.building, node.floor, "supernode")
            graph.nodes[supernode] = []
            supernodes.append([node.building, node.floor])

    for supernode in graph.nodes:
        if supernode.type != 'supernode':
            continue
        for node2 in graph.nodes:
            if (node2.type != 'supernode' and node2.building == supernode.building and node2.floor == supernode.floor):
                if (node2.type != 'ea' and node2.type != 'sa'):
                    graph.nodes[supernode].append(node2)
                    graph.nodes[node2].append(supernode)
    
    for node in graph.nodes:
        if node.building == '1' or node.building == '3' or node.building == '10':
            if node.floor == 1 and node.type == 'ee' or node.type== 'supernode':
                print(node, [str(n) for n in graph.nodes[node]])
            print()
    

    # convert to djikstar

    graph.convert_to_djikstar("full_pipeline_files_test/abstract_graph.pickle")


    # create all edges
        #iterate through all nodes
            #iterate through all nodes
                # continue if node 1 is already in node 2 adjacency list
                # check the type of node 1
                # if the type is ea or sa
                    # connect to corresponding eh & sh
                    # check type of node 2 and check that all other attributes are same
                    # add node1 to node 2 adjacency list & vice versa
                # if the type is ea or sa
                    # connect to ea/sa +-1
                    # check that eveyrthing is same except floor is +-1
                    # add node1 to node 2 adjacency list & vice versa
                # if type is ee
                    # Check that building, floor, id, and type of node2 is the connection of node 1 or if id is 99
                        # add node1 to node 2 adjacency list & vice versa 

                
    # output pickle file

if __name__ == '__main__':
    main()