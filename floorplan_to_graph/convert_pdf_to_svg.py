pdf_dir = "/content/drive/MyDrive/FreshStart/PDF Floor Plans" # replace with corresponding pdf_dir
svg_dir = "/content/drive/MyDrive/FreshStart/SVG Floor Plans" # replace with corresponding svg_dir
from os import listdir, system
from os.path import isfile, join
import subprocess
import time

pdfs = [f for f in listdir(pdf_dir) if isfile(join(pdf_dir, f))]

for pdf in pdfs:
  new_name = pdf[:-4] + ".svg"
  pdf_path = join(pdf_dir, pdf)
  svg_path = join(svg_dir, new_name)
  subprocess.call(["/usr/bin/pdftocairo", pdf_path, svg_path, "-svg", "-expand"]) # note that inkscape did not work
  print(f"Converted {svg_path}")
print(f"Done! Converted {len(pdfs)} pdfs into svgs!")  
