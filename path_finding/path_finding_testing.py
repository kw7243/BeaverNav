import time
import pickle
from path_finding_prototype import *
from deprecated_methods import distance_to_black

########################
#        TESTING       #
########################

def ask_for_coords():
    """
    Appends user-given coordinates to list
    and returns it
    """
    coords = []
    user = ""
    while user != "done":
        user = input("Type in coordinates (ex. 120 150): ")
        try:
            coord = tuple(int(num) for num in user.split())
            coords.append(coord)
        except ValueError as e:
            pass
    
    return coords


def test_crop_and_reduce(DIRECTORY, floor_plan, reduction_factor=16):
    original_filename = f"../nontext_PNG_floor_plans/{floor_plan}.png"
    cropped_filename = f"{DIRECTORY}/{floor_plan}_cropped.png"
    reduced_filename = f"{DIRECTORY}/{floor_plan}_reduced.png"

    try: # in case already cropped and reduced already
        return load_color_image(reduced_filename)

    except FileNotFoundError as e:
        start = time.perf_counter()
        cropped = crop_image(original_filename, cropped_filename)
        end_crop = time.perf_counter()
        print(f"Crop time: {end_crop - start}")

        reduced = reduce_resolution(cropped, reduced_filename, reduction_factor)
        end_reduce = time.perf_counter()
        print(f"Reduce time: {end_reduce - end_crop}")
        print(f"Total time: {end_reduce - start}")
        return reduced  


def test_duplicate_graph(DIRECTORY, floor_plan, reduced_im):
    print("\nCREATING GRAPH...")
    start = time.perf_counter()
    graph = preprocessing_via_duplicate_graph(reduced_im, 25)
    print("FINISHED GRAPH CREATION...")
    print(f"Duplicate graph creation: {time.perf_counter() - start}")

    # Save graph to pickle file
    with open(f"{DIRECTORY}/{floor_plan}_graph.pickle", "wb") as f:
        pickle.dump(graph, f)
    
    return graph


def test_path_finding(DIRECTORY, floor_plan, graph, start, end, reduction_factor=16):
    """
    Given a graph, a start and end coordinate on the UNALTERED IMAGE,
    return an image w/ the shortest path drawn between start and end
    """
    start_reduced = (start[0]//reduction_factor, start[1]//reduction_factor)
    end_reduced = (end[0]//reduction_factor, end[1]//reduction_factor)

    # Get path
    t_start = time.perf_counter()
    path_low_res = Dijkstar_duplicated_graph(graph, start_reduced, end_reduced)
    t_find_path = time.perf_counter()
    print(f"Dijkstar find_path (duplicated graph) time: {t_find_path - t_start}")

    path_high_res = expand_coords(path_low_res, reduction_factor)
    t_expand_coords = time.perf_counter()
    print(f"Expanding coords time: {t_expand_coords - t_find_path}")

    # Draw path onto CROPPED image
    cropped_filename = f"{DIRECTORY}/{floor_plan}_cropped.png"
    new_filename = f"{DIRECTORY}/{floor_plan}_{start}_{end}_path.png"

    save_image_with_path_drawn(cropped_filename, new_filename, path_high_res)
    print(f"Draw path time: {time.perf_counter() - t_expand_coords}")

    print(f"User interface time: {time.perf_counter() - t_start}")


def test_full(DIRECTORY, floor_plan, reduction_factor=16):
    """
    Given a floor plan, reduction factor,
    and its directory w.r.t. path_finding, runs a full test:

    1. Crop and reduce image
    2. Ask user for start and end coordinates
    3. Create graph if doesn't already exist
    4. Draw the shortest path between the start and end coords.
    """
    reduced = test_crop_and_reduce(DIRECTORY, floor_plan, reduction_factor)

    print("\nEnter start coordinates")
    start_coords = ask_for_coords()
    print("\nEnter end coordinates")
    end_coords = ask_for_coords()

    try:
        with open(f"{DIRECTORY}/{floor_plan}_graph.pickle", "rb") as f:
            graph = pickle.load(f)
    except FileNotFoundError as e:
        graph = test_duplicate_graph(DIRECTORY, floor_plan, reduced)

    for start, end in zip(start_coords, end_coords):
        test_path_finding(DIRECTORY, floor_plan, graph, start, end, reduction_factor)


def test():
    floor_plan = input("Floor plan? (ex. 1_2): ")
    DIRECTORY = f"tests/{floor_plan}_test"
    reduction_factor = int(input("Reduction factor?: "))

    ### DO WHATEVER TESTS YOU NEED STARTING HERE ###
    test_full(DIRECTORY, floor_plan, reduction_factor)
    # reduced = test_crop_and_reduce(DIRECTORY, floor_plan, reduction_factor)

    # with open(f"{DIRECTORY}/{floor_plan}_before_distances.pickle", "rb") as f:
    #     before = pickle.load(f)

    # with open(f"{DIRECTORY}/{floor_plan}_after_distances.pickle", "rb") as f:
    #     after = pickle.load(f)
    
    # save_image_with_path_drawn(f"{DIRECTORY}/{floor_plan}_cropped.png", f"{DIRECTORY}/{floor_plan}_distances.png", expand_coords(after.keys()))

if __name__ == "__main__":
    test()