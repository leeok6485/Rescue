import sys
import time
import random
import sqlite3
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from socket import *
from threading import *

connection = sqlite3.connect("edu.db", check_same_thread = False)
cur = connection.cursor()
cur.execute("select * from english")
result1 = cur.fetchall()

eduappwin = uic.loadUiType("eduapp.ui")[0]
sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('', 7500))

# 메인화면
class Eduapp(QMainWindow, eduappwin):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 출제할 문제를 저장할 딕셔너리
        self.quiz_dic = {}

# 파이큐티 슬롯
        self.rcv = Receive()
        self.rcv.signal1.connect(self.recv_msg)
        # self.rcv.signal2.connect(self.recv_msg_1)
        self.rcv.start()
        print("check - 1")

        for i in result1:
            self.textBrowser.append(f'{i[0]} ) {i[1]}  -  {i[2]}')


# 시그널
        self.backbtn.clicked.connect(self.movetopage0)
        self.pushButton1.clicked.connect(self.movetopage1)
        self.pushButton2.clicked.connect(self.movetopage2)
        self.pushButton3.clicked.connect(self.movetopage3)
        self.pushButton4.clicked.connect(self.movetopage4)
        self.pushButton5.clicked.connect(self.movetopage6)
        self.move_signup_page_btn.clicked.connect(self.movetopage5)
        self.counsel_input_chat.returnPressed.connect(self.append_text)
        self.send_btn.clicked.connect(self.append_text)
        self.exit_btn.clicked.connect(self.exit_counsel_page)
        self.quiz_lineedit.returnPressed.connect(self.quiz_reset)

# 시그널 함수
    def movetopage1(self):
        self.stackedWidget.setCurrentWidget(self.page1)
    def movetopage2(self):
        self.stackedWidget.setCurrentWidget(self.page2)
        cur.execute("select * from english order by random() limit 1")
        result2 = cur.fetchall()
        for i in result2:
            print(i)
            self.quiz_dic[i[1]] = i[2]
            self.quiz_label.setText(f'{i[1]}')
            print("딕셔너리 잘 드갔니 ?", self.quiz_dic)
    def movetopage3(self):
        self.stackedWidget.setCurrentWidget(self.page3)
    def movetopage4(self):
        self.stackedWidget.setCurrentWidget(self.page4)
    def movetopage5(self):
        self.stackedWidget.setCurrentWidget(self.page5)
    def movetopage6(self):
        self.stackedWidget.setCurrentWidget(self.page6)
    def movetopage0(self):
        self.stackedWidget.setCurrentWidget(self.page0)

    def quiz_reset(self):
        time.sleep(0.1)
        self.quiz_label.setText("")
        self.make_quiz()
        self.quiz_lineedit.clear()

    def make_quiz(self):
        cur.execute("select * from english order by random() limit 1")
        result2 = cur.fetchall()
        # 문제 정답 검토
        for j in self.quiz_dic:
            print("제이!", j, self.quiz_dic[j])
            if self.quiz_lineedit.text() == self.quiz_dic[j]:
                print(f"답 : {self.quiz_lineedit.text()} 정답 : {self.quiz_dic[j]}")
                print("정답")
            elif self.quiz_lineedit.text() != self.quiz_dic[j]:
                print(f"답 : {self.quiz_lineedit.text()} 정답 : {self.quiz_dic[j]}")
                print("ㅋㅋ붕신~")
        # 다음 문제를 위해서 문제 없애기
        self.quiz_dic.clear()
        # 문제 출제하기
        for i in result2:
            print(i)
            self.quiz_dic[i[1]] = i[2]
            self.quiz_label.setText(f'{i[1]}')
            print("딕셔너리 잘 드갔니 ?", self.quiz_dic)


    # 상담 채팅 창에 채팅 띄우기, 서버에 메세지 보내기
    def append_text(self):
        inputchat = self.counsel_input_chat.text()
        sock.send(inputchat.encode())
        self.counsel_chat_box.append(f'학생 : {inputchat}')
        self.counsel_input_chat.clear()

    # 상담 페이지 벗어나는 함수
    def exit_counsel_page(self):
        self.counsel_chat_box.clear()
        self.stackedWidget.setCurrentWidget(self.page0)

    # 아이디 비번 확인 절차를 위해 서버에 전송
    def id_check(self):
        input_id = self.id_lineedit.text()
        input_pw = self.pw_lineedit.text()
        sock.send(f'#({input_id}, {input_pw})'.encode())

    # 회원가입 시 아이디 중복확인 절차
    def id_double_check(self):
        make_id_line = self.make_id_line.text()
        sock.send(f'##{make_id_line}'.encode())



    @pyqtSlot(str)
    def recv_msg(self, msg):
        print("여기까지 오니 ?")
        self.counsel_chat_box.append(msg)

    # @pyqtSlot(str)
    # def recv_msg_1(self, msg):
    #     print("여기까지 오니 ?")
    #     self.counsel_chat_box.append(msg)

# 받기, 큐 쓰레드
class Receive(QThread):
    signal1 = pyqtSignal(str)
    # signal2 = pyqtSignal(str)
    print("check - 2")

    def run(self):
        while True:
            print("3", sock)
            msg = sock.recv(1024)
            data = msg.decode()
            print("check - 4", data)
            self.signal1.emit(f'선생님 : {data}')
            # self.signal2.emit(f'{data}')
        self.sock.close()



if __name__ == "__main__" :
    app = QApplication(sys.argv)
    eduapp = Eduapp()
    eduapp.show()
    app.exec_()