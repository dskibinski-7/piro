import os
from skimage import io
from skimage import measure 
from matplotlib import pyplot as plt
import cv2


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
        cv2.drawContours(img, [approx], 0, (0, 0, 255), 5) 
      
        # Used to flatted the array containing
        # the co-ordinates of the vertices.
        n = approx.ravel() 
        i = 0
      
        for j in n :
            if(i % 2 == 0):
                x = n[i]
                y = n[i + 1]
      
                vertices.append((x,y))
                img = cv2.circle(img, (x,y), radius=3, color=(0, 255, 0), thickness=-1)
                
    
            i = i + 1
    
    return vertices





features = {}


images, smallest_shape = read_images(6, r"C:\Users\skibi\OneDrive\Dokumenty\Informatyka\Piro\Proj1\set0") 

i=0
for image in images:
    #smallest
    image = cv2.resize(image, (smallest_shape[0], smallest_shape[1]))

    
    vertices = find_vertices(image)
    features[i] = {'num_of_vertices':len(vertices)}
    
    i+=1


#focus na liczbie krawedzi i wierzcholkow

            
        
        
#DODATKOWO - KRAWEDZIE (PODSTAWA I BOKI) POWINNY BYC DLUGOSCIAMI PODOBNYMI DO ODPOWIADAJACEGO PROSTOKAT
            #TJ PODSTAWA DO PODSTAWY TO SKALA, - INFO ZESZYT
            #DO TEGO ODLEGLOSC OD PODSTAWY DO WIERZCHOLKA? DLUGOSCI TEZ POWINNY SUMOWAC SIE DO DLUGOSCI BOKU