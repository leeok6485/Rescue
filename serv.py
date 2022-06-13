import socket
import threading
import sqlite3

con = sqlite3.connect("serv.db", check_same_thread = False)
db = con.cursor()

def handler(c, a):
    global connections
    while True:
        data = c.recv(1024).decode()
        if not data:
            connections.remove(c)
            c.close()
            break
        if data == '1':
            c.send('ID를 입력해주세요.'.encode())
            userid = c.recv(1024).decode()
            c.send('PW를 입력해주세요.'.encode())
            userpw = c.recv(1024).decode()
            db.execute(f"SELECT COUNT(*) FROM usertbl where id = '{userid}' and pw = '{userpw}'")
            if int(db.fetchall()[0][0]) == 0:
                c.send('로그인 실패.'.encode())
            else:
                c.send('로그인 성공.'.encode())
        elif data == '2':
            c.send('ID를 입력해주세요.'.encode())
            userid = c.recv(1024).decode()
            c.send('PW를 입력해주세요.'.encode())
            userpw = c.recv(1024).decode()
            c.send('이름을 입력해주세요.'.encode())
            name = c.recv(1024).decode()                
            c.send('전화번호를 입력해주세요.'.encode())
            phone = c.recv(1024).decode()
            db.execute(f"SELECT COUNT(*) FROM usertbl where id = '{userid}'")
            if int(db.fetchall()[0][0]) == 0:
                db.execute(f"insert into usertbl values ('{userid}','{userpw}','{name}','{phone}', 't')")
                c.send('회원가입이 완료되었습니다.'.encode())
            else:
                c.send('중복되는 아이디가 있습니다.'.encode())
        elif data == '3':
            sel = c.recv(1024).decode()
            if sel == '1':
                c.send('이름을 입력해주세요.'.encode())
                name = c.recv(1024).decode()
                c.send('전화번호를 입력해주세요.'.encode())
                phone = c.recv(1024).decode()
                db.execute(f"SELECT id FROM usertbl where username = '{name}' and phone = '{phone}'")
                userid = db.fetchall()
                if not userid:
                    c.send('잘못 입력하셨습니다.'.encode())
                else:
                    c.send(f'ID : {userid[0][0]}'.encode())
            elif sel == '2':
                c.send('ID를 입력해주세요.'.encode())
                userid = c.recv(1024).decode()
                c.send('전화번호를 입력해주세요.'.encode())
                phone = c.recv(1024).decode()
                db.execute(f"SELECT pw FROM usertbl where id = '{userid}' and phone = '{phone}'")
                userpw = db.fetchall()
                if not userpw:
                    c.send('잘못 입력하셨습니다.'.encode())
                else:
                    c.send(f'PW : {userpw[0][0]}'.encode())
            elif sel == '3':
                continue

    while True:
        data = c.recv(1024).decode()
        if not data:
            connections.remove(c)
            c.close()
        if data == '1':
            c.send('문제업데이트를 선택하셨습니다.'.encode())
            c.send('제출하고 싶은 문제를 입력해주세요.'.encode())
            quiz = c.recv(1024).decode()
            c.send('문제의 정답을 입력해주세요.'.encode())
            ans = c.recv(1024).decode()
            db.execute(f"insert into usertbl values ('{userid}', '{quiz}', '{ans}')")
            c.send('문제가 등록되었습니다.'.encode())
        elif data == '2':
            c.send('점수통계확인을 선택하셨습니다.'.encode())
        elif data == '3':
            c.send('부족한 Part 확인을 선택하셨습니다.'.encode())
        elif data == '4':
            c.send('Q&A를 선택하셨습니다.'.encode())
        elif data == '5':
            c.send('실시간 학생상담을 선택하셨습니다.'.encode())
            

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("",9035))
sock.listen(1)
connections = []

while True:
    c, a = sock.accept()
    job = c.recv(1024)
    if job.decode() == 'teacher':
        print('선생님입니다.')
    if job.decode() == 'students':
        print('학생입니다.')
    connections.append(c)
    cThread = threading.Thread(target = handler, args = (c, a))
    cThread.daemon = True
    cThread.start()
    print(connections)