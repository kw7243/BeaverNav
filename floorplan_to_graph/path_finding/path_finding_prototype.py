from ../png_helper_methods import *
from graph_helper_methods import *

########################
#   PREPROCESSING      #
########################

def distances_to_black(image):
    """
    Given an image (internal rep.),
    return the shortest distance of 
    every white pixel to the nearest black pixel

    Runs a BFS w/ every black pixel as the source node
    """
    distances = {} # (x, y) --> distance to black pixel
    visited = set()

    q = deque([])
    for x in range(image['width']):
        for y in range(image['height']):
            if sum(get_pixel(image, x, y)) < 3*250: # if black pixel
                distances[(x, y)] = 0 
                q.append((x, y)) # add black pixels into q
    
    while q:
        coord = q.popleft()

        for neighbor_coord in get_white_neighbors(image, *coord):
            if neighbor_coord not in visited:
                distances[neighbor_coord] = distances[coord] + 1
                q.append(neighbor_coord)
                visited.add(neighbor_coord)
    
    return distances


def preprocessing_via_duplicate_graph(image, k=1000):
    """
    Given internal rep. of an image, 
    returns a graph w/ 2 layers described as follows:

    For every coordinate u in image, we define
    
    Nodes
    u_horizontal - arriving at coordinate u via 
    left-right neighbor

    u_vertical - arriving at coordinate u via 
    up-down neighbor

    Node ex. --> ((2, 5), "horizontal")


    Edges
    (u_horiz, v_horiz) = k/d^2
    (u_vert, v_vert) = k/d^2
    where d = distance of v (horiz and vert respectively)
    from the nearest black pixel

    (u_vert, v_horiz) = (u_horiz, v_vert) = k
    This is to discourage "turns." 
    (ex. an optimal horizontal path leading to 
    node u_horiz should continue along a horizontal
    path rather than turn up-down)
    """
    graph = Graph()
    distances = distances_to_black(image) # stores pixel distances of white coords to nearest black pixel

    for x in range(image['width']):
        for y in range(image['height']):
            
            if sum(get_pixel(image, x, y)) < 250*3:
                continue

            u = (x, y)
            for v_horizontal in get_left_right_neighbors(image, *u):
                # w(u_horiz, v_horiz) = k/d^2
                edge_weight = k*1/(distances[v_horizontal])**2
                graph.add_edge((u, 'horizontal'), (v_horizontal, 'horizontal'), edge_weight)

                # w(u_vert, v_horiz) = k
                edge_weight = k
                graph.add_edge((u,'vertical'), (v_horizontal,'horizontal'), edge_weight)
                
            for v_vertical in get_up_down_neighbors(image, *u):
                # w(u_vert, v_vert) = k/d^2
                edge_weight = k* 1/(distances[v_vertical])**2
                graph.add_edge((u, 'vertical'), (v_vertical, 'vertical'), edge_weight)

                # w(u_horiz, v_vert) = k
                edge_weight = k
                graph.add_edge((u,'horizontal'), (v_vertical,'vertical'), edge_weight)
            
    return graph


########################
#       Dijkstar       #
########################

def Dijkstar_duplicated_graph(duplicated_graph, start, end):
    """
    Given a duplicated graph and start and end
    coordinates, return the shortest path 
    among ALL paths between the possible
    node states of the duplicated graph
    """
    start_A = (start, 'horizontal')
    start_B = (start, 'vertical')
    end_A = (end, 'horizontal')
    end_B = (end, 'vertical')

    path_info = [find_path(duplicated_graph, start, end) 
                    for start in [start_A, start_B] 
                        for end in [end_A, end_B]]
    
    # From list of paths' info, return the nodes
    # comprising the path w/ the lowest cost
    nodes, edges, costs, total_cost = min(path_info, key = lambda x: x[3])
    return nodes

