import pickle
from dijkstar import Graph

class Node():
    def __init__(self, building, floor, type, coordinates = None, id = None, connection = None):
        self.building = building # stored as a string
        self.floor = floor # stored as a int
        self.type = type # string
        self.coordinates = coordinates
        self.id = id
        self.connection = connection
    def check_condition_ea_sa(self, node2):
        return (self.building == node2.building
            and self.id == node2.id
            and abs(self.floor%10 - node2.floor%10) == 1
            and self.type == node2.type)
    def check_condition_eh_sh(self, node2):
        return (self.building == node2.building
            and self.id == node2.id
            and self.floor == node2.floor)
    def check_condition_ee(self, node2):
        if "G" in str(self.connection[1]): self.connection[1] = int(self.connection[1][1:]) + 20
        if "D" in str(self.connection[1]): self.connection[1] = int(self.connection[1][1:]) + 40
        return  (str(self.connection[0]) == str(node2.building)
            and str(self.connection[1]) == str(node2.floor)
            and str(node2.connection[0]) == str(self.building)
            and str(node2.connection[1]) == str(self.floor)
            and (self.id == node2.id or node2.id == '99' or self.id == '99')) or  (node2.building == self.building and node2.floor == self.floor)
    def check_condition_ee_sh_eh(self, node2):
        return  ((node2.building == self.building and node2.floor == self.floor)
            and (self.type == 'eh' or self.type == 'sh' or node2.type == 'sh' or node2.type == 'sh'))
  
    def __str__(self):
        return str(["building " + self.building, "floor " + str(self.floor), "type " + self.type,"id " + str(self.id), "connections " + str(self.connection)])

    
class Internal_Graph():
    def __init__(self, nodes = {}):
        self.nodes = nodes # dictionary of nodes, with values being lists of their neighbors
        self.graph = Graph()
    def __str__(self):
        s = ''
        for node in self.nodes:
            s += str(node) +  ": " +  str( [str(node1) for node1 in self.nodes[node]] ) +'\n' + '\n' + '\n' + '\n' + '\n' + '\n'
        return s
    def save_to_file(self,name):
        with open(name, 'wb') as f:
            pickle.dump(self,f)
    def convert_to_djikstar(self, file_name):
        graph = Graph(undirected = True)
        for node in self.nodes:
            for node_neighbor in self.nodes[node]:
                if node.type == 'supernode' or node_neighbor.type == 'supernode':
                    graph.add_edge(node,node_neighbor,100)
                else: graph.add_edge(node,node_neighbor,1)
        with open(file_name, 'wb') as f:
            pickle.dump(graph,f)
