import os
txt_dir = "full_pipeline_files_test/text_locations"
new_txt_dir = "full_pipeline_files_test/cleaned_text_locations"
import json

def main():
    problem_floors = []
    for i, floor in enumerate(os.listdir(txt_dir)):
        if "DS" in floor:
            continue
        with open(f"{txt_dir}/{floor}", 'r') as f:
            text = json.load(f)
        newtext = {}
        
        for t in text:
            # convert everythin to uppercase
            new_t = t[0].upper()
            # check for 0 vs O. 
            if "O" in new_t:
                # if a middle character is O, change it to zero
                # otherwise, if the text length is 3, the O should be zero
                if new_t[-1] != "O" or len(new_t) < 4:
                    new_t = new_t.replace('O', '0')
            # check the first # of each room 
            if floor[-6] != new_t[0] and floor[-6] != 'M':
                print("problem")
                print(floor+" "+new_t)
                if floor not in problem_floors: problem_floors.append(floor)
    print(len(problem_floors))
if __name__ == "__main__":
    main()