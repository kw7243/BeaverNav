from svg_helper_methods import *
import os
import time
import pickle

def test():
    DIRECTORY = "../SVG_floor_plans"
    test_dir = "tests/"
    start = time.perf_counter()

    print("Starting... ")
    print(f"Total floor plans to process: {len(os.listdir(DIRECTORY))}")

    svg_attr_size = []
    for i, floorplan in enumerate(os.listdir(DIRECTORY)):
        if '.svg' not in floorplan:
            continue
        
        print(f"Processing number {i}: {floorplan}...")
        paths, attr, svg_attr = svg2paths2(f"{DIRECTORY}/{floorplan}")
        threshold = determining_threshold_dots(svg_attr)

        paths, attr = remove_empty_paths(paths, attr)
        paths, attr = remove_doors(paths, attr)
        paths, attr = remove_dots(paths, attr, threshold)

        wsvg(paths, filename=f"{test_dir}/{floorplan[:-4]}_no_doors-dots.svg", attributes=attr, svg_attributes=svg_attr)

        svg_attr_size.append((svg_attr['width'], svg_attr['height']))

    
    print(f"Total time: {time.perf_counter() - start}")

    print(f"SVG attr total size: {len(svg_attr_size)}")
    with open("svg_attr_dimensions.pickle", "wb") as f:
        pickle.dump(svg_attr_size, f)


if __name__ == "__main__":
    test()