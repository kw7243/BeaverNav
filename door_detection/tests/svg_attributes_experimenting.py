from svg_helper_methods import *

def main():
    file_name = "32_1.svg"
    paths, attributes, svg_attributes = svg2paths2(file_name)
    paths, attributes = remove_empty_paths(paths, attributes)
    
    new_paths, new_attributes = remove_doors(paths, attributes)
    wsvg(paths, filename="32_1_no_doors.svg", attributes=attributes, svg_attributes=svg_attributes)

if __name__ == "__main__":
    main()