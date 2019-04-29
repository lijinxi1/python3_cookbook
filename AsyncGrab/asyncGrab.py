# --coding:utf-8 --
#@author:lijinxi
import asyncio
from bs4 import BeautifulSoup
import aiohttp
import pdfkit
import  requests
import logging
import time
import re
from PyPDF2 import PdfFileReader,PdfFileWriter
headers={
'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
}
htmlTemplate = '''
<!DOCTYPE html>
<html lang="en">
{head}
    <body>
    {content}
    </body>
</html>'''

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

addscript='''
READTHEDOCS_DATA['page'] = 'c02/p02_match_text_at_start_end'
READTHEDOCS_DATA['source_suffix'] = '.rst'
'''
class AsyncGrab(object):
    def  __init__(self,url,savefile):
        self.url=url
        #self.urls=[]
        self.urls=url
        self.savefile=savefile
        self.results=[]
    def get_urls(self):
        response=requests.get(self.url,headers=headers)
        bsObj=BeautifulSoup(response.text,'html5lib')
        urls=bsObj.find('div',{'class':'toctree-wrapper compound'}).find_all('a',{'class':'reference internal'})
        for url in urls:
            href=url['href']
            if href  not in self.urls:
                self.urls.append(self.url+href)                # absolute path
        #print(self.urls)

    def  parse(self,html):
        try:
            bsObj=BeautifulSoup(html,'html5lib')
            head=bsObj.find('head')
            links=head.find_all('link')
            next=head.find('link',{'rel':'next'})
            prev = head.find('link', {'rel': 'prev'})
            next.extract()
            prev.extract()
            for link in links:
                if link.attrs['href']  is not None:
                    if link['href'].startswith('..') :
                        reallink='https://python3-cookbook.readthedocs.io/zh_CN/latest'+link['href'].replace('..','')
                    elif link['href'].startswith('_'):
                        reallink = 'https://python3-cookbook.readthedocs.io/zh_CN/latest/' + link['href']
                    link['href']=reallink
            scripts=head.find_all('script')
            for script in scripts:
                #print(script)
                if  script.get_text() is not  None:
                    #print(script.get_text())
                    script.extract()
            scripts = head.find_all('script')
            for script in scripts:
                if script['src'].startswith('..'):
                    realscript='https://python3-cookbook.readthedocs.io/zh_CN/latest'+script['src'].replace('..','')
                    script['src']=realscript
            # 上面有一个script不小心删掉,在此加上
            addsp=bsObj.new_tag('script',{'type':'text/javascript'})
            addsp.string=addscript
            head.insert(12,addsp)
            content=bsObj.find('div',{'role':'main','class':'document'})
            #head=BeautifulSoup(headtext,'html5lib')
            # 去掉一些不好看的东西¶,but I fail to do it
            # contentext=(content.text).replace('¶','')
            # content=BeautifulSoup(contentext,'html5lib')
            '''
            aobjs=content.find_all('a')
            print(aobjs)
            for obj in aobjs:
                if obj.get_text=='¶':
                    obj.extract()
            '''
            #regx=re.compile(r'/|(\*?)')
            titleObj=bsObj.find('h1')
            title=titleObj.get_text().strip('¶').replace('/','').replace('*','')
            print(title)
            #titleObj.extract()
            #print(content)
            html=htmlTemplate.format(head=head,content=content)
            with open(r'./htmls/{}.html'.format(str(title)),'w',encoding='utf-8') as f:
                f.write(html)
            #pdfkit.from_file(str(title)+'.html',str(title)+'.pdf',options=options)
        except Exception as e:
            raise e
        if title:
            self.results.append(title)
    async def get_respone(self,url):
        async  with aiohttp.ClientSession() as session:
            async with session.get(url,timeout=30,headers=headers) as resp:
                assert resp.status==200
                html=await resp.read()
                return html
    async  def  get_result(self,url):
        html=await self.get_respone(url)
        self.parse(html)
        print('Done')
    async def hand_tasks(self,work_queue):
        while not work_queue.empty():
            current_url=await work_queue.get()
            try:
                print(current_url)
                time.sleep(20)
                task_status=await  self.get_result(current_url)
            except Exception as e:
                logging.exception('Error for {}'.format(current_url),exc_info=True)

    def eventloop(self):
        q=asyncio.Queue()
        [q.put_nowait(url) for url in self.urls]
        loop=asyncio.get_event_loop()
        tasks=[self.hand_tasks(q) ]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()
        with open('result.txt','w',encoding='utf-8') as f:
            for  r in self.results:
                f.write(r+'\n')

    def save_mergedpdf(self):
        for title in self.results:
            pdfkit.from_file('./htmls/'+str(title)+'./html','./pdfs/'+str(title)+'.pdf',options=options)
        pdflist=['./pdfs/'+str(title)+'.pdf' for title in self.results]
        out = PdfFileWriter()
        outpages = 0
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
        fout = open(self.savefile, 'wb')
        out.write(fout)
        fout.close()

if __name__ == '__main__':

    #asyncgrab=AsyncGrab('https://python3-cookbook.readthedocs.io/zh_CN/latest/','python3-cookbook.pdf')
    #asyncgrab.get_urls()
    #asyncgrab.eventloop()
    #asyncgrab.save_mergedpdf()
    # 处理TimeOut url:
    urls=['https://python3-cookbook.readthedocs.io/zh_CN/latest/c01/p04_find_largest_or_smallest_n_items.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c01/p16_filter_sequence_elements.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c02/p14_combine_and_concatenate_strings.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c04/p13_create_data_processing_pipelines.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c05/p06_io_operations_on_string.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c05/p20_communicating_with_serial_ports.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c06/p06_parse_modify_rewrite_xml.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/chapters/p09_meta_programming.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c09/p08_define_decorators_as_part_of_class.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c09/p12_using_decorators_to_patch_class_definitions.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c09/p16_enforce_argument_signature_on_args_kwargs.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c09/p20_implement_multiple_dispatch_with_function_annotations.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c12/p04_locking_critical_sections.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c12/p09_dealing_with_gil_stop_worring_about_it.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c12/p10_defining_an_actor_task.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c12/p11_implement_publish_subscribe_messaging.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c12/p12_using_generators_as_alternative_to_threads.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c12/p13_polling_multiple_thread_queues.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c13/p01_accept_input_via_redirect_pips_or_input_files.html',
    ]
    urls2=[
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c05/p06_io_operations_on_string.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c09/p16_enforce_argument_signature_on_args_kwargs.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c12/p11_implement_publish_subscribe_messaging.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c12/p12_using_generators_as_alternative_to_threads.html',
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c13/p01_accept_input_via_redirect_pips_or_input_files.html'
    ]
    url=[
        'https://python3-cookbook.readthedocs.io/zh_CN/latest/c12/p08_perform_simple_parallel_programming.html',
    ]
    asyncgrab=AsyncGrab(url,'python3_cookbook.pdf')
    asyncgrab.eventloop()

