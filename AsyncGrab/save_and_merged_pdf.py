#--coding:utf-8--
#@author:lijinxi
from PyPDF2 import PdfFileReader,PdfFileWriter
import threading
import pdfkit
options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',



        'encoding': "UTF-8",
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
        'cookie': [
            ('cookie-name1', 'cookie-value1'),
            ('cookie-name2', 'cookie-value2'),
        ],
        'outline-depth': 10,
    }

def topdf(html,pdf):
    pdfkit.from_file(html,pdf,options=options)

def save_merge(savefile):
    htmlslist=[]
    pdflist=[]
    with open('result.txt','r',encoding='utf-8') as f:
        for title in f:
            if title!='':
                title=title.replace('\n','').strip()
                htmlslist.append('./htmls/'+str(title)+'.html')
                pdflist.append('./pdfs/'+str(title)+'.pdf')
    threads=[]
    len1=len(htmlslist)
    '''
    for i in range(len1):
        threads.append(threading.Thread(target=topdf,args=(htmlslist[i],pdflist[i])))
    for t in threads:                 # threading
        t.setDaemon(daemonic=True)
        t.start()
        t.join()
    '''
    out = PdfFileWriter()
    outpages = 0
    print(pdflist)
    for pdf in pdflist:
        fin = PdfFileReader(open(pdf, 'rb'))
        pageCount = fin.getNumPages()
        title = fin.getDocumentInfo()['/Title'].replace(' — python3-cookbook 3.0.0 文档', '')  # 添加书签信息
        print(title)
        outpages += pageCount
        print("页数：%d" % pageCount)
        for i in range(pageCount):
            out.addPage(fin.getPage(i))
        out.addBookmark(title=title, pagenum=outpages - pageCount)
    print('总页数：%d' % outpages)
    fout = open(savefile, 'wb')
    out.write(fout)
    fout.close()


if __name__ == '__main__':
    save_merge('python3_cookbook.pdf')