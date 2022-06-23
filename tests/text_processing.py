# Should not end in backslash. This is the drive folder where everything will be written
from BeaverNav import text_processing_methods

text_dir = "/content/drive/MyDrive/FreshStart/Text Files" 
text_png_dir = "/content/drive/MyDrive/FreshStart/Text PNGs" 
nontext_png_dir = "/content/drive/MyDrive/FreshStart/Nontext PNGs" 
nontext_svg_dir = "/content/drive/MyDrive/FreshStart/Nontext SVGs" 
text_svg_dir = "/content/drive/MyDrive/FreshStart/Text SVGs" 
color_widths("1_3", nontext_png_dir, text_dir, text_png_dir, nontext_svg_dir, text_svg_dir, init_threshold=10, overwrite_drive=False) # apply main "color_widths" func to room
