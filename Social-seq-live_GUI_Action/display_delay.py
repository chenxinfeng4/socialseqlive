import time
import numpy as np
import picklerpc
import pandas as pd
import threading

from PySide6.QtWidgets import QLabel, QLineEdit
from labels_profile import df_bhv_labels

from check_devices import remove_rpc_ip_port

class PyThreadDelay(threading.Thread):
    def __init__(self, qwidget:QLineEdit=None, ip:str=None):
        super().__init__()
        self.qwidget = qwidget
        self.ip = ip
        self.to_continue = True

    def run(self):
        # rpcclient = picklerpc.PickleRPCClient((self.ip, 8092))
        rpcclient = picklerpc.PickleRPCClient(remove_rpc_ip_port)
        while self.to_continue:
            try:
                delay:float = rpcclient.bhv_queue_get()
            except:
                rpcclient = picklerpc.PickleRPCClient(remove_rpc_ip_port)
                delay:float = rpcclient.bhv_queue_get()
            delay_mm = ((delay+1) * 33.34)  #the stream back latency is average 1 frame
            text = 'nan' if np.isnan(delay_mm) else '{:>4} ms'.format(int(delay_mm))
            self.qwidget.setText(text)
            time.sleep(0.1)
        rpcclient.disconnect()


class PyThreadBhvUSVLabel(threading.Thread):
    def __init__(self, qwidget:QLabel=None, ip:str=None):
        super().__init__()
        self.qwidget = qwidget
        self.ip = ip
        self.to_continue = True
        df_bhv_labels2:pd.DataFrame = df_bhv_labels.sort_values(by=['cls_id'])
        self.bhv_cluster_names = df_bhv_labels2['bhv_name'].to_list()

    def run(self):
        rpcclient = picklerpc.PickleRPCClient(remove_rpc_ip_port)

        while self.to_continue:
            try:
                bhv_int:int = rpcclient.label_int()
            except:
                rpcclient = picklerpc.PickleRPCClient(remove_rpc_ip_port)
                bhv_int:int = rpcclient.label_int()
            if bhv_int>=0:
                self.bhv_cluster_names[bhv_int]
                text = self.bhv_cluster_names[bhv_int][:30]
                self.qwidget.setText(text)

        rpcclient.disconnect()


class PyThreadStimulate(threading.Thread):
    def __init__(self, bhv_inds:list, obj_serial):
        self.to_continue = True
        self.obj_serial = obj_serial
        self.bhv_inds = bhv_inds

    def run(self):
        rpcclient = picklerpc.PickleRPCClient(remove_rpc_ip_port)
        while  self.to_continue and self.obj_serial.isconnect:
            try:
                bhv_int:int = rpcclient.label_int()
            except:
                rpcclient = picklerpc.PickleRPCClient(remove_rpc_ip_port)
                bhv_int:int = rpcclient.label_int()
            if bhv_int in self.bhv_inds:
                self.obj_serial.send_message('P')
            time.sleep(0.05)
        
        rpcclient.disconnect()
