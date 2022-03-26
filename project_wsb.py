# -----------------------------------------------------------------------
# --------------------------- Projects ----------------------------------
# -----------------------------------------------------------------------

from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from collections import namedtuple
import numpy as np

path_esika = r'https://esika.tiendabelcorp.com/pe'

def func_res(link):
    response = requests.get(link)
    if response.status_code == 200:
        page = BeautifulSoup(response.text, 'html.parser')
        return page

def comp_link_func(link):
    page = func_res(link)
    components_links = []
    for div in page.find('div', attrs={'class': 'yCmsComponent yComponentWrapper'}):
        if div.name == 'a':
            if div.get('href'):
                components_links.append(div.get('href'))
    return components_links

def head_link_func(link):
    head_links = []

    page = func_res(link)
    for li in page.find_all('li'):
        if li.a:
                #print(li.a)
            if li.a.get('href'):
                link_int = li.a.get('href')
                if re.search(r'^https://esika.*?esika\-\d{2}\b',link_int):
                    head_links.append(link_int)

    return head_links

def link_favo_func(link):
    page =func_res(link)
    s = set()

    for element in page.find('h2').next_elements:
        if element.name == 'h2':
            print(element.text)
            break
        if element.name == 'a':
            if element.get('href') and (element.get('href') != '#'):

                mid_link = element.get('href')
                # aylis = w.get('href')
                link_com = urljoin(path_esika, mid_link)
                s.add(link_com)
    return list(s)

comp_link_func(path_esika)

link_favo_func(path_esika)

def data_by_product(link):
    #link = 'https://esika.tiendabelcorp.com/pe/labial-de-larga-duracion-colorfix-duo-tattoo-edicion-limitada/p/200109391'
    page = func_res(link)
    price_name = {}

    # prices
    try:
        for tages in page.find_all('span', attrs={'class': re.compile(r'.*title.*price.*')}):
            price, name = tages.text.replace('\n', ''), tages.get('class')[0]
            price_name[name] = price
    except:
        print(link, 'invalid')

    # Title
    try:
        text_title = page.find('h1').text.replace('\n', '')

    except:
        print(link, 'title text')

    txt_comp = '|'.join(text_title.split(' '))
    # color name code
    try:
        pag_div = page.find_all('div', attrs={'data-url': re.compile(rf'{txt_comp}', re.I)})
        color_code = {}
        for pag in pag_div:
            if pag.div:
                color_code[pag['data-mouseover-text']] = pag['data-code']
    except:
        color_code = {}
        print(link, 'data code','div data url')

    # link img base
    response_pag = page.find_all('a', attrs={'class': re.compile(r'.*gallery.*', re.I)})
    if response_pag:
        for page_a in response_pag:
            if page_a.img.get('src'):
                link_img = page_a.img.get('src')
                if re.search(r'auto\/(.*fondoblanco.*)', link_img, re.I) or re.search(
                        r'auto\/(.*\d{9}\-foto\w+cto\.\w{3})', link_img, re.I):

                    link_img_base = re.search(r'auto\/(.*)', link_img).group(1)
                    break
                    # link_img_base = re.search(r'auto\/(.*)', link_img).group(1)
                    print(link_img_base, 'link_img_base')

                else:
                    link_img_base = {}
            else:
                link_img_base = {}

    else:
        link_img_base = {}
        print(link)

    # link color final
    data_img_color_id = namedtuple('dataurl', ['color_c', 'code_c', 'urlimg'])

    img_color = []
    #print(link)
    if color_code and link_img_base:

        try:
            for name_c, code_c in color_code.items():
                link_img_final = re.sub(r'\d{9}', f'{code_c}', link_img_base)
                data_img = data_img_color_id(color_c=name_c, code_c=code_c, urlimg=link_img_final)
                img_color.append(data_img)
        except:
            print(link, 'img color')
    else:
        if link_img_base:
            code_c = re.search(r'.*(\d{9}).*',link_img_base).group(1)
            data_img = data_img_color_id(color_c=np.NAN, code_c=code_c, urlimg=link_img_base)
            img_color.append(data_img)

    # join all data
    DF = pd.DataFrame(img_color)
    if not DF.empty:
        DF['title'] = text_title
        for name_p, price in price_name.items():
            DF[name_p] = price

    return DF

def link_pagination_by_head(link):
    page = func_res(link)
    page.find_all('ul', attrs={'class': 'pagination'})
    links_pagion = set()
    for pag_a in page.find_all('a', attrs={'href': re.compile(r'.*page.*')}):
        # print(c)
        link_ion = urljoin(link, pag_a.get('href'))
        # print(wds)
        links_pagion.add(link_ion)

    return list(links_pagion)

def link_products_page(link):
    page = func_res(link)
    lpp = set()
    for pag_a in page.find_all('a', attrs={'id': re.compile(r'.*productname.*', re.I)}):
        links_ptus = urljoin(link, pag_a.get('href'))
        lpp.add(links_ptus)
    return list(lpp)

path_esika = r'https://esika.tiendabelcorp.com/pe'
megalist = []
for head in head_link_func(path_esika):

        lppages= link_products_page(head)

        for lph in link_pagination_by_head(head):
            lppages_pgion = link_products_page(lph)
            lppages.extend(lppages_pgion)

        for lp in lppages:
            data_lp = data_by_product(lp)
            megalist.append(data_lp)

len(set(megalist))
len(megalist)
qa = pd.concat(megalist)

qa.title.unique().shape