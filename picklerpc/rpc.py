
import pickle
import socket
import inspect
from threading import Thread

SIZE = 1024

def recvall(sock:socket.socket):
    fragments = []
    while True: 
        chunk = sock.recv(SIZE)
        fragments.append(chunk)
        endbin = 0x2E
        if chunk[-1] == endbin:
            break
    arr = b''.join(fragments)
    return arr


class PickleRPCServer:

    def __init__(self, addr=None) -> None:
        if addr is None:
            addr = ('localhost', 8080)
        self.address = addr[0], int(addr[1])
        self.n_connection = 0
        self.funcs = {}

    def help(self) -> None:
        print('REGISTERED METHODS:')
        for method in self.funcs.items():
            print('\t',method)
    
    def register(self, name=None):
        """Registers a function to respond to Pickle-RPC requests.

        The optional name argument can be used to set a Unicode name
        for the function.
        """
        def decorator(func):
            _name = func.__name__ if name is None else name
            self.funcs[_name] = func
            return func
        return decorator

    def register_function(self, function=None, name=None):
        """Registers a function to respond to Pickle-RPC requests.

        The optional name argument can be used to set a Unicode name
        for the function.
        """
        # decorator factory
        if name is None:
            name = function.__name__
        self.funcs[name] = function

        return function
    
    def register_instance(self, instance=None) -> None:
        try:
            # Regestring the instance's methods
            for functionName, function in inspect.getmembers(instance, predicate=inspect.ismethod):
                if not functionName.startswith('__'):
                    self.funcs.update({functionName: function})
        except:
            raise Exception('A non class object has been passed into RPCServer.registerInstance(self, instance)')

    '''
        handle: pass client connection and it's address to perform requests between client and server (recorded fucntions or) 
        Arguments:
        client -> 
    '''
    def __handle__(self, client:socket.socket, address:tuple):
        print(f'Managing requests from {address}.')
        self.n_connection += 1
        while True:
            try:
                functionName, args, kwargs = pickle.loads(recvall(client))
            except: 
                print(f'! Client {address} disconnected.')
                break
            # Showing request Type            
            try:
                response = self.funcs[functionName](*args, **kwargs)
            except Exception as e:
                # Send back exeption if function called by client is not registred 
                print(e)
                client.sendall(pickle.dumps(str(e)))
            else:
                client.sendall(pickle.dumps(response))

        self.n_connection -= 1
        print(f'Completed request from {address}.')
        client.close()
    
    def serve_forever(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(self.address)
            sock.listen()

            print(f'+ Server {self.address} running')
            while True:
                try:
                    client, address = sock.accept()

                    Thread(target=self.__handle__, args=[client, address]).start()

                except KeyboardInterrupt:
                    print(f'- Server {self.address} interrupted')
                    break



class PickleRPCClient:
    def __init__(self, addr=None) -> None:
        if addr is None:
            addr = ('localhost', 8080)
        self.__sock = None
        self.__address = (addr[0], int(addr[1]))
        self.connect()

    def isConnected(self):
        try:
            self.__sock.sendall(b'test')
            self.__sock.recv(SIZE)
            return True

        except:
            return False

    def connect(self):
        try:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sock.settimeout(0.5)
            self.__sock.connect(self.__address)
        except EOFError as e:
            print(e)
            raise Exception('Client was not able to connect.')
    
    def disconnect(self):
        if self.__sock is None: return
        try:
            self.__sock.close()
        except:
            pass

    def __getattr__(self, __name: str):
        def excecute(*args, **kwargs):
            self.__sock.sendall(pickle.dumps((__name, args, kwargs)))

            response = pickle.loads(recvall(self.__sock))
   
            return response
        
        return excecute

    def __del__(self):
        self.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.disconnect()