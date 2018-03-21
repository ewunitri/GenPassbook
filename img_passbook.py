# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 16:22:18 2018

@author: 455495
"""
from os.path import isfile
import imutils
import numpy as np
import cv2
import sys

saveImgforDebug = 0


#-------------------------------------------------------------------------------
# saveCvImg
# save debug image by referencing 'alwaysSave'
#-------------------------------------------------------------------------------

def saveCvImg(imgName, img, alwaysSave = 0):
    if (alwaysSave):
        cv2.imwrite(imgName, img)
        
        
        
#-------------------------------------------------------------------------------
#   convert_to_gray()
#   before return the grayscalce img, guassianBlur(7x7 kernel) is applied
#-------------------------------------------------------------------------------
def convert_to_gray(img, doBlur = 0):
    
    if (doBlur is 0):
        img = cv2.GaussianBlur(img,(7,7),0)
    return cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)    



#-------------------------------------------------------------------------------
#   get_edge()
#   return the edge with dilation applied of the image
#-------------------------------------------------------------------------------    
def get_edge(img):
    ## convert into binary
    ret, img_b = cv2.threshold(img,254, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU) #220, 255
    #edges = cv2.Canny(img_b,200,230,apertureSize = 3)    
    edges = cv2.Canny(img_b,230,250,apertureSize = 3)    

    dilate = cv2.dilate(edges,np.ones((3,3)),2)
    #saveCvImg('source/dilate3_2.jpg', dilate, saveImgforDebug)    
    return dilate





#-------------------------------------------------------------------------------
#   add_item()
#   check if 'i' is considered to be added in data_list.
#   add 'i' only when there is no item within the margin of 'i',
#   or i in within the margin of someone but larger, 
#   then add 'i' and remove that someone as 'i' is considered better
#-------------------------------------------------------------------------------
def add_item(data_list, i, margin):
    
    for x in data_list:
        if ((i<x) and ((x-i) < margin)):    ## within the margin considered as the same data
            return data_list
        elif (i>x) and (i - x < margin) :   ## within the margin but larger,considered as the same but better data
            data_list.remove(x)
            data_list.append(i)
            return data_list
    data_list.append(i)                     ## a suitable item to be appended
    
    return data_list    





#-------------------------------------------------------------------------------
#   pick_horizontal_line()
#   paste the lines that is long enough as a row separator on the original image,
#   and ask user to look at the result from the output file and pick the 4 lines.
#   the location of the four lines are returned
#-------------------------------------------------------------------------------
def pick_horizontal_line(bg_img, lines, indent=0):
    img_hor = bg_img.copy()
    
    
    for line in lines:
        cv2.line(img_hor, (indent, line), (img_hor.shape[1]-indent,line), 255, 2, cv2.LINE_AA)       
    
    #print (img_hor.shape) #shape: height, width. channels
    img_hor_small = cv2.resize(img_hor, (0,0), fx=0.5, fy=0.5)
    
    saveCvImg('source/houghlines_h_small.jpg',img_hor_small, 1) 
    
    in_str = []
    
    picked_line=[]
    while (len(picked_line)!= 4):
        in_str = raw_input("check file [houghlines_h_small.jpg] and pick the lines: ")
        if (in_str[0] is 'q'):
            return None
    
        lines_no = list(map(int,in_str.split()))
        lines = np.array(lines)
        picked_line = list(lines[lines_no])
    
    return picked_line





#-------------------------------------------------------------------------------
#   find_row_location()
#   use find Contours to locate the center of the row lines, 
#   user can pick the boundaries of the up/down 2 pages. 
#   then calculate the average row height. 
#   ignore_margin refers to the lines within this margin will be considered as 
#   on the same line     
#   return row location after calculation
#-------------------------------------------------------------------------------
def find_row_location(img, img_row, ignore_margin = 20):
    ## in case lines on the same row are mis-retrieved, set ignored margin to solve this issue
    ## eg. within 50 pixels, consider there is only one column line (pick the left most)
    
    close = cv2.morphologyEx(img_row,cv2.MORPH_DILATE,None,iterations = 2);
    #saveCvImg('source/close_img_row.jpg',close, saveImgforDebug) 

    cnts = cv2.findContours(close.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE);
    cnts = cnts[0] if imutils.is_cv2() else cnts[1];
    
    rowCntPerPage=[]
    while (len(rowCntPerPage)!= 2):
        in_str = raw_input("Input row count per page: ")
        if (in_str[0] is 'q'):
            return None
    
        rowCntPerPage = list(map(int,in_str.split()))
                       
    loc = []    
    for c in cnts:
        ## compute the center of the contour
        M  = cv2.moments(c)
        cY = int(M["m01"] / M["m00"])       ## center of gird point: cY
        loc = add_item(loc, cY, ignore_margin)
    loc.sort()
    
    temp_loc = pick_horizontal_line(img, loc)
    if (temp_loc is None):
        return None
    new_loc = []
    page  = 0
    
    for x in rowCntPerPage: 
        lineHeight = (temp_loc[page*2+1] - temp_loc[page*2]) / rowCntPerPage[page];
        newList = range(0,x)
        newList = [ i* lineHeight + temp_loc[page*2] for i in newList]
        new_loc.append(newList)        
        page +=1        
    
    return new_loc[0] + new_loc[1]




#-------------------------------------------------------------------------------
#   pick_vertical_line()
#   paste the lines that is long enough as a row separator on the original image,
#-------------------------------------------------------------------------------
def pick_vertical_line(bg_img, lines, indent=0):
    img_ver = bg_img.copy()
    
    
    for line in lines:
        cv2.line(img_ver, (line, indent), (line, img_ver.shape[1]-indent), 255, 2, cv2.LINE_AA)       
    
    #print (img_hor.shape) #shape: height, width. channels
    img_ver_small = cv2.resize(img_ver, (0,0), fx=0.5, fy=0.5)
    saveCvImg('source/houghlines_v_small.jpg',img_ver_small, 1) 
    
    in_str = []
    
    picked_line=[]
    while (len(picked_line)== 0):
        in_str = raw_input("check file [houghlines_v_small.jpg] and pick the lines: ")
        if (in_str[0] is 'q'):
            return None
    
        lines_no = list(map(int,in_str.split()))
        lines = np.array(lines)
        picked_line = list(lines[lines_no])
    
    return picked_line




#-------------------------------------------------------------------------------
#   find_column_location()
#   use find Contours to locate the center of the column lines, 
#   ignore_margin refers to the lines within this margin will be considered as 
#   on the same line   
#   return all detectable column location    
#-------------------------------------------------------------------------------
def find_column_location(img, img_col, ignore_margin = 50):
    ## in case lines on the same column are mis-retrieved, set ignored margin to solve this issue
    ## eg. within 50 pixels, consider there is only one column line (pick the left most)
    close = cv2.morphologyEx(img_col,cv2.MORPH_DILATE,None,iterations = 2);
    saveCvImg('source/find_column_location_close.jpg',close,saveImgforDebug) 
    cnts = cv2.findContours(close.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1];
    loc = []    
    for c in cnts:
        ## compute the center of the contour
        M  = cv2.moments(c)
        cX = int(M["m10"] / M["m00"])       ## center of gird point: cX
        loc = add_item(loc, cX, ignore_margin)
    loc.sort()
    loc = pick_vertical_line(img, loc)
    
    return  loc




    
#-------------------------------------------------------------------------------
#   fetch_line()
#   After getting detectable lines, separate the lines into horizontal and vertical    
#   return both images    
#-------------------------------------------------------------------------------
def fetch_line(master_img='source/0.png'):
    
    page_right_indent = 50
    img = cv2.imread(master_img)
    gray = convert_to_gray(img)
    width, height, channels = img.shape
    edges = get_edge(gray)
    saveCvImg('source/edges.jpg',edges,saveImgforDebug) 
    lines = cv2.HoughLinesP(image=edges,rho=1,theta=np.pi/180, threshold=330,lines=np.array([]), minLineLength=100,maxLineGap=80)
    
    a,b,c = lines.shape

    img_ver = np.zeros((width,height, 1), np.uint8);
    img_hor = np.zeros((width,height, 1), np.uint8);
    for i in range(a):
        x1,y1,x2,y2 = lines[i][0]
        thr = 3
        
        ## vertical lines
        if ((x1+ page_right_indent <width) and (abs(x1-x2)<thr) and (abs(y1-y2)>(height/3))):
            cv2.line(img_ver, (x1, y1), (x2,y2), 255, 1, cv2.LINE_AA)
            
        ## horizontal line    
        if ((abs(x1-x2)>(width/3)) and (abs(y1-y2)<thr)):
            cv2.line(img_hor, (x1, y1), (x2,y2), 255, 1, cv2.LINE_AA)        
            
        saveCvImg('source/houghlines_v.jpg',img_ver,saveImgforDebug) 
        saveCvImg('source/houghlines_h.jpg',img_hor,saveImgforDebug) 
    
    return img_ver, img_hor, img





#-------------------------------------------------------------------------------
#   getCoordFilename()
#   return the grid coordination filename according the passbook image filename   
#-------------------------------------------------------------------------------
def getCoordFilename(imgPath):
    return  (imgPath.split('.'))[0]  +'_coord_result.txt'





#-------------------------------------------------------------------------------
#   check_coord_result_file_existed()
#   check if the coordination file is existed. 
#   If positive, return True and the row/column location points read from txt file
#   otherwise, return False    
#-------------------------------------------------------------------------------
def check_coord_result_file_existed(imgPath):
    resultFilename = getCoordFilename(imgPath)
    if (isfile(resultFilename)):
        with open(resultFilename) as f:
            Xs_line = f.readline().rstrip()
            Ys_line = f.readline().rstrip()  
            f.close()
        Xs = [int(x) for x in Xs_line.split(',')]
        Ys = [int(y) for y in Ys_line.split(',')]
        fileExisted = True
    else:
        Xs = 0
        Ys = 0
        fileExisted = False
        
    return Xs, Ys, fileExisted    




    
#-------------------------------------------------------------------------------
#   gen_coord_result_file()
#   generate the coordination text file    
#   from horizontal lines and vertical lines information, 
#   put the point of the leftTop corner of each cell on the passbook image. 
#   save the row/column information into a txt file    
#-------------------------------------------------------------------------------
def gen_coord_result_file(master_img):
    print ('[generate coordinate result file]')
    img_ver_line, img_hor_line, ori_img = fetch_line(master_img);
    Xs = find_column_location(ori_img,img_ver_line)
    Ys = find_row_location(ori_img, img_hor_line)        
    
    if ((Ys is None) or (Xs is None)):
        return None, None
    for y in Ys:
        for x in Xs:
            #print('%d, %d' % (x,y))
            cv2.circle(ori_img,(x,y), 5, (255,0,0), -1)
    saveCvImg('source/grid_with_points.jpg', ori_img, 1)   

    coordFilename = getCoordFilename(master_img)
    outCoordFile = open(coordFilename,'w')
    delimeter = ','
    Xs_str = delimeter.join([str(x) for x in Xs])
    Ys_str = delimeter.join([str(y) for y in Ys])
    outCoordFile.write(Xs_str +'\n')
    outCoordFile.write(Ys_str +'\n')
    outCoordFile.close()
    print ('%s is generated.' % (coordFilename))
    
    return Xs, Ys   
  
    



#-------------------------------------------------------------------------------
#   get_Coords()
#   given a passbook image, find the coordinates on the passbook.
#   row/column locations are returned   
#-------------------------------------------------------------------------------
def get_Coords(master_img):
    ## find result file first
    Xs, Ys, fileExisted = check_coord_result_file_existed(master_img)
    
    if (fileExisted is False):
        Xs, Ys = gen_coord_result_file(master_img)
        if (Ys is None):
            print ('lines not found!')
            return None, None
    else:
        print('Coord result file is existed.')

    return Xs, Ys





if __name__ == "__main__":
    #master_img = 'source/0_1.png'
    if (sys.argv[1:][0]):
        master_img = 'source/'+ sys.argv[1:][0]
        
    else:
        master_img = 'source/0.png'
        print ('parameter missing. 0.png is used!')
    
    get_Coords(master_img)
    
      

        
    