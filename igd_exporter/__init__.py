import argparse
import functools
import ipaddress
import signal
import threading
import wsgiref.simple_server

from . import wsgiext
from . import exporter
from . import config

def main():
    '''
    You are here.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--bind-address', type=ipaddress.ip_address, default='::', help='IPv6 or IPv4 address to listen on')
    parser.add_argument('--bind-port', type=int, default=9196, help='Port to listen on')
    parser.add_argument('--bind-v6only', type=int, choices=[0, 1], help='If 1, prevent IPv6 sockets from accepting IPv4 connections; if 0, allow; if unspecified, use OS default')
    parser.add_argument('--thread-count', type=int, help='Number of request-handling threads to spawn')
    parser.add_argument('--internet-gateway-device', type=int, default=1, help='ID of the InternetGatewayDevice from the SSDP desc.xml')
    parser.add_argument('--wan-device', type=int, default=1, help='ID of the WANDevice from the SSDP desc.xml')
    parser.add_argument('--wan-common-interface-config', type=int, default=1, help='ID of the WANCommonInterfaceConfig from the SSDP desc.xml')
    config.args = parser.parse_args()

    server = wsgiext.Server((config.args.bind_address, config.args.bind_port), wsgiext.SilentRequestHandler, config.args.thread_count, config.args.bind_v6only)
    server.set_app(exporter.wsgi_app)
    wsgi_thread = threading.Thread(target=functools.partial(server.serve_forever, 86400), name='wsgi')

    def handle_sigterm(signum, frame):
        server.shutdown()
    signal.signal(signal.SIGTERM, handle_sigterm)

    wsgi_thread.start()

    wsgi_thread.join()

    server.server_close()
