# Parser for aldi talk website
```bash
(venv) kmille@linbox aldi-talk-parser master % python aldi.py
Found cookies
Get inet usage of current month
Volumen: 1,7/2 GB - läuft bis Donnerstag, 26.12.2019 23:59 Uhr (MEZ)
```

```bash
(venv) kmille@linbox aldi-talk-parser master % python aldi.py
Found cookies. will not login. if the cookie is too old this will not work
Get sumary of current month
12.12.2019   Thursday  05:05:37    64.36 MB
02.12.2019   Monday    07:48:40    44.86 MB
01.12.2019   Sunday    09:10:24    32.92 MB
03.12.2019   Tuesday   07:57:10    29.29 MB
06.12.2019   Friday    13:27:44    25.66 MB
30.11.2019   Saturday  15:21:02    14.06 MB
...
```
```bash
(venv) kmille@linbox aldi-talk-parser master % python aldi.py
Found cookies. will not login. if the cookie is too old this will not work
Iterating over months
Doing 2019/1
Dump data to data/aldi-2019-01.json
Doing 2019/2
Dump data to data/aldi-2019-02.json
Doing 2019/3
Dump data to data/aldi-2019-03.json
Doing 2019/4
Dump data to data/aldi-2019-04.json
Doing 2019/5
Dump data to data/aldi-2019-05.json
Doing 2019/6
Dump data to data/aldi-2019-06.json
Doing 2019/7
Dump data to data/aldi-2019-07.json
Doing 2019/8
Dump data to data/aldi-2019-08.json
Doing 2019/9
Dump data to data/aldi-2019-09.json
Doing 2019/10
Dump data to data/aldi-2019-10.json
Doing 2019/11
Dump data to data/aldi-2019-11.json
Doing 2019/12
Dump data to data/aldi-2019-12.json
```

```bash
(venv) kmille@linbox aldi-talk-parser master % python aldi.py
Found cookies. will not login. if the cookie is too old this will not work
Datenverbrauch der letzten 180 Tage mit Tarifoption
Paket S   '09.08.2019 -06.09.2019' 389 MB               2000 MB              0 MB
Paket S   '12.07.2019 -09.08.2019' 1123 MB              2000 MB              0 MB
Paket S   '01.11.2019 -29.11.2019' 809 MB               2000 MB              0 MB
Paket S   '29.11.2019 -13.12.2019' 267 MB               2000 MB              0 MB
Paket S   '04.10.2019 -01.11.2019' 1061 MB              2000 MB              0 MB
Paket S   '14.06.2019 -12.07.2019' 1728 MB              2000 MB              0 MB
Paket S   '06.09.2019 -04.10.2019' 917 MB               2000 MB              0 MB
```
