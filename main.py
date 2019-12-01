import prometheus_client
import http.server as server
import speedtest
import argparse


def measure(args):
    servers = args.servers
    s = speedtest.Speedtest()
    s.get_servers(servers)
    s.get_best_server()
    if not args.no_down:
        s.download(threads=(None, 1)[args.single])
    if not args.no_up:
        s.upload(threads=(None, 1)[args.single])
    results_dict = s.results.dict()
    print(results_dict)
    return results_dict


def get_servers(list_all=False):
    s = speedtest.Speedtest()
    if not list_all:
        servers = s.get_closest_servers(20)
        for server in servers:
            print('%(id)s %(sponsor)s (%(name)s, %(country)s) [%(d)0.2f km]' % server)
    else:
        s.get_servers()
        servers = s.servers
        for _, servers in sorted(servers.items()):
            for server in servers:
                print('%(id)s %(sponsor)s (%(name)s, %(country)s) [%(d)0.2f km]' % server)


class MyHandler(prometheus_client.MetricsHandler):
    down = prometheus_client.Gauge('stne_download', 'Download speed [bps]', ['server', 'connection'])
    up = prometheus_client.Gauge('stne_upload', 'Upload speed [bps]', ['server', 'connection'])
    ping = prometheus_client.Gauge('stne_ping', 'Ping [ms]', ['server', 'connection'])
    sent = prometheus_client.Gauge('stne_sent', 'Sent [byte]', ['server', 'connection'])
    received = prometheus_client.Gauge('stne_received', 'Received [byte]', ['server', 'connection'])
    args = None

    def do_GET(self):
        result = measure(self.args)
        server = "{}: {}".format(result['server']['id'], result['server']['sponsor'])
        if self.args.single:
            connection = 'Single'
        else:
            connection = 'Multiple'
        self.down.labels(server, connection).set(result['download'])
        self.received.labels(server, connection).set(result['bytes_received'])
        if self.args.no_down:
            self.down.remove(server, connection)
            self.received.remove(server, connection)
        self.up.labels(server, connection).set(result['upload'])
        self.sent.labels(server, connection).set(result['bytes_sent'])
        if self.args.no_up:
            self.up.remove(server, connection)
            self.sent.remove(server, connection)
        self.ping.labels(server, connection).set(result['ping'])

        prometheus_client.MetricsHandler.do_GET(self)
        return

    def set_args(self, args):
        self.args = args


def start_server(args, server_class=server.ThreadingHTTPServer, handler_class=MyHandler):
    server_address = (args.listen, args.port)
    print("Starting http server at {}:{}".format(args.listen, args.port))
    handler_class.set_args(handler_class, args)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(description='Speedtest exporter for Prometheus')
    parser.add_argument('--listen', dest='listen', default='', nargs='?',
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

    print(args)

    if args.list or args.list_all:
        if args.list_all:
            get_servers(True)
        else:
            get_servers()
        exit(0)
    start_server(args)


if __name__ == "__main__":
    main()
