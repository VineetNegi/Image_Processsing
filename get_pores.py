# -*- coding: utf-8 -*-
'''
codebname: GET_PORES
Description: This code reads in a Black&White image and detects the pores (white regions) in the image.
The codes uses a variantion of Breadth-First graph search algorithm, where neighbors of a graph-vertex (pixel)
are added to two separates queues - a queue for black pixels, and a queue for white pixels. The white pixels
queue is given the priority while processing. Whenever, the white pixel queue goes empty a pore is detected. 
The pore pixels are the processed white pixels when the white pixel's queue become empty. The time complexity
of the code is therefore O(N), where N is the total number of pixels in the image.

created by - VN
(3/15/2019)
'''

# Import modules
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.cm as cmx

#define global functions
    
def print_bw_image(bwimg):
    '''
    This function prints the binary image
    '''
    sx, sy = bwimg.shape
    img1 = np.zeros((sx, sy, 3))
    img1[:,:,0] = bwimg[:,:]
    img1[:,:,1] = bwimg[:,:]
    img1[:,:,2] = bwimg[:,:]
    plt.imshow(img1)
    
def get_adjncy_list(loc, img):
    '''
    This function finds the location of pixel adjacent to 'loc' pixel in image 'img'
    '''
    sx, sy = img.shape
    neighbors = []
    for j in range(-1,2):
        for i in range(-1, 2):
            if(i != 0 or j != 0 and (i == 0 or j == 0)):
                x = loc[0] + i
                y = loc[1] + j
                if(x >= 0 and x < sx and y >= 0 and y < sy):
                    neighbors.append((x,y))
                    
    return neighbors
    
def get_pores(bw):
    '''
    This function processes the black & white image to get the 
    numbers and sizes of pores in the image
    '''
    
    "define relevant data structures"
    w_queue = []
    b_queue = []
    pore = []
    pores = []
    status = np.zeros(bw.shape, dtype=int)
    "note - status=0 means unvisited, status=1 means queued, status=2 means processed"
    
    
    "define counters"
    n_processed = 0
    n_queued = 0
    n_notvisited = np.size(bw)
    
    "initialize the process"
    if(bw[0,0] == 1):
        w_queue.append((0,0))
    else:
        b_queue.append((0,0))
    status[0,0] = 1 # set queued status
    n_notvisited -= 1
    n_queued += 1
        
    "this algorithm is based on breadth first search graph algorithm"
    while(n_queued > 0):
        
        "here we give preference to white elements over black"
        if(len(w_queue) > 0):
            
            n_processed += 1
            n_queued -= 1
            
            "remove the item from queue"
            loc = w_queue[0]
            del w_queue[0]
            
            pore.append(loc) #add to the pore
            
            status[loc[0], loc[1]] = 2 #set processed status
            adjncy_list = get_adjncy_list(loc, bw) # get list of neighbors
            
            "go through the adjncy list and queue the neighbors if not visited"
            for item in adjncy_list:
                i, j = item
                if(status[i, j] == 0): # not visited yet
                    if(bw[i, j] == 1):  
                        "queue in white queue"
                        w_queue.append(item)
                    else:
                        "queue in black list"
                        b_queue.append(item)
                    status[i, j] = 1 # visited status
                    n_queued += 1
                    n_notvisited -= 1

        else:
            
            "if pore has been detected. We need to catalog it"
            if(len(pore) > 0):
                
                pores.append(pore) # catalog the pore
                del pore
                pore = []
                
            "process the black pixels"
            n_processed += 1
            n_queued -= 1
            
            "remove the item from (black) queue"
            loc = b_queue[0]
            del b_queue[0]
            
            status[loc[0], loc[1]] = 2 #set processed status
            adjncy_list = get_adjncy_list(loc, bw) # get list of neighbors        
        
            "go through the adjncy list and queue the neighbors if not visited"
            for item in adjncy_list:
                i, j = item
                if(status[i, j] == 0): # not visited yet
                    if(bw[i, j] == 1):  
                        "queue in white queue"
                        w_queue.append(item)
                    else:
                        "queue in black list"
                        b_queue.append(item)
                    status[i, j] = 1 # visited status
                    n_queued += 1
                    n_notvisited -= 1
                    
    return pores


def threshold_pores(bw, pores, size_threshold = 0):
    '''
    This function goes over the pores list and deletes pores of size (measured in no. of pixels)
    smaller than a certain threshold. It also fills the regions in the black&white image 'bw'
    corresponsing to small pores (size < size_threshold)
    '''
    final_pores = []
    for pore in pores:
        if(len(pore) < size_threshold): #len(pore) = number of pixels in the pore
            for loc in pore:
                i, j = loc
                "fill the small pores"
                bw[i, j] = 0
        else:
            final_pores.append(pore)
                                       
    return final_pores    
    
def plot_pores(bw, pores):
    '''
    This code plots an RGB image showing pores in different colors
    '''
    N_pores = len(pores)
    
    "set the colors"
    norm = mpl.colors.Normalize(0, N_pores)
    cmap = cmx.jet
    m = cmx.ScalarMappable(norm, cmap)
    
    "convert the bw to rgb image"
    sx, sy = bw.shape
    img = np.zeros((sx, sy, 3))
    img[:,:,0] = bw[:,:]
    img[:,:,1] = bw[:,:]
    img[:,:,2] = bw[:,:]
    
    "paint the pores with colors"
    colrs = np.arange(len(pores))
    np.random.shuffle(colrs)
    for i, pore in enumerate(pores):
        r, g, b, alpha = m.to_rgba(colrs[i]) # get the color and alpha
        for loc in pore:
            x, y = loc
            img[x, y, 0] = r
            img[x, y, 1] = g
            img[x, y, 2] = b             
            
    "show the image"
    plt.imshow(img)
    
    return
    
    
############################### MAIN SCRIPT ###################################
# enter the pixel_size in terms of micrometer^2
pixel_size = 1.35**2

# Read the BW image
img = mpimg.imread('I8_bw.png')

#convert the image to binary
#bw = img[:,:,0]
bw = img[:,:]

#detect the pores
pores = get_pores(bw)

#delete the small pores
pore_size_threshold = 20 #atleast this size 
pores = threshold_pores(bw, pores[:], pore_size_threshold)

#plot an RGB representation of pores
plot_pores(bw, pores)
##############################################################################
