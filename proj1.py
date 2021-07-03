import os
from matplotlib import pyplot as plt
import cv2
import numpy as np


def read_images(num_of_images, path):
    images = []
    smallest_width = float('inf')
    for im in range(num_of_images):
        filename = os.path.join(path, str(im)+'.png')
        img = cv2.imread(filename)
        images.append(img)
        
        curr_width = img.shape[1]
        if curr_width < smallest_width:
            smallest_width = curr_width
    
    return images, smallest_width

    
def find_vertices(img):
    
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 127, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    vertices = []
    
    # Going through every contours found in the image.
    for cnt in contours :

        approx = cv2.approxPolyDP(cnt, 0.005 * cv2.arcLength(cnt, True), True)
      
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
        
    
    first_side_length = np.sqrt((side_overstart_vertex[0]-base[0][0])**2+(side_overstart_vertex[1]-base[0][1])**2)
    second_side_length = np.sqrt((side_overend_vertex[0]-base[1][0])**2+(side_overend_vertex[1]-base[1][1])**2)
    
    return side_overstart_vertex, side_overend_vertex, first_side_length, second_side_length




def check_similitary_scale(features):
    #bierzemy dlugosc podstawy danego image i porownujemy do dlugosci pozostalych
    #powstaje nam k
    
    similitary = {}
    
    #skalujemy przez k pozostale image i sprawdzamy gdzie dlugosci bokow pasuja do siebie
    for i in range(len(features)):
        i_base = features[i]['base_length']
        i_first_side = features[i]['first_side_length']
        i_second_side = features[i]['second_side_length']
        for j in range(len(features)):
            if i == j:
                continue
            j_base = features[i]['base_length']
            j_first_side = features[j]['first_side_length']
            j_second_side = features[j]['second_side_length']
            #skala
            k = i_base/j_base
            
            scaled_j_first_side = k*j_first_side
            scaled_j_second_side = k*j_second_side
            
            sum_l_side = i_first_side + scaled_j_second_side
            sum_r_side = i_second_side + scaled_j_first_side
            
            #CZY MOŻE PODZIELIC TO JESZCZE PRZEZ 'COS'? ze wzgledu na rozne wielkosci tych prostokatow roznica dlugosci moze nie byc tak miarodajna
            abs_diff = abs(sum_l_side - sum_r_side)
            
            similitary[str(i)+'-'+str(j)] = abs_diff
            
    return similitary
            
    
    
    #funckja niech dorzuca do slownika features do ktorego dany obrazek najbardziej by pasowal na podstawie skali podobienstwa






features = {}
images, smallest_width = read_images(6, ".\set0") 

i=0
for image in images:

    #image = cv2.resize(image, (smallest_shape[1], smallest_shape[0]))

    
    vertices = find_vertices(image)
    base_length, base_cord = find_base(vertices)
    first_side_vertex, second_side_vertex, first_side_length, second_side_length = find_sides(vertices, base_cord)
    
    features[i] = {'base_length':base_length, 'first_side_length':first_side_length,
            'second_side_length':second_side_length}
    
    testowe = check_similitary_scale(features)

    #skalowanie obrazow:
#    scale = smallest_width/image.shape[1]
#    scaled_width = int(image.shape[1]*scale)
#    scaled_height = int(image.shape[0]*scale)  
#    image = cv2.resize(image, (scaled_width, scaled_height))
    
    #features[i]['num of vertices'] = find_vertices(image)
    
    #wyswietlenei obrazow
#    image = cv2.circle(image, base_cord[0], radius=1, color=(0, 255, 0), thickness=-1)
#    image = cv2.circle(image, base_cord[1], radius=1, color=(170, 245, 145), thickness=-1)
#    
#    image = cv2.circle(image, first_side_vertex, radius=1, color=(255, 0, 0), thickness=-1)
#    image = cv2.circle(image, second_side_vertex, radius=1, color=(245, 145, 180), thickness=-1)
#
#    plt.figure()
#    plt.imshow(image)
#    plt.show 

    
    i+=1

