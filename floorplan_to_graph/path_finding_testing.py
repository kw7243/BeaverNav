import time
import pickle
from path_finding_prototype import *
from create_file_paths import *
#from deprecated_methods import distance_to_black

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

    try:  # in case already cropped and reduced already
        return load_color_image(reduced_filename)

    except FileNotFoundError as e:
        start = time.perf_counter()
        cropped = crop_image(original_filename, cropped_filename)
        end_crop = time.perf_counter()
        print(f"Crop time: {end_crop - start}")

        reduced = reduce_resolution(
            cropped, reduced_filename, reduction_factor)
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


def find_corners(path_low_res):
    '''
    Takes in the low resolution path (representing a list of pixels that must be traversed)
    Returns a sequence of pixels representing the CORNERS ONLY in the path
    '''

    path_low_res = [coord for coord, tag in path_low_res]

    direction = None
    corners = []

    for i in range(1, len(path_low_res)):
        curr_pixel = path_low_res[i]
        pixel_before = path_low_res[i-1]

        vertical_diff = abs(curr_pixel[0] - pixel_before[0])
        horizontal_diff = abs(curr_pixel[1] - pixel_before[1])

        if direction == 'vertical':
            if horizontal_diff == 1:
                corners.append(pixel_before)
                direction = 'horizontal'
                continue

        elif direction == 'horizontal':
            if vertical_diff == 1:
                corners.append(pixel_before)
                direction = 'vertical'
                continue

        elif direction == None:
            if vertical_diff == 1:
                direction = 'vertical'
                corners.append(pixel_before)
                continue

            elif horizontal_diff == 1:
                direction = 'horizontal'
                corners.append(pixel_before)
                continue

    # THIS WAS THE FIX!!!
    corners.append(curr_pixel)

    return corners


def map_corners_lowres_to_highres(path_low_res, r=16):
    return [(x*r, y*r)
            for (x, y) in path_low_res]


def test_path_finding(DIRECTORY, floor_plan, graph, start, end, reduction_factor=16):
    """
    Given a graph, a start and end coordinate on the UNALTERED IMAGE,
    return an image w/ the shortest path drawn between start and end
    """
    start_reduced = (int(start[0]//reduction_factor),
                     int(start[1]//reduction_factor))
    end_reduced = (int(end[0]//reduction_factor),
                   int(end[1]//reduction_factor))

    # Get path
    path_low_res = Dijkstar_duplicated_graph(graph, start_reduced, end_reduced)

    start_time_drawing = time.perf_counter()
    print("DRAWING IMAGE PROCEDURES STARTED: ")
    corners = find_corners(path_low_res)

    print("floorplan is: ",floor_plan)
    if floor_plan == '8_1':
        reduction_factor = 17
    if floor_plan == '8_3':
        reduction_factor = 16
    
    high_res_corners = map_corners_lowres_to_highres(
            corners, r=int(reduction_factor))

    cropped_filename = f"{DIRECTORY}/{floor_plan}.png"
    new_filename = f"{results_dir}/{floor_plan}_{start}_{end}_path.png"

    high_res_image = cv2.imread(cropped_filename)

    # Drawing start/end locations
    start_loc = high_res_corners[0]
    end_loc = high_res_corners[-1]

    cv2.circle(high_res_image, start_loc, 5 *
               int(reduction_factor), (255, 0, 0), -1)
    cv2.circle(high_res_image, start_loc, 5*int(reduction_factor),
               (255, 255, 255), int(1*(reduction_factor)))
    cv2.circle(high_res_image, start_loc, 5*int(reduction_factor),
               (0, 0, 0), int(0.5*(reduction_factor)))

    rows, cols = high_res_image.shape[:2]
    print((int(0.05*rows), int(0.95*cols)))
    cv2.putText(high_res_image, 'Start', (int(0.9*cols), int(0.1*rows)), cv2.FONT_HERSHEY_SIMPLEX, int(
        reduction_factor/2), (255, 0, 0), int(2*reduction_factor), cv2.LINE_AA)
    cv2.putText(high_res_image, 'End', (int(0.9*cols), int(0.2*rows)), cv2.FONT_HERSHEY_SIMPLEX, int(
        reduction_factor/2), (55, 175, 212), int(2*reduction_factor), cv2.LINE_AA)

    cv2.circle(high_res_image, end_loc, 5 *
               int(reduction_factor), (55, 175, 212), -1)
    cv2.circle(high_res_image, end_loc, 5*int(reduction_factor),
               (55, 175, 212), int(1*(reduction_factor)))
    cv2.circle(high_res_image, end_loc, 5*int(reduction_factor),
               (255, 255, 255), int(0.5*(reduction_factor)))

# cv2.line(image, start_point, end_point, color, thickness)
    for i in range(1, len(high_res_corners)):
        start_corner = high_res_corners[i-1]
        end_corner = high_res_corners[i]
        high_res_image = cv2.arrowedLine(
            high_res_image, start_corner, end_corner, (0, 0, 255), int(reduction_factor), tipLength=0.1)
    print("FULL DRAWING TIME IS: ", time.perf_counter() - start_time_drawing)

    cv2.imwrite(new_filename, high_res_image)

    return new_filename


# def test_path_finding(DIRECTORY, floor_plan, graph, start, end, reduction_factor=16):
#     """
#     Given a graph, a start and end coordinate on the UNALTERED IMAGE,
#     return an image w/ the shortest path drawn between start and end
#     """
#     start_reduced = (int(start[0]//reduction_factor), int(start[1]//reduction_factor))
#     end_reduced = (int(end[0]//reduction_factor), int(end[1]//reduction_factor))

#     # Get path
#     t_start = time.perf_counter()
#     path_low_res = Dijkstar_duplicated_graph(graph, start_reduced, end_reduced)
#     t_find_path = time.perf_counter()
#     print(f"Dijkstar find_path (duplicated graph) time: {t_find_path - t_start}")

#     path_high_res = expand_coords(path_low_res, int(reduction_factor))
#     t_expand_coords = time.perf_counter()
#     print(f"Expanding coords time: {t_expand_coords - t_find_path}")

#     # Draw path onto CROPPED image
#     cropped_filename = f"{DIRECTORY}/{floor_plan}.png"
#     new_filename = f"{results_dir}/{floor_plan}_{start}_{end}_path.png"

#     save_image_with_path_drawn(cropped_filename, new_filename, path_high_res)
#     print(f"Draw path time: {time.perf_counter() - t_expand_coords}")

#     print(f"User interface time: {time.perf_counter() - t_start}")

#     return new_filename


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
        test_path_finding(DIRECTORY, floor_plan, graph,
                          start, end, reduction_factor)


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
