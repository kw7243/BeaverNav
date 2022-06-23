def find_edge(image,size,borders):
  top_boundaries = []
  cv2_imshow(image[borders[0][1]:borders[1][1]])
  for i in range(borders[0][0]+size//2,borders[1][0]+size//2-size):
    cut1 = (np.sum(image[borders[0][1]:borders[1][1],i-size//2:i+1]-255, axis=1)==0)
    cut2 = (np.sum(image[borders[0][1]:borders[1][1],i:i-size//2+size]-255, axis=1)==0)
    cut = np.logical_or(cut1,cut2)
    if i == 5000:
      print(image[borders[0][1]:borders[1][1],i-size//2:i-size//2+size].shape)

    if np.all(cut):
      top_boundaries.append(None)
    else:
      top_bound = borders[0][1]+np.argmax(np.logical_not(cut))-1
      bottom_bound = borders[0][1]+cut.shape[0]-1-np.argmax(np.logical_not(cut)[::-1])+1
      top_boundaries.append((top_bound, bottom_bound))

  image_copy = image.copy()
  for i in range(len(top_boundaries)):
    if top_boundaries[i] != None:
      image_copy[:top_boundaries[i][0],borders[0][0]+i+size//2] = 0
      image_copy[top_boundaries[i][1]:,borders[0][0]+i+size//2] = 0
    else:
      image_copy[:,borders[0][0]+i+size//2]=0
  
  return (top_boundaries, image_copy)


def find_top_bottom(image):
  vertical_border = np.logical_not(np.sum(image,axis=1)/(255.0*image.shape[1])>0.1)

  top = np.argmax(vertical_border)
  while top<vertical_border.shape[0] and vertical_border[top]:
    top+=1
  
  if np.any(vertical_border):
    bottom = vertical_border.shape[0]-1-np.argmax(vertical_border[::-1])
  else:
    bottom = image.shape[0]-1
  
  bottom_prev = bottom

  while bottom != top-1:
    bottom_prev = bottom
    vertical_border = vertical_border[:bottom]
    if np.any(vertical_border):
      bottom = vertical_border.shape[0]-1-np.argmax(vertical_border[::-1])
    else:
      bottom = top-1
  
  bottom = bottom_prev

  return (top,bottom)

def crop_image(image):
  left,right = find_top_bottom(image.T)
  image = image[:,left:right]

  top,bottom = find_top_bottom(image)
  image_map = image[top:bottom,:]
  image_legend = image[bottom:,:]

  return (top,bottom,left,right,image_map,image_legend)

def get_interior(image):
  image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  top,bottom,left,right,_,_ = crop_image(image)
  boundaries,new_img = find_edge(image,200,((left,top),(right,bottom-1)))
  k=5
  blurrednp=cv2.GaussianBlur(new_img, (k,k), 0)
  blurrednp[blurrednp!=255]=0

  flooded = cv2.floodFill(blurrednp, None, (image.shape[1]//2, image.shape[0]//2), 100)[1]
  flooded[flooded!=100]=0
  flooded[flooded==100]=255

  return flooded
