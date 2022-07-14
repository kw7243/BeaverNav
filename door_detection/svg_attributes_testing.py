from svgpathtools import svg2paths2 

from svgpathtools import svg2paths2, wsvg, Path

def main():
    filepath = "1_2.svg"
    # Path object = sequence of segments like lines or curves

    # paths = list of Path objects
    # attributes = list of dictionaries of SVG path attributes
    # default attributes: "style" and "d" for data
    # optional- "transform": 'matrix(0,-0.12,-0.12,0,1222,790)'
    paths, attributes, svg_attributes = svg2paths2(filepath)
    for i, path in enumerate(paths):
        if path == Path():
            print(paths[i - 1])
            print(path)
            print(paths[i + 1])


    wsvg(paths=paths, filename="test.svg", attributes=attributes, svg_attributes=svg_attributes)

    # print(f"Paths: {paths[0]}")
    # print(f"Attributes: {len(attributes[0])}")
    # print(f"svg_Attributes: {svg_attributes}")
    

if __name__ == "__main__":
    main()