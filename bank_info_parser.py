# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 14:45:40 2018

@author: 455495
"""

#import sys
import re
import uniout  #(*for chinese list)
import _uniout


class NewBankPassbook:
    def __init__(self):
        #pass
        self.bank  = ''
        self.bank_id = ''
        self.saveCharImg = 0
        self.bgImg = ''
        self.pages = 20
        self.totalRow = 24
        self.totalCol = 6
        self.fontsize = 36
        self.fonttype = ''
        self.font = 0
        self.maxShift_X = 0
        self.maxShift_Y = 0
        self.max_shift_block = 0
        self.shift_mode = 0
        self.col_item = ''
        self.right_align = []
        self.memo_out = ''
        self.memo_in = ''
        self.banksStr = ''
        self.shopStr = ''
        self.usernameStr = ''
        self.atmStr = ''
        self.debitStr = ''
        

    def getTotalCol(self):
        return len(self.col_item)
        
    ## print data
    def printall(self):
        print (self.bank                    + ', ' +\
              self.bank_id                  + ', ' +\
              str(self.saveCharImg)         + ', ' +\
              self.bgImg                    + ', ' +\
              str(self.pages)               + ', ' +\
              str(self.font)                + ', ' +\
              str(self.fontsize)            + ', ' +\
              str(self.maxShift_X)          + ', ' +\
              str(self.maxShift_Y)          + ', ' +\
              str(self.max_shift_block)     + ', ' +\
              str(self.shift_mode)          + ', ' +\
              str(self.totalRow)            + ', ' +\
              str(self.col_item)            + ', ' +\
              str(self.right_align)         + ', ' +\
              str(self.getTotalCol()))
        print str(self.memo_out)           
        print str(self.memo_in)           
        print str(self.banksStr)
        print str(self.shopStr)            
        print str(self.usernameStr)
        print str(self.atmStr)              
        print str(self.debitStr) 
        print ('\n')
              

       
def splitStrWithComma(Str, isUnicode=0):
    if (',' in Str):
        if (isUnicode):
            return [unicode(x.strip(),'UTF-8') for x in Str.split(',')]
        else:
            return [x.strip() for x in Str.split(',')]
    else:
        if (isUnicode):
            return [unicode(Str,'UTF-8')]
        else:
            return [Str]
        
        
def read_general_bank_info(infofile):
    lineNo = 0

    try:
        allBank = []
        curBank = None
        with open(infofile) as f:
            for line in f:
                lineNo +=1
                line = line.strip()                         ## remove space before and after data, and '\n'
                if (len(line)== 0):
                    continue
                if (line[0] == '#'):                        ## skip comment line
                    continue
                if (line[0] == '{'):
                    curBank = NewBankPassbook()             ## start a new bank
                    continue
                if (line[0] == '}'):
                    allBank.append(curBank)                 ## save this bank
                    continue

                line = re.sub("'","",line)                  ## remove (')
                line = re.sub('\[\]\@\!\$\%','', line)      ## remove special character ([]@!$%)
                data = line.split('=')                      ## remove space and split data into variable/value
                data = [x.strip() for x in data]
                
                if (data[0] == 'bank'):
                    curBank.bank = data[1]
                elif (data[0] == 'bank_id'):
                    curBank.bank_id = data[1] 
                #elif (data[0] == 'saveCharImg'): 
                #    curBank.saveCharImg = int(data[1])
                elif (data[0] == 'bgImg'):
                    curBank.bgImg = data[1]
                elif (data[0] == 'pages'): 
                    curBank.pages = int(data[1])
                elif (data[0] == 'font_type'): 
                    curBank.fonttype = data[1]
                elif (data[0] == 'font_size'): 
                    curBank.fontsize = int(data[1])
                elif (data[0] == 'maxShift_X'): 
                    curBank.maxShift_X = int(data[1])
                elif (data[0] == 'maxShift_Y'): 
                    curBank.maxShift_Y = int(data[1])
                elif (data[0] == 'shift_mode'): 
                    curBank.shift_mode = int(data[1])
                elif (data[0] == 'max_shift_block'): 
                    curBank.max_shift_block = int(data[1])
                elif (data[0] == 'total_row'):
                    curBank.total_row =  int(data[1])
                elif (data[0] == 'col_item'):
                    curBank.col_item = splitStrWithComma(data[1])
                    curBank.totalCol = curBank.getTotalCol()
                elif (data[0] == 'right_align'):
                    curBank.right_align = [int(x) for x in splitStrWithComma(data[1])]
                elif (data[0] == 'MEMO_OUT'):
                    curBank.memo_out = splitStrWithComma(data[1],1)
                elif (data[0] == 'MEMO_IN'):
                    curBank.memo_in = splitStrWithComma(data[1],1)
                elif (data[0] == 'SHOP_STR'):
                    curBank.shopStr = splitStrWithComma(data[1],1)
                elif (data[0] == 'USERNAME_STR'):
                    curBank.usernameStr = splitStrWithComma(data[1],1)
                elif (data[0] == 'BANK_STR'):
                    curBank.banksStr = splitStrWithComma(data[1],1)
                elif (data[0] == 'ATM_STR'):
                    curBank.atmStr = splitStrWithComma(data[1],1)
                elif (data[0] == 'DEBIT_STR'):
                    curBank.debitStr = splitStrWithComma(data[1],1)

            f.close()    
            return allBank
            
    except ValueError:
        print('data type error. Cound not convert data.')
    except IOError:
        print ('Info file not found.')
    except:
        print ('error, line %d' % (lineNo))
        
        
if __name__ == "__main__":
    
    allBank = read_general_bank_info('../source/bank_info.txt')
    allBank[0].printall()
    allBank[1].printall()
    