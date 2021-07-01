import os
from skimage import io
from skimage import measure 
from matplotlib import pyplot as plt
import cv2
import numpy as np


def read_images(num_of_images, path):
    images = []
    smallest_sum_shape = float('inf')
    for im in range(num_of_images):
        filename = os.path.join(path, str(im)+'.png')
        img = cv2.imread(filename)
        images.append(img)
        
        shape = img.shape
        if shape[0]+shape[1] < smallest_sum_shape:
            smallest_shape = shape
    
    return images, smallest_shape

    
def find_vertices(img):
    
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 127, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    vertices = []
    
    # Going through every contours found in the image.
    for cnt in contours :

        approx = cv2.approxPolyDP(cnt, 0.005 * cv2.arcLength(cnt, True), True)
      
        # draws boundary of contours.
        #cv2.drawContours(img, [approx], 0, (0, 0, 255), 5) 
      
        # Used to flatted the array containing
        # the co-ordinates of the vertices.
        n = approx.ravel() 
        i = 0
      
        for j in n :
            if(i % 2 == 0):
                x = n[i]
                y = n[i + 1]
      
                vertices.append((x,y))
                #img = cv2.circle(img, (x,y), radius=3, color=(0, 255, 0), thickness=-1)
                
    
            i = i + 1
    
    return vertices



def find_base(vertices):
    
    #base is probably? the longest segment
    max_dist = 0
    
    for v in range(len(vertices)):
        x_a = vertices[v][0]
        y_a = vertices[v][1]
        
        try:
            x_b = vertices[v+1][0]
            y_b = vertices[v+1][1]
        except IndexError:
            x_b = vertices[0][0]
            y_b = vertices[0][1]
            
        current_dist = np.sqrt((x_b-x_a)**2+(y_b-y_a)**2)
        
        if current_dist > max_dist:
            max_dist = current_dist
            base = [(x_a,y_a),(x_b,y_b)]
            
            
    return max_dist, base


def find_sides(vertices, base):
    pass


features = {}


images, smallest_shape = read_images(6, ".\set0") 

i=0
for image in images:
    #smallest
    image = cv2.resize(image, (smallest_shape[0], smallest_shape[1]))

    
    vertices = find_vertices(image)
    base_length, base_cord = find_base(vertices)
    #sides = find_sides...
    features[i] = {'num_of_vertices':len(vertices), 'base_length':base_length}
    


    
    i+=1


#focus na liczbie krawedzi i wierzcholkow

#plt.imshow(image)
#plt.show           
        
        
#DODATKOWO - KRAWEDZIE (PODSTAWA I BOKI) POWINNY BYC DLUGOSCIAMI PODOBNYMI DO ODPOWIADAJACEGO PROSTOKAT
            #TJ PODSTAWA DO PODSTAWY TO SKALA, - INFO ZESZYT
            #DO TEGO ODLEGLOSC OD PODSTAWY DO WIERZCHOLKA? DLUGOSCI TEZ POWINNY SUMOWAC SIE DO DLUGOSCI BOKU