#-*-coding:utf-8-*-
#@author:lijinxi
import os
'''
寻找因为TimeOut或其他异常因素而未完成的html
'''
def findfile():
    allfile=[]
    with open('result.txt','r',encoding='utf-8') as f:
        for i in f:
            allfile.append(i.strip())
    print(allfile)
    partfile=[]
    #for i in os.listdir('./htmls/'):
        #partfile.append(i.replace('.html',''))
    for i in os.listdir('./pdfs/'):
        partfile.append(i.replace('.pdf', ''))
    losefile=[]
    for i in allfile:
        if i in partfile:
            continue
        else:
            losefile.append(i)
    with open('losefile.txt','w',encoding='utf-8') as f:
        for i in losefile:
            f.write(i+'\n')

if __name__ == '__main__':
    findfile()