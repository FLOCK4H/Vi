from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *
import sys
from PySide6.QtSvgWidgets import *
import ctypes
import cv2
import numpy as np
import pygetwindow as gw
from mss import mss
import time
from pynput import keyboard
import subprocess
import os

appid = u'vi.flytechvi.videorec.screenrec'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

class IconWidget(QSvgWidget):
    clickSignal = Signal(str)
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.def_anim()

    def def_anim(self):
        self.anim = QPropertyAnimation(self, b"size")
        self.anim.setDuration(500)
        self.anim.setEasingCurve(QEasingCurve.InOutCubic)

    def anim_toggle(self, toggle):
        if self.parent.width() > 198:
            if toggle == "hover":
                self.anim.stop()
                self.anim.setEndValue(QSize(140, 140))
                self.anim.start()
            if toggle == "unhover":
                self.anim.stop()
                self.anim.setEndValue(QSize(128, 128))
                self.anim.start()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clickSignal.emit("clicked")

    def enterEvent(self, event):
        super().enterEvent(event)
        self.setCursor(Qt.PointingHandCursor)  
        self.anim_toggle("hover")

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.setCursor(Qt.ArrowCursor)
        self.anim_toggle("unhover")

class IconLabel(QLabel):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


    def enterEvent(self, event):
        super().enterEvent(event)
        self.setCursor(Qt.PointingHandCursor)  

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.setCursor(Qt.ArrowCursor)


class SideBar(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.hovered = False
        self.initSidebar()
        self.load_imgs()
        self.init_anims()

    def load_imgs(self):
        if self.layout() is not None:
            QWidget().setLayout(self.layout())

        outer_layout = QVBoxLayout(self)
        outer_layout.addStretch()

        self.icon_layout = QVBoxLayout() 
        spacer2 = QSpacerItem(50, 150, QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.icon_layout.addItem(spacer2)

        # Arrow icon
        self.arrow = IconWidget(self)
        self.arrow.load("imgs/arrow_right.svg")
        self.arrow.setFixedSize(48, 48)
        self.icon_layout.setContentsMargins(12,0,0,0)
        self.icon_layout.addWidget(self.arrow, 0, Qt.AlignHCenter)
        # Recorder icon
        self.rec = IconWidget(self)
        self.rec.load("imgs/recorder.svg")
        self.rec.setFixedSize(128, 128)
        self.icon_layout.addWidget(self.rec, 0, Qt.AlignHCenter)

        # Screenshot icon
        self.screenshot = IconLabel(self)
        self.screenshot.setPixmap(QPixmap("imgs/ss_icon.png").scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.icon_layout.addWidget(self.screenshot, 0, Qt.AlignHCenter)

        # Microphone icon
        self.mic = IconLabel(self)
        self.mic.setPixmap(QPixmap("imgs/mic_icon.png").scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.icon_layout.addWidget(self.mic, 0, Qt.AlignHCenter)

        spacer = QSpacerItem(20, 150, QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.icon_layout.addItem(spacer)
        
        # Banner icon
        self.banner = IconLabel(self)
        self.banner.setPixmap(QPixmap("imgs/banner.png").scaled(168, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.icon_layout.addWidget(self.banner, 0, Qt.AlignHCenter)

        self.banner.hide()
        
        self.mic.hide()
        self.screenshot.hide()
        self.rec.hide()

        self.icon_layout.setSpacing(20)

        outer_layout.addLayout(self.icon_layout)
        outer_layout.addStretch()
        self.setLayout(outer_layout) 



    def initSidebar(self):
        self.screen_size = self.parent.screen_size
        self.sh, self.sw = self.parent.sh, self.parent.sw
        self.setGeometry(QRect(QPoint(-20, 400), QSize(70, self.sh - 800)))
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        if self.hovered:
            painter = QPainter(self)
            painter.setBrush(QBrush(QColor(0,5,20,230)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(self.rect(), 24, 24)
            self.arrow.hide()
            self.rec.show()
            self.screenshot.show()
            self.mic.show()
            
            self.banner.show()
        else:
            painter = QPainter(self)
            painter.setBrush(QBrush(QColor(0,0,0,120)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(self.rect(), 16, 16)
            self.arrow.show()
            self.rec.hide()
            self.screenshot.hide()
            self.mic.hide()
            self.banner.hide()

    def init_anims(self):
        self.size_anim = QPropertyAnimation(self, b"geometry")
        self.size_anim.setDuration(500)
        self.size_anim.setEasingCurve(QEasingCurve.InOutCubic)



    def handle_anims(self, **kwargs):
        self.mode = kwargs.get("mode", None)

        if self.mode == "hover":
            self.size_anim.stop()
            self.size_anim.setEndValue(QRect(QPoint(-20, 300), QSize(200, self.sh - 600)))
            self.size_anim.start()
        elif self.mode == "unhover":
            self.size_anim.stop()
            self.size_anim.setEndValue(QRect(QPoint(-20, 400), QSize(70, self.sh - 800)))
            self.size_anim.start()

    def enterEvent(self, event):
        super().enterEvent(event)
        self.hovered = True
        self.handle_anims(mode="hover")

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.hovered = False
        self.handle_anims(mode="unhover")

class VideoThread(QThread):
    notify_show_signal = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.is_recording = False
        self.date = None
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.ffmpeg_process = None

    def on_press(self, key):
        if key == keyboard.Key.shift:
            self.stop_recording()

    def start_recording(self):
        self.notify_show_signal.emit("show", "started")
        self.is_recording = True
        self.date = time.strftime("%d_%m-%H_%M_%S")
        if not os.path.exists("videos"):
            os.system("mkdir videos")
        output_file = f"videos/capture_{self.date}.mp4"
        ffmpeg_path = input("Enter path to ffmpeg.exe binary (modify source code to include permanent path): ") # To make the app run please install ffmpeg and point here to its exe
        screen_size = QApplication.primaryScreen().geometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()

        command = [
            ffmpeg_path,
            "-f", "gdigrab",
            "-framerate", "50",
            "-video_size", f"{screen_width}x{screen_height}",
            "-i", "desktop",
            "-c:v", "hevc_nvenc", # HEVC NVENC (NVIDIA GPU acceleration)
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-crf", "17",
            output_file
        ]

        self.ffmpeg_process = subprocess.Popen(command, stdin=subprocess.PIPE, text=True)
        self.listener.start()


    def stop_recording(self):
        if self.ffmpeg_process:
            self.ffmpeg_process.communicate('q')
            self.ffmpeg_process = None
        self.is_recording = False
        self.listener.stop()
        self.notify_show_signal.emit("show", "finished")

    def run(self):
        while self.is_recording:
            time.sleep(1)
            
class Notify(QWidget):
    def __init__(self, parent=None,*args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.screen = QApplication.primaryScreen().geometry()
        self.setGeometry(QRect(QPoint(self.screen.width() - 330, self.screen.height() + 200), QSize(270,100)))
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.notify = QLabel(self)

        self.rec_finished = QPixmap("imgs/recording_finished.png").scaled(250,100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.recording_started = QPixmap("imgs/recording_started.png").scaled(250,100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.notify_welcome = QPixmap("imgs/notify_welcome.png").scaled(250,100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.notify.setGeometry(QRect(QPoint(20, -50), QSize(250,200)))

        self.notify.setPixmap(self.notify_welcome)


        self.init_anims()
 

    def init_anims(self):
        self.pos_anim = QPropertyAnimation(self, b"geometry")
        self.pos_anim.setDuration(1000)
        self.pos_anim.setEasingCurve(QEasingCurve.InOutCubic)

    def show_n_anim(self, mode, notify=None):
        if notify == "welcome":
            self.notify.setPixmap(self.notify_welcome)
        elif notify == "finished":
            self.notify.setPixmap(self.rec_finished)
        elif notify == "started":
            self.notify.setPixmap(self.recording_started)

        if mode == "show":
            self.show()
            self.pos_anim.stop()
            self.pos_anim.setEndValue(QRect(QPoint(self.screen.width() - 330, self.screen.height() - 200), QSize(270,100)))
            self.pos_anim.start()
        if mode == "hide":
            self.pos_anim.stop()
            self.pos_anim.setEndValue(QRect(QPoint(self.screen.width() - 330, self.screen.height() + 200), QSize(270,100)))
            self.pos_anim.start()


    def paintEvent(self, event):
        painter = QPainter(self)
        
        painter.setBrush(QBrush(QColor(0, 0, 35, 150)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 16, 16) 


class MainBox(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notify = Notify(self)
        self.connected = False
        self.notify.show_n_anim("show", "welcome")
        QTimer.singleShot(4000, lambda: self.notify.show_n_anim("hide"))
        self.init_() 
        self.setWindowIcon(QIcon('imgs/logo.png'))
        self.show()
        self.store_positions()

    def init_(self):
        self.screen_size = QApplication.primaryScreen().geometry()
        self.sh, self.sw = self.screen_size.height(), self.screen_size.width()
        self.setGeometry(QRect(QPoint(0,0), QSize(self.sw, self.sh)))
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.video_thread = VideoThread(self)  
        self.sidebar = SideBar(self)

        self.sidebar.rec.clickSignal.connect(self.onIconClicked)

    def onIconClicked(self):
        print("Initiating...")
        if not self.video_thread.is_recording:
            self.video_thread = VideoThread(self)  
            self.video_thread.start()
            self.notify.show_n_anim("show", "started")
            QTimer.singleShot(4000, lambda: self.notify.show_n_anim("hide"))
            self.video_thread.start_recording()
            if not self.connected:

                self.video_thread.notify_show_signal.connect(self.handle_notify_show) 
                self.connected = True

        else:
            self.video_thread.stop_recording()

    def handle_notify_show(self, mode, message):
        self.notify.show_n_anim(mode, message)  
        QTimer.singleShot(4000, lambda: self.notify.show_n_anim("hide"))

    def store_positions(self):
        self.positions = []

        for widget in self.findChildren(QWidget):
            widget_name = widget.objectName() if widget.objectName() else str(widget.__class__.__name__)
            self.positions.append({
                "object_name": widget_name,
                "geometry": widget.geometry()
            })

        for pos in self.positions:
            print(pos)

        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainBox()
    sys.exit(app.exec())  
