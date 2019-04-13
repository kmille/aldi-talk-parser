#!/usr/bin/env python3
import os.path
import requests
from bs4 import BeautifulSoup
import json
import arrow

from ipdb import set_trace

from credentials import username, password

output_dir = "data"
dump_file = "aldi-{}-{:02d}.json"
cookie_file = "cookies.json"


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
    if os.path.exists(cookie_file):
        session.cookies.update(json.load(open(cookie_file)))
        print("Found cookies")
        return
    else:
        data = { '_csrf_token': get_csrf_token(),
                 'form[username]': username,
                 'form[password]': password,
               }

        resp = session.post(base_url % "/login_check", data=data, allow_redirects=False)
        assert resp.status_code == 302, "Got no 302 back, login failed. Got {}".format(resp.headers)
        assert resp.headers['Location'] == "/de/", "Got wrong redirect: '{}'".format(resp.headers['Location'])
        with open(cookie_file, "w") as f:
            json.dump(dict(session.cookies), f)
        print("Login ok")


def dump(data, date_string):
    output_file =  os.path.join("data", date_string)
    with open(output_file, "w") as f:
        json.dump(data, f)
    print("Dump data to {}".format(output_file))


def get_kilobyte(volume, unit):
    factor = 1.0
    if unit == "KB":
        factor = 1.0/1024.0
    if unit == "GB":
        factor = 1024.0
    return round(float(volume)*factor, 2)


def get_einzelverbindung_of_month(year, month):
    data = []
    url = "https://www.alditalk-kundenbetreuung.de/de/konto/kontoubersicht/einzelverbindungen?month={}-{:02d}&date=&voice=&data=&sms=&extended=".format(year, month)
    resp = session.get(url)
    bs = BeautifulSoup(resp.text, 'html.parser')
    for entry in bs.findAll('tr', attrs={'class':"egn-free"}):
        if not "Volumen" in entry.text:
            # do nothing for a call
            continue
        __, date, time, __, __, __, volume, unit = entry.text.strip().split()
        data.append({'date': date, 'time': time, 'volume': get_kilobyte(volume, unit), 'unit': 'MB' })
    date_string = dump_file.format(year, month)
    #dump(data, date_string)
    return data


def iterate_months():
    for month in range(1, 5):
        get_einzelverbindung_of_month(2019, month)


def get_abo_infos():
    print("get abo infos")
    resp = session.get("https://www.alditalk-kundenbetreuung.de/de")
    bs = BeautifulSoup(resp.text, 'html.parser')
    free = bs.find("span", attrs={'class':'pack__usage-remaining'}).text
    total = bs.find("span", attrs={'class':'pack__usage-total'}).text
    unit = bs.find("span", attrs={'class':'pack__usage-unit'}).text
    table_ugly = bs.find("div", attrs={'class':'table'})
    abo_bis = table_ugly.findAll("td")[4].text
    return "Volumen: {}/{} {} - läuft bis {}".format(free, total, unit, abo_bis)


def get_summary_of_current_month():
    print("get sumary of month")
    today = arrow.now()
    data = get_einzelverbindung_of_month(today.year, today.month)
    data = sorted(data, key=lambda x: x['volume'], reverse=True)[:10]
    output = []
    for e in data:
        day_of_week = arrow.get(e['date'], "DD.MM.YYYY").format("dddd")
        output.append("{}   {:9s} {:10s} {:6.2f} {}".format(e['date'], day_of_week, e['time'], e['volume'], e['unit']))
    #print("\n".join(output))
    return output


def go():
    login()
    output = []
    output.append(get_abo_infos())
    output.extend(get_summary_of_current_month())
    #print(output)
    return output

if __name__ == '__main__':
    #login()
    #iterate_months()
    go()
