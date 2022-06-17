import sys
import time
import random
import sqlite3
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from socket import *

connection = sqlite3.connect("edu_stdt.db", check_same_thread=False)
cur = connection.cursor()
# db에서 출력시킬 문제를 불러옴

eduappwin = uic.loadUiType("eduapp.ui")[0]
sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('', 9039))
sock.send("student".encode())


# 메인화면
class Eduapp(QMainWindow, eduappwin):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 문제 관련 변수
        self.row_count = -1             # 퀴즈 개수만큼 테이블 행 만들기위한 카운트
        self.qna_row_cont = -1          # qna 테이블 행 만들기위한 카운트
        self.quiz_count = 0             # 푼 개수
        self.correct_quiz_answer = 0    # 맞힌 퀴즈 개수
        self.incorrect_quiz_answer = 0  # 틀린 퀴즈 개수
        self.quiz_list = []             # 퀴즈 불러와서 저장할 리스트 ( 이게 0이 되면 퀴즈 끝 )

        cur.execute("select num from english")
        self.AllQuizCount = len(cur.fetchall())     # 801

        # if not qqqq:    # 없다면, qqqq가 비었다면
        #     print("암것도없음")
        # if qqqq == []:    # 없다면, 빈칸이라면
        #     print("암것도없음")

        # 파이큐티 슬롯, Q쓰레드 실행
        self.rcv = Receive()
        self.rcv.signal1.connect(self.recv_msg)         # 리시브
        self.rcv.signal2.connect(self.id_check_recv)    # 로그인
        self.rcv.signal3.connect(self.id_double_check)  # 아이디 중복확인
        self.rcv.signal4.connect(self.recv_ExtraQuiz)   # 여분 퀴즈 받기
        self.rcv.signal5.connect(self.qna_refresh)      # qna 새로고침
        self.rcv.start()

        # 학습하기 출력
        cur.execute("select * from english")
        result1 = cur.fetchall()
        for i in result1:
            self.textBrowser.append(f'{i[0]} ) {i[1]}  -  {i[2]}')
        print("학습하기 출력")

        # 시그널
        self.backbtn.clicked.connect(self.movetopage0)          # 메인페이지
        self.pushButton1.clicked.connect(self.movetopage1)      # 학습하기
        self.pushButton2.clicked.connect(self.movetopage2)      # 문제풀기
        self.pushButton3.clicked.connect(self.movetopage3)      # 점수보기
        self.pushButton4.clicked.connect(self.movetopage4)      # QnA
        self.pushButton5.clicked.connect(self.movetopage6)      # 상담하기
        self.move_signup_page_btn.clicked.connect(self.movetopage5)      # 회원가입하기
        self.counsel_input_chat.returnPressed.connect(self.append_text)  # 상담창에서 엔터로 메세지 보내기
        self.send_btn.clicked.connect(self.append_text)                  # 상담창에서 보내기 버튼으로 메세지 보내기
        self.exit_btn.clicked.connect(self.exit_counsel_page)            # 상담창에서 나가기 버튼으로 나가기
        self.quiz_lineedit.returnPressed.connect(self.quiz_reset)        # 문제풀이 창에서 엔터로 답 입력하기
        self.login_btn.clicked.connect(self.id_check)                    # 로그인 확인하기
        self.add_quiz_btn.clicked.connect(self.add_quiz)                 # 문제 추가
        self.id_check_btn.clicked.connect(self.id_double_check1)         # 중복확인 클릭 시 아이디 서버로 전송
        self.signup_btn.clicked.connect(self.pw_double_check)            # 회원가입 버튼 클릭 시 회원가입 가능 or 불가능
        self.save_quiz_btn.clicked.connect(self.send_ExtraQuiz)          # 여분 퀴즈 서버에 보내기
        self.load_quiz_btn.clicked.connect(self.add_ExtraQuiz)           # 여분 퀴즈 불러오기
        self.qna_send_btn.clicked.connect(self.qna_send_to_serv)         # 질문 등록
        self.movetomainbtn.clicked.connect(self.movetomain1)             # 점수 칸에서 메인 페이지로 돌아가기
        self.qna_back_btn.clicked.connect(self.movetomain2)              # QnA 칸에서 메인 페이지로 돌아가기
        self.qna_refresh_btn.clicked.connect(self.qna_request_refresh)   # QnA 칸에서 새로고침

    # 시그널 함수
    def movetopage1(self):  # 학습하기 창
        self.stackedWidget.setCurrentWidget(self.page2)
        print("학습하기 창")

    # 페이지 이동 + 문제 제출하는 함수
    def movetopage2(self):  # 문제풀기 창
        self.stackedWidget.setCurrentWidget(self.page3)
        self.load_quiz_btn.setEnabled(True)
        self.add_quiz_btn.setEnabled(True)
        print("문제풀기 창")

        # cur.execute(f"select id from ExtraQuiz where id = '{self.id_lineedit.text()}'")
        # abc = cur.fetchall()
        #
        # if not abc:
        #     self.load_quiz_btn.setEnabled(False)
        # else:
        #     self.add_quiz_btn.setEnabled(False)

        # 테이블 위젯 설정
        cur.execute("select count(*) count from english")
        row_count = cur.fetchall()[0][0]
        self.quiztable.setRowCount(row_count)
        self.quiztable.setColumnWidth(0, 95)
        print("테이블 위젯 설정", row_count, type(row_count))

        # 문제풀기 재입장 시 조건 설정
        self.quiztable.clearContents()      # 테이블 위젯 다 삭제
        self.quiz_label.clear()             # 텍스트 라벨 클리어
        self.OXlabel.clear()                # OX 그림 라벨 클리어
        self.correct_answer.display(0)      # 맞은 퀴즈 개수 LCD 초기화
        self.incorrec_answer.display(0)     # 틀린 퀴즈 개수 LCD 초기화
        self.quiz_counter.display(0)        # 푼 퀴즈 개수  LCD 초기화
        self.correct_quiz_answer = 0        # 맞은 퀴즈 개수 초기화
        self.incorrect_quiz_answer = 0      # 틀린 퀴즈 개수 초기화
        self.quiz_count = 0                 # 푼 퀴즈 개수 초기화
        self.row_count = -1                 # 테이블 위젯 행 초기화
        self.quiz_list.clear()              # 퀴즈 리스트 초기화

        # 재입장 시 버튼들도 초기화
        if len(self.quiz_list) == 0:
            self.add_quiz_btn.setEnabled(True)
        else:
            self.add_quiz_btn.setEnabled(False)

    def movetopage3(self):  # 점수확인 창
        self.stackedWidget.setCurrentWidget(self.page4)
        self.label_3.setText(f"{self.correct_quiz_answer} / {self.quiz_count}")
        print("점수확인 창")

    def movetopage4(self):  # QnA 창
        self.qna_name_input.clear()
        self.qna_question_input.clear()
        self.qna_tablewidget.clearContents()  # 테이블 위젯 다 삭제
        self.stackedWidget.setCurrentWidget(self.page5)
        self.qna_tablewidget.setRowCount(999)
        self.qna_tablewidget.setColumnWidth(0, 100)
        self.qna_tablewidget.setColumnWidth(1, 350)
        self.qna_tablewidget.setColumnWidth(2, 400)
        print("QnA 창")

    def movetopage5(self):  # 회원가입 창
        self.make_id_line.clear()    # 회원가입 창 드갈 때마다
        self.make_pw_line.clear()    #
        self.check_pw_line.clear()   #
        self.make_name_line.clear()  # 싹 다
        self.make_mail_line.clear()  #
        self.id_check_label.clear()  #
        self.pw_check_label.clear()  # 비워주기
        self.signup_btn.setEnabled(False)  # 회원가입 버튼 비활성화 시켜놓기
        self.stackedWidget.setCurrentWidget(self.page6)
        print("회원가입 창")

    def movetopage6(self):  # 상담하기 창
        self.stackedWidget.setCurrentWidget(self.page7)
        print("상담하기 창")

    def movetopage0(self):  # 메인 페이지로 돌아가기 창
        self.stackedWidget.setCurrentWidget(self.page1)
        print("임시버튼")

    def movetomain1(self):  # 점수확인에서 메인페이지로
        self.stackedWidget.setCurrentWidget(self.page1)
        self.label_2.clear()
        self.label_3.clear()
        print("점수확인 >> 메인")

    def movetomain2(self):  # QnA에서 메인페이지로
        self.stackedWidget.setCurrentWidget(self.page1)
        self.qna_name_input.clear()
        self.qna_question_input.clear()
        print("QnA >> 메인")

    # 제일 처음 문제 출제하기
    def add_quiz(self):  # -> 커넥트 시그널
        # DB에서 문제 뽑아오기
        cur.execute("select * from english")
        allquiz = cur.fetchall()
        print("젤 첫 문제 출제")

        # 뽑아온 문제들 리스트에 저장
        for i in allquiz:
            self.quiz_list.append(i[1:])
        random.shuffle(self.quiz_list)  # 섞어주고
        print("리스트 셔플", self.quiz_list, "\n", len(self.quiz_list))

        # 리스트 길이가 0이면 문제풀이 시작하기 버튼 on, 아니면 off
        if len(self.quiz_list) == 0:
            self.add_quiz_btn.setEnabled(True)
        else:
            self.add_quiz_btn.setEnabled(False)

        # 화면에 문제 출력
        self.quiz_label.setText(f'{self.quiz_list[0][1]}')
        self.all_quiz_counter.display(self.quiztable.rowCount())  # 퀴즈 총 개수
        print("화면에 문제 출력", type(self.quiztable.rowCount()), self.quiztable.rowCount())

    def add_ExtraQuiz(self):
        cur.execute(f"select * from ExtraQuiz where id = '{self.id_lineedit.text()}'")
        allquiz = cur.fetchall()

        cur.execute(f"select id, OorX, count(*) from ExtraQuizCounter where id = '{self.id_lineedit.text()}' group by OorX")
        result = cur.fetchall()
        self.C_QuizCount = int(result[0][2])
        self.inC_QuizCount = int(result[1][2])

        # 뽑아온 문제들 리스트에 저장
        for i in allquiz:
            self.quiz_list.append(i[1:])
        random.shuffle(self.quiz_list)  # 섞어주고
        print("리스트 셔플2", self.quiz_list, "\n", len(self.quiz_list))

        # 리스트 길이가 0이면 문제풀이 시작하기 버튼 on, 아니면 off
        if len(self.quiz_list) == 0:
            self.add_quiz_btn.setEnabled(True)
        else:
            self.add_quiz_btn.setEnabled(False)

        # 화면에 문제 출력
        self.quiz_label.setText(f'{self.quiz_list[0][1]}')
        self.all_quiz_counter.display(len(self.quiz_list))  # 퀴즈 총 개수
        self.quiz_counter.display(self.AllQuizCount - len(self.quiz_list)) # 푼 퀴즈 개수

    # 다음 문제로 넘어가기위한 함수
    def quiz_reset(self):  # -> 커넥트 시그널
        self.quiz_label.setText("")
        self.make_quiz()
        self.quiz_lineedit.clear()
        print("퀴즈 리셋")

    # 계속해서 문제를 만들어주는 함수
    def make_quiz(self):  # -> quiz_reset
        self.row_count += 1
        quiz_text = self.quiz_lineedit.text()

        # 정답 입력 시
        if self.quiz_lineedit.text() == self.quiz_list[0][0]:
            print(f"정답(정) : {self.quiz_list[0][0]} 문제 : {self.quiz_list[0][1]}")
            a = self.OXlabel.setPixmap(QPixmap("O7070.png"))
            self.quiz_count += 1
            self.correct_quiz_answer += 1
            self.quiz_counter.display(self.quiz_count)  # 푼 문제 개수
            self.correct_answer.display(self.correct_quiz_answer)  # 맞힌 개수
            # 테이블 위젯에 정보들 입력, 0-출제된 문제, 1-내가 쓴 답, 2-문제의 정답, 3-O,X표시
            self.quiztable.setItem(self.row_count, 0, QTableWidgetItem(str(self.quiz_list[0][1])))
            self.quiztable.setItem(self.row_count, 1, QTableWidgetItem(str(quiz_text)))
            self.quiztable.setItem(self.row_count, 2, QTableWidgetItem(str(self.quiz_list[0][0])))
            self.quiztable.setItem(self.row_count, 3, QTableWidgetItem(str('O')))
            sock.send(f'^ {self.quiz_list[0][1]} {self.quiz_list[0][0]} O'.encode())
            cur.execute(f"insert into ExtraQuizCounter(id, OorX) values('{self.id_lineedit.text()}', 'O')")
            connection.commit()

        # 오답 입력 시
        elif self.quiz_lineedit.text() != self.quiz_list[0][0]:
            print(f"정답(오) : {self.quiz_list[0][0]} 문제 : {self.quiz_list[0][1]}")
            self.OXlabel.setPixmap(QPixmap("X7070.png"))
            self.quiz_count += 1
            self.incorrect_quiz_answer += 1
            self.quiz_counter.display(self.quiz_count)  # 푼 문제 개수
            self.incorrec_answer.display(self.incorrect_quiz_answer)  # 틀린 개수
            self.quiztable.setItem(self.row_count, 0, QTableWidgetItem(str(self.quiz_list[0][1])))
            self.quiztable.setItem(self.row_count, 1, QTableWidgetItem(str(quiz_text)))
            self.quiztable.setItem(self.row_count, 2, QTableWidgetItem(str(self.quiz_list[0][0])))
            self.quiztable.setItem(self.row_count, 3, QTableWidgetItem(str('X')))
            sock.send(f'^ {self.quiz_list[0][1]} {self.quiz_list[0][0]} X'.encode())
            cur.execute(f"insert into ExtraQuizCounter(id, OorX) values('{self.id_lineedit.text()}', 'X')")
            connection.commit()

        # 리스트에서 출제된 문제 삭제 후 다음 문제 표시해주기
        del self.quiz_list[0]
        print("리스트 삭제 후 다음 문제", self.quiz_list, len(self.quiz_list))
        self.quiz_label.setText(f'{self.quiz_list[0][1]}')

    # 여분 퀴즈 보내기 함수
    def send_ExtraQuiz(self):

        dialog = QDialog()
        dialog.setWindowTitle("저장 중, 기다려주세요")
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.resize(200, 100)
        dialog.show()

        # 남은 문제에 대한 점수(수치) 보내기 {특수문자+푼 개수 | 행 개수(전체 문제 수) | 맞은 개수 | 틀린 개수 | 점수}
        score = round((((self.quiz_count - self.incorrect_quiz_answer) / (self.quiztable.rowCount())) * 100), 3)
        print("전체 문제 수", self.quiztable.rowCount(), "\n틀린 개수", self.incorrect_quiz_answer)
        print("남은 문제 보내기",
              f'{chr(1111)} {self.quiz_count} {self.quiztable.rowCount()} {self.correct_quiz_answer} {self.incorrect_quiz_answer} {score}')
        sock.send(
            f'{chr(1111)} {self.quiz_count} {self.quiztable.rowCount()} {self.correct_quiz_answer} {self.incorrect_quiz_answer} {score}'.encode())
        self.stackedWidget.setCurrentWidget(self.page1)
        sock.send("버퍼사이즈크게".encode())
        time.sleep(0.1)
        data_msg = ""
        for i in self.quiz_list:
            data_msg += f'{chr(1003)}{i[1]}{chr(1001)}{i[0]}'
        print("여분 퀴즈 보내기", f'{chr(1003)}{i[1]}{chr(1001)}{i[0]}')
        print("보낼메시지 사이즈는", len(data_msg.encode()))
        if len(data_msg.encode()) >= 2 ** 14:
            print(f"\n\nㅗㅗ보낼려는 메시지가 {2 ** 14}바이트 보다 커요ㅗㅗ\n\n")
        sock.send(data_msg.encode())
        time.sleep(0.1)
        sock.send("버퍼사이즈원래".encode())
        for j in self.quiz_list:
            cur.execute(f"insert into ExtraQuiz(id, quiz, answer) values ('{self.id_lineedit.text()}', '{j[1]}', '{j[0]}')")
            connection.commit()

        self.quiz_list.clear()  # 퀴즈 리스트 초기화
        print("퀴즈 리스트 초기화", len(self.quiz_list))


    # 상담 채팅 창에 채팅 띄우기, 서버에 메세지 보내기
    def append_text(self):  # -> 커넥트 시그널
        msg = self.counsel_input_chat.text()
        data = "@상담학생"+self.counsel_input_chat.text()
        sock.send(data.encode())
        self.counsel_chat_box.append(msg)
        self.counsel_input_chat.clear()
        # inputchat = self.counsel_input_chat.text()
        # sock.send(('@상담학생' + inputchat).encode())
        # self.counsel_chat_box.append(f'학생 {inputchat}')
        # self.counsel_input_chat.clear()


    # 상담 페이지 벗어나는 함수
    def exit_counsel_page(self):  # -> 커넥트 시그널
        self.counsel_chat_box.clear()
        self.stackedWidget.setCurrentWidget(self.page0)
        print("상담 페이지 벗어나기")

    # 아이디 비번 확인 절차를 위해 서버에 전송
    def id_check(self):  # -> 커넥트 시그널
        input_id = self.id_lineedit.text()
        input_pw = self.pw_lineedit.text()
        sock.send(f'# {input_id} {input_pw}'.encode())
        print("아이디 비번 확인 절차, 서버에 전송")

    # 아이디 중복확인 절차 함수
    def id_double_check1(self):  # -> 커넥트 시그널
        make_id_line = self.make_id_line.text()
        sock.send(f'? {make_id_line}'.encode())
        print("아이디 중복확인 절차")

    # 회원가입 함수
    def pw_double_check(self):  # -> 커넥트 시그널
        print("회원가입 성공하니 ?")
        if self.id_check_label.text() == "사용가능 아이디":
            print(" 회원가입 성공 1 ")
            if self.make_pw_line.text() == self.check_pw_line.text():
                print(" 회원가입 성공 2 ")
                if self.make_name_line.text():
                    print(" 회원가입 성공 3 ")
                    if bool(self.make_mail_line.text()):
                        print(" 회원가입 성공 4 ")
                        sock.send(
                            f'{chr(2000)} {self.make_id_line.text()} {self.make_pw_line.text()} {self.make_name_line.text()} {self.make_mail_line.text()}'.encode())
                        self.stackedWidget.setCurrentWidget(self.page0)

            elif self.make_pw_line.text() != self.check_pw_line.text():
                self.pw_check_label.setText("")
                self.pw_check_label.setText("비번이 서로 다름")

    # QnA 서버에 보내는 함수
    def qna_send_to_serv(self):
        print("qna 서버 보내기, 올리기")
        self.qna_row_cont += 1
        # self.qna_tablewidget.setRowCount(self.qna_row_cont)
        sock.send(f'{chr(3333)} {self.qna_name_input.text()} {self.qna_question_input.text()}'.encode())
        print("큐엔에이 이렇게 갑니다", f'{chr(3333)} {self.qna_name_input.text()} {self.qna_question_input.text()}')
        self.qna_tablewidget.setItem(self.qna_row_cont, 0, QTableWidgetItem(str(self.qna_name_input.text())))
        self.qna_tablewidget.setItem(self.qna_row_cont, 1, QTableWidgetItem(str(self.qna_question_input.text())))
        self.qna_tablewidget.setItem(self.qna_row_cont, 2, QTableWidgetItem(str("답 변 대 기")))
        self.qna_name_input.clear()
        self.qna_question_input.clear()

    # 새로고침 요청 함수
    def qna_request_refresh(self):
        print("새로고침 요청")
        sock.send(f'{chr(4444)}'.encode())

    # 받은 메세지 상담 창에 띄워주기
    @pyqtSlot(str)
    def recv_msg(self, msg):
        print("7")
        self.counsel_chat_box.append(msg)


    # 아이디, 비번 맞을 시 로그인 성공
    @pyqtSlot(str)
    def id_check_recv(self, msg):
        print("8", msg)
        if "OK, GO!" == msg:
            self.stackedWidget.setCurrentWidget(self.page1)

    # 아이디 중복 확인
    @pyqtSlot(str)
    def id_double_check(self, msg):
        if msg == "중복됨":
            self.id_check_label.setText("")
            self.id_check_label.setText("중복된 아이디")
            print("아이디 중복됨")
        elif msg == "사용가능한 아이디":
            self.id_check_label.setText("")
            self.id_check_label.setText("사용가능 아이디")
            self.signup_btn.setEnabled(True)
            self.make_id_line.setEnabled(False)
            print("아이디 사용 가능")

    # 여분 퀴즈 받아오기
    @pyqtSlot(str)
    def recv_ExtraQuiz(self, data):
        if chr(3000) in data:
            data_split1 = data.split(chr(3000))
            print("여분 퀴즈 왔읍니다 ~", data_split1)
            # cur.execute(f"insert into ExtraQuiz (id, quiz, answer) values ('{}', '{}', '{}')")
            # connection.commit()

    @pyqtSlot(str)
    def qna_refresh(self, msg):
        teacher_answer = msg.split("/")
        self.qna_tablewidget.setItem(int(teacher_answer[1]) - 1, 2, QTableWidgetItem(str(teacher_answer[2])))
        print("qna 새로고침", msg)





# 받기, 큐 쓰레드
class Receive(QThread):
    signal1 = pyqtSignal(str)  # 리시브
    signal2 = pyqtSignal(str)  # 로그인
    signal3 = pyqtSignal(str)  # 아이디 중복 확인
    signal4 = pyqtSignal(str)   # 여분 퀴즈 받아오기
    signal5 = pyqtSignal(str)  # qna 새로고침
    print("9")

    def run(self):
        while True:
            print("10", sock)
            msg = sock.recv(8192)
            data = msg.decode()
            print("11", data)
            if not data:
                print("메세지 없어서 종료")
                break
            if "OK, GO!" == data:
                self.signal2.emit(f'OK, GO!')
            elif "중복됨" == data or "사용가능한 아이디" == data:
                if data == "중복됨":
                    self.signal3.emit(f'중복됨')
                elif data == "사용가능한 아이디":
                    self.signal3.emit("사용가능한 아이디")
            elif chr(3000) in data:
                self.signal4.emit(data)
            elif chr(4444) == data[0]:
                print("4444", data)
                self.signal5.emit(data)
            elif "@상담교사" == data[:len("@상담교사")]:
                self.signal1.emit(f'교사 : {data[len("@상담교사"):]}')
                print("교사 체팅을 서버가 보내줌")
            # else:
            #     print("else:")
            #     # self.signal1.emit(data[len("@상담교사"):])
            #     self.signal1.emit(data[len("@상담교사"):])
        # try:
        #     self.sock.close()
        # except:
        #     print("소켓이 이미 꺼져있음")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    eduapp = Eduapp()
    eduapp.show()
    app.exec_()