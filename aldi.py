#!/usr/bin/env python3
import os.path
import requests
from bs4 import BeautifulSoup
import json

from ipdb import set_trace

from credentials import username, password

output_dir = "data"
dump_file = "aldi-{}-{:02d}.json"


base_url = "https://www.alditalk-kundenbetreuung.de/de%s"
headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36" }

session = requests.Session()
session.headers.update(headers)


def get_csrf_token():
    resp = session.get(base_url % "/")
    bs = BeautifulSoup(resp.text, 'html.parser')
    token = bs.find('input', attrs={'name':'_csrf_token'}).attrs['value']
    print("Got csrf token {}".format(token))
    return token


def login():
    data = { '_csrf_token': get_csrf_token(),
             'form[username]': username,
             'form[password]': password,
           }

    resp = session.post(base_url % "/login_check", data=data, allow_redirects=False)
    assert resp.status_code == 302, "Got no 302 back, login failed. Got {}".format(resp.headers)
    assert resp.headers['Location'] == "/de/", "Got wrong redirect: '{}'".format(resp.headers['Location'])
    print("Login ok")


def dump(data, date_string):
    print(output_dir)
    print(date_string)
    set_trace()
    with open(os.path.join(output_dir, date_string), "w") as f:
        json.dump(data, f)
    print("Dump data to {}".format(dump_file))


def get_einzelverbindung_of_month(year, month):
    data = []
    url = "https://www.alditalk-kundenbetreuung.de/de/konto/kontoubersicht/einzelverbindungen?month={}-{:02d}&date=&voice=&data=&sms=&extended=".format(year, month)
    resp = session.get(url)
    bs = BeautifulSoup(resp.text, 'html.parser')
    for entry in bs.findAll('tr', attrs={'class':"egn-free"}):
        if not "Volumen" in entry.text:
            # do nothing for a call
            continue
        _type, date, time, price, __, __, volume, unit = entry.text.strip().split()
        data.append({'type': _type, 'date': date, 'time': time, 'price': price, 'volume': volume, 'unit': unit })
    date_string = dump_file.format(year, month)
    dump(data, date_string)
    print("done with {}".format(date_string))


def iterate_months():
    for month in range(1, 5):
        get_einzelverbindung_of_month(2019, month)


if __name__ == '__main__':
    login()
    iterate_months()
