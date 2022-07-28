from png_helper_methods import *
from graph_helper_methods import *


def preprocess_via_threshold(image, threshold=4):
    """
    DEPRECATED!!!!!!

    Given an image, returns a set of pixels that 
    are not within "threshold" pixels of darker pixels
    (white pixels a good distance away from black pixels)

    This is to produce a BFS tree w/ paths that don't 
    hug against walls (to produce more realistic paths)
    """
    acceptable_pixels = set()

    for x in range(image['width']):
        for y in range(image['height']):
            new_coord = (x,y)

            if (sum(get_pixel(image, *new_coord)) > 250*3 and 
                    all(sum(get_pixel(image, *coord)) > 250*3 
                        for coord in get_radial_sweep(image, *new_coord, threshold))):
                # add in coordinate only if it itself is white
                # and all neighbors 
                # in "threshold" pixel radius are white
                acceptable_pixels.add(new_coord)

    return acceptable_pixels        



def distance_to_black(image, coord):
    """
    DEPRECATED

    Given a coordinate and image (internal rep.), 
    return the MANHATTAN distance to the 
    nearest black pixel (sum of its RGB values < 240)

    Uses BFS to search from the source coordinate until
    a black pixel is reached
    """
    agenda = [(coord, 0)] # (coordinate, distance so far)
    visited = set()

    while agenda:
        curr_node = agenda.pop(0)

        if sum(get_pixel(image, *curr_node[0])) < 3*250:
            # found a black pixel, so return its distance from 
            # the source coordinate
            return curr_node[1] 

        # if curr_node[1] >= 20:
        #     return 20

        for neighbor_coord in get_neighbors(image, *curr_node[0]):
            if neighbor_coord not in visited:
                agenda.append((neighbor_coord, curr_node[1] + 1))
                visited.add(neighbor_coord)
        
    return float("inf") # if no black pixels exist in image



def weight_func(image, coord, k):
    """
    DEPRECATED!!!!

    
    Given an image, coordinate "v", and constant k,
    w(u, v) = k/d^2

    k = parameter to toggle (higher k --> less tolerance
        for pixels closer to black pixels or image strokes)
    d = distance of v from nearest black pixel
    """
    return k*(1/((distance_to_black(image, coord))**2))



def preprocessing_via_graph_creation(image, k=1000):
    """
    DEPRECATED!!!!

    
    Given an image, return a weighted directed graph as such:
    Nodes
    - Pixel coordinates

    Edges
    - (coord1, coord2)
    - Weighted by weight function above

    Graph in the form of adjacency set
    
    k = parameter to toggle (higher k --> less tolerance
    for pixels closer to black pixels or image strokes)
    """
    graph = Graph() 
    
    for x in range(image['width']):
        for y in range(image['height']):
            u = (x, y)

            for v in get_white_neighbors(image, *u):
                # add edge (u, v) to graph w/ w(u, v) as weight
                edge_weight = weight_func(image, v, k) 
                graph.add_edge(u, v, edge_weight)

    return graph



def Dijkstar_shortest_path(graph, start, end):
    """
    DEPRECATED!!!!
    
    Returns nodes (pixel coordinates) comprising
    shortest path from start --> end
    """
    nodes, edges, costs, total_cost = find_path(graph, start, end)
    return nodes



def conversion_to_real_paths(svg_file):
    paths, attributes, svg_attributes = svg2paths2(svg_file)

    dict_length_to_paths = {}

    for path,attribute in zip(paths,attributes):
        if path == Path():
            continue
        real_path = get_real_path(path,attribute)
        curved_length = real_path.length()

        if curved_length not in dict_length_to_paths:
            dict_length_to_paths[curved_length] = [(real_path,path,attribute)]
        else:
            dict_length_to_paths[curved_length].append((real_path,path,attribute))

    return dict_length_to_paths, svg_attributes