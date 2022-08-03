from ../door_detection.svg_helper_methods.py import *
import cairosvg
import os


def main():
    svg_dir = "floor_plans"
    test_dir = "tests/"

    print("Starting... ")
    print(f"Total floor plans to process: {len(os.listdir(svg_dir))}")

    svg_attr_size = []
    for i, floorplan in enumerate(os.listdir(svg_dir)):
        print(f"SVG processing number {i}: {floorplan}...")
        paths, attr, svg_attr = svg2paths2(f"{svg_dir}/{floorplan}")
        threshold = determining_threshold_dots(svg_attr)

        paths, attr = remove_empty_paths(paths, attr)
        paths, attr = remove_doors(paths, attr)
        paths, attr = remove_dots(paths, attr, threshold)

        wsvg(paths, filename=f"{test_dir}/{floorplan[:-4]}_no_doors-dots.svg", attributes=attr, svg_attributes=svg_attr)


    


if __name__ == "__main__":
    main()
