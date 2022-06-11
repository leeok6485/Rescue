import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import time
from PyQt5.QtCore import *
from socket import *

form_class = uic.loadUiType("교사용.ui")[0]
sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('', 7500))


class Window(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # 버튼 기능
        self.q_upload_btn.clicked.connect(self.move_q_upload_page)
        self.q_upload_btn.setText("문제출제하기")
        self.chat_btn.clicked.connect(self.move_chat_page)
        self.chat_btn.setText("실시간 상담")
        self.qna_btn.clicked.connect(self.move_qna_page)
        self.qna_btn.clicked.connect(self.qna_view)
        self.qna_btn.setText("QnA 게시판")
        self.student_info_btn.clicked.connect(self.move_info_page)
        self.student_info_btn.setText("학생정보열람")
        self.upload_back_btn.clicked.connect(self.move_start_page)
        self.upload_back_btn.setText("뒤로가기")
        self.info_back_btn.clicked.connect(self.move_start_page)
        self.info_back_btn.setText("뒤로가기")
        self.qna_back_btn.clicked.connect(self.move_start_page)
        self.qna_back_btn.setText("뒤로가기")
        self.chat_back_btn.clicked.connect(self.move_start_page)
        self.chat_back_btn.setText("뒤로가기")
        # 문제출제창 설정
        # 리스트위젯을 써서 현재 존재하는 모든 문제를 출력
        # 입력칸을 만들어서 문제를 입력할까?

        # 학생정보열람창 설정
        # self.student_info_browser
        # 학생의 이름을 입력 했을 때 DB내의 그 학생의 값을 전부 출력할 부분
        # self.student_info_inputname
        # 학생이름을 그냥 입력 받을곳

        # Q&A창 설정
        self.qna_list.resize(1100, 500)
        # self.qna_list.setRowCount(50)
        self.qna_list.setColumnCount(3)
        header1 = self.qna_list.horizontalHeader()
        header1.resizeSection(0, 80)
        header2 = self.qna_list.horizontalHeader()
        header2.resizeSection(1, 300)
        header3 = self.qna_list.horizontalHeader()
        header3.resizeSection(2, 600)
        self.qna_list.currentCellChanged.connect(self.cellchanged_event)
        # 실시간 상담(체팅기능)
        self.chat_input.returnPressed.connect(self.chatting)
        # self.chat_window


    def move_start_page(self):
        self.stackedWidget.setCurrentWidget(self.start_page)

    def move_q_upload_page(self):
        self.stackedWidget.setCurrentWidget(self.q_upload_page)

    def move_info_page(self):
        self.stackedWidget.setCurrentWidget(self.student_info_page)

    def move_qna_page(self):
        self.stackedWidget.setCurrentWidget(self.qna_page)

    def move_chat_page(self):
        self.stackedWidget.setCurrentWidget(self.chat_page)

    def qna_view(self):
        rows = []
        student = ""
        question = ""
        answer = ""
        # 전부 갱신받으면서 답변은 따로 입력한 값으로 전송
        # 혹은 기존처럼 그 칸에 직접 변경하고 내가 저장함
        QnA = [student, question, answer]
        for i in range(10):
            rows.append(QnA[:])
        i = 0
        for row in range(len(rows)):
            self.qna_list.setRowCount((i + 1))
            QnA_data = rows[row]
            self.qna_list.setItem(i, 0, QTableWidgetItem(QnA_data[0]))
            self.qna_list.setItem(i, 1, QTableWidgetItem(QnA_data[1]))
            self.qna_list.setItem(i, 2, QTableWidgetItem(QnA_data[2]))
            i += 1

    def cellchanged_event(self, row, col):
        qna_change = self.qna_list.item(row, col)
        print("변경 : ", qna_change)

    def chatting(self):
        msg = self.chat_input.text()
        sock.send(msg.encode())
        self.chat_window.append(msg)
        self.chat_input.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = Window()
    myWindow.show()
    app.exec_()