import picklerpc
from ffmpegcv.stream_info import get_info
from multiprocessing.pool import ThreadPool

remove_rpc_ip_port = ('localhost', 8002)
def check_stream_url(url):
    try:
        info = get_info(url, 2.8)
        assert info.width>100 and info.height>100
    except:
        return False
    return True

def check_stream_urls(urls):
    # using threading to check the stream urls, get the result and show the result in the GUI
    pool = ThreadPool(processes=len(urls))
    results = pool.map(check_stream_url, urls)
    pool.close()
    pool.join()
    return results


def check_cloud_server(ip):
    try:
        # rpcclient = picklerpc.PickleRPCClient((ip, 8001))
        rpcclient = picklerpc.PickleRPCClient(remove_rpc_ip_port)
        result = rpcclient.about()
        assert result=='Social-seq live server'
        rpcclient.disconnect()
    except:
        return False
    return True
