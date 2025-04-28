
import numpy as np
import pyvirtualcam
import tqdm
import cv2
import socketserver
import threading

HOST, PORT = "0.0.0.0",20173


downratio = 2
width, height = 240//downratio, 120//downratio
vout = pyvirtualcam.Camera(width=width+40, height=height, fps=30, device='OBS Virtual Camera')
isactivate = False
strn = '000'


def thread_cam():
    global strn
    tbar = tqdm.tqdm()
    n=0
    global isactivate
    countdown = 15
    while True:
        tbar.update()
        frame = np.zeros((height, width+40, 3), np.uint8)
        if isactivate:
            frame[:,width+4:,1] = 255
            countdown -= 1
            if countdown <=0:
                isactivate = False
                countdown = 15
        
        strn = str(n%1000).zfill(3)
        cv2.putText(frame, strn, (5//downratio, 105//downratio), 
                    cv2.FONT_HERSHEY_SIMPLEX, 4//downratio, (255,255,255), 2)
        n+=1
        vout.send(frame)
        vout.sleep_until_next_frame()
    

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client

        print("conn is :",self.request) # conn
        print("addr is :",self.client_address) # addr

        try:
            while True:
                #收消息
                data = self.request.recv(1024)
                msg = data.decode("utf-8").strip()
                self.msgfilter(msg)
                if not data:break
                # print("收到客户端的消息是",data.decode("utf-8"))
                #发消息
        except Exception as e:
            print(e)

        print('Closed a request')

    def msgfilter(self, msg):
        global isactivate
        if msg=='start_record':
            isactivate = True
            self.request.sendall('starting'.encode("utf-8"))
        elif msg=='stop_record':
            isactivate = False
            self.request.sendall('stopping'.encode("utf-8"))
        elif msg=='get_status':
            self.request.sendall(strn.encode("utf-8"))
        else:
            self.request.sendall(msg.upper())



if __name__ == "__main__":
    threading.Thread(target=thread_cam, name='thread_cam').start()

    # Create the server, binding to localhost on port 9999
    print('start socket server')
    with ThreadedTCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()


