import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from socket import *

form_class = uic.loadUiType("teacher.ui")[0]
sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('', 9036))
sock.send("teacher".encode())


class Window(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 버튼 기능
        self.q_upload_btn.clicked.connect(self.move_q_upload_page)
        self.q_send_btn.clicked.connect(self.append_question)
        # self.q_send_btn.clicked.connect(self.check)
        self.q_send_btn.setText("문제 출제")
        self.q_upload_btn.setText("문제출제하기")
        self.chat_btn.clicked.connect(self.move_chat_page)
        self.q_list_check.clicked.connect(self.show_question)
        self.q_list_check.setText("문제확인")
        self.chat_btn.setText("실시간 상담")
        self.qna_btn.clicked.connect(self.move_qna_page)
        # self.qna_btn.clicked.connect(self.qna_view)
        self.qna_aupload.clicked.connect(self.send_qna_a)
        self.qna_btn.setText("QnA 게시판")
        self.s_info_btn.clicked.connect(self.move_info_page)
        self.s_info_btn.setText("학생정보열람")
        self.upload_back_btn.clicked.connect(self.move_start_page)
        self.upload_back_btn.clicked.connect(self.clear)
        self.upload_back_btn.setText("뒤로가기")
        self.info_back_btn.clicked.connect(self.move_start_page)
        self.info_back_btn.clicked.connect(self.clear)
        self.info_back_btn.setText("뒤로가기")
        self.qna_back_btn.clicked.connect(self.move_start_page)
        self.qna_back_btn.clicked.connect(self.clear)
        self.qna_back_btn.setText("뒤로가기")
        self.chat_back_btn.clicked.connect(self.move_start_page)
        self.chat_back_btn.clicked.connect(self.clear)
        self.chat_back_btn.setText("뒤로가기")

        # 문제출제창 설정
        # 리스트위젯을 써서 현재 존재하는 모든 문제를 출력
        # 입력칸을 만들어서 문제를 입력할까?
        self.q_list.resize(900, 450)
        self.q_upload.resize(300, 40)
        self.a_upload.resize(300, 40)
        self.q_up_label.setText("단어")
        self.a_up_label.setText("뜻")
        self.rcv = Receive()
        self.rcv.chat.connect(self.recv_chat)
        self.rcv.chat2.connect(self.recv_chat2)
        self.rcv.chat3.connect(self.recv_chat3)
        self.rcv.chat4.connect(self.recv_chat4)
        self.rcv.start()

        # 학생정보열람창 설정
        # 학생의 이름을 입력 했을 때 DB내의 그 학생의 값을 전부 출력할 부분
        # 학생이름을 그냥 입력 받을곳
        self.s_info_browser.resize(900, 450)
        self.s_info_inputname.resize(900, 50)
        self.s_info_inputname.returnPressed.connect(self.info_check)

        # Q&A창 설정
        self.qna_list.resize(1000, 300)
        self.qna_list.setColumnCount(3)
        self.qna_aex.setText("예시: 3(답하고자 하는 질문 번호)/답변내용")
        self.qna_alabel.setText("답변입력: ")
        self.qna_check.setText("새로고침")
        self.qna_aupload.setText("답변 보내기")
        # self.qna_aupload.clicked.connect(self.send_qna_a) <-넣어야 함
        header1 = self.qna_list.horizontalHeader()
        header1.resizeSection(0, 80)
        header2 = self.qna_list.horizontalHeader()
        header2.resizeSection(1, 300)
        header3 = self.qna_list.horizontalHeader()
        header3.resizeSection(2, 600)
        self.qna_list.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.qna_check.clicked.connect(self.check_qna)
        self.qna_check.clicked.connect(self.qna_view)

        # 실시간 상담(체팅기능)
        self.chat_input.returnPressed.connect(self.send_chat)
        self.chat_window.resize(900, 450)
        self.chat_input.resize(900, 50)

    def move_start_page(self):
        self.stackedWidget.setCurrentWidget(self.start_page)

    def move_q_upload_page(self):
        self.stackedWidget.setCurrentWidget(self.q_upload_page)

    def move_info_page(self):
        self.stackedWidget.setCurrentWidget(self.s_info_page)

    def move_qna_page(self):
        self.stackedWidget.setCurrentWidget(self.qna_page)

    def move_chat_page(self):
        self.stackedWidget.setCurrentWidget(self.chat_page)

    # 서버에게 특수문자+문제 를 붙여서 메시지 전송하면 서버가 문제출제 저장요청으로 인식
    def show_question(self):
        question_check = "@문제확인"
        sock.send(question_check.encode())
        self.q_upload.clear()

    def append_question(self):
        # 라인에디터를 하나 더 만들어서 문제와 답안을 따로 입력하고 문제 제출 버튼으로 서버에 둘다 전송할것
        question = f"@문제출제 {self.q_upload.text()} {self.a_upload.text()}"
        print("문제를 출제함", question)
        sock.send(question.encode())
        self.q_upload.clear()
        self.a_upload.clear()

    # 서버에게 특수문자+학생이름 을 붙여서 메시지 전송하면 서버가 학생정보 요청으로 인식
    def info_check(self):
        s_name = "@학생이름 "+self.s_info_inputname.text()
        sock.send(s_name.encode())
        # 학생 이름을 전송하면 서버에서 DB를 확인하여 해당하는 학생의 정보를 문자열로 보냄
        # 클라이언트에서 데이터를 잘 풀어서 정보를 출력할 것
        print("학생이름 보냄 :", s_name)
        # s_info = sock.recv(1024).decode()
        # self.s_info_browser.append(s_info)
        self.s_info_inputname.clear()

    def qna_view(self):
        # rows = [("학생1","학생6","학생1","학생5","학생2","학생7","학생5"),("질문1","질문2","질문3","질문4","질문5","질문6","질문7"),
        #         ("답변1","답변2","답변대기","답변4","답변5","답변대기","답변대기")]  # 서버로부터 받아올 qna리스트
        data = sock.recv(1024).decode()
        rowss = eval(data)
        self.qna_list.setRowCount(len(rowss))
        for i in range(len(rowss)):
            rows = rowss[i]
            # {chr(3001)}{i[0]}{chr(2999)}{i[1]}{chr(2999)}{i[2]}{chr(2999)}{i[3]}
            print("qna 수신 확인용", rows)
            # 어펜드 해주면 들어갈 리스트들
            # student = ["학생1","학생6","학생1","학생5","학생2","학생7","학생5"]
            student = rows[1]
            print(student)
            # question = ["질문1","질문2","질문3","질문4","질문5","질문6","질문7"]
            question = rows[2]
            # answer = ["답변1","답변2","답변대기","답변4","답변5","답변대기","답변대기"]
            answer = rows[3]
            # 리시브 한 데이터를 특정 문자열로 구분해서 저장 분류
            # [(학생 이름만),(질문내용만),(답변만)]
            # 받아서 보여주기만 하자
            QnA = [student, question, answer]
            print(QnA)
            # for i in range(len(question)):
            #     rows.append(QnA)
            for j in range(len(QnA)):
                # QnA_data = rows[row]
                self.qna_list.setItem(i, j, QTableWidgetItem(str(QnA[j])))
                self.qna_list.setItem(i, j, QTableWidgetItem(str(QnA[j])))
                self.qna_list.setItem(i, j, QTableWidgetItem(str(QnA[j])))

    # qna관련해서 계속 갱신 버튼을 눌러서 데이터를 받아옴
    def check_qna(self):
        a = "@qna갱신"
        sock.send(a.encode())
        print("qna 갱신요청 보냄")

    # qna답변을 보낼 함수
    # 또다른 라인에디터 하나 만들어서 답변을 입력하고
    # 답변 입력 후 답변 추가 하기 하면 그 메시지를 단순히 서버에 보내자
    # 서버는 그냥 qna답변을 위에서부터 차례대로 받아서 갱신하자
    # 이거 아니면 답이 없는거 같다...
    # 예시) 3/그 질문에 대한 것은 이거이거이다
    # @qna답변 3/답변~~~~
    def send_qna_a(self):
        msg = self.qna_ainput.text()
        data = "@qna답변 "+msg
        sock.send(data.encode())
        print("qna답변 보냈음")
        self.qna_ainput.clear()

    # 체팅은 그냥 클라이언트끼리니 서버는 구분없이 그냥 사이 중계만 하면 될 듯
    def send_chat(self):
        msg = self.chat_input.text()
        data = "@상담교사"+self.chat_input.text()
        sock.send(data.encode())
        self.chat_window.append(msg)
        self.chat_input.clear()

    def clear(self):
        self.chat_window.clear()
        self.q_list.clear()
        self.s_info_browser.clear()

    @pyqtSlot(str)
    def recv_chat(self, msg):
        print("상담 메세지 수신", msg)
        self.chat_window.append(msg)

    @pyqtSlot(str)
    def recv_chat2(self, msg):
        print("문제 메세지 수신", msg)
        self.q_list.addItem(msg)

    @pyqtSlot(str)
    def recv_chat3(self, msg):
        print("학생정보 메시지 수신", msg)
        self.s_info_browser.append(msg)

    @pyqtSlot(str)
    def recv_chat4(self, msg):
        print("Q&A 메시지 수신", msg)
        self.qna_view()


class Receive(QThread):
    chat = pyqtSignal(str)
    chat2 = pyqtSignal(str)
    chat3 = pyqtSignal(str)
    chat4 = pyqtSignal(str)
    print("큐쓰레드 수신")

    def run(self):
        while True:
            try:
                msg = sock.recv(10024)
                if not msg:
                    break
            except:
                print("리시브 오류")
                break
            else:
                data = msg.decode()
                self.chat2.emit(data)
                # self.chat4.emit(data)
                if "@문제" == data[:len("@문제")]:
                    if "중복된 단어" in data:
                        self.chat2.emit(data[len("@문제"):])
                        print("@문제 중복", data)
                    elif "성공" in data:
                        self.chat2.emit(data[len("@문제"):])
                        print("@문제 제출성공", data)
                    else:
                        self.chat2.emit(data[len("@문제"):])
                        print("단순 문제 출력")
                elif "@상담학생" == data[:len("@상담학생")]:
                    self.chat.emit(f"학생 : {data[len('@상담학생'):]}")
                    print("@1대1 체팅 수신", data)
                elif "@학생정보" == data[:len("@학생정보")]:
                    self.chat3.emit(data[len("@학생정보"):])
                    print("@학생정보 아이디로 갱신요청", data)
                elif "@qna갱신" == data[:len("@qna갱신")]:
                    self.chat4.emit(data[len("@qna갱신"):])
                    print("@qna갱신 DB에서 보내줌", data)
                else:
                    print(f"메시지를 인식하지 못함{data}")
        print("q스레드 종료")
        # sock.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = Window()
    myWindow.show()
    app.exec_()