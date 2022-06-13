from socket import *
from threading import *
import sqlite3

con = sqlite3.connect("edu.db", check_same_thread = False)
db = con.cursor()

class Serv:
    def __init__(self):
        super(Serv, self).__init__()
        self.sclients = []
        self.tclients = []
        self.ip = ''
        self.port = 9035
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
            data = c_sock.recv(1024).decode()
            if data == 's': # 학생일 경우
                print(f"{c_sock} 접속함")
                if c_sock not in self.sclients:
                    self.sclients.append(c_sock, 0) # 선생님과 채팅을 활성화시키기 위해 0 추가
                print(f'{r_host}:{str(r_port)}가 연결되었습니다.')
            elif data == 't': # 선생일 경우
                if c_sock not in self.tclients:
                    self.tclients.append(c_sock, 0) # 선생님과 채팅을 활성화시키기 위해 0 추가
                print(f'{r_host}:{str(r_port)}가 연결되었습니다.')
            c_thd = Thread(target=self.recv_msg, args=(c_sock,))
            c_thd.start()

    def recv_msg(self, c_sock):
        idcount = 0
        advice = 0
        while True:
            try:
                data = c_sock.recv(1024).decode()
                print(f"받은 메세지 : {data}")
                if not data:
                    break
            except:
                continue
            else:
                print(data)
                data = data.split('')
                if data[0] == '1': # 로그인 하려고 아이디와 비밀번호를 넘겼을 경우
                    # 넘어올것으로 예상되는 데이터
                    # 아이디, 비밀번호
                    db.execute(f"select count(*) from usertbl where id = '{data[1]} and pw = '{data[2]}'")
                    if int(db.fetchall()[0][0]) == 0:
                        c_sock.send('로그인 성공'.encode())
                    else:
                        c_sock.send('로그인 실패'.encode())
                elif data[0] == '2': # 로그인화면에서 아이디 중복확인
                    # 넘어올것으로 예상되는 데이터
                    # 아이디
                    idcount = 0
                    db.execute(f"select count(*) from usertbl where id = '{data[1]}'")
                    if int(db.fetchall()[0][0]) > 0:
                        c_sock.send('아이디 중복됨'.encode())
                    else:
                        c_sock.send('사용해도 되는 아이디입니다.'.encode())
                        idcount = 1  # 아이디 중복여부 확인
                elif data[0] == '3': # 회원가입
                    # 넘어올것으로 예상되는 데이터
                    # 아이디, 비밀번호, 비밀번호 확인, 이름, 이메일
                    if data[2] == data[3] and idcount == 1: # 비밀번호가 일치 and 아이디 중복여부 확인한 상태
                        db.execute(f"insert into usertbl values('{data[1]}','{data[2]}','{data[4]}','{data[5]}')")
                        c_sock.send('회원가입이 완료되었습니다.'.encode())
                        # 클라이언트 리스트에 학생아이디 추가
                        for i in self.sclients:
                            if c_sock in i:
                                i.append(data[1])
                    else:
                        c_sock.send('비밀번호가 일치하지 않습니다.'.encode())
                elif data[0] == '4': # 문제를 풀고 난 후
                    # 넘어올 것으로 예상되는 데이터
                    # 학생아이디, 문제, 정답, 문제분야, 맞춘문제 갯수, 틀린문제 갯수
                    db.execute(f"insert into resulttbl values('{data[1]}','{data[2]}','{data[3]}','{data[4]}','{data[5]}','{data[6]}')")
                elif data[0] == '5': # 점수확인
                    # 넘어올 것으로 예상되는 데이터
                    # 학생아이디
                    db.execute(f"select * from quiztbl where id = '{data[1]}'")
                    while c_sock.send(db.fetchone().encode()) != 0: pass
                elif data[0] == '6': # Q&A에서 질문하는 버튼을 눌렀을 때
                    # 넘어올 것으로 예상되는 데이터
                    # 학생아이디, 질문
                    db.execute(f"insert into qnatbl values('{data[1]}','{data[2]}',NULL)")
                elif data[0] == '7': # 상담버튼을 눌렀을 경우
                    # 넘어올 것으로 예상되는 데이터
                    # 학생아이디, 연결을 요청할 선생님아이디
                    tid = data[2]
                    for i in self.sclients:
                        if data[1] in i:
                            i[1] = 1
                    for j in self.tclients:
                        if tid in j:
                            j[1] = 1
                    advice = 1
                if advice == 0:
                    self.send_all_clients(c_sock, data)
                else:# 만약 상담을 하고 있는 상태라면 메세지를 해당 선생님에게만 보냄
                    self.send_clients(i, data) # 자신과 상태(client의 두번째 인자)가 같은 선생님에게만 메세지를 송출
        c_sock.close()

    def send_all_clients(self, c_sock, final_msg):
            for client in self.sclients:
                socket = client
                if socket is not c_sock:
                    try:
                        socket.send(final_msg.encode())
                    except:
                        self.sclients.remove(client)
    def send_clients(self, sclient, data):
            for tclient in self.tclients:
                if sclient[1] == tclient[1]:
                    tclient[0].send(data)

if __name__ == "__main__":
    Serv()