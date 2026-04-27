import psutil

def collect_data():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    connections = len(psutil.net_connections())
    net = psutil.net_io_counters()
    bytes_sent = net.bytes_sent
    bytes_recv = net.bytes_recv

    return [cpu, memory, connections, bytes_sent, bytes_recv]