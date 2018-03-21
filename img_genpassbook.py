# -*- coding: utf-8 -*-
"""
Created on Thu Feb 08 11:00:33 2018

@author: 455495
"""
# -*- coding: utf8 -*-
# coding: utf8  (*for chinese word)
#import uniout  #(*for chinese list)
#import _uniout

#This file: "cv_general.py"
#Python 2-3 compatible
try:
    xrange
except NameError: # will be 3.x series
    xrange = range
#
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import datetime
import random
import os 
from os import listdir
from os.path import isfile, join, isdir, splitext

from img_passbook              import   get_Coords, convert_to_gray
from print_f.print_f           import print_spaceL, new_RGBA_text, get_word_width
from dict.bank_info_parser       import read_general_bank_info, NewBankPassbook
from dict.bank_table             import get_bankdataline, get_AcRow
from dict.info_dict              import get_autogenWDB
from img_process.general       import   im_save, im_image_paste_to_bottomImage


#-------------------------------------------------------------------------------
#   get_font()
#   get a font from 'font/'.
#   if randomMode is off, 'wt001.tff' is used as default
#-------------------------------------------------------------------------------                             
def get_font(cur_path, randomMode = 0):
    cur_path = join(cur_path, 'font/')
    if (randomMode):
        onlyfiles = [f for f in listdir(cur_path) if isfile(join(cur_path, f))]
        randfont = random.randint (0, len(onlyfiles)-1)
        font = cur_path + onlyfiles[randfont]
    else:    
        font = cur_path +'wt001.ttf'
    return  font




#-------------------------------------------------------------------------------
#   isChinese()
#   check if 'ch' is a printable ascii character,
#   if yes, it is a character able to be printed alone
#   otherwise, it is a port of a chinese character    
#-------------------------------------------------------------------------------    
def isChinese(ch):
    if (ord(ch)>=32) and (ord(ch)<=126):
        return False
    else:
        return True

        
    

#-------------------------------------------------------------------------------    
#   set_drawTxt()        
#   this function does multiple actions: 
#   1. print 'cell' on 'txt'(text image) at 'x,y' with 'font/text_color/font_size'
#   2. add this 'cell' into 'xmlfile'(.xml file) according to it data type (by referencing 'col_item')        
#      while, font type and text width/height will be needed on the .xml dataline.
#   3. if the global 'saveChar' is true, every single character will be save as an image and stored under 'outdir'
#-------------------------------------------------------------------------------    
def set_drawTxt(txt, cell, col_item, row, col, x, y, font, font_type, text_color, font_size, xmlfile, outdir):

    global saveChar
    global saveImgNo
    
    saveTempImgName = ''
    if saveChar:
        if os.path.exists(outdir) is False:
            os.makedirs(outdir)

     
    chCnt = 0  
    xmlCell = cell.encode('UTF-8').strip()
    
    fontStr = font_type.split('/')[-1]  ## get the filename of the font type
    
    if col_item != None:
        ## the 1st row
        ## warning: CTBC has 'continued' printed on the 1st row, it has 3 items on this line
        ##          otherwise, there should be only 2 items (account number field and remain balance field)
        if row == 0:
            if ((len(col_item)==4) and (col ==0)):
                xmlfile.write('\t\t<AccountNoField>\n')
            elif ((len(col_item)==3) and (col ==0)) or \
                 ((len(col_item)==4) and (col ==2)):
                xmlfile.write('\t\t<ContinuedField>\n')
            elif ((len(col_item)==3) and (col ==1)) or \
                 ((len(col_item)==4) and (col ==1)):
                xmlfile.write('\t\t<AccoountField>\n')
            elif ((len(col_item)==3) and (col ==2)) or \
                 ((len(col_item)==4) and (col ==3)):
                xmlfile.write('\t\t<RemainBalanceField>\n')
        ## for the rest of the dataline should be transaction for each line
        elif (row > 0):
            ## if it is the beginning of the row, 'transaction Record Row' tag is added
            if (col ==0):
                xmlfile.write('\t\t<TransactionRecordRow index = \"%d\">\n' % row)
            ## add the item string as field tag
            if (len(cell.strip())>0):    
                xmlfile.write('\t\t\t<%sField>\n' % col_item[col])
    else:
        xmlfile.write('\t\t<TurnPageField>\n')
        
    x_lcl = x    
    y_lcl = y
    ch_x, ch_width = 0, 0

    if len(xmlCell):
        i = 0
        ## break the cell into characters
        while i < len(xmlCell):
            if saveChar:
                imgfile = "{:0>5d}.jpg".format(saveImgNo)
                #imgfile = "temp.jpg"
                saveTempImgName =  join(outdir, imgfile)
            ## get the x/y/width/height of this single character, if saveChar is enable. the image will be created in this function        
            ch_x, ch_y, ch_width, ch_height = get_word_width(cell[chCnt], font_type=font_type, font_size=font_size, saveImgName = saveTempImgName)
            
            #saveImgName = saveTempImgName
            if (saveChar and ch_width>0):
                saveImgNo +=1
                #if isinstance(cell[chCnt],unicode):
                #    uni_imgfilename = cell[chCnt]+unicode('_{}_{}.jpg'.format(font_size,fontStr), 'UTF-8')
                #else:                    
                #    uni_imgfilename = unicode('{}_{}_{}.jpg'.format(cell[chCnt],font_size,fontStr), 'UTF-8')
                #saveImgName = join(outdir,uni_imgfilename)
                
                #if (isfile(saveImgName) is False):
                #    os.rename(saveTempImgName, saveImgName)
                #    saveImgNo +=1

            if (row>0):
                xmlfile.write('\t')                

            if (isChinese(xmlCell[i])):
                ## if this character is a part of a chinese character, combine the rest of 2 into a chinese character
                ch = xmlCell[i:i+3]
                ## get the printed width of this character
                charPrintWidth = txt.textsize(unicode(ch,'utf-8'), font)[0]
                ## draw text on the text image, need to decode to' utf-8'
                txt.text((x_lcl, y_lcl), unicode(ch,'utf-8'), font=font, fill=text_color)
                i+=3
            else:    
                ## if this character is a printable ascii character, print it
                ch = xmlCell[i]
                ## get the printed width of this character
                charPrintWidth = txt.textsize(ch, font)[0]
                ## draw text on the text image
                txt.text((x_lcl, y_lcl), ch, font=font, fill=text_color )
                i+=1
            ## compose the dataline of xml data
            xmlfile.write('\t\t\t<Char index=\"%d\" bbox=\"%d,%d,%d,%d\" value=\"%s\" font=\"%s\"/>\n' % (chCnt+1,x_lcl+ch_x,y_lcl+ch_y,ch_width,ch_height, ch,fontStr))           
            ## set the location of x according to the minimum needed text_width
            if (ch_width ==0):
                x_lcl +=charPrintWidth
            else:                
                x_lcl += min(charPrintWidth, ch_x+ch_width+2)
            chCnt+=1
            

    if col_item != None:
        ## the closing tag of the row
        if row == 0: 
            if ((len(col_item)==4) and (col ==0)):
                xmlfile.write('\t\t</AccountNoField>\n')
            elif ((len(col_item)==3) and (col ==0)) or \
                 ((len(col_item)==4) and (col ==2)):
                xmlfile.write('\t\t</ContinuedField>\n')
            elif ((len(col_item)==3) and (col ==1)) or \
                 ((len(col_item)==4) and (col ==1)):
                xmlfile.write('\t\t</AccoountField>\n')
            elif ((len(col_item)==3) and (col ==2)) or \
                 ((len(col_item)==4) and (col ==3)):
                xmlfile.write('\t\t</RemainBalanceField>\n')
        elif (row > 0):
            if (len(cell.strip())>0):    
                xmlfile.write('\t\t\t</%sField>\n' % col_item[col])   
            
            if  col == (len(col_item)-1):
                xmlfile.write('\t\t</TransactionRecordRow>\n')
        
    else:
        xmlfile.write('\t\t</TurnPageField>\n')

    ## return 'txt'(text image) for next operation
    return txt





#-------------------------------------------------------------------------------    
#   data_augmentation()
#   generates passbook images by using the curbank information    
#   the specified passbook background image will be used as background.
#-------------------------------------------------------------------------------    
def data_augmentation(root_path, curbank):
    
    global saveChar
    master_img = curbank.bgImg
    
    bgimgsub_s = master_img.split('/')[-1].split('.')[0]
    Coord_X, Coord_Y = get_Coords(master_img)
    #for x in Coord_X: print ('x = %d' % (x))
    #for y in Coord_Y: print ('y = %d' % (y))
    print ('data augmentation started...')

    im          = Image.open(master_img)
    im_w, im_h  = im.size
    nim         = im.copy()

    ## 'pages' of images will be produced
    saveChar    = curbank.saveCharImg
    pages       = curbank.pages
    font_size   = curbank.fontsize
    
    ## shift(x,y) will be randomly picked 
    maxShift_X     = curbank.maxShift_X//4
    maxShift_Y     = curbank.maxShift_Y//4
    mu_X = np.mean(range(-maxShift_X,maxShift_X+1))
    sigma_X = np.std(range(-maxShift_X,maxShift_X))
    mu_Y = np.mean(range(-maxShift_Y,maxShift_Y+1))
    sigma_Y = np.std(range(-maxShift_Y,maxShift_Y))
    rows_all    = pages * curbank.totalRow

    Ndivide     = pages/1000 if(pages/1000 is not 0) else 1
    days        = rows_all/Ndivide
    date_begin  = datetime.datetime.now()- datetime.timedelta(days=days)
    day_step    = datetime.timedelta(days=1)
    date        = date_begin
    day_count   = 0
    

    balance     = 1e5 * random.randint(1,5);
    withdraw_cyc= len(curbank.memo_out)
    income_cyc  = len(curbank.memo_in)
    interest = 0.01

    img_dirPath = 'out/'
    rowIDmax    = len(Coord_Y)
    
    ## add the width of the passbook image as the boundary information    
    Coord_X.append(im_w)
    
    if os.path.exists(img_dirPath) is False:
        os.makedirs(img_dirPath)
    ## generates the passbook image one-by-one, every images will have its .xml file correspondingly
    for page in xrange(pages):
        imgID       = page
        img_fileName= '%s_%s_%06d.jpg' %(curbank.bank, bgimgsub_s, imgID)
        xml_fileName= '%s_%s_%06d.xml' %(curbank.bank, bgimgsub_s, imgID)
        font_type   = get_font(root_path, randomMode = 1)
        
        print (join(img_dirPath,xml_fileName))
        #xml_file = open(join(img_dirPath,xml_fileName),'w')
        with open(join(img_dirPath,xml_fileName),'w') as xml_file:
            im_txt, draw_txt, font = new_RGBA_text(im_w, im_h, font_type, font_size)
            curbank.font = font_type
            rowIDmax_toPrint= random.randint(5,rowIDmax*2)
            xShift, yShift = 0,0
            
            ## add xml beginning
            
            xml_file.write('<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n')
            xml_file.write('<Page box=\"0,0,{},{}\">\n'.format(im_w,im_h))
            xml_file.write('\t<Passbook{} box=\"0,0,{},{}\">\n'.format(curbank.bank_id,im_w,im_h))
                
            shiftBlock = 0
            for row, coordy in enumerate(Coord_Y):
                if shiftBlock == 0:
                    ## pick a font type for this data block
                    font_type   = get_font(root_path, randomMode = 1)
                    curbank.font = font_type
                    font     = ImageFont.truetype( font_type, font_size);
                    shiftBlock = random.randint(0, curbank.max_shift_block)
                    xShift = random.randint(-maxShift_X, maxShift_X) if (curbank.shift_mode) else int(min(maxShift_X, max(-maxShift_X, random.gauss(mu_X,sigma_X))))
                    yShift = random.randint(-maxShift_Y, maxShift_Y) if (curbank.shift_mode) else int(min(maxShift_Y, max(-maxShift_Y, random.gauss(mu_Y,sigma_Y))))
                    xShift *=4
                    yShift *=4
                else:
                    ## block line number count down
                    shiftBlock -=1
                
                ## generates date
                if(day_count%Ndivide is 0): 
                    date+= day_step 
                    day_count+=1
                if (row < rowIDmax) and (row < rowIDmax_toPrint):
                    ## text's color:
                    text_color = (0,0,0, random.randint(120,255))
                    
                    ## the first account line:
                    if row == 0:
                        acRow, x_st = get_AcRow(curbank, balance, Coord_X)
                        for col, coordx in enumerate(x_st):       
                            
                            y, x = coordy + yShift, coordx + xShift
                            cell = acRow[col]
    
                            if (curbank.bank=='CTBC') and (col ==0):
    
                                cell = unicode("承前頁",'UTF-8')
    
                            if (curbank.bank=='LAND'): 
                                y, x = coordy, coordx  ## don't shift for these cells
                                if (col ==0):
                                    cell = unicode("帳號(A/C NO)",'UTF-8')
                                elif (col ==2):
                                    cell = unicode("承前頁",'UTF-8')
                                    
    
                            draw_txt = set_drawTxt(draw_txt,cell,acRow,row,col,x,y,font=font, font_type=font_type, text_color=text_color,\
                                                   font_size=font_size, xmlfile = xml_file, outdir = join(img_dirPath, "charImg"))
                    else:                            
                    ## transactions of inner page:
                        
                        ## start_action: to skip withdrawal action, deposit comes after withdrawal 
                        ## +1 to skip interest if balance is 0 (interest counts on balance)
                        action_st = 0 if (int(balance*interest)>0) else (withdraw_cyc+1) 
                        action = random.randint(action_st, withdraw_cyc+income_cyc-1) 
                        withdrawal, deposit, balance, = \
                        get_autogenWDB(action, balance, income_cyc, withdraw_cyc,incomeRatio = interest) 
                        
                        ## get dataline from specified bank format
                        words = get_bankdataline(curbank, date, action, withdrawal, deposit, balance)
    
                        ## col by col
                        for col, coordx in enumerate(Coord_X):
                            if (col<(len(words))):  ## skip the last entry: end_of_line
                                if len(words[col]):
                                    cell = words[col]
                                    ## set the printing shift(x,y)
                                    y, x = coordy + yShift, coordx + xShift
                                    ## if the item is set as right-align
                                    if (curbank.right_align[col]):
                                        _,_,text_width, _ = get_word_width(cell, font_type=font_type, font_size=font_size)
                                        x += Coord_X[col+1] - coordx    
                                        x = min(Coord_X[-1]-text_width- font_size/2 ,  x-text_width- font_size/2 )  # font_size/2 is for slightly off the end on the right
                                        
                                    ## set text into text image, and write dataline into .xml, and save character images as well    
                                    draw_txt = set_drawTxt(draw_txt,cell,curbank.col_item,row,col,x,y,font=font, font_type=font_type, text_color=text_color,\
                                                           font_size=font_size, xmlfile = xml_file, outdir = join(img_dirPath, "charImg"))  
                                    
            ## for CTBC, extra 'please turn page' is to be printed                                        
            if (curbank.bank=='CTBC') and (rowIDmax_toPrint >= rowIDmax):
                x = im_w-250
                y = 2*Coord_Y[-1]-Coord_Y[-3] + yShift
                draw_txt = set_drawTxt(draw_txt,unicode("請翻次頁",'UTF-8'),None,-1,-1,x,y,font=font, font_type=font_type, text_color=text_color, \
                                       font_size=font_size, xmlfile = xml_file, outdir = join(img_dirPath, "charImg"))
    
            if (curbank.bank=='LAND'):
                x = 833
                y = 1616
                draw_txt = set_drawTxt(draw_txt,unicode("過次頁",'UTF-8'),None,-1,-1,x,y,font=font, font_type=font_type, text_color=text_color, \
                                       font_size=40, xmlfile = xml_file, outdir = join(img_dirPath, "charImg"))
    
    
            
            ## before ending this page, add ending tags of .xml files, and then save and close .xml
            xml_file.write('\t</Passbook{}>\n'.format(curbank.bank_id))
            xml_file.write('</Page>\n')
            xml_file.close()
        
        ## dave the text image and paste onto the passbook background image. save as .jpg in the end
        nim_save= im_image_paste_to_bottomImage(nim.copy(), im_txt, \
            box=(0, 0), mask=im_txt, show=False, delay_ms=200,\
            win_title='paste txt to master image')
        nim_save = nim_save.convert("RGB")
        im_save(nim_save, img_dirPath, img_fileName, saveFormat='JPEG')
        
    print ('augmentation done.\n')                                      
    return

    

if __name__ == "__main__":
    ## set global varialbles for saving character images for training. 
    ## starting from 0, increased the index after every character image is saved.
    saveChar = 0    
    saveImgNo = 0                                    
    
    allBank = read_general_bank_info('./source/bank_info.txt')
    for bank in allBank:
        data_augmentation('./', bank)
