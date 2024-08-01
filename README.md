# BeaverNav

![Header Image](assets/beaver_nav/header.png)

**Description:** Dec 2022  
**Category:** Fun  
**Importance:** 1  

---

### Problem

MIT is a large campus with thousands of rooms, hallways, buildings, staircases, and elevators. Finding one’s way around campus can be difficult and daunting.

### Our Solution

Indoor navigation for MIT’s campus: Enables users to navigate between rooms, provides routes from start destination to end destination

**Note this is still a work in progress & is not yet a live website**

![Navigation inside a building](assets/beaver_nav/AIM%20Labs%20Demo%202-2.png)
*Navigation inside a building*

![Navigation between buildings](assets/beaver_nav/AIM%20Labs%20Demo%202.png)
*Navigation between buildings*

We built this using the following pipeline:

1. Scrape Floor Plans from MIT website, and process into images.
2. Extract key information (room coordinate locations & names) via pre-trained neural network text detection and recognition models (EAST, Easy OCR).
3. Remove all doors & text from the floorplans & downsample (reduce resolution).
4. Create a graph treating every pixel as a node in the graph.
5. Condense graph offline by running an additional all-pairs shortest paths algorithm (APSP) & use A* for online planning.
6. Create an “abstracted graph” of MIT’s campus using elevators, staircases, and entry-exits between buildings.

![High-Level Graph](assets/beaver_nav/AIM%20Labs%20Demo%202-3.png)
*High-Level Graph*

More in-depth explanation can be found below.

## [**Code**](https://github.com/kw7243/BeaverNav)

## [**Demo**](assets/beaver_nav/demo_vid.mov)

<div>
<iframe src="assets/beaver_nav/demo_vid.mov" width="100%" height="600px"></iframe>
</div>

## [**Project Presentation**](assets/beaver_nav/AIM%20Labs%20Demo%202.pdf)

<div>
<iframe src="assets/beaver_nav/AIM%20Labs%20Demo%202.pdf" width="100%" height="600px"></iframe>
</div>
