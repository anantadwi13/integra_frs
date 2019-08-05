#!/usr/bin/python

import logging
import threading
import requests
from bs4 import BeautifulSoup
import pickle
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
import html

"""
START CONFIG
"""

USERNAME = "05111740000029"
PASSWORD = "Password"

NRP = "5117100029"
SEMESTER = "1"
TAHUN_AJARAN = "2019"
PILIHAN_KELAS = [
    {'kode': 'IF184501', 'kelas': 'A'},
    {'kode': 'IF184502', 'kelas': 'B'},
    {'kode': 'IF184506', 'kelas': 'D'},
]

# Format POST Field
FORMAT_VALUE = "{}|{}|2018|51100|0"

COOKIES_FILE = "cookies"
URL_INTEGRA = "https://integra.its.ac.id"
URL_SIAKAD = "https://akademik.its.ac.id"
baseHeaders = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
}

"""
END CONFIG
"""


def send_post(type, item):
    try:
        logging.info('Info: {} - Ambil [{}]'.format(type, str(item['text'])))
        postData = {'act': 'ambil', 'kelasjur': item['value'], 'key': item['value'], 'nrp': NRP,
                    'semesterTerm': SEMESTER, 'thnAjaran': TAHUN_AJARAN}

        r = session.post(URL_SIAKAD +"/list_frs.php", headers=baseHeaders, data=postData)
        # print(r.text)

        if r.status_code == 200:
            logging.info('Info: {} - Selesai [{}]'.format(type, str(item['text'])))
        else:
            logging.error('Error: {} - ERROR Response {} [{}]'.format(type, str(r.status_code), str(item['text'])))
        # print(postData)
    except Exception:
        if item is not None:
            logging.error('Error: {} - Error Ambil [{}]'.format(type, str(item['text'])))
        else:
            logging.error('Error: {} - Error Ambil Matkul'.format(type))


def ambil_matkul_v1():
    try:
        logging.info('Info: v1 - Fetching class list')
        r = session.post(URL_SIAKAD + "/list_frs.php", headers=baseHeaders,
                         data={'act': 'gantinrp', 'key': '', 'nrp': NRP, 'semesterTerm': SEMESTER,
                               'thnAjaran': TAHUN_AJARAN})
        dom = BeautifulSoup(r.text, features="html.parser")

        # DUMMY
        # filehtml = html.unescape(str(open("[SIAKAD-ITS] Formulir Rencana Studi (FRS).html", "rb").read(), 'Latin'))
        # dom = BeautifulSoup(filehtml, features="html.parser")
        # END DUMMY

        kelas = []
        for option in dom.find(attrs={'id': 'kelasjur'}).findChildren("option", recursive=False):
            value = option.get('value')
            text = option.text
            for pilihan in PILIHAN_KELAS:
                if pilihan['kode'] in text and " " + pilihan['kelas'] + " " in text:
                    kelas.append({'value': value, 'text': text})

        logging.info('Info: v1 - Found '+str(kelas.__len__())+' class(es)')

        # Submit
        for item in kelas:
            mthread = threading.Thread(target=send_post, args=('v1', item,))
            mthread.start()
    except Exception:
        logging.info('Error: v1 - Unable to fetch class list')


def ambil_matkul_v2():
    try:
        logging.info('Info: v2 - Force sending request')
        kelas = []
        for pilihan in PILIHAN_KELAS:
            value = FORMAT_VALUE.format(pilihan['kode'], pilihan['kelas'])
            kelas.append({'value': value, 'text': value})

        logging.info('Info: v2 - Sending '+str(kelas.__len__())+' class(es)')

        #Submit
        for item in kelas:
            mthread = threading.Thread(target=send_post, args=('v2', item,))
            mthread.start()
    except Exception:
        logging.info('Error: v2 - Unable to do this job')


def login():
    # Login Integra
    try:
        logging.info('Info: Logging in to Integra')
        r = session.get(URL_INTEGRA, headers=baseHeaders)
        dom = BeautifulSoup(r.text, features="html.parser")
        strpubkey = dom.find(attrs={'id': 'pubkey'}).get('value')
        public_key = RSA.import_key(strpubkey)
        ciphertext = PKCS1_v1_5.new(public_key).encrypt(str(USERNAME + "|||" + PASSWORD).encode("utf-8"))
        content = str(base64.b64encode(ciphertext), 'utf-8')
        r = session.post(URL_INTEGRA, headers=baseHeaders, data={'content': content, 'n': '', 'p': ''})
        dom = BeautifulSoup(r.text, features="html.parser")
        if "Login gagal" in dom.text:
            logging.info("Error: Login failed, Username/Password didnt match")
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
    logging.info('Info: '+str(session.cookies))

    return True


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    session = requests.session()
    try:
        with open(COOKIES_FILE, 'rb') as file:
            session.cookies.update(pickle.load(file))
    except Exception:
        logging.info("Cookies Not Found")

    if login() != False:
        ambil_matkul_v1()
        ambil_matkul_v2()
