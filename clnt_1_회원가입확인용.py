import sys
import random
import sqlite3
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from socket import *

# connection = pymysql.connect(host='localhost', port=3306, user='root', password='1234',
#                              db='education', charset='utf8')
connection = sqlite3.connect("edu.db", check_same_thread = False)
cur = connection.cursor()
cur.execute("select * from english")
result1 = cur.fetchall()

# eduappwin = uic.loadUiType("eduapp(copy).ui")[0]
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
        self.quiz_count = 0
        self.correct_quiz_answer = 0
        self.incorrect_quiz_answer = 0

# 파이큐티 슬롯
        self.rcv = Receive()
        self.rcv.signal1.connect(self.recv_msg)
        # self.rcv.signal2.connect(self.id_check_recv)
        self.rcv.start()

        for i in result1:
            self.textBrowser.append(f'{i[0]} ) {i[1]}  -  {i[2]}')


# 시그널
        self.backbtn.clicked.connect(self.movetopage0)                  # 메인페이지
        self.pushButton1.clicked.connect(self.movetopage1)              # 학습하기
        self.pushButton2.clicked.connect(self.movetopage2)              # 문제풀기
        self.pushButton3.clicked.connect(self.movetopage3)              # 점수보기
        self.pushButton4.clicked.connect(self.movetopage4)              # QnA
        self.pushButton5.clicked.connect(self.movetopage6)              # 상담하기
        self.move_signup_page_btn.clicked.connect(self.movetopage5)     # 회원가입하기
        self.counsel_input_chat.returnPressed.connect(self.append_text) # 상담창에서 엔터로 메세지 보내기
        self.send_btn.clicked.connect(self.append_text)                 # 상담창에서 보내기 버튼으로 메세지 보내기
        self.exit_btn.clicked.connect(self.exit_counsel_page)           # 상담창에서 나가기 버튼으로 나가기
        self.quiz_lineedit.returnPressed.connect(self.quiz_reset)       # 문제풀이 창에서 엔터로 답 입력하기
        self.login_btn.clicked.connect(self.id_check)                   # 로그인 확인하기
        self.id_check_btn.clicked.connect(self.id_double_check)         # 회원가입시 아이디 중복확인하기(아이디 전송)
        # self.id_double_check2()

# 시그널 함수
    def movetopage1(self):  # 학습하기 창
        self.stackedWidget.setCurrentWidget(self.page2)
    # 페이지 이동 + 문제 제출하는 함수
    def movetopage2(self):  # 문제풀기 창
        self.stackedWidget.setCurrentWidget(self.page3)
        cur.execute("select * from english order by random() limit 1")
        result2 = cur.fetchall()
        for i in result2:
            print("0", i)
            self.quiz_dic[i[1]] = i[2]
            self.quiz_label.setText(f'{i[2]}')
            print("딕셔너리 잘 드갔니 ?", self.quiz_dic)
    def movetopage3(self):  # 점수확인 창
        self.stackedWidget.setCurrentWidget(self.page4)
    def movetopage4(self):  # QnA 창
        self.stackedWidget.setCurrentWidget(self.page5)
    def movetopage5(self):  # 회원가입 창
        self.stackedWidget.setCurrentWidget(self.page6)
    def movetopage6(self):  # 상담하기 창
        self.stackedWidget.setCurrentWidget(self.page7)
    def movetopage0(self):  # 메인 페이지로 돌아가기 창
        self.stackedWidget.setCurrentWidget(self.page1)

    # 문제를 표시해주고 제출해주는 함수
    def quiz_reset(self):
        self.quiz_label.setText("")
        self.make_quiz()
        self.quiz_lineedit.clear()
    # 문제를 만들어주는 함수
    def make_quiz(self):
        cur.execute("select * from english order by random() limit 1")
        result2 = cur.fetchall()
        # 문제 정답 검토
        for j in self.quiz_dic:
            if self.quiz_count == 20:
                self.quiz_count = 0
            else :
                self.quiz_count += 1
                self.quiz_counter.display(self.quiz_count)
                print("제이!", j, self.quiz_dic[j])
                if self.quiz_lineedit.text() == j:
                    print(f"답 : {self.quiz_lineedit.text()} 정답 : {self.quiz_dic[j]}")
                    print("정답")
                    self.OXlabel.setPixmap(QPixmap("O7070.png"))
                    self.correct_quiz_answer += 1
                    self.correct_answer.display(self.correct_quiz_answer)
                elif self.quiz_lineedit.text() != j:
                    print(f"답 : {self.quiz_lineedit.text()} 정답 : {self.quiz_dic[j]}")
                    print("ㅋㅋ틀렸네 붕신~")
                    self.OXlabel.setPixmap(QPixmap("X7070.png"))
                    self.incorrect_quiz_answer += 1
                    self.incorrec_answer.display(self.incorrect_quiz_answer)
        # 다음 문제를 위해서 문제 없애기
        self.quiz_dic.clear()
        # 문제 출제하기
        for i in result2:
            print(i)
            self.quiz_dic[i[1]] = i[2]
            self.quiz_label.setText(f'{i[2]}')
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
        sock.send(f'# {input_id} {input_pw}'.encode())

    # 회원가입 시 아이디 중복확인 절차
    def id_double_check(self):
        make_id_line = self.make_id_line.text()
        sock.send(f'{make_id_line}'.encode())  # 서버에 아이디 중복 체크를 위해 아이디를 전송

    def id_double_check2(self):
        data = sock.recv(1024)
        msg = data.decode()
        print("가입여부 :", msg)
        # 아이디를 서버 DB내의 정보와 비교하여 동일하면 거절







    @pyqtSlot(str)
    def recv_msg(self, msg):
        print("여기까지 오니 ?")
        if '선생님 :' in msg:
            self.counsel_chat_box.append(msg)

    @pyqtSlot(str)
    def id_check_recv(self, msg):
        msg = sock.recv(1024)
        print("서버 ID 확인 체크", msg)
        data = msg.decode()
        print("check - id recv", data)
        if data == "no":
            self.id_check_label.setText("존재 하는 ID 입니다")
        else:
            self.id_check_label.setText("존재 하지 않는 ID 입니다")

# 받기, 큐 쓰레드
class Receive(QThread):
    signal1 = pyqtSignal(str)
    signal2 = pyqtSignal(str)
    print("check - 2")

    def run(self):
        while True:
            print("3", sock)
            msg = sock.recv(1024)
            data = msg.decode()
            print("check - 4", data)
            self.signal1.emit(f'선생님 : {data}')
            if "no" == data:
                self.signal2.emit(f'OK, GO!')
        self.sock.close()



if __name__ == "__main__" :
    app = QApplication(sys.argv)
    eduapp = Eduapp()
    eduapp.show()
    app.exec_()