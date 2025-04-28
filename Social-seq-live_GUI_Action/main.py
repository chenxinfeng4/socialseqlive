# conda activate py310
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QGridLayout, QLineEdit, QComboBox, 
    QVBoxLayout, QHBoxLayout, QSizePolicy, QSpacerItem, QMessageBox
)
from PySide6.QtGui import (
    QIcon, QFont, QStandardItemModel, QStandardItem, QScreen,
    QImage, QPixmap, QPainter,QPalette
)

from PySide6.QtCore import QSize, Qt, QThread, Signal, QTimer
from serialproxy import list_serial_ports, SerialCommunicator, simulators
import ffmpegcv


import picklerpc
import threading
from typing import List
import numpy as np
import pandas as pd

from labels_profile import chk_box_bhv_list
from display_delay import PyThreadDelay, PyThreadBhvLabel
from display_delay import PyThreadStimulate


from check_devices import check_stream_urls, check_cloud_server


frames = [None for i in range(3)]
frames_lock = [threading.Lock() for i in range(len(frames))]


class VideoThread(QThread):
    frame_ready = Signal(object)  # 定义帧就绪信号

    def __init__(self, ipannel, video_path):
        super().__init__()
        self.video_path = video_path
        self.ipannel = ipannel
        self.to_continue = True

    def run(self):
        cap = ffmpegcv.VideoCaptureStreamRT(self.video_path, pix_fmt='rgb24')
        
        with cap:
            while self.to_continue:
                ret, frame = cap.read()
                with frames_lock[self.ipannel]:
                    frames[self.ipannel] = frame
                if not ret:
                    break
                # 更新图像数据
                image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(image)
                self.frame_ready.emit(pixmap)  # 发送帧就绪信号
        forever = threading.Event() #不知道什么鬼原因，不能直接让QThread quit，所以用这个方法
        forever.wait()


class CheckableComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.view().pressed.connect(self.handle_item_pressed)
        self.setModel(QStandardItemModel(self))
        self.setFont(QFont("Arial", 24))  # 设置下拉框的字体大小
        self.callback = None
        self.update_display_text()

    def handle_item_pressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
        self.update_display_text()

    def add_checkable_items(self, items):
        for item_text in items:
            item = QStandardItem(f"   {item_text}")  # 在文本前添加空格
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
            item.setFont(QFont("Arial", 14))  # 设置选项的字体大小
            self.model().appendRow(item)
        self.update_display_text()

    def update_display_text(self):
        checked_items = [self.model().item(i).text() for i in range(self.model().rowCount()) if self.model().item(i).checkState() == Qt.Checked]
        if len(checked_items)>1:
            self.setCurrentText('...')
        elif len(checked_items)==1:
            self.setCurrentText(checked_items[0])  # 仅显示第一个选中的选项
        else:
            self.setCurrentText("Select options")  # 如果没有选项被选中，显示默认提示
        if self.callback is not None:
            self.callback(checked_items)

class SingleCombaBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setFont(QFont("Arial", 24))  # 设置下拉框的字体大小
        self.callback = None
        self.update_display_text()

    def add_items(self, items):
        for item_text in items:
            self.addItem(item_text)
        self.update_display_text()

    def update_display_text(self):
        if self.currentIndex()>=0:
            self.setCurrentText(self.currentText())
        else:
            self.setCurrentText("Select options")  # 如果没有选项被选中，显示默认提示
        if self.callback is not None:
            self.callback(self.currentText())


class SingleLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setFont(QFont("Arial", 24))  # 设置下拉框的字体大小
        self.callback = None


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # varibles
        self.pythread_delay = PyThreadDelay()
        self.pythread_outlabel = PyThreadBhvLabel()
        self.pythread_stimu = PyThreadStimulate()
        self.bhv_items = []
        self.sitm_items = []

        # 设置主窗口标题
        self.setWindowIcon(QIcon('image/soical-seq-live-icon.jpg'))
        self.setWindowTitle('Social-Seq Live')
        # 在初始化窗口时，设置窗口的初始大小
        self.resize(1200, 800)  # 设置宽度为1200，高度为800

        # 设置全局字体大小为原来的两倍
        font = QFont("Arial", 24)
        font14 = QFont("Arial", 14)
        self.setFont(font)

        # 设置主布局为网格布局
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)  # 保持原来的水平间距
        grid.setVerticalSpacing(10)    # 保持原来的垂直间距
        grid.setColumnStretch(0, 1)    # 设置列自适应
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)
        grid.setColumnStretch(4, 1)
        grid.setColumnStretch(5, 1)
        self.setLayout(grid)

        # 创建左上角的Cloud IP和Arduino标签及输入框
        cloud_ip_label = QLabel('Cloud IP:')
        self.cloud_ip_input = QLineEdit('10.50.60.6')
        arduino_label = QLabel('Arduino:')
        self.arduino_combo = QComboBox()
        serial_ports = list_serial_ports()
        self.serialCommunicator = SerialCommunicator(None)
        self.arduino_combo.addItems(serial_ports)

        # 固定 Cloud IP 输入框的长度
        self.cloud_ip_input.setFixedWidth(200)  # 例如设置为200像素宽

        # 固定 Arduino 下拉框的长度
        self.arduino_combo.setFixedWidth(200)  # 例如设置为200像素宽

        connect_cloud_button = QPushButton('Connect')
        disconnect_cloud_button = QPushButton('Disc')
        connect_arduino_button = QPushButton('Connect')
        disconnect_arduino_button = QPushButton('Disc')

        # 美化按钮样式
        button_style = """
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            padding: 5px;
           font-size: 20px;
        }
        QPushButton:pressed {
            background-color: #45a049;
        }
        QPushButton:disabled {
            background-color: #ccc;
            color: #666;
        }
        """
        connect_cloud_button.setStyleSheet(button_style)
        disconnect_cloud_button.setStyleSheet(button_style)
        connect_arduino_button.setStyleSheet(button_style)
        disconnect_arduino_button.setStyleSheet(button_style)

        # 将这些组件紧贴地添加到布局中
        grid.addWidget(cloud_ip_label, 0, 0)
        grid.addWidget(self.cloud_ip_input, 0, 1)
        grid.addWidget(connect_cloud_button, 0, 2)
        grid.addWidget(disconnect_cloud_button, 0, 3)
        grid.addWidget(arduino_label, 1, 0)
        grid.addWidget(self.arduino_combo, 1, 1)
        grid.addWidget(connect_arduino_button, 1, 2)
        grid.addWidget(disconnect_arduino_button, 1, 3)

        # 创建三个用于显示画面的Widget区域和标题
        title_font = QFont("Arial", 28, QFont.Bold)
        widget2 = QLabel()

        # 设置画面显示区域的大小和边框
        widget2.setMinimumSize(400, 350)
        # 设置画面显示区域的大小和边框
        widget2.setStyleSheet("border: 5px solid #F0F0F0; background-color: #E0E0E0;")

        widget2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
        self.pixelWidgets:List[QLabel] = [widget2, ]
        for widget in self.pixelWidgets:
            widget.setScaledContents(True)
        self.vid_threads:List[VideoThread] = []
        self.vid_conn_handles:List[Signal] = []

        # 将标题和画面显示区域添加到布局中
        # grid.addWidget(widget1, 3, 0, 1, 3)
        grid.addWidget(widget2, 4, 0, 1, 6)

        # 创建右侧的标签和多选下拉列表，并使用嵌套布局
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)  # 保持原来的垂直间距
        right_layout.setContentsMargins(0, 0, 0, 0)  # 去掉右边的外边距

        # 使用 QVBoxLayout 使标签和下拉框紧贴排列
        condition_layout = QVBoxLayout()
        condition_layout.setSpacing(0)  # 保持标签和下拉框之间的间距
        condition_label = QLabel('   Action labels:')
        condition_label.setFixedHeight(30)  # 将 QLabel 的最小高度设置为30
        self.condiction_bhv_combo = CheckableComboBox()
        self.condiction_bhv_combo.add_checkable_items(chk_box_bhv_list+['...'])
        self.condiction_bhv_combo.setMaximumWidth(350)  # 设置最大宽度
        self.condiction_bhv_combo.callback = self.condiction_bhv_combo_change
        self.condiction_bhv_output = QLabel('')
        self.condiction_bhv_output.setWordWrap(True)
        self.condiction_bhv_output.setFixedWidth(350)
        self.condiction_bhv_output.setFont(font14)
        self.load_default_profile()

        hint_label = QLabel('Trigger ↓')
        hint_label.setFixedWidth(350)
        hint_label.setFont(font)
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setStyleSheet("color: #4CAF50")
        condition_layout.addWidget(QLabel(''))
        condition_layout.addWidget(condition_label)
        condition_layout.addWidget(self.condiction_bhv_combo)
        condition_layout.addWidget(self.condiction_bhv_output)
        condition_layout.addWidget(hint_label)
        # connect condiction_bhv_combo changed signal to an callback

        arduino_layout = QVBoxLayout()
        arduino_layout.setSpacing(10)
        stimu_label = QLabel('   Stimulation:')
        stimu_label.setFixedHeight(30)  # 将 QLabel 的最小高度设置为30
        stimu_label.setFixedHeight(30)  # 将 QLabel 的最小高度设置为30
        self.arduino_comba = SingleCombaBox()
        self.arduino_comba.add_items(simulators)
        self.arduino_comba.setMaximumWidth(350)  # 设置最大宽度
        self.condiction_arduino_output = QLabel('')

        self.stimu_label = stimu_label
        arduino_layout.addWidget(stimu_label)
        arduino_layout.addWidget(self.arduino_comba)
        right_layout.addLayout(condition_layout)
        right_layout.addLayout(arduino_layout)

        # 将右侧布局添加到网格布局，并紧贴右边框
        grid.addLayout(right_layout, 2, 6, 4, 1)  # 只占用一列，紧贴右边

        # 创建底部的延迟标签和输入框及其他标签
        latency_label = QLabel('Latency')
        self.latency_input = QLineEdit('----')
        self.latency_input.setReadOnly(True)
        outcomelabel = QLabel('<--BEHAVIOR LABEL-->', self)
        outcomelabel.setStyleSheet("background-color: rgba(255, 255, 255, 128); color: black")

        #set font size
        # font18 = QFont()
        # font18.setPointSize(18)
        # outcomelabel.setFont(font)
        hint3 = QLabel('3D pose  ', self)
        # hint3.setStyleSheet("color: #0066B4")
        hint3.setFont(QFont("Arial", 16))
        hint3.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        outcomelabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widget2.moveEvent = lambda event: outcomelabel.setGeometry(widget2.x()+30, widget2.y() + widget2.height()-70, widget2.width()-60, 50) or \
                                    hint3.setGeometry(widget2.x(), widget2.y(), widget2.width(), 40)
        self.outcomelabel = outcomelabel
        self.bhv_image = widget2
        font16 = QFont()
        font16.setPointSize(16)

        grid.addWidget(latency_label, 5, 0)
        grid.addWidget(self.latency_input, 5, 1)
        # grid.addWidget(outcomelabel, 8, 2,1,3)

        # 创建 ICON 的水平布局区域
        icon_layout = QVBoxLayout()

        # 在 ICON 上方添加一个垂直的 spacer
        spacer_above_icons = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        icon_layout.addItem(spacer_above_icons)

        # 创建 ICON 按钮并添加到布局中
        icon_buttons_layout = QHBoxLayout()  # 使用水平布局将图标靠在一起
        spacer_after_icons = QSpacerItem(10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        icon_buttons_layout.addSpacerItem(spacer_after_icons)
        icon_size = QSize(50, 50)
        self.icon_images = {
            0: ['image/obs_cam_off.png', 'image/obs_cam_on.png'],
            1: ['image/cloudAI_off.png', 'image/cloudAI_on.png'],
            2: ['image/arduino_off.png', 'image/arduino_on.png'],
        }

        self.icon_states = {
            0: True,
            1: True,
            2: True,
        }

        self.icon_buttons = []

        for i, key in enumerate(self.icon_images.keys()):
            btn = QLabel(self)
            # btn set icon
            # btn.setIcon(QIcon(self.icon_images[key][1]))
            # btn.setIconSize(icon_size)
            btn.setPixmap(QIcon(self.icon_images[key][0]).pixmap(70, 70))
            btn.setFixedSize(icon_size + QSize(30, 30))
            btn.setStyleSheet(
                "border-radius: 25px; border: 2px solid black; background-color: #E0E0E0;")
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            # btn.clicked.connect(lambda checked, k=key, b=btn: self.toggle_icon(k, b))
            self.icon_buttons.append(btn)
            icon_buttons_layout.addWidget(btn)  # 将图标添加到水平布局中

        # 将 ICON 按钮布局添加到 ICON 的垂直布局中
        icon_layout.addLayout(icon_buttons_layout)

        # 将 ICON 的布局添加到主网格布局中
        grid.addLayout(icon_layout, 0, 6, 2, 3)

        connect_cloud_button.clicked.connect(lambda *_: self.click_connect_cloud_button(True))
        disconnect_cloud_button.clicked.connect(lambda *_: self.click_connect_cloud_button(False))
        self.connect_cloud_button = connect_cloud_button
        self.disconnect_cloud_button = disconnect_cloud_button
        self.click_connect_cloud_button(False)

        connect_arduino_button.clicked.connect(lambda *_: self.click_connect_arduino_button(True))
        disconnect_arduino_button.clicked.connect(lambda *_: self.click_connect_arduino_button(False))
        self.connect_arduino_button = connect_arduino_button
        self.disconnect_arduino_button = disconnect_arduino_button
        self.click_connect_arduino_button(False)

        # move window to the center of the screen
        screen_size = QScreen.availableGeometry(QApplication.primaryScreen())
        w, h = 1050, 650
        x = max((screen_size.width() - w) / 2, 10)
        y = max((screen_size.height()-200 - h) / 2, 10)
        
        self.setGeometry(x, y, w, h)

        self.vid_threads:List[VideoThread] = []
        self.vid_conn_handles:List[Signal] = []

    def trigger_display(self, activate:bool):
        if activate:
            self.stimu_label.setStyleSheet("font-size: 28px; background-color: yellow;")
            self.bhv_image.setStyleSheet("border: 5px solid yellow;")
            QTimer.singleShot(1000, lambda:self.trigger_display(False))   # auto reset
        else:
            self.stimu_label.setStyleSheet("font-size: 28px;")
            self.bhv_image.setStyleSheet("border: 5px solid #F0F0F0;")

    def condiction_bhv_combo_change(self, checkeditems):
        self.condiction_bhv_output.setText(','.join(checkeditems))
        self.bhv_items = checkeditems

    def update_urls(self):
        ip = self.cloud_ip_input.text().strip()
        self.cloud_ip = ip
        self.urls = [f'rtsp://{ip}:8554/mystream_9cam',
                    f'rtsp://{ip}:8554/mystream_behaviorlabel_result']
        self.video_pannels = [
            f'rtsp://{ip}:8554/mystream_behaviorlabel_result',
        ]

    def load_default_profile(self):
        item_to_select = np.array([10, 23, 27, 28, 33, 34]) - 1 # start from 0
        for item_i in item_to_select:
            self.condiction_bhv_combo.model().item(item_i).setCheckState(Qt.Checked)
        self.condiction_bhv_combo.update_display_text()

    def display_frame(self, ipannel, pixmap):
        self.pixelWidgets[ipannel].setPixmap(pixmap)

    def click_connect_cloud_button(self, status:bool):
        if status:
            self.connect_cloud_button.setEnabled(False)
            self.disconnect_cloud_button.setEnabled(True)
            self.cloud_ip_input.setEnabled(False)
            self.update_urls()
            valids = check_stream_urls(self.urls[:2])
            valids.append(check_cloud_server(self.cloud_ip))
            print('valids', valids)
            self.toggle_icon_status(0, valids[0])
            self.toggle_icon_status(1, valids[1])
            if not all(valids):
                # create a QMessageBox object with a warning icon and a message
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Failed to connect to cloud")
                msg.setInformativeText("Please check the connection and try again.")
                msg.setWindowTitle("Error")
                msg.exec()
            else:
                self.pythread_delay = PyThreadDelay(self.latency_input, self.cloud_ip)
                self.pythread_delay.start()
                self.pythread_outlabel = PyThreadBhvLabel(self.outcomelabel)
                self.pythread_outlabel.start()
                bhv_inds = [int(x.strip()[1:].split(']')[0])-1 for x in self.bhv_items] # start from 0
                self.pythread_stimu = PyThreadStimulate(bhv_inds, self.serialCommunicator)
                self.pythread_stimu.start()
                self.vid_threads.clear()
                self.vid_conn_handles.clear()
                self.pythread_stimu.trigger.connect(lambda x:self.trigger_display(x))
                for ipannel, url in enumerate(self.video_pannels):
                    video_thread = VideoThread(ipannel, url)
                    self.vid_conn_handles.append(video_thread.frame_ready.connect(lambda x,i=ipannel:self.display_frame(i, x)))
                    self.vid_threads.append(video_thread)

                for video_thread in self.vid_threads:
                    video_thread.start()  # 启动视频线程
                
        else:
            self.connect_cloud_button.setEnabled(True)
            self.disconnect_cloud_button.setEnabled(False)
            self.cloud_ip_input.setEnabled(True)
            self.toggle_icon_status(0, False)
            self.toggle_icon_status(1, False)
            # self.pythread_stimu.trigger.disconnect()
            for video_thread in self.vid_threads:
                video_thread.to_continue = False
                # video_thread.exit()
            self.vid_threads.clear()
            self.pythread_delay.to_continue = False
            self.pythread_outlabel.to_continue = False
            self.pythread_stimu.to_continue = False
            self.latency_input.setText('----')

    def click_connect_arduino_button(self, status:bool):
        if status:
            self.connect_arduino_button.setEnabled(False)
            self.disconnect_arduino_button.setEnabled(True)
            self.arduino_combo.setEnabled(False)
            serialport = self.arduino_combo.currentText()
            self.serialCommunicator.com_port = serialport
            self.serialCommunicator.connect()
            if self.serialCommunicator.isValid:
                self.toggle_icon_status(2, True)
            else:
                self.toggle_icon_status(2, False)
                # create a QMessageBox object with a warning icon and a message
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Failed to connect to Arduino")
                msg.setInformativeText("Please check the connection and try again.")
                msg.setWindowTitle("Error")
                msg.exec()
        else:
            self.connect_arduino_button.setEnabled(True)
            self.disconnect_arduino_button.setEnabled(False)
            self.arduino_combo.setEnabled(True)
            self.serialCommunicator.close()
            self.toggle_icon_status(2, False)

    def toggle_icon_status(self, key:int, status:bool):
        current_icon = self.icon_images[key][status]
        self.icon_buttons[key].setPixmap(QIcon(current_icon).pixmap(70, 70))
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())
