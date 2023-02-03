from create_file_paths import *
import json

def main():
    with open(outdoor_coordinates, 'r') as f:
        outdoor_nodes = json.load(f)
    
    with open(special_features, 'r') as f:
        abstract_graph_nodes = json.load(f)

    abstract_graph_nodes["0_0"] = {}
    abstract_graph_nodes["0_0"]["0_0"] = {}
    abstract_graph_nodes["0_0"]["0_0"]["ea"] = []
    abstract_graph_nodes["0_0"]["0_0"]["sa"] = []
    abstract_graph_nodes["0_0"]["0_0"]["eh"] = []
    abstract_graph_nodes["0_0"]["0_0"]["sh"] = []
    abstract_graph_nodes["0_0"]["0_0"]["ee"] = []

    for building_floor in outdoor_nodes:
        building = int(building_floor.split('_')[0])
        floor = int(building_floor.split('_')[1])
        for door in outdoor_nodes[building_floor]:
            coords = outdoor_nodes[building_floor][door]
            id = int(door)
            abstract_graph_nodes["0_0"]["0_0"]["ee"].append([coords[0], coords[1], building,floor,id])
    

    with open(special_features, 'w') as f:
       json.dump(abstract_graph_nodes, f, indent=5)

if __name__ == "__main__":
    main()