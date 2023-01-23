"""
Import this file for any file paths 
"""

import os
beavernav = os. getcwd() + '/'
svg_originals_dir = beavernav + "backend_file_storage/svg_original_files"
svg_doors_dots_removed_dir = beavernav + "backend_file_storage/doors_dots_removed_svg"
svg_doors_dots_removed_dir_temp = beavernav + "backend_file_storage/doors_dots_removed_svg_temp"
cropped_png_files_dir = beavernav + "backend_file_storage/cropped_png_files"
cropped_pristine_png_files_dir = beavernav + "backend_file_storage/cropped_pristine_png_files"
reduced_res_png_dir = beavernav + "backend_file_storage/graph_creation_reduced_res_png"
graph_storage_dir = beavernav + "backend_file_storage/graph_storage"
non_text_pngs_dir = beavernav + "backend_file_storage/non_text_cropped_pngs"
svg_no_lines_dir = beavernav + "backend_file_storage/no_lines_svgs"
cropped_png_no_lines_dir = beavernav + "backend_file_storage/no_lines_cropped_pngs"
bbox_dir = beavernav + "backend_file_storage/bounding_boxes"
modified_png_dir = beavernav + "backend_file_storage/boxed_text_pngs"
txt_png_dir = beavernav + "backend_file_storage/pngs_with_recognized_text"
txt_dir = beavernav + "backend_file_storage/raw_text_locations"
cleaned_txt_dir = beavernav + "backend_file_storage/text_locations"
floorplan_name_graph_correspondence_dir = beavernav + "backend_file_storage/floorplan_name_graph_correspondence/floorplan_name_graph_correspondence.json"
cropped_pristine_png_files = beavernav + "backend_file_storage/cropped_pristine_png_files"
cropping_offsets = beavernav + "backend_file_storage/cropping_offsets"
temp_dir = beavernav + 'backend_file_storage/pruned_graphs'
abstract_graph = beavernav + "backend_file_storage/abstract_graph.pickle"
results_dir = beavernav + "backend_file_storage/results"
pruned_graphs = beavernav + "backend_file_storage/pruned_graphs"
special_features = beavernav + "backend_file_storage/special_feature_coordinates.json"
labelled_pngs = beavernav + "backend_file_storage/labelled_pngs"
labelling_legend = beavernav + "backend_file_storage/labelling_legend.json"
scaling_factors_path = reduced_res_png_dir + "/scaling_factors.json"
results_dir = beavernav + "backend_file_storage/results"
testing_results = beavernav + "backend_file_storage/testing_results.json"
testing_errors = beavernav + "backend_file_storage/testing_errors.json"
