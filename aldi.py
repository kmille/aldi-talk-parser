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
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"}

session = requests.Session()
session.headers.update(headers)


def get_csrf_token():
    resp = session.get(base_url % "/")
    assert resp.status_code == 200
    bs = BeautifulSoup(resp.text, 'html.parser')
    token = bs.find('input', attrs={'name': '_csrf_token'}).attrs['value']
    print("Got csrf token {}".format(token))
    return token


def login():
    if os.path.exists(cookie_file):
        session.cookies.update(json.load(open(cookie_file)))
        print("Found cookies. will not login. if the cookie is too old this will not work")
        return
    else:
        data = {'_csrf_token': get_csrf_token(),
                'form[username]': username,
                'form[password]': password,
               }

        resp = session.post(base_url % "/login_check", data=data, allow_redirects=False)
        assert resp.status_code == 302, "Got no 302 back, login failed. Got {}".format(resp.headers)
        assert resp.headers['Location'] == "/de/", "Got wrong redirect: '{}'".format(resp.headers['Location'])
        with open(cookie_file, "w") as f:
            json.dump(dict(session.cookies), f)
        print("Login ok")


def file_dump(data, date_string):
    output_file = os.path.join("data", date_string)
    with open(output_file, "w") as f:
        json.dump(data, f)
    print("Dump data to {}".format(output_file))


def get_kilobyte(volume, unit):
    factor = 1.0
    if unit == "KB":
        factor = 1.0 / 1024.0
    if unit == "GB":
        factor = 1024.0
    return round(float(volume) * factor, 2)


def get_einzelverbindung_of_month(year, month, dump_to_file=False):
    data = {}
    data['records'] = []
    url = "https://www.alditalk-kundenbetreuung.de/de/konto/kontoubersicht/einzelverbindungen?month={}-{:02d}&date=&voice=&data=&sms=&extended=".format(year, month)
    resp = session.get(url)
    assert resp.status_code == 200
    bs = BeautifulSoup(resp.text, 'html.parser')
    total_used_volume = 0
    for entry in bs.findAll('tr', attrs={'class': "egn-free"}):
        if "Volumen" not in entry.text:
            # do nothing for a call
            continue
        __, date, time, __, __, __, volume, unit = entry.text.strip().split()
        total_used_volume += get_kilobyte(volume, unit)
        data['records'].append({'date': date, 'time': time, 'volume': get_kilobyte(volume, unit), 'unit': 'MB'})
    data["total_used_volume"] = total_used_volume
    print("usage on {}/{}: {} GB".format(year, month, total_used_volume/1024.0/1024.0))
    date_string = dump_file.format(year, month)
    if dump_to_file:
        file_dump(data, date_string)
    return data


def iterate_months(year=2019):
    print("Iterating over months")
    for month in range(12, 13):
        print("Doing {}/{}".format(year, month))
        get_einzelverbindung_of_month(year, month, dump_to_file=True)


def get_abo_infos():
    print("Get inet usage of current month")
    resp = session.get("https://www.alditalk-kundenbetreuung.de/de")
    assert resp.status_code == 200
    bs = BeautifulSoup(resp.text, 'html.parser')
    free = bs.find("span", attrs={'class': 'pack__usage-remaining'}).text
    total = bs.find("span", attrs={'class': 'pack__usage-total'}).text
    unit = bs.find("span", attrs={'class': 'pack__usage-unit'}).text
    table_ugly = bs.find("div", attrs={'class': 'table'})
    abo_bis = table_ugly.findAll("td")[4].text.strip()
    print("Volumen: {}/{} {} - läuft bis {}".format(free, total, unit, abo_bis))
    #return "Volumen: {}/{} {} - läuft bis {}".format(free, total, unit, abo_bis)


def get_summary_of_current_month(last=99999999):
    print("Get sumary of current month")
    today = arrow.now()
    data = get_einzelverbindung_of_month(today.year, today.month)
    # sort by volume and only get the last $last entries
    data = sorted(data, key=lambda x: x['volume'], reverse=True)[:last]
    output = []
    for e in data:
        day_of_week = arrow.get(e['date'], "DD.MM.YYYY").format("dddd")
        output.append("{}   {:9s} {:10s} {:6.2f} {}".format(e['date'], day_of_week, e['time'], e['volume'], e['unit']))
    print("\n".join(output))
    return output


def summary():
    print("Datenverbrauch der letzten 180 Tage mit Tarifoption")
    resp = session.get("https://www.alditalk-kundenbetreuung.de/de/konto/kontoubersicht")
    assert resp.status_code == 200
    bs = BeautifulSoup(resp.text, 'html.parser')
    table_ugly = bs.find("div", attrs={'class': 'table table--usage'})
    data = {}
    for row in table_ugly.find("tbody").findAll("tr"):
        d = {}
        d['product'] = row.findAll("td")[0].text.strip()
        d['time'] = row.findAll("td")[1].text.strip()
        d['volume'] = row.findAll("td")[2].text.strip()
        d['used'] = row.findAll("td")[3].text.strip()
        d['used_after_throttle'] = row.findAll("td")[4].text.strip()
        print("{}   '{:9s}' {:20s} {:20s} {}".format(d['product'], d['time'], d['used'],
                                                     d['volume'], d['used_after_throttle']))
        data[d['time']] = d


if __name__ == '__main__':
    login()
    #get_abo_infos()
    #get_summary_of_current_month()
    #iterate_months()
    #summary()
