import json
import pickle
from dijkstar import Graph
from graph_class import Node, Internal_Graph
import os

abstract_graph_path = "full_pipeline_files_test/abstract_graph.pickle"
graph_storage_dir = "full_pipeline_files_test/graph_storage"
reduced_res_png_dir = "full_pipeline_files_test/graph_creation_reduced_res_png"


def main():
    # need to read in abstract graph
    with open(abstract_graph_path, 'rb') as f:
        abstract_graph = pickle.load(f)
    #print(abstract_graph)
    # instantiate a super graph
    super_graph = abstract_graph
    scaling_factors = {}
    with open(reduced_res_png_dir + '/scaling_factors.json', 'r') as out:
            scaling_factors = json.load(out)
    # read in every graph in graph storage
    for i,graph in enumerate(os.listdir(graph_storage_dir)):
        graph_name = graph[:-13]
        if(graph_name + ".png" not in os.listdir(reduced_res_png_dir)):
            continue
        (building,floor) = graph_name.split("_")
        if (floor[0] == 'D'):
            floor = int(floor[1:]) + 20
        elif (floor[0] == 'G'):
            floor = int(floor[1:]) + 40
        floor = int(floor)
        print(building,floor)
        graph = pickle.load(open((graph_storage_dir + '/' + graph), 'rb'))
        # connect it to the super graph
        # to do this, we need to get the scaling factors to determine which 
        # pixel to connect to each node in the graph
        scaling_factor = scaling_factors[graph_name + ".png"]
        # we also need to identify which building the pixels correspond to 
        # in the supergraph
        # create a node object out of each 
        pixels = graph.get_data()
        for pixel in pixels:
            p = Node(building, floor, "pixel", pixel,0)
            super_graph.add_node(p)
            print(p)
        for pixel in super_graph.get_data():
            if (pixel.type != 'pixel'):
                continue
            neighbors = graph.get_node(pixel)

        #print(pixels)

if __name__ == '__main__':
    main()