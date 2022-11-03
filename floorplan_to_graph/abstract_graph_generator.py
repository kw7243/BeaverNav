import json

abstract_graph = "full_pipeline_files_test/special_feature_coordinates.json"

class Node():
    def __init__(self, building, floor, type, coordinates, id, connection = None):
        self.building = building
        self.floor = floor
        self.type = type
        self.coordinates = coordinates
        self.id = id
        self.connection = connection
    def check_condition_ea_sa(self, node2):
        return (self.building == node2.building
            and self.id == node2.id
            and abs(self.floor - node2.floor) == 1
            and self.type == node2.type)
    def check_condition_eh_sh(self, node2):
        return (self.building == node2.building
            and self.id == node2.id
            and self.floor == node2.floor)
    def check_condition_ee(self, node2):
        return  (str(self.connection[0]) == str(node2.building)
            and str(self.connection[1]) == str(node2.floor)
            and str(node2.connection[0]) == str(self.building)
            and str(node2.connection[1]) == str(self.floor)
            and (self.id == node2.id or node2.id == '99' or self.id == '99'))
    def __str__(self):
        return str(["building " + self.building, "floor " + str(self.floor), "type " + self.type,"id " + str(self.id), "connections " + str(self.connection)])

    
class Graph():
    def __init__(self, nodes = {}):
        self.nodes = nodes # dictionary of nodes, with values being lists of their neighbors
    def __str__(self):
        s = ''
        for node in self.nodes:
            s += str(node) +  ": " +  str( [str(node1) for node1 in self.nodes[node]] ) +'\n' + '\n' + '\n' + '\n' + '\n' + '\n'
        return s
def main():
    # read in special features
    with open( abstract_graph, 'r') as out:
        special_features = json.load(out)
    graph = Graph()
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
    print(graph)
    for node1 in graph.nodes:
        print("node1: ", node1.building, node1.floor)
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
    
    print(graph)
                    

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