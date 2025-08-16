import time
import numpy as np
import picklerpc
import pandas as pd
import threading
import socket

from PySide6.QtWidgets import QLabel, QLineEdit
from labels_profile import df_bhv_labels, df_usv_labels


picklerpc_addr = ('localhost', 8001)

class PyThreadDelay(threading.Thread):
    def __init__(self, qwidget:QLineEdit=None, qwidget_usv:QLineEdit=None, ip:str=None):
        super().__init__()
        self.qwidget = qwidget
        self.qwidget_usv = qwidget_usv
        self.ip = ip
        self.to_continue = True

    def run(self):
        # rpcclient = picklerpc.PickleRPCClient((self.ip, 8092))
        rpcclient = picklerpc.PickleRPCClient(picklerpc_addr)
        while self.to_continue:
            try:
                delay:float = rpcclient.bhv_queue_get()
            except:
                rpcclient = picklerpc.PickleRPCClient(picklerpc_addr)
                delay:float = rpcclient.bhv_queue_get()
            delay_mm = ((delay+1) * 33.34)  #the stream back latency is average 1 frame
            text = 'nan' if np.isnan(delay_mm) else 'pose {:>4} ms'.format(int(delay_mm))
            self.qwidget.setText(text)
            time.sleep(0.1)
        rpcclient.disconnect()


class PyThreadBhvUSVLabel(threading.Thread):
    def __init__(self, qwidget:QLabel=None, qwidgetusv:QLabel=None, ip:str=None,
                 bhv_cluster_idchoose:list=None,
                 usv_cluster_idchoose:list=None):
        super().__init__()
        self.qwidget = qwidget
        self.qwidgetusv = qwidgetusv
        self.ip = ip
        self.to_continue = True
        df_bhv_labels2:pd.DataFrame = df_bhv_labels.sort_values(by=['cls_id'])
        df_usv_labels2:pd.DataFrame = df_usv_labels.sort_values(by=['yolo_id'])
        self.bhv_cluster_names = df_bhv_labels2['bhv_name'].to_list()
        self.bhv_cluster_idchoose = bhv_cluster_idchoose
        self.usv_cluster_names = np.array(df_usv_labels2['usv_name'].to_list())
        self.usv_cluster_idchoose = usv_cluster_idchoose

    def run(self):
        # rpcclient = picklerpc.PickleRPCClient((self.ip, 8092))
        rpcclient = picklerpc.PickleRPCClient(picklerpc_addr)
        while self.to_continue:
            try:
                bhv_int:int = rpcclient.label_int()
            except:
                rpcclient = picklerpc.PickleRPCClient(picklerpc_addr)
                bhv_int:int = rpcclient.label_int()
            if bhv_int>=0:
                self.bhv_cluster_names[bhv_int]
                text = self.bhv_cluster_names[bhv_int][:30]
                self.qwidget.setText(text)

            time.sleep(0.05)

        rpcclient.disconnect()


class PyThreadStimulate(threading.Thread):
    def __init__(self, bhv_inds:list=None, usv_inds:list=None, 
                 qwidgetstimu:QLabel=None, ip:str=None, obj_serial=None):
        super().__init__()
        self.to_continue = True
        self.obj_serial = obj_serial
        self.bhv_inds = bhv_inds
        self.usv_inds = usv_inds
        self.qwidgetstimu = qwidgetstimu
        self.ip = ip
        self.downcounter = 20
        
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect(('localhost', 20173))

    def run(self):
        # rpcclient = picklerpc.PickleRPCClient((self.ip, 8092))
        rpcclient = picklerpc.PickleRPCClient(picklerpc_addr)
        print("======begin stimuli condition")
        # set the 'qwidgetstimu' font color to red

        while self.to_continue and self.obj_serial.isValid:
            try:
                bhv_int:int = rpcclient.label_int()
            except:
                rpcclient = picklerpc.PickleRPCClient(picklerpc_addr)
                bhv_int:int = rpcclient.label_int()
            if bhv_int in self.bhv_inds:
                self.downcounter = 20
                self.qwidgetstimu.setStyleSheet("font-size: 28px; background-color: yellow;")
                self.obj_serial.send_message('b')
                self.tcp_socket.send(b'start_record')
                self.tcp_socket.recv(1024)
            else:
                self.downcounter -= 1
                if self.downcounter == 0:
                    self.qwidgetstimu.setStyleSheet("font-size: 28px;")
            # usv_int:np.ndarray = rpcclient.label_usv_int()
            time.sleep(0.05)
        
        print("======end stimuli")
        self.qwidgetstimu.setStyleSheet("font-size: 28px;")
        rpcclient.disconnect()
