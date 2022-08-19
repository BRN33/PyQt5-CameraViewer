from ctypes import alignment
from glob import glob
from tkinter import LEFT, TOP, VERTICAL
from turtle import left, right
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, \
    QLabel, QGridLayout, QScrollArea, QSizePolicy
from PyQt5.QtGui import QPixmap, QIcon, QImage, QPalette
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QEvent, QObject
from PyQt5 import QtCore
import sys
# import some PyQt5 modules
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap,QFont
from PyQt5.QtCore import QTimer
from jsonOku import *

Camera_Direct=""
Camera_İp=""
Camera_Name=""
Camera_Model=""
global combo_Cam
global cmbText


class CaptureIpCameraFramesWorker(QThread):
    # Signal emitted when a new image or a new frame is ready.
    ImageUpdated = pyqtSignal(QImage)
   
    def __init__(self, url) -> None:
        super(CaptureIpCameraFramesWorker, self).__init__()
        # Declare and initialize instance variables.
        self.url = url
        
        self.__thread_active = True
        self.fps = 0
        self.__thread_pause = False



    def run(self) -> None:
        # Capture video from a network stream.
        global Camera_1,Camera_2,Camera_3,Camera_4
        cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        # Get default video FPS.
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        print("FPS",self.fps)
        # If video capturing has been initialized already.q
        if cap.isOpened():
            # While the thread is active.
            while self.__thread_active:
                #
                if not self.__thread_pause:
                    # Grabs, decodes and returns the next video frame.
                    ret, frame = cap.read()
                    # Get the frame height, width and channels.
                    height, width, channels = frame.shape
                    # Calculate the number of bytes per line.
                    bytes_per_line = width * channels
                    # If frame is read correctly.
                    if ret:
                        # Convert image from BGR (cv2 default color format) to RGB (Qt default color format).
                        cv_rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        # Convert the image to Qt format.
                        qt_rgb_image = QImage(cv_rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
                        # Scale the image.
                        qt_rgb_image_scaled = qt_rgb_image.scaled(1080, 720, Qt.KeepAspectRatio)  # 1280 720p
                        # qt_rgb_image_scaled = qt_rgb_image.scaled(1920, 1080, Qt.KeepAspectRatio)
                        # Emit this signal to notify that a new image or frame is available.
                        self.ImageUpdated.emit(qt_rgb_image_scaled)
                     
                    else:
                        print("baglı degil")
                        break
        # When everything done, release the video capture object.
        cap.release()
        # Tells the thread's event loop to exit with return code 0 (success).
        self.quit()

    def stop(self) -> None:
        self.__thread_active = False

    def pause(self) -> None:
        self.__thread_pause = True

    def unpause(self) -> None:
        self.__thread_pause = False

class MainWindow(QMainWindow): 

    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        
        self.__comboList()
       
        global Camera_Model
        
        
        cmbText=str(self.combo_Cam.currentText())
        # if Camera_Model=="Axis":
        #     self.url_1 = ('rtsp://admin:a741953A@{}/onvif-media/media.amp?profile=profile_1_h264&sessiontimeout=60&streamtype=unicast').format(cmbText,self)
        # else:
        #     self.url_1 = ('rtsp://admin:a741953A@{}:554/udpstream').format(cmbText,self)
        # rtsp://<Username>:<Password>@<IP Address>:<Port>/cam/realmonitor?channel=1&subtype=0
        self.url_1 = ('rtsp://admin:a741953A@{}/onvif-media/media.amp?profile=profile_1_h264&sessiontimeout=60&streamtype=unicast').format(self,cmbText)
        #self.url_1 = ('rtsp://admin:a741953A@{}:554/udpstream').format(str(cmbText),self)
        self.url_2 = ('rtsp://admin:a741953A@{}:554/udpstream').format(str(cmbText),self)
        self.url_3 = ('rtsp://admin:a741953A@{}:554/udpstream').format(str(cmbText),self)
        self.url_4 = ('rtsp://admin:a741953A@{}:554/udpstream').format(str(cmbText),self)

        # Dictionary to keep the state of a camera. The camera state will be: Normal or Maximized.
        self.list_of_cameras_state = {}

        # Create an instance of a QLabel class to show camera 1.
        self.camera_1 = QLabel()
        self.camera_1.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_1.resize(QtCore.QSize(20,10))
        # self.camera_1.setFixedSize(800,480)
        self.camera_1.setScaledContents(True)
        self.camera_1.installEventFilter(self)
        self.camera_1.setObjectName("Camera_1")
        self.list_of_cameras_state["Camera_1"] = "Normal"

        # Create an instance of a QScrollArea class to scroll camera 1 image.
        
        
        self.QScrollArea_1 = QScrollArea()
        self.QScrollArea_1.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_1.setWidgetResizable(True)
        self.QScrollArea_1.setWidget(self.camera_1)
        # self.QScrollArea_1.setFixedSize(800,480)
        

        # Create an instance of a QLabel class to show camera 2.
        self.camera_2 = QLabel()
        self.camera_2.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_2.setScaledContents(True)
        self.camera_2.installEventFilter(self)
        self.camera_2.setObjectName("Camera_2")
        self.list_of_cameras_state["Camera_2"] = "Normal"

        # Create an instance of a QScrollArea class to scroll camera 2 image.
        self.QScrollArea_2 = QScrollArea()
        self.QScrollArea_2.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_2.setWidgetResizable(True)
        self.QScrollArea_2.setWidget(self.camera_2)
        

        # Create an instance of a QLabel class to show camera 3.
        self.camera_3 = QLabel()
        self.camera_3.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_3.setScaledContents(True)
        self.camera_3.installEventFilter(self)
        self.camera_3.setObjectName("Camera_3")
        self.list_of_cameras_state["Camera_3"] = "Normal"

        # Create an instance of a QScrollArea class to scroll camera 3 image.
        self.QScrollArea_3 = QScrollArea()
        self.QScrollArea_3.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_3.setWidgetResizable(True)
        self.QScrollArea_3.setWidget(self.camera_3)

        # Create an instance of a QLabel class to show camera 4.
        self.camera_4 = QLabel()
        self.camera_4.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_4.setScaledContents(True)
        self.camera_4.installEventFilter(self)
        self.camera_4.setObjectName("Camera_4")
        self.list_of_cameras_state["Camera_4"] = "Normal"

        # Create an instance of a QScrollArea class to scroll camera 4 image.
        self.QScrollArea_4 = QScrollArea()
        self.QScrollArea_4.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_4.setWidgetResizable(True)
        self.QScrollArea_4.setWidget(self.camera_4)



        self.button = QPushButton("Show Camera ", self)
        self.button.setStyleSheet("background-color:green") 
        self.button.setGeometry(QtCore.QRect(750, 60, 210, 31))
        self.button.setFont(QFont('Times',16))
        
        self.button1 = QPushButton("Show", self)
        self.button1.setFixedSize(80,40)
        self.button1.setIcon(QIcon("kam.png"))
        self.button1.setIconSize(QtCore.QSize(30, 30))
        self.button1.move(300,650)
        self.button1.setFont(QFont('Times',9))
       
        
        self.cmb_Camera=QComboBox(self)
        self.cmb_Camera.setFixedSize(180,30)
        self.cmb_Camera.setGeometry(100,50,180,20)
        # self.cmb_Camera.move(500,200)
        self.cmb_Camera.setFont(QFont('Times',10))
        
        
        for i in self.list_of_cameras_state:
          
            self.cmb_Camera.addItem(i)
                
        self.button.clicked.connect(self.find)
        self.QScrollArea_Test = QScrollArea()
        self.QScrollArea_Test.setFixedSize(220,480)
        self.QScrollArea_Test.setGeometry(QtCore.QRect(570, 100, 381, 31))
        self.QScrollArea_Test.move(300,100)
        self.QScrollArea_Test.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom)
        
        
        
        
        self.camera_İp = QLabel()
        self.camera_İp.setFont(QFont('Times',16))
        self.camera_İp.setText("İP SECİNİZ")
        
        self.camera_Lcd = QLabel()
        self.camera_Lcd.setFont(QFont('Times',16))
        self.camera_Lcd.setText("KAMERA SECİNİZ")
        
        self.degisken_Layout=QVBoxLayout()
        self.degisken_Layout.setGeometry(QtCore.QRect(500,250,220,200))
        self.degisken_Layout.setSpacing(0)
        self.degisken_Layout.setStretch(2,20)
        
        self.degisken_Layout.addWidget(self.camera_İp)
        self.degisken_Layout.addWidget(self.combo_Cam)
        self.degisken_Layout.addWidget(self.camera_Lcd)
        self.degisken_Layout.addWidget(self.cmb_Camera)
        
        # self.degisken_Layout.addWidget(self.button1)
        self.degisken_Layout.addWidget(self.button)
        
        
        
        
    
      
        self.QScrollArea_Test.setWidget(self.button)
        self.QScrollArea_Test.setFixedHeight(100)
        self.button1.clicked.connect(self.Showx)
        
        
        
        
        
        
        # Set the UI elements for this Widget class.
        self.__SetupUI()


        # Create an instance of CaptureIpCameraFramesWorker.
        self.CaptureIpCameraFramesWorker_1 = CaptureIpCameraFramesWorker(self.url_1)
        self.CaptureIpCameraFramesWorker_1.ImageUpdated.connect(lambda image: self.ShowCamera1(image))

        # Create an instance of CaptureIpCameraFramesWorker.
        self.CaptureIpCameraFramesWorker_2 = CaptureIpCameraFramesWorker(self.url_2)
        self.CaptureIpCameraFramesWorker_2.ImageUpdated.connect(lambda image: self.ShowCamera2(image))

        # Create an instance of CaptureIpCameraFramesWorker.
        self.CaptureIpCameraFramesWorker_3 = CaptureIpCameraFramesWorker(self.url_3)
        self.CaptureIpCameraFramesWorker_3.ImageUpdated.connect(lambda image: self.ShowCamera3(image))

        # Create an instance of CaptureIpCameraFramesWorker.
        self.CaptureIpCameraFramesWorker_4 = CaptureIpCameraFramesWorker(self.url_4)
        self.CaptureIpCameraFramesWorker_4.ImageUpdated.connect(lambda image: self.ShowCamera4(image))

        # Start the thread getIpCameraFrameWorker_1.
        self.CaptureIpCameraFramesWorker_1.start()

        # Start the thread getIpCameraFrameWorker_2.
        self.CaptureIpCameraFramesWorker_2.start()

        # Start the thread getIpCameraFrameWorker_3.
        self.CaptureIpCameraFramesWorker_3.start()

        # Start the thread getIpCameraFrameWorker_4.
        self.CaptureIpCameraFramesWorker_4.start()
    
    def Showx(self):
       self.QScrollArea_Test.show()
       self.combo_Cam.show()
       self.cmb_Camera.show()
       self.button1.hide()

    def Keept(self):
        self.QScrollArea_Test.hide()
        self.combo_Cam.hide()
        self.cmb_Camera.hide()
        self.button1.show()
        
    def __comboList(self)->None:
        self.combo_Cam =QComboBox(self)
        # self.combo_Cam.setGeometry(QtCore.QRect(840, 10, 100, 31))
        self.combo_Cam.setGeometry(QtCore.QRect(840, 10, 10, 31))
        self.combo_Cam.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.combo_Cam.setAutoFillBackground(True)
        self.combo_Cam.setStyleSheet("background-color: rgb(0, 206, 215);")
        self.combo_Cam.setCurrentText("Kamera Seciniz")
        self.combo_Cam.setInsertPolicy(QComboBox.InsertAtCurrent)
        self.combo_Cam.setObjectName("combo_Cam")
        self.combo_Cam.setVisible(True)
        self.combo_Cam.setFixedSize(180,30)
        self.combo_Cam.setFont(QFont('Times',12))
        
        
        # self.combo_Cam.setFont(QFont('Times', 20)
        
        cam_List=[]
        data=JsonOku("cam.json")
        for i in data:
            cam_List.append(i["cam_ip"])
            Camera_Name=i["cam_Name"]
            Camera_Model=i["cam_model"]
            # print(cam_List)
        cam_List.sort()
        self.combo_Cam.addItems(cam_List)
       
        
        # cmbText=self.combo_Cam.currentIndex()
        
        # print(cmbText)
   
    def find(self):
        global cmbText
        
        # finding the content of current item in combo box
        
  
        # showing content on the screen though label
        
        if self.cmb_Camera.currentText()=="Camera_1":
            content = self.combo_Cam.currentText()
            global Camera_Name
            cmbText=str(content)
            print("Kamera İP si degisti",cmbText)
            print("Camera_1 Secildi")
            self.CaptureIpCameraFramesWorker_1.stop()
            print(Camera_Name)
            if Camera_Name=="Axis":
                self.url_1 = ('rtsp://admin:a741953A@{}/onvif-media/media.amp?profile=profile_1_h264&sessiontimeout=60&streamtype=unicast').format(str(cmbText),self)
                print("url 1 Axis secildi...>",self.url_1)
            else:
                self.url_1 = ('rtsp://admin:a741953A@{}:554/udpstream').format(str(cmbText),self)
                print("url 1 Moxa  secildi...>",self.url_1)
            #self.url_1 = ('rtsp://admin:a741953A@{}:554/udpstream').format(str(cmbText),self)
            self.CaptureIpCameraFramesWorker_1 = CaptureIpCameraFramesWorker(self.url_1)
            self.CaptureIpCameraFramesWorker_1.ImageUpdated.connect(lambda image: self.ShowCamera1(image))
            self.CaptureIpCameraFramesWorker_1.start()
        elif self.cmb_Camera.currentText()=="Camera_2":
            content = self.combo_Cam.currentText()
            cmbText=str(content)
            print("Camera_2 Secildi")
            self.CaptureIpCameraFramesWorker_2.stop()
            self.url_2 = ('rtsp://admin:a741953A@{}:554/udpstream').format(str(cmbText),self)
            self.CaptureIpCameraFramesWorker_2 = CaptureIpCameraFramesWorker(self.url_2)
            self.CaptureIpCameraFramesWorker_2.ImageUpdated.connect(lambda image: self.ShowCamera2(image))
            self.CaptureIpCameraFramesWorker_2.start()    
        elif self.cmb_Camera.currentText()=="Camera_3":
            content = self.combo_Cam.currentText()
            cmbText=str(content)
            print("Camera_3 Secildi")
            self.CaptureIpCameraFramesWorker_3.stop()
            self.url_3 = ('rtsp://admin:a741953A@{}:554/udpstream').format(str(cmbText),self)
            self.CaptureIpCameraFramesWorker_3 = CaptureIpCameraFramesWorker(self.url_3)
            self.CaptureIpCameraFramesWorker_3.ImageUpdated.connect(lambda image: self.ShowCamera3(image))
            self.CaptureIpCameraFramesWorker_3.start()
        elif self.cmb_Camera.currentText()=="Camera_4":
            content = self.combo_Cam.currentText()
            cmbText=str(content)
            print("Camera_4 Secildi")
            self.CaptureIpCameraFramesWorker_4.stop()
            self.url_4 = ('rtsp://admin:a741953A@{}:554/udpstream').format(str(cmbText),self)
            self.CaptureIpCameraFramesWorker_4 = CaptureIpCameraFramesWorker(self.url_4)
            self.CaptureIpCameraFramesWorker_4.ImageUpdated.connect(lambda image: self.ShowCamera4(image))
            self.CaptureIpCameraFramesWorker_4.start()
        
        # self.Keept()
   
    def __SetupUI(self) -> None:
        # Create an instance of a QGridLayout layout.
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(200, 0, 0, 0)
        
        grid_layout.addWidget(self.QScrollArea_1, 0, 0)
        # grid_layout.addWidget(self.QScrollArea_Test,0,150,0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        # grid_layout.addWidget(self.combo_Cam,1,130,0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        # grid_layout.addWidget(self.button1,0, 120, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        # grid_layout.addWidget(self.cmb_Camera,0,160,0, QtCore.Qt.AlignTop)
      
        grid_layout.addWidget(self.QScrollArea_2, 0, 1)
        grid_layout.addWidget(self.QScrollArea_3, 1, 0)
        grid_layout.addWidget(self.QScrollArea_4, 1, 1)

        # Create a widget instance.
        self.widget = QWidget(self)
        self.widget.setLayout(grid_layout)
        
           
        self.widget2=QWidget(self)
        self.widget2.setGeometry(2,30,200,300)
        self.widget2.setLayout(self.degisken_Layout)
        
        
        # Gizle
        # self.QScrollArea_Test.hide()
        # self.combo_Cam.hide()
        # self.cmb_Camera.hide()
       

        # Set the central widget.
        self.setCentralWidget(self.widget)
        self.setMinimumSize(800, 600)
        self.showMaximized()
        self.setStyleSheet("QMainWindow {background: 'pink';}")
        self.setWindowIcon(QIcon(QPixmap("camera.png")))
        # Set window title.
        self.setWindowTitle("IP Camera System")
        
  
        
    @QtCore.pyqtSlot()
    def ShowCamera1(self, frame: QImage) -> None:
        self.camera_1.setPixmap(QPixmap.fromImage(frame))

    @QtCore.pyqtSlot()
    def ShowCamera2(self, frame: QImage) -> None:
        self.camera_2.setPixmap(QPixmap.fromImage(frame))

    @QtCore.pyqtSlot()
    def ShowCamera3(self, frame: QImage) -> None:
        self.camera_3.setPixmap(QPixmap.fromImage(frame))

    @QtCore.pyqtSlot()
    def ShowCamera4(self, frame: QImage) -> None:
        self.camera_4.setPixmap(QPixmap.fromImage(frame))

    # Override method for class MainWindow.
    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        """
        Method to capture the events for objects with an event filter installed.
        :param source: The object for whom an event took place.
        :param event: The event that took place.
        :return: True if event is handled.
        """
        #
        if event.type() == QtCore.QEvent.MouseButtonDblClick:
            if source.objectName() == 'Camera_1':
                #
                if self.list_of_cameras_state["Camera_1"] == "Normal":
                    self.QScrollArea_2.hide()
                    self.QScrollArea_3.hide()
                    self.QScrollArea_4.hide()
                    self.button1.hide()
                    self.list_of_cameras_state["Camera_1"] = "Maximized"
                else:
                    self.QScrollArea_2.show()
                    self.QScrollArea_3.show()
                    self.QScrollArea_4.show()
                    self.button1.show()
                    self.list_of_cameras_state["Camera_1"] = "Normal"
            elif source.objectName() == 'Camera_2':
                #
                if self.list_of_cameras_state["Camera_2"] == "Normal":
                    self.QScrollArea_1.hide()
                    self.QScrollArea_3.hide()
                    self.QScrollArea_4.hide()
                    self.button1.hide()
                    self.list_of_cameras_state["Camera_2"] = "Maximized"
                else:
                    self.QScrollArea_1.show()
                    self.QScrollArea_3.show()
                    self.QScrollArea_4.show()
                    self.button1.show()
                    self.list_of_cameras_state["Camera_2"] = "Normal"
            elif source.objectName() == 'Camera_3':
                #
                if self.list_of_cameras_state["Camera_3"] == "Normal":
                    self.QScrollArea_1.hide()
                    self.QScrollArea_2.hide()
                    self.QScrollArea_4.hide()
                    self.button1.hide()
                    self.list_of_cameras_state["Camera_3"] = "Maximized"
                else:
                    self.QScrollArea_1.show()
                    self.QScrollArea_2.show()
                    self.QScrollArea_4.show()
                    self.button1.show()
                    self.list_of_cameras_state["Camera_3"] = "Normal"
            elif source.objectName() == 'Camera_4':
                #
                if self.list_of_cameras_state["Camera_4"] == "Normal":
                    self.QScrollArea_1.hide()
                    self.QScrollArea_2.hide()
                    self.QScrollArea_3.hide()
                    self.button1.hide()
                    self.list_of_cameras_state["Camera_4"] = "Maximized"
                else:
                    self.QScrollArea_1.show()
                    self.QScrollArea_2.show()
                    self.QScrollArea_3.show()
                    self.button1.show()
                    self.list_of_cameras_state["Camera_4"] = "Normal"
            else:
                return super(MainWindow, self).eventFilter(source, event)
            return True
        else:
            return super(MainWindow, self).eventFilter(source, event)

    # Overwrite method closeEvent from class QMainWindow.
    def closeEvent(self, event) -> None:
        # If thread getIpCameraFrameWorker_1 is running, then exit it.
        if self.CaptureIpCameraFramesWorker_1.isRunning():
            self.CaptureIpCameraFramesWorker_1.quit()
        # If thread getIpCameraFrameWorker_2 is running, then exit it.
        if self.CaptureIpCameraFramesWorker_2.isRunning():
            self.CaptureIpCameraFramesWorker_2.quit()
        # If thread getIpCameraFrameWorker_3 is running, then exit it.
        if self.CaptureIpCameraFramesWorker_3.isRunning():
            self.CaptureIpCameraFramesWorker_3.quit()
        if self.CaptureIpCameraFramesWorker_4.isRunning():
            self.CaptureIpCameraFramesWorker_4.quit()    
        # Accept the event
        event.accept()

def main() -> None:
    # Create a QApplication object. It manages the GUI application's control flow and main settings.
    # It handles widget specific initialization, finalization.
    # For any GUI application using Qt, there is precisely one QApplication object
    app = QApplication(sys.argv)
    # Create an instance of the class MainWindow.
    window = MainWindow()
    # Show the window.
    window.show()
    # Start Qt event loop.
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
