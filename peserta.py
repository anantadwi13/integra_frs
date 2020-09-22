#!/usr/bin/python

import datetime
import time
import logging
import threading
import requests
from bs4 import BeautifulSoup
import pickle
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
import json
import html
import csv
import os

def get_config():
    try:
        with open('config.json', 'rb') as config:
            return json.load(config)
    except:
        logging.error('Error: Unable to load config file!')
        return None


"""
MAIN CONFIG
"""

COOKIES_FILE = get_config()['cookies_file']
URL_INTEGRA = get_config()['url_integra']
URL_SIAKAD = get_config()['url_siakad']
baseHeaders = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
}

"""
END CONFIG
"""

TRY_LOGIN = False


def login(force=False):
    global TRY_LOGIN

    if TRY_LOGIN and not force:
        return True
    TRY_LOGIN = True

    # Login Integra
    try:
        logging.info('Info: Logging in to Integra')
        r = session.get(URL_INTEGRA, headers=baseHeaders)
        dom = BeautifulSoup(r.text, features="html.parser")
        strpubkey = dom.find(attrs={'id': 'pubkey'}).get('value')
        public_key = RSA.import_key(strpubkey)
        ciphertext = PKCS1_v1_5.new(public_key).encrypt(str(get_config()['username'] + "|||" + get_config()['password'])
                                                        .encode("utf-8"))
        content = str(base64.b64encode(ciphertext), 'utf-8')
        r = session.post(URL_INTEGRA, headers=baseHeaders, data={'content': content, 'n': '', 'p': ''})
        dom = BeautifulSoup(r.text, features="html.parser")
        if "Login gagal" in dom.text:
            logging.info("Error: Login failed, Username/Password didnt match")
            TRY_LOGIN = False
            return False
        else:
            logging.info("Info: Logged in to Integra")
    except Exception:
        logging.info("Warning: Unable to login to Integra, it might be logged in")

    # Login Siakad
    try:
        logging.info('Info: Logging in to SIAKAD')
        r = session.get(URL_INTEGRA + "/dashboard.php", headers=baseHeaders, params={'sim': 'AKAD__10__'})
        dom = BeautifulSoup(r.text, features="html.parser")
        nextURL = dom.find('meta').get('content').split('URL=')[1]
        params = {}
        for field in nextURL.split('?')[1].split('&'):
            field_data = field.split('=')
            params[field_data[0]] = field_data[1]

        session.get(nextURL, headers=baseHeaders, params=params)
        logging.info('Info: Logged in to SIAKAD')
    except Exception:
        logging.info('Warning: Unable to login to SIAKAD, it might be logged in')

    with open(COOKIES_FILE, 'wb') as file:
        pickle.dump(session.cookies, file)
    #logging.info('Info: ' + str(session.cookies))
    TRY_LOGIN = False
    return True


def fetch_kelas(kelas, output_folder='default'):
    r = session.get(URL_SIAKAD + "/lv_peserta.php", headers=baseHeaders,
                        params={'mkJur': kelas[3], 'mkID': kelas[0], 'mkKelas': kelas[1],
                            'mkSem': get_config()['semester'], 'mkThn': get_config()['tahun_ajaran']})
    
    dom = BeautifulSoup(r.text, features="html.parser")

    table = dom.find('table', {'class': 'GridStyle'})
    
    pesertas = []

    i = 0
    for peserta in table.findChildren("tr", recursive=False):
        if i != 0: 
            data = peserta.findChildren("td", recursive=False)
            row = {'no': data[0].text, 'nrp': data[1].text, 'nama': data[2].text}
            pesertas.append(row)
        i += 1
    
    if len(pesertas)>0 :
        title = dom.findAll('td', {'class':'PageTitle'})[1].text
        filepath = 'dump/{}/peserta-{}.csv'.format(output_folder, title)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, pesertas[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(pesertas)



if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%Y-%m-%d %H:%M:%S", handlers=[
                            logging.FileHandler("log.txt"),
                            logging.StreamHandler()
                        ])

    session = requests.session()
    try:
        with open(COOKIES_FILE, 'rb') as file:
            session.cookies.update(pickle.load(file))
    except Exception:
        logging.info("Cookies Not Found")

    login(True)

    r = session.post(URL_SIAKAD + "/list_frs.php", headers=baseHeaders,
                        data={'act': 'gantinrp', 'key': '', 'nrp': get_config()['nrp'],
                            'semesterTerm': get_config()['semester'], 'thnAjaran': get_config()['tahun_ajaran']})
    dom = BeautifulSoup(r.text, features="html.parser")

    # DUMMY
    # filehtml = html.unescape(str(open("sample_page/2020_ganjil/[SIAKAD-ITS] Formulir Rencana Studi (FRS).html", "rb").read(), 'Latin'))
    # dom = BeautifulSoup(filehtml, features="html.parser")
    # END DUMMY
    
    for option in dom.find(attrs={'id': 'kelasjur'}).findChildren("option", recursive=False):
        try:
            kelas = option.get('value').split('|')
            fetch_kelas(kelas, 'jurusan')
        except Exception:
            logging.info("Gagal {}".format(option.text))
            pass

    for option in dom.find(attrs={'id': 'kelastpb'}).findChildren("option", recursive=False):
        try:
            kelas = option.get('value').split('|')
            fetch_kelas(kelas, 'tpb')
        except Exception:
            logging.info("Gagal {}".format(option.text))
            pass

    for option in dom.find(attrs={'id': 'kelaspengayaan'}).findChildren("option", recursive=False):
        try:
            kelas = option.get('value').split('|')
            fetch_kelas(kelas, 'pengayaan')
        except Exception:
            logging.info("Gagal {}".format(option.text))
            pass
