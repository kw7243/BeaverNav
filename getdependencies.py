/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> /Users/yajva/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
pip3 install --upgrade pip
brew install poppler-utils 
pip3 install opencv-python
pip3 install pdf2image # to convert pdf's to images
brew install poppler
pip3 install IPython # interactive python shell
brew install tesseract # optical character recognition tool
pip3 install pytesseract # optical character recognition tool
pip3 install pillow # image processing library
pip3 install svgpathtools #for analyzing svg
pip3 install cairosvg # for converting to png