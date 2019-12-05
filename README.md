# Speedtest exporter for Prometheus

I have missed exporter with configurable options for servers to perform tests against or maybe I was just unlucky with searching. 
So I have decided to create own simple wrapper for speedtest-cli api and export measured values.

Why is it called `stne`? **S**peed**T**est.**n**et **e**xporter

## Docker image

You can build image and run container directly using `docker-compose`:
```
docker-compose run -d
```

This will build image and run container. Just edit parameter `command` in `docker-compose.yml` to provide your desired parameters.

You can also build image without using `docker-compose`:
```
docker build -t stne:latest .
```

## Running container

When image is built, you can get wrapper's help:
```
docker run -ti stne:latest --help
usage: main.py [-h] [--listen [LISTEN]] [--port [PORT]]
               [--servers [SERVERS [SERVERS ...]]] [--no-download]
               [--no-upload] [--single] [--list] [--list-all]

Speedtest exporter for Prometheus

optional arguments:
  -h, --help            show this help message and exit
  --listen [LISTEN]     Listen address for exporter (default: 0.0.0.0)
  --port [PORT]         Port for exporter (default: 9591)
  --servers [SERVERS [SERVERS ...]]
                        Filter for servers to test against (default: )
  --no-download         Don't test download (default: False)
  --no-upload           Don't test upload (default: False)
  --single              Use single connection (default: False)
  --list                Get list of 20 closest servers (default: False)
  --list-all            Get list of all servers (default: False)
```

Get closest servers:
```
docker run -ti stne:latest --list
21975 Nordic Telecom s.r.o. (Prague, Czech Republic) [5.50 km]
20411 Dial Telecom, a.s. (Prague, Czech Republic) [7.04 km]
9788 JM-Net z.s. (Prague, Czech Republic) [7.04 km]
4162 ISP Alliance a.s. (Prague, Czech Republic) [7.04 km]
4424 Nej TV a.s. (Prague, Czech Republic) [7.04 km]
18718 T-Mobile Czech Republic a.s. (Prague, Czech Republic) [7.04 km]
23744 WVG solution s.r.o. (Prague, Czech Republic) [7.04 km]
11181 NFX, z.s.p.o. (Prague, Czech Republic) [7.04 km]
17717 cloudinfrastack, s.r.o. (Prague, Czech Republic) [7.04 km]
8068 Elektro Solution s.r.o. (Prague, Czech Republic) [7.04 km]
10053 NewLink (Prague, Czech Republic) [7.04 km]
23715 GIGANET.cz (Prague, Czech Republic) [7.04 km]
26824 Centronet a.s. (Prague, Czech Republic) [7.04 km]
21429 CZNET.CZ (Praha, Czech Republic) [7.04 km]
28795 ColocationIX 10G (Prague, Czech Republic) [7.04 km]
28985 GIGANET.cz (Dobřejovice, Czech Republic) [7.04 km]
14793 UVT Internet s.r.o. (Jesenice, Czech Republic) [12.07 km]
17015 JM-Net z.s. (Jesenice, CZ) [12.07 km]
5094 INTERCONNECT s.r.o (Krenice, Czech Republic) [12.48 km]
17018 JM-Net z.s. (Říčany, CZ) [13.73 km]
```

You can filter servers which you want to use for testing by providing server id to `--servers` argument:
```
docker run -d --name prometheus_speedtest -p 9591:9591/tcp stne:latest --servers 21975 4468
```
This will filter out obtained server list with provided ids, meaning specified ids will be used for further selection.

## Example metrics:
```
# HELP stne_download Download speed [bps]
# TYPE stne_download gauge
stne_download{connection="Multiple",server="21975: Nordic Telecom s.r.o."} 6.582121055835301e+07
# HELP stne_sent Sent [byte]
# TYPE stne_sent gauge
stne_sent{connection="Multiple",server="21975: Nordic Telecom s.r.o."} 1.1444224e+07
# HELP stne_upload Upload speed [bps]
# TYPE stne_upload gauge
stne_upload{connection="Multiple",server="21975: Nordic Telecom s.r.o."} 8.900405245724995e+06
# HELP stne_received Received [byte]
# TYPE stne_received gauge
stne_received{connection="Multiple",server="21975: Nordic Telecom s.r.o."} 8.2476196e+07
# HELP stne_ping Ping [ms]
# TYPE stne_ping gauge
stne_ping{connection="Multiple",server="21975: Nordic Telecom s.r.o."} 49.894
```