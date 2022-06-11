import sqlite3
from socket import *
from threading import *


# connection = pymysql.connect(host='localhost', port=3306, user='root', password='1234',
#                              db='education', charset='utf8')
connection = sqlite3.connect("edu.db", check_same_thread = False)
cur = connection.cursor()

class Serv:
    def __init__(self):
        super(Serv, self).__init__()
        self.clients = []
        self.ip = ''
        self.port = 7500
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(5)
        print(" 접 속 자 대 기 중 . . . ")
        self.accept()

# 클라 연결 요청
    def accept(self):
        while True:
            print("1")
            c_sock, (r_host, r_port) = self.sock.accept()
            print(f"{c_sock} 접속함")
            if c_sock not in self.clients:
                self.clients.append(c_sock)
            print(f'{r_host}:{str(r_port)}가 연결되었습니다.')

            c_thd = Thread(target=self.recv_msg, args=(c_sock,))
            c_thd.start()

    def recv_msg(self, c_sock):
        while True:
            try:
                data = c_sock.recv(1024)
                print(f"받은 메세지 : {data.decode()}")
                if not data:
                    break
            except:
                continue
            else:
                final_msg = data.decode()
                print(final_msg)
                self.send_all_clients(c_sock,final_msg)
        c_sock.close()

    def send_all_clients(self, c_sock,final_msg):
        for client in self.clients:
            socket = client
            if socket is not c_sock:
                try:
                    socket.send(final_msg.encode())
                except:
                    self.clients.remove(client)



if __name__ == "__main__":
    Serv()