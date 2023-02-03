from matplotlib import scale
from create_file_paths import *
import os
import cv2
import pytesseract
import json

# we want to calculate a scaling factor between pixels on floorplans and the real-life foot distance

orb = cv2.ORB_create()
matcher = cv2.BFMatcher()

def main():
    reference_image = cv2.imread(f"{distance_scale_dir}/distance_scale_reference.png")
    # trainKeypoints, trainDescriptors = orb.detectAndCompute(reference_image,None)
    
    trial_img = cv2.imread(f"{cropped_pristine_png_files_dir}/10_1.png")
    # trialKeypoints, trialDescriptors = orb.detectAndCompute(trial_img,None)
    
    # matches = matcher.match(trialDescriptors,trainDescriptors)

    # final_img = cv2.drawMatches(trial_img, trialKeypoints, reference_image, trainKeypoints, matches[:20],None)
    
    # cv2.imshow("Matches", final_img)
    # cv2.waitKey(3000)       

    distance_scale_storage = {}
    building_dir = {}

    for png_file in os.listdir(cropped_pristine_png_files_dir):
        if(png_file == "0_0.png") or ".DS" in png_file:
            continue
        print(f"{cropped_pristine_png_files_dir}/{png_file}")
        img = cv2.imread(f"{cropped_pristine_png_files_dir}/{png_file}")
        img = img[11840:12754,5750:9345]
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(img, config=custom_config)
        text = text.split(" ")
        try:
            max_feet = int(text[-1])
            scale_factor = max_feet/1802 # assuming that the scale box has exactly 1802 pixels 
            building_dir[png_file[:-4].split('_')[0]] = scale_factor
        except:
            print(text)
            pass 

        distance_scale_storage[png_file[:-4]] = scale_factor

    for png_file in os.listdir(cropped_pristine_png_files_dir):
        if(png_file == "0_0.png") or ".DS" in png_file or png_file[:-4] in distance_scale_storage:
            continue
        img = cv2.imread(f"{cropped_pristine_png_files_dir}/{png_file}")
        img = img[11840:12754,5750:9345]
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(img, config=custom_config)
        text = text.split(" ")
        try:
            max_feet = int(text[-1])
            scale_factor = max_feet/1802 # assuming that the scale box has exactly 1802 pixels 
            building_dir[png_file[:-4].split('_')[0]] = scale_factor
        except:
            print(text)
            scale_factor = building_dir[png_file[:-4].split('_')[0]]

        distance_scale_storage[png_file[:-4]] = scale_factor


    with open(f"{distance_scale_dir}/distance_scales.json", 'w') as f:
        json.dump(distance_scale_storage, f, indent = 5)



if __name__ == "__main__":
    main()