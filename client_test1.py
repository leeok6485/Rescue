import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

svrIP = input("IP입력(디폴트:127.0.0.1) : ")
if svrIP == '':
    svrIP = '127.0.0.1'

port = input("port(디폴트:3000) : ")
if port == '':
    port = 3000
else:
    port = int(port)

sock.connect((svrIP, port))
print(svrIP, "에서 연결")

while True:
    msg = input("보낼 메시지 : ")
    if not msg:
        continue
    try:
        sock.send(msg.encode())

    except:
        print("연결 종료")
        break
    try:
        msg = sock.recv(1024)
        if not msg:
            print("연결 종료")
            break
        print(f'받은 메시지 : {msg.decode()}')

    except:
        print("연결 종료")
        break
sock.close()