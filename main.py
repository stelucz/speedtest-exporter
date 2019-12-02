import prometheus_client
import prometheus_client.core
import http.server as server
import speedtest
import argparse
import logging


class SpeedTest:
    def __init__(self, args):
        self.args = args

    def measure(self):
        servers = self.args.servers
        s = speedtest.Speedtest()
        s.get_servers(servers)
        s.get_best_server()
        if not self.args.no_down:
            s.download(threads=(None, 1)[self.args.single])
        if not self.args.no_up:
            s.upload(threads=(None, 1)[self.args.single])
        results_dict = s.results.dict()
        print(results_dict)
        logging.info("Measured: " + str(results_dict))
        return results_dict


def get_servers(list_all=False):
    s = speedtest.Speedtest()
    if not list_all:
        logging.info("Getting closest servers")
        servers = s.get_closest_servers(20)
        for server in servers:
            print('%(id)s %(sponsor)s (%(name)s, %(country)s) [%(d)0.2f km]' % server)
    else:
        logging.info("Getting all servers")
        s.get_servers()
        servers = s.servers
        for _, servers in sorted(servers.items()):
            for server in servers:
                print('%(id)s %(sponsor)s (%(name)s, %(country)s) [%(d)0.2f km]' % server)


class Collector(object):
    def __init__(self, client=SpeedTest):
        self.client = client

    def collect(self):
        results_dict = self.client.measure()
        server = "{}: {}".format(results_dict['server']['id'], results_dict['server']['sponsor'])
        if self.client.args.single:
            connection = 'Single'
        else:
            connection = 'Multiple'

        down = prometheus_client.core.GaugeMetricFamily('stne_download', 'Download speed [bps]',
                                                        labels=['server', 'connection'])
        down.add_metric([server, connection], results_dict['download'])
        yield down

        sent = prometheus_client.core.GaugeMetricFamily('stne_sent', 'Sent [byte]',
                                                        labels=['server', 'connection'])
        sent.add_metric([server, connection], results_dict['bytes_sent'])
        yield sent

        up = prometheus_client.core.GaugeMetricFamily('stne_upload', 'Upload speed [bps]',
                                                      labels=['server', 'connection'])
        up.add_metric([server, connection], results_dict['upload'])
        yield up

        received = prometheus_client.core.GaugeMetricFamily('stne_received', 'Received [byte]',
                                                            labels=['server', 'connection'])
        received.add_metric([server, connection], results_dict['bytes_received'])
        yield received

        ping = prometheus_client.core.GaugeMetricFamily('stne_ping', 'Ping [ms]',
                                                        labels=['server', 'connection'])
        ping.add_metric([server, connection], results_dict['ping'])
        yield ping


def start_server(args, server_class=server.ThreadingHTTPServer):
    server_address = (args.listen, args.port)
    prometheus_client.REGISTRY.register(Collector(SpeedTest(args)))
    httpd = server_class(server_address, prometheus_client.MetricsHandler)
    logging.info("Starting http server at {}:{}".format(args.listen, args.port))
    httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(description='Speedtest exporter for Prometheus')
    parser.add_argument('--listen', dest='listen', default='0.0.0.0', nargs='?',
                        help='Listen address for exporter (default: 0.0.0.0)')
    parser.add_argument('--port', dest='port', default='9591', nargs='?', type=int,
                        help='Port for exporter (default: 9591)')
    parser.add_argument('--servers', dest='servers', default='', nargs='*',
                        help='Filter for servers to test against (default: '')')
    parser.add_argument('--no-download', dest='no_down', action='store_true',
                        help='Don\'t test download (default: False)')
    parser.add_argument('--no-upload', dest='no_up', action='store_true',
                        help='Don\'t test upload (default: False)')
    parser.add_argument('--single', dest='single', action='store_true',
                        help='Use single connection (default: False)')
    parser.add_argument('--list', dest='list', action='store_true',
                        help='Get list of 20 closest servers (default: False)')
    parser.add_argument('--list-all', dest='list_all', action='store_true',
                        help='Get list of all servers (default: False)')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.info("Started with following arguments: " + str(args))
    if args.list or args.list_all:
        if args.list_all:
            get_servers(True)
        else:
            get_servers()
        exit(0)
    start_server(args)


if __name__ == "__main__":
    main()
