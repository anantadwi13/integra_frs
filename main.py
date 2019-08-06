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


def send_post(type, item):
    try:
        logging.info('Info: {} - Ambil [{}]'.format(type, str(item['text'])))
        postData = {'act': 'ambil', 'kelasjur': item['value'], 'key': item['value'], 'nrp': get_config()['nrp'],
                    'semesterTerm': get_config()['semester'], 'thnAjaran': get_config()['tahun_ajaran']}

        r = session.post(URL_SIAKAD + "/list_frs.php", headers=baseHeaders, data=postData)
        # print(r.text)
        if "Formulir Rencana Studi (FRS)" not in r.text:
            logging.info('Error: Not Authorized')
            login()
        elif r.status_code == 200:
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
                         data={'act': 'gantinrp', 'key': '', 'nrp': get_config()['nrp'],
                               'semesterTerm': get_config()['semester'], 'thnAjaran': get_config()['tahun_ajaran']})
        dom = BeautifulSoup(r.text, features="html.parser")

        if "Formulir Rencana Studi (FRS)" not in r.text:
            logging.info('Error: Not Authorized')
            login()
            return

        # DUMMY
        # filehtml = html.unescape(str(open("[SIAKAD-ITS] Formulir Rencana Studi (FRS).html", "rb").read(), 'Latin'))
        # dom = BeautifulSoup(filehtml, features="html.parser")
        # END DUMMY

        kelas = []
        for option in dom.find(attrs={'id': 'kelasjur'}).findChildren("option", recursive=False):
            value = option.get('value')
            text = option.text
            for pilihan in get_config()['pilihan_kelas']:
                if pilihan['kode'] in text and " " + pilihan['kelas'] + " " in text:
                    kelas.append({'value': value, 'text': text})

        logging.info('Info: v1 - Found ' + str(kelas.__len__()) + ' class(es)')

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
        for pilihan in get_config()['pilihan_kelas']:
            value = get_config()['format_value'].format(pilihan['kode'], pilihan['kelas'])
            kelas.append({'value': value, 'text': value})

        logging.info('Info: v2 - Sending ' + str(kelas.__len__()) + ' class(es)')

        # Submit
        for item in kelas:
            mthread = threading.Thread(target=send_post, args=('v2', item,))
            mthread.start()
    except Exception:
        logging.info('Error: v2 - Unable to do this job')


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
    logging.info('Info: ' + str(session.cookies))
    TRY_LOGIN = False
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

    # login(True)

    while True:
        try:
            time_ambil = datetime.datetime.strptime(get_config()['time_ambil'], '%Y-%m-%d %H:%M:%S')
            diffTime = datetime.datetime.now() - time_ambil

            if diffTime.total_seconds() > 0 and get_config()['mulai']:
                try:
                    with open(COOKIES_FILE, 'rb') as file:
                        session.cookies.update(pickle.load(file))
                except Exception:
                    logging.info("Cookies Not Found")
                    threading.Thread(target=login).start()

                v1 = threading.Thread(target=ambil_matkul_v1)
                v2 = threading.Thread(target=ambil_matkul_v2)
                v1.start()
                v2.start()
            else:
                logging.info('Info: Not Started, {} s remaining'.format(diffTime.total_seconds()))
            time.sleep(get_config()['time_sleep'])
        except Exception:
            logging.error('Error: Unexpected error!')
            time.sleep(5)
