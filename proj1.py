import os
from skimage import io
from skimage import measure 
from matplotlib import pyplot as plt
import cv2
import numpy as np


def read_images(num_of_images, path):
    images = []
    biggest_width = 0
    for im in range(num_of_images):
        filename = os.path.join(path, str(im)+'.png')
        img = cv2.imread(filename)
        images.append(img)
        
        curr_width = img.shape[1]
        if curr_width > biggest_width:
            biggest_width = curr_width
    
    return images, biggest_width

    
def find_vertices(img):
    
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 127, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    vertices = []
    
    # Going through every contours found in the image.
    for cnt in contours :

        approx = cv2.approxPolyDP(cnt, 0.009 * cv2.arcLength(cnt, True), True)
      
        for appr in approx:
            x=appr[0][0]
            y=appr[0][1]
            vertices.append((x,y))
        break
    #najpierw slownik, potem lista, poniewaz oryginalnie (od razu lista) byly problemy z kolejnoscia wierzcholkow przy rozpoznawaniu bokow na podstawie podstawy
    #na liste:
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
    
    base_start_vertex_index = vertices.index(base[0])
    base_end_vertex_index = vertices.index(base[1])
    
    #wierzcholek pierwszego boku (znajdujacego sie 'nad' wierzcholkiem startowym podstawy)
    try:
        #jest to element poprzedzajacy na liscie wierzcholkow
        side_overstart_vertex = vertices[base_start_vertex_index-1]
    except IndexError:
        side_overstart_vertex = vertices[-1]
    
    #wierzcholek drugiego boku (znajdujacego sie 'nad' wierzcholkiem koncowym podstawy)
    try:
        #jest to element kolejny na liscie wierzcholkow
        side_overend_vertex = vertices[base_end_vertex_index+1]
    except IndexError:
        side_overend_vertex = vertices[0]
        
    
    return side_overstart_vertex, side_overend_vertex

features = {}


images, biggest_width = read_images(6, ".\set0") 

i=0
for image in images:
    
    if i ==3:
        print('show me this piece of shit')
    
    #smallest
    #nowe skalowanie - procentowe wzgledem szerokosci najmniejszego (aby zachować k)
    
#    scale = biggest_width/image.shape[1]
#
#    scaled_width = int(image.shape[1]*scale)
#    scaled_height = int(image.shape[0]*scale)
#    
#    image = cv2.resize(image, (scaled_width, scaled_height))
    #image = cv2.resize(image, (smallest_shape[1], smallest_shape[0]))

    
    vertices = find_vertices(image)
    base_length, base_cord = find_base(vertices)
    first_side, second_side = find_sides(vertices, base_cord)
    features[i] = {'num_of_vertices':len(vertices), 'base_length':base_length}
    
    #in find_sides function add their length, 
    #add new function that counts k and then scale figure with k and check in sides matches
    
    
    image = cv2.circle(image, base_cord[0], radius=2, color=(0, 255, 0), thickness=-1)
    image = cv2.circle(image, base_cord[1], radius=2, color=(170, 245, 145), thickness=-1)
    
    image = cv2.circle(image, first_side, radius=2, color=(255, 0, 0), thickness=-1)
    image = cv2.circle(image, second_side, radius=2, color=(245, 145, 180), thickness=-1)

    plt.figure()
    plt.imshow(image)
    plt.show 

    
    i+=1


#focus na liczbie krawedzi i wierzcholkow

#plt.imshow(image)
#plt.show           
        
        
#DODATKOWO - KRAWEDZIE (PODSTAWA I BOKI) POWINNY BYC DLUGOSCIAMI PODOBNYMI DO ODPOWIADAJACEGO PROSTOKAT
            #TJ PODSTAWA DO PODSTAWY TO SKALA, - INFO ZESZYT
            #DO TEGO ODLEGLOSC OD PODSTAWY DO WIERZCHOLKA? DLUGOSCI TEZ POWINNY SUMOWAC SIE DO DLUGOSCI BOKU