import os
#from matplotlib import pyplot as plt
import cv2
import numpy as np
import statistics
import sys


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
    
    
    for cnt in contours :

        approx = cv2.approxPolyDP(cnt, 0.005 * cv2.arcLength(cnt, True), True)
      
        for appr in approx:
            x=appr[0][0]
            y=appr[0][1]
            vertices.append((x,y))
        

        if len(approx)>5:
            break

    #show vertices 
#    i=0
#    for vertex in vertices:
#        img = cv2.circle(img, vertex, radius=1, color=(255,0,255), thickness=-1)
#        cv2.putText(img, str(i), vertex, cv2.FONT_HERSHEY_COMPLEX, 0.3, (255, 0, 0))
#        i+=1
#    plt.figure()
#    plt.imshow(img)
#    plt.show
    return vertices
  

def find_base(vertices):
    
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


def scale_image(image, smallest_width):
    scale = smallest_width/image.shape[1]
    scaled_width = int(image.shape[1]*scale)
    scaled_height = int(image.shape[0]*scale)  
    scaled_image = cv2.resize(image, (scaled_width, scaled_height))
    
    scale_percent = 70
    width = int(scaled_image.shape[1] * scale_percent / 100)
    height = int(scaled_image.shape[0] * scale_percent / 100)
    dim = (width, height)
    
    return cv2.resize(scaled_image, dim, interpolation = cv2.INTER_AREA)

def count_vertex_base_distance(base_cord, vertices):
    #wzor na funkcje przechodzaca przez podstawe
    #funkcja liniowa postac ogolna:
    x_a = base_cord[0][0]
    y_a = base_cord[0][1]
    
    x_b = base_cord[1][0]
    y_b = base_cord[1][1]
    
    A=y_a-y_b
    B=x_b-x_a
    C=y_b*x_a - y_a*x_b
    
    #obliczenie odleglosci punktu od prostej
    distances = {}
    for vertex in vertices:
        if vertex == base_cord[0] or vertex == base_cord[1]:
            continue
        x_0 = vertex[0]
        y_0 = vertex[1]
        
        d = (abs(A*x_0 + B*y_0 + C))/(np.sqrt(A**2 + B**2))
        distances[vertex] = d
    
    return distances
        

def count_side_vertex_distance(vertices, base_cord, side_vertex, which_side):
    #wzor na funkcje przechodzaca przez jeden z bokow
    #funkcja liniowa postac ogolna:
    x_a = base_cord[which_side][0]
    y_a = base_cord[which_side][1]
    
    x_b = side_vertex[0]
    y_b = side_vertex[1]
    
    A=y_a-y_b
    B=x_b-x_a
    C=y_b*x_a - y_a*x_b
    
    #wyrzucenie podstaw - sprawdzam tylko punkty na lamanej
   
    distances = {}
    for vertex in vertices:
        if vertex == base_cord[0] or vertex == base_cord[1]:
            continue
        x_0 = vertex[0]
        y_0 = vertex[1]
        
        d = (abs(A*x_0 + B*y_0 + C))/(np.sqrt(A**2 + B**2))
        distances[vertex] = d
    
    return distances
    

def compare_vertex_base_distances(features):
    comparison = {}
    for i in range(len(features)):
        i_base = features[i]['base_length']
        i_base_vertex_distances = features[i]['base_vertices_distances']
        i_fside_vertex_distances = features[i]['first_side_vertices_distances']
        i_amount_of_vertices = len(i_fside_vertex_distances)
        
        comparison[i] = {}
        
        for j in range(len(features)):
            if i==j:
                continue
            
            
            j_base = features[j]['base_length']
            j_base_vertex_distances = features[j]['base_vertices_distances']
            j_sside_vertex_distances = features[j]['second_side_vertices_distances']
            
            k = i_base/j_base
            
            #scaled_j_base_vertex_distances = [distance*k for distance in list(j_base_vertex_distances.values())]
            scaled_j_base_vertex_distances = j_base_vertex_distances.copy()
            scaled_j_base_vertex_distances.update((cord, d*k) for cord, d in scaled_j_base_vertex_distances.items())
            
            #scaled_j_sside_vertex_distances = [distance*k for distance in list(j_sside_vertex_distances.values())]
            scaled_j_sside_vertex_distances = j_sside_vertex_distances.copy()
            scaled_j_sside_vertex_distances.update((cord, d*k) for cord, d in scaled_j_sside_vertex_distances.items())
            
            
            j_amount_of_vertices = len(scaled_j_sside_vertex_distances)
            #teraz sprawdzic ktory wierzcholek z ktorym porownac
            #przejechac przez wszystkie wierzcholki, ale tam, gdzie jest mniej!
            if i_amount_of_vertices <= j_amount_of_vertices:
                vertices_to_check = list(i_base_vertex_distances.keys())
            else:
                vertices_to_check = list(j_base_vertex_distances.keys())
                
            #znajdz odpowiadajace wierzcholki (najmniejsza roznica miedzy side odleglosciami)
            vertices_to_compare = []

            for i_item in i_fside_vertex_distances.items():
                smallest_diff = float('inf')
                for j_item in scaled_j_sside_vertex_distances.items():
                    diff = abs(i_item[1]-j_item[1])
                    if diff < smallest_diff:
                        smallest_diff=diff
                        vertex_with_smallest_diff = j_item[0]
                if i_item[0] in vertices_to_check or vertex_with_smallest_diff in vertices_to_check:
                    vertices_to_compare.append((i_item[0], vertex_with_smallest_diff))

                            
            
            totals = []
            
            for vertices_to_comp in vertices_to_compare:
                v_i = vertices_to_comp[0]
                v_j = vertices_to_comp[1]
                
                sum = i_base_vertex_distances[v_i] + scaled_j_base_vertex_distances[v_j]
                totals.append(sum)
                
#            print('Totals for ' + str(i) + ' and ' + str(j) + ': ' + str(totals))
#            print('*'*12)
            comparison[i][j] = statistics.variance(totals)
            
    for c in range(len(comparison)):
        features[c]["match_by_length_vertex_base_variance"] = sorted(comparison[c], key=comparison[c].get)

            

#def check_similarity_scale(features):
#    #bierzemy dlugosc podstawy danego image i porownujemy do dlugosci pozostalych
#    #powstaje nam k
#    
#    similarity = {}
#    
#    #skalujemy przez k pozostale image i sprawdzamy gdzie dlugosci bokow pasuja do siebie
#    for i in range(len(features)):
#        i_base = features[i]['base_length']
#        i_first_side = features[i]['first_side_length']
#        i_second_side = features[i]['second_side_length']
#        
#        #shorter longer?
#        
#        similarity[i] = {}
#        for j in range(len(features)):           
#          
#            if i == j:
#                continue
#            j_base = features[j]['base_length']
#            j_first_side = features[j]['first_side_length']
#            j_second_side = features[j]['second_side_length']
#            #skala
#            k = i_base/j_base
#
#            
#            scaled_j_first_side = k*j_first_side
#            scaled_j_second_side = k*j_second_side
#            
#            
#            sum_l_side = i_first_side + scaled_j_second_side
#            sum_r_side = i_second_side + scaled_j_first_side
#            
#            #CZY MO??E PODZIELIC TO JESZCZE PRZEZ 'COS'? ze wzgledu na rozne wielkosci tych prostokatow roznica dlugosci moze nie byc tak miarodajna
#            abs_diff = abs(sum_l_side - sum_r_side)
#            
#            similarity[i][j] = abs_diff
#
#            
#            
#    for s in range(len(similarity)):
#        features[s]["match_by_sides_similarity"] = sorted(similarity[s], key=similarity[s].get)
            
    

def compare_images():
    #path_to_images = '.\set8'
    #amount_of_images = 100
    
    try:
        path_to_images = str(sys.argv[1])
        amount_of_images = int(sys.argv[2])
        images, smallest_width = read_images(amount_of_images, path_to_images) 
    except:
        print('Invalid input')
        exit()
        
    features = {}  
    i=0
    for image in images:
     
        vertices = find_vertices(image)
        base_length, base_cord = find_base(vertices)
        first_side_vertex, second_side_vertex, first_side_length, second_side_length = find_sides(vertices, base_cord)
        base_vertices_distances = count_vertex_base_distance(base_cord, vertices)
        first_side_vertices_distances = count_side_vertex_distance(vertices, base_cord, first_side_vertex, 0)
        second_side_vertices_distances = count_side_vertex_distance(vertices, base_cord, second_side_vertex, 1)
        
           
        features[i] = {'vertices_len':len(vertices), 'vertices_cord':vertices, 'base_cord':base_cord,'base_length':base_length, 'first_side_length':first_side_length,
                'second_side_length':second_side_length, 'base_vertices_distances': base_vertices_distances,
                'first_side_vertices_distances':first_side_vertices_distances, 'second_side_vertices_distances':second_side_vertices_distances}
        
      
        i+=1
    
    #similarity = check_similarity_scale(features)
    compare_vertex_base_distances(features)
    
    #wyprintuj wszystkie
    for i in range(len(features)):
        matches = features[i]['match_by_length_vertex_base_variance']
        for match in matches:
            print(match, end=' ', sep=' ')
        print('')
    
    #wyprintuj tylko pierwsze
    #a=[]
    #for i in range(len(features)):
    #    #print(features[i]['match_by_length_vertex_base_variance'][0])
    #    a.append(features[i]['match_by_length_vertex_base_variance'][0])
    #print(a)
    
    
compare_images()