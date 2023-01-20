import os
txt_dir = "backend_file_storage/raw_text_locations"
new_txt_dir = "backend_file_storage/text_locations"
import json
import re 

def main():
    problem_floors = []
    for i, floor in enumerate(os.listdir(txt_dir)):
        if "DS" in floor:
            continue
        with open(f"{txt_dir}/{floor}", 'r') as f:
            text = json.load(f)
        newtext = []
        
        for t in text:
            # convert everythin to uppercase
            new_t = t[0].upper()
            # check for numbers
            if not any((char.isdigit() and char!='0') for char in new_t):
                continue
            # remove non alphanumeric characters
            new_t = re.sub(r'\W+', '', new_t)
            # check for 0 vs O. 
            if "O" in new_t:
                # if a middle character is O, change it to zero
                # otherwise, if the text length is 3, the O should be zero
                if new_t[-1] != "O" or len(new_t) < 4:
                    new_t = new_t.replace('O', '0')
            # check the first # of each room 
            if floor[-6] != new_t[0] and floor[-6] != 'M':
                if floor[:2] == "32" and len(floor[:-5].split('_')[1]) == 2:
                    if len(new_t) > 3:
                        new_t = floor[3:5] + new_t[2:]
                    else: print(floor+" "+new_t)
                    continue
                if len(new_t) > 2:
                    new_t = floor[-6] + new_t[1:]
                    continue
                print(floor+" "+new_t)
                if floor not in problem_floors: problem_floors.append(floor)
            newtext.append([new_t, t[1]])
        if len(newtext) == 0: print(floor)
        with open(f"{new_txt_dir}/{floor}", 'w') as f:
             json.dump(newtext, f, indent=5)
    # FOR FUTURE TODO, DEAL WITH REMAINING PROBLEMS       
    print(problem_floors)
if __name__ == "__main__":
    main()
