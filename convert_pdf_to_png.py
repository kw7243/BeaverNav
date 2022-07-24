import text_detection_with_east

def main():
	buildings = [1, 2, 3, 4, 5, 6, '6C', 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 24, 26, 31, 32, 33, 34, 35, 36, 37, 38, 39, 56, 57, 66, 68]
	b2 = []
	for b in buildings:
		b2.append(str(b))
	relevant = []
	for floor in text_detection_with_east.pdffiles:
		floor = floor[:-4]
		b = floor[:floor.index('_')]
		if b in b2:
			relevant.append(floor)

	floors = relevant
	#floors = random.sample(relevant, 10)
	for floor in floors:
		text_detection_with_east.convertPDFtoPNG(floor, 960)

	
if __name__ == "__main__":
		main()
