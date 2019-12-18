# -*-coding:utf-8-*-
# @author:lijinxi
import asyncio
from bs4 import BeautifulSoup
import aiohttp
import pdfkit
import requests
import logging
import time
import os


class AsyncGrab(object):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                      '/74.0.3729.28 Safari/537.36 OPR/61.0.3298.6 (Edition developer)',
    }
    templates = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title></title>
        {css}
        {js}
    </head>
    <body>
    {content}
    </body>
    </html>"""

    start_time = time.time()

    def __init__(self, start_url, pdf_to_save_name, css_save_path='./_static/css/',
                 js_save_path='./_static/js/'):
        self.start_url = start_url
        self.pdf_to_save_name = pdf_to_save_name
        self.css_save_path = css_save_path
        self.js_save_path = js_save_path
        self.urls = []
        self.css = []
        self.js = []
        self.contents = []

        if not os.path.exists(self.js_save_path):
            os.makedirs(self.js_save_path)

        if not os.path.exists(self.css_save_path):
            os.makedirs(self.css_save_path)

    def get_urls_js_css(self):
        response = requests.get(self.start_url, headers=self.headers)
        bs_obj = BeautifulSoup(response.text, 'html5lib')
        bs_obj.declared_html_encoding = 'utf-8'
        menu = bs_obj.find('div', {'class': 'toctree-wrapper compound'})
        self.urls.append(self.start_url)
        num = 0
        for link in menu.find_all('a', {'class': 'reference internal'}):
            absolute_url = self.start_url + link['href']
            if '#' not in absolute_url:
                self.urls.append(absolute_url)
        print("已经获取所有urls。")
        # css
        links = bs_obj.findAll('link', {'rel': 'stylesheet'})
        for link in links:
            if link.attrs['href'] is not None:
                if link['href'].startswith('_'):
                    real_link = 'https://python3-cookbook.readthedocs.io/zh_CN/latest/' + link['href']
                else:
                    real_link = link['href']
                res = requests.get(real_link, headers=self.headers)
                with open(self.css_save_path + os.path.basename(real_link), 'w', encoding='utf-8') as f:
                    f.write(res.text)
                # link['href'] = self.css_save_path + os.path.basename(real_link)
                link['href'] = real_link
                self.css.append(link)
        # js
        scripts = bs_obj.findAll('script', attrs={'src': True})
        for script in scripts:
            if script['src'].startswith('_'):
                real_script = 'https://python3-cookbook.readthedocs.io/zh_CN/latest/' + script['src']
            else:
                real_script = script['src']
            res = requests.get(real_script, headers=self.headers)
            with open(self.js_save_path + os.path.basename(real_script), 'w', encoding='utf-8') as f:
                f.write(res.text)
            # script['src'] = self.js_save_path + os.path.basename(real_script)
            script['src']=real_script
            self.js.append(script)

    def parse_content(self, html):
        try:
            bs_obj = BeautifulSoup(html, 'html5lib')
            content = bs_obj.find('div', {'role': 'main', 'class': 'document'})
            objs = content.findAll('a', {'class': 'headerlink'})
            for obj in objs:
                obj.extract()
            title = content.find('h1').get_text()
            self.contents.append(content)
        except Exception as e:
            print(e)
        else:
            print("采集完成：{title} ，耗时{time}。".format(title=title, time=time.time() - self.start_time))

    async def get_response(self, url):
        print("开始采集：{url}。".format(url=url))
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=1000, headers=self.headers) as resp:
                assert resp.status == 200
                html = await resp.read()
                return html

    async def get_result(self, url):
        html = await self.get_response(url)
        self.parse_content(html)

    async def hand_tasks(self, work_queue):
        while not work_queue.empty():
            current_url = await work_queue.get()
            try:
                time.sleep(1)
                await self.get_result(current_url)
            except Exception as e:
                logging.exception('Error for {},Exception {}'.format(current_url, e), exc_info=True)

    def event_loop(self):
        q = asyncio.Queue()
        [q.put_nowait(url) for url in self.urls]
        loop = asyncio.get_event_loop()
        tasks = [self.hand_tasks(q)]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()
        self.template_format()
        self.save_to_pdf()

    def template_format(self):
        with open('content.html', 'w', encoding='utf-8') as f:
            for content in self.contents:
                f.write(str(content))
        with open('css.html', 'w', encoding='utf-8') as f:
            for css in self.css:
                f.write(str(css))

        with open('js.html', 'w', encoding='utf-8') as f:
            for js in self.js:
                f.write(str(js))

        with open('content.html', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('css.html', 'r', encoding='utf-8') as f:
            css = f.read()

        with open('js.html', 'r', encoding='utf-8') as f:
            js = f.read()

        html = self.templates.format(content=content, css=css, js=js)
        with open('templates.html', 'w', encoding='utf-8') as f:
            f.write(html)

    def save_to_pdf(self):
        options = {
            'page-size': 'Letter',
            'margin-top': '10px',
            'margin-right': '10px',
            'margin-bottom': '10px',
            'margin-left': '10px',
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

        toc = {
            'xsl-style-sheet': 'toc.xls'
        }
        '''
        cover = 'cover.html'
        '''
        pdfkit.from_file('templates.html', self.pdf_to_save_name, options=options)

        # pdfkit.from_file('file.html', options=options, toc=toc, cover=cover, cover_first=True)


if __name__ == '__main__':
    async_grab = AsyncGrab('https://python3-cookbook.readthedocs.io/zh_CN/latest/', 'python3-cookbook.pdf')
    async_grab.get_urls_js_css()
    async_grab.event_loop()
