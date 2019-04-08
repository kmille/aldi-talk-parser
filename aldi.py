#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json

from ipdb import set_trace

from credentials import username, password
 
dump_file = "aldi.json"


base_url = "https://www.alditalk-kundenbetreuung.de/de%s"
headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36" }
session = requests.Session()
session.headers.update(headers)

def get_csrf_token():
    resp = session.get(base_url % "/")
    bs = BeautifulSoup(resp.text, 'html.parser')
    token =  bs.find('input', attrs={'name':'_csrf_token'}).attrs['value']
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


def get_einzelverbindung_of_month(year, month):
    data = []
    url = "https://www.alditalk-kundenbetreuung.de/de/konto/kontoubersicht/einzelverbindungen?month={}-{}&date=&voice=&data=&sms=&extended=".format(year, month)
    resp = session.get(url)
#    with open("data", "r") as f:
#        html = f.read()
    bs = BeautifulSoup(resp.text, 'html.parser')
    for entry in bs.findAll('tr', attrs={'class':"egn-free"}):
        #print(entry.text)
        _type, date, time, price, __, __, volume, unit = entry.text.strip().split()
        data.append({'type': _type, 'date': date, 'time': time, 'price': price, 'volume': volume, 'unit': unit })
    return data


def iterate_months():
    great_power_to_destroy_the_world = []
    for month in range(1, 5):
        great_power_to_destroy_the_world.extend(get_einzelverbindung_of_month(2019, month))
        print("Len of data {}".format(len(great_power_to_destroy_the_world)))
    with open(dump_file, "w") as f:
        json.dump(great_power_to_destroy_the_world, f)
    print("Dump data to {}".format(dump_file))
    #set_trace()


if __name__ == '__main__':
    login()
    iterate_months()
