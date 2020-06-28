from Main1 import Ui_MainWindow
from sys import argv, exit
import qimage2ndarray
from PyQt5.QtWidgets import QMainWindow,QStyleFactory,QFileDialog,QApplication,QGraphicsOpacityEffect
from PyQt5.QtGui import QMovie,QIcon,QPixmap,QPalette,QFont,QColor,QCursor
from PyQt5.QtCore import QTimer,Qt,QUrl,QSize
from PyQt5.QtMultimedia import QMediaContent,QMediaPlayer
import time
import qtawesome as qta
import webbrowser
from PyQt5.QtWebEngineWidgets import QWebEngineView
import os
import random
from UI.getweather import getWeather
from CapDetect import *
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
fourcc_record = cv2.VideoWriter_fourcc(*'MPG4')
cameraWIDTH = 1280
cameraHEIGHT = 720
class MyMainWindow(QMainWindow,Ui_MainWindow):
    def __del__(self):
        try:
            self.camera.release()  # 释放资源
        except:
            return
    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.setupUi(self)
        self.initIconBtn()                      #实现每个按钮的图标初始化
        self.PrepWidgets()
        self.PrepParameters()
        self.CallBackFunctions()
        self.Timer = QTimer()
        self.Timer1=QTimer()
        self.Timer2=QTimer()
        self.player = QMediaPlayer()
        self.Timer.timeout.connect(self.TimerOutFun)
        self.Timer1.timeout.connect(self.TimerOutFun1)
        self.Timer2.timeout.connect(self.TimerOutFun2)
        self.setWindowFlags(Qt.FramelessWindowHint) #无边框了 好吧 因为放大了会很丑 先固定成这样吧……
        self.FontSure.clicked.connect(self.changeFont)
        self.ColorSure.clicked.connect(self.changePaletteColor)
        self.fontSizeSld.valueChanged.connect(self.changeFontSize)
####################### weather ##################################
        self.searchWeather.clicked.connect(self.GetWeather)
#********************** music *******************************
        self.songs_list = []
        self.song_formats = ['mp3', 'm4a', 'flac', 'wav', 'ogg']
        # self.settingfilename = 'setting.ini'
        self.defaultMP3 = "defaultMP3.wav"

        self.cur_path = os.path.abspath(os.path.dirname(__file__))
        self.cur_playing_song = ''
        self.is_switching = False
        self.is_pause = True

        # --播放时间
        self.label1.setStyle(QStyleFactory.create('Fusion'))
        self.label2.setStyle(QStyleFactory.create('Fusion'))
        # --滑动条
        self.slider.sliderMoved[int].connect(lambda: self.player.setPosition(self.slider.value()))
        self.slider.setStyle(QStyleFactory.create('Fusion'))
        # --播放按钮
        self.play_button.clicked.connect(self.playMusic)
        self.play_button.setStyle(QStyleFactory.create('Fusion'))
        # --上一首按钮
        self.preview_button.clicked.connect(self.previewMusic)
        self.preview_button.setStyle(QStyleFactory.create('Fusion'))
        # --下一首按钮
        self.next_button.clicked.connect(self.nextMusic)
        self.next_button.setStyle(QStyleFactory.create('Fusion'))
        # --打开文件夹按钮
        self.open_button.setStyle(QStyleFactory.create('Fusion'))
        self.open_button.clicked.connect(self.openDir)
        # --显示音乐列表
        self.musicListWidget.itemDoubleClicked.connect(self.doubleClicked)

        # --如果有初始化setting, 导入setting
        # self.loadSetting()
        # --播放模式
        self.cmb.setStyle(QStyleFactory.create('Fusion'))

        # --计时器
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.playByMode)

    def changeFontSize(self):
        self.setFont(QFont(self.FontCbx.currentText(),self.fontSizeSld.value()))

    def changeFont(self):
        self.setFont(QFont(self.FontCbx.currentText()))

    def changePaletteColor(self):
        if self.colorCbx.currentText()=='白天模式':
            self.dayflag = 0
            self.setPalette(QPalette(QColor('#ebf6f7')))
            self.music_label.setPixmap(QPixmap('img/mount.png'))
            self.movie = QMovie("img/gif2.gif")
            self.music_label.setScaledContents(True)
        elif self.colorCbx.currentText()=='黑夜模式':
            self.dayflag = 1
            self.setPalette(QPalette(QColor('#3F5D95')))
            self.music_label.setPixmap(QPixmap('img/music_pic1.png'))
            self.music_label.setScaledContents(True)
            self.movie = QMovie("img/gif1.gif")
        elif self.colorCbx.currentText()=='护眼模式':
            self.setPalette(QPalette(QColor('#d3f5ce')))

    # 模式设定
    def playByMode(self):
        if (not self.is_pause) and (not self.is_switching):
            self.slider.setMinimum(0)
            self.slider.setMaximum(self.player.duration())
            self.slider.setValue(self.slider.value() + 1000)
        self.label1.setText(time.strftime('%M:%S', time.localtime(self.player.position() / 1000)))
        self.label2.setText(time.strftime('%M:%S', time.localtime(self.player.duration() / 1000)))
        # 顺序播放
        if (self.cmb.currentIndex() == 1) and (not self.is_pause) and (not self.is_switching):
            if self.musicListWidget.count() == 0:
                return
            if self.player.position() == self.player.duration():
                self.nextMusic()
        # 单曲循环
        elif (self.cmb.currentIndex() == 2) and (not self.is_pause) and (not self.is_switching):
            if self.musicListWidget.count() == 0:
                return
            if self.player.position() == self.player.duration():
                self.is_switching = True
                self.setCurPlaying()
                self.slider.setValue(0)
                self.playMusic()
                self.is_switching = False
        # 随机播放
        elif (self.cmb.currentIndex() == 3) and (not self.is_pause) and (not self.is_switching):
            if self.musicListWidget.count() == 0:
                return
            if self.player.position() == self.player.duration():
                self.is_switching = True
                self.musicListWidget.setCurrentRow(random.randint(0, self.musicListWidget.count() - 1))
                self.setCurPlaying()
                self.slider.setValue(0)
                self.playMusic()
                self.is_switching = False
# 打开文件夹
    def openDir(self):
        self.cur_path = QFileDialog.getExistingDirectory(self, "选取文件夹", self.cur_path)
        # print(self.cur_path)
        if self.cur_path:
            self.showMusicList()
            self.cur_playing_song = ''
            self.setCurPlaying()
            self.label1.setText('00:00')
            self.label2.setText('00:00')
            self.slider.setSliderPosition(0)
            self.is_pause = True
            self.play_button.setText('播放')

    # 从文件夹里选取音乐
    def showMusicList(self):
        self.musicListWidget.clear()
        # self.updateSetting()
        # print(self.cur_path)
        for song in os.listdir(self.cur_path):
            try:
                if song.split('.')[-1] in self.song_formats:
                    self.musictip.clear()
                    self.songs_list.append([song, os.path.join(self.cur_path, song).replace('\\', '/')])
                    self.musicListWidget.addItem(song)
                    # print(1)

            except Exception as  e:
                # print(e)
                pass


        self.musicListWidget.setCurrentRow(0)
        if self.songs_list:
            self.cur_playing_song = self.songs_list[self.musicListWidget.currentRow()][-1]
            self.play_button.setEnabled(True)
            self.next_button.setEnabled(True)
            self.preview_button.setEnabled(True)

    # 目前只有双击播放音乐 还没单击= =
    def doubleClicked(self):
        self.slider.setValue(10)
        self.is_switching = True
        self.setCurPlaying()
        self.playMusic()
        self.is_switching = False

    # 当前播放的音乐在这里设置
    def setCurPlaying(self):
        try:
            self.cur_playing_song = self.songs_list[self.musicListWidget.currentRow()][-1]

            self.player.setMedia(QMediaContent(QUrl(self.cur_playing_song)))
            self.player.setVolume(self.voiceSld.value())
        except Exception as e:
            # print(e)

            self.musictip.setText('该文件夹里没有音乐')

    # 播放音乐
    def playMusic(self):
        if self.musicListWidget.count() == 0:
            self.musictip.setText('当前无可播放音乐')
            return

        if not self.player.isAudioAvailable():
            self.setCurPlaying()
        if self.is_pause or self.is_switching:
            self.player.play()
            self.is_pause = False
            self.play_button.setText('暂停')
            self.play_button.setIcon(qta.icon('fa.pause-circle', scale_factor=1, color='#BFDEEF'))
            self.play_button.setIconSize(QSize(200,200))
            # 设置cacheMode为CacheAll时表示gif无限循环，注意此时loopCount()返回-1
            self.movie.setCacheMode(QMovie.CacheAll)
            # 播放速度
            self.movie.setSpeed(100)
            # self.movie_screen是在qtdesigner里定义的一个QLabel对象的对象名，将gif显示在label上
            self.music_label.setMovie(self.movie)
            self.music_label.setScaledContents(True)
            # 开始播放，对应的是movie.start()
            self.movie.start()
        elif (not self.is_pause) and (not self.is_switching):
            self.player.pause()
            self.movie.stop()
            if self.dayflag == 1:
                self.music_label.setPixmap(QPixmap('img\music_pic1.png'))
            else:
                self.music_label.setPixmap(QPixmap('img\music day.png'))
            self.is_pause = True
            self.play_button.setText('播放')
            self.play_button.setIcon(qta.icon('fa.play-circle', scale_factor=1, color='#BFDEEF'))
            self.play_button.setIconSize(QSize(200,200))
    # 上一首
    def previewMusic(self):
        self.slider.setValue(0)
        if self.musicListWidget.count() == 0:
            self.musictip.setText('当前无可播放音乐')
            return
        pre_row = self.musicListWidget.currentRow() - 1 if self.musicListWidget.currentRow() != 0 else self.musicListWidget.count() - 1
        self.musicListWidget.setCurrentRow(pre_row)
        self.is_switching = True
        self.setCurPlaying()
        self.playMusic()
        self.is_switching = False
    # 下一首
    def nextMusic(self):
        self.slider.setValue(0)
        if self.musicListWidget.count() == 0:
            self.musictip.setText('当前无可播放音乐')
            return
        next_row = self.musicListWidget.currentRow() + 1 if self.musicListWidget.currentRow() != self.musicListWidget.count() - 1 else 0
        self.musicListWidget.setCurrentRow(next_row)
        self.is_switching = True
        self.setCurPlaying()
        self.playMusic()
        self.is_switching = False

    def mousePressEvent(self, event):
        # 定义鼠标点击事件
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        # 定义鼠标移动事件
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_drag = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def PrepWidgets(self):  # 这个是设置按钮 button 刚开始都是f
        # self.AgainBt_2.setDisabled(True)
        self.AgainBt_3.setDisabled(True)
        self.StopBt.setEnabled(False)
        self.RecordBt.setEnabled(False)
        # self.radioSbx.setEnabled(False)
        self.radioSld.setEnabled(False)
        # self.StopBt_2.setEnabled(False)
        self.StopBt_3.setEnabled(False)
        self.play_button.setEnabled(False)
        self.preview_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.ShowBt_3.setEnabled(False)
        # self.ShowBt.setEnabled(False)
        # self.videockb.isChecked(True)
        self.voiceSld.hide()
        self.setRe.hide()
        self.StopBt.hide()
        self.MsgTE.hide()
        self.btnReturn.hide()
        # self.musictip.hide()
        self.weatherLineEdit.setText('南京')
        self.GetWeather()

    def PrepCamera(self):
        try:
            if self.videockb.isChecked()== True:
                if self.ShowBt.text()=='开始':
                    filename,filetype = QFileDialog.getOpenFileName(self, 'Choose file')
                    self.camera = cv2.VideoCapture(filename)#'materials/videos/video_1.mp4'
                    self.MsgTE.clear()
                    self.MsgTE.append('选择测试视频')
                # else:
                #     self.camera = cv2.VideoCapture(filename)
                # self.MsgTE.setPlainText()

            elif self.camerackb.isChecked()==True:
                self.camera = cv2.VideoCapture(0,apiPreference=cv2.CAP_DSHOW)
                # fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                self.camera.set(cv2.CAP_PROP_FOURCC, fourcc)
                self.camera.set(cv2.CAP_PROP_FPS, 30)
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, cameraWIDTH)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, cameraHEIGHT)
                if self.camera.isOpened()==True:
                    self.MsgTE.clear()
                    self.MsgTE.append('摄像头已连接')
                else:
                    self.DispLb.setText('摄像头未连接或打开失败，请检查')

        #
        except Exception as e:
            self.MsgTE.clear()
            self.MsgTE.append(str(e))

    def PrepParameters(self):
        # self.PrepCamera()
        # self.RecordPath = QFileDialog.getExistingDirectory(self, "浏览", '.')
        # self.frame_8.hide()
        self.ShowBt.setEnabled(False)
        self.stackedWidget.setCurrentIndex(0)
        self.helpStackedWidget.setCurrentIndex(0)
        self.SetStackedWidget.setCurrentIndex(0)
        self.RecordFlag = 0
        self.RecordPath = 'record' #默认值
        self.FilePathLE.setText(self.RecordPath)
        for i in os.listdir(self.RecordPath):
            self.RecordListWidget.addItem(i)
        self.Image_num = 0
        self.Image_num1 = 0
        self.Image_num2 = 0
        self.ReFlag = 0
        self.ReVideoFlag = 0
        self.flag1=0
        self.clickNum = 0
        self.clickNum1 = 0
        self.weatherLineEdit.setText('请输入查询城市')

    def GetWeather(self):
        try:
            self.weatiplab.clear()
            self.cityc = self.weatherLineEdit.text()
            w1,t1 = getWeather(self.cityc)
            self.citinamelab.setText(self.cityc)
            self.temlab.setText(t1)
            self.wealab.setText(w1)

            if w1[0:2] == '阵雨'or w1[0:2] == '大雨':
                self.weaLabel.setPixmap(QPixmap('icon/icons8-倾盆大雨-96.png'))
            elif w1[0:2] ==  '暴雨'or w1[0:2] == '特大':
                self.weaLabel.setPixmap(QPixmap('icon/icons8-强降雨-96.png'))
            elif w1[0:2] == '小雨':
                self.weaLabel.setPixmap(QPixmap('icon/icons8-小雨-96.png'))
            elif w1[0:2] == '中雨':
                self.weaLabel.setPixmap(QPixmap('icon/icons8-中雨-96.png'))
            elif w1[0:2] == '多云' or w1[0:2] =='阴转'or w1[0:2] =='阴 ':
                self.weaLabel.setPixmap(QPixmap('icon/icons8-云-96.png'))
            elif w1[0:2] == '雷阵':
                self.weaLabel.setPixmap(QPixmap('icon/icons8-风暴-96.png'))
            elif w1[0:2] == '晴' or w1[0:2] == '晴转':
                self.weaLabel.setPixmap(QPixmap('icon/icons8-太阳-480.png'))
            elif w1[0:2] == '大雪' or w1[0:2] == '小雪':
                self.weaLabel.setPixmap(QPixmap('icon/icons8-小雪-96.png'))
            else:
                self.weaLabel.setPixmap(QPixmap('icon/icons8-彩虹-96.png'))

        except:
            self.weatiplab.setText('请重新输入城市名')
            self.citinamelab.setText('城市名不存在')
            self.temlab.clear()
            self.wealab.clear()
            self.weaLabel.setPixmap(QPixmap('icon/icons8-彩虹-96.png'))

    # ======== 选取行车记录文件夹里的视频 然后添加到左侧的列表里 =========
    def viewList(self):
        # print(self.RecordPath)
        for i in os.listdir(self.RecordPath):
            self.RecordListWidget.addItem(i)

    # ============== 设置槽函数 ===============
    def CallBackFunctions(self):
        self.FilePathLE.hide()
        self.FilePathBt.hide()
        self.label_4.hide()
        self.FilePathBt_2.hide()
        self.FilePathBt.clicked.connect(self.SetFilePath)
        self.FilePathBt_2.clicked.connect(self.SetFilePath)
        self.ShowBt.clicked.connect(self.StartCamera)
        # self.ShowBt_2.clicked.connect(self.openDemo)
        self.StopBt.clicked.connect(self.StopCamera)
        # self.StopBt_2.clicked.connect(self.StopDemo)
        self.RecordBt.clicked.connect(self.RecordCamera)
        self.mapSure.clicked.connect(self.openMap)
        # self.AgainBt_2.clicked.connect(self.Rebroadcast)
        self.AgainBt_3.clicked.connect(self.Rebroadcast1)
        self.btnReturn.clicked.connect(self.clickReturn)  # 返回键的设置
        self.setRe.clicked.connect(self.clickSetReturn)
        self.bt1.clicked.connect(self.slotBtnClicked)
        self.bt2.clicked.connect(self.slotBtnClicked)
        self.bt3.clicked.connect(self.slotBtnClicked)
        self.bt4.clicked.connect(self.slotBtnClicked)
        self.bt5.clicked.connect(self.slotBtnClicked)
        self.bt6.clicked.connect(self.slotBtnClicked)
        self.bt11.clicked.connect(self.SetBtnClicked)
        self.bt22.clicked.connect(self.SetBtnClicked)
        self.bt33.clicked.connect(self.SetBtnClicked)
        self.bt44.clicked.connect(self.SetBtnClicked)
        self.bt111.clicked.connect(self.introBtnClicked)
        self.bt222.clicked.connect(self.introBtnClicked)
        self.RecordListWidget.itemDoubleClicked.connect(self.openRecords)
        self.RecordListWidget.itemClicked.connect(self.getRecordName)
        self.ShowBt_3.clicked.connect(self.openRecords)
        self.StopBt_3.clicked.connect(self.StopVideo)
        self.voiceSld.valueChanged.connect(self.changeVoice)
        self.voicebtlabel.clicked.connect(self.voiceLabelDisplay)
        self.exitBt.clicked.connect(self.ExitCamera)
        self.voiceTbn.clicked.connect(self.voiceLabelDisplay)
        self.exitBt.hide()
        self.videockb.clicked.connect(self.enableShow)
        self.camerackb.clicked.connect(self.enableShow)


        # self.FilePathLE.hide()
        # self.videockb.isChecked.connect(self.SetFilePath)
    def enableShow(self):
        self.ShowBt.setEnabled(True)
    def voiceTbnDisplay(self):
        self.clickNum1 += 1
        if self.clickNum % 2 != 0:
            self.radioSld.show()
            self.voiceTbn.setIcon(QIcon("icon\icons8-音量-enab.png"))
        else:
            self.radioSld.hide()
            self.voiceTbn.setIcon(QIcon("icon\icons8-音量-disable.png"))

    def voiceLabelDisplay(self):
        self.clickNum += 1
        if self.clickNum%2 != 0:
            self.voiceSld.show()
            self.voicebtlabel.setIcon(QIcon("icon\icons8-音量-enab.png"))
        else:
            self.voiceSld.hide()
            self.voicebtlabel.setIcon(QIcon("icon\icons8-音量-disable.png"))

    def changeVoice(self):
        self.player.setVolume(self.voiceSld.value())

    def getRecordName(self):
        self.filename1 = self.RecordListWidget.currentItem().text()
        self.ShowBt_3.setDisabled(False)

    def Rebroadcast(self):
        self.ReFlag = 1
        self.AgainBt_2.setEnabled(False)
        # self.openDemo()
        # print("demo重播")

    def Rebroadcast1(self):
        #self.ReVideoFlag = 1
        self.AgainBt_3.setEnabled(False)
        self.openRecords()
        # print("记录重播")

    # ============ 第三个 行车记录显示 ==============
    def openRecords(self):
        # print(self.RecordListWidget.currentItem().text())
        self.filename1 = self.RecordListWidget.currentItem().text()
        # print(self.RecordPath+self.filename1)
        try:
            img = cv2.imread(self.RecordPath+self.filename1)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            qimg = qimage2ndarray.array2qimage(img)
            self.Disp_lab3.setPixmap(QPixmap(qimg))
            self.Disp_lab3.show()
            # print("图像显示")
        except:
            self.StopBt_3.setEnabled(True)
            if self.ShowBt_3.text()=="播放":
                self.ShowBt_3.setIcon(QIcon("icon\icons8-停止-80.png"))
                self.ShowBt_3.setText("停止")
                # print(self.RecordPath+'/'+self.filename1)
                self.camera2=cv2.VideoCapture(self.RecordPath+'/'+self.filename1)
                # self.ShowBt_3.setDisabled(True)
                self.Timer2.start(1)
                # print("记录播放")
                self.time2b = time.clock()
            elif self.ShowBt_3.text()=="停止":
                self.ShowBt_3.setText("播放")
                self.ShowBt_3.setIcon(QIcon(qta.icon('fa.play-circle', scale_factor=1, color='#a2d7dd')))
                self.Timer2.stop()
                self.Disp_lab3.setText("记录停止")

    def StopVideo(self):
        if self.StopBt_3.text()=='暂停':
            self.StopBt_3.setText('继续')
            self.StopBt_3.setIcon(qta.icon('fa.play', scale_factor=1, color='#a2d7dd'))
            self.Timer2.stop()
        elif self.StopBt_3.text()=='继续':
            self.StopBt_3.setText('暂停')
            self.StopBt_3.setIcon(qta.icon('fa.pause', scale_factor=1, color='#a2d7dd'))
            self.Timer2.start(1)

    def StartCamera(self):
        # self.ShowBt.setEnabled(False)
        self.PrepCamera()
        # print(self.ShowBt.text())
        if self.ShowBt.text()=='开始':
            self.ShowBt.setText('停止')
            self.ShowBt.setIcon(qta.icon('fa.stop-circle', scale_factor=1, color='#abced8'))
            self.StopBt.setEnabled(True)
            self.RecordBt.setEnabled(True)
            self.RecordBt.setText('录像')
            self.Timer.start(1)
            self.timelb = time.clock()
        elif self.ShowBt.text()=='停止':
            self.ShowBt.setText('开始')
            self.ShowBt.setIcon(qta.icon('fa.play-circle', scale_factor=1, color='#abced8'))
            self.Timer.stop()
            self.DispLb.clear()
    # ============第一个 校正摄像头=========
    def jiaozheng(self):
        # print('aaaaaaaaaaaaaaaaa')
        self.camera1 = cv2.VideoCapture(0, apiPreference=cv2.CAP_DSHOW)
        self.camera1.set(cv2.CAP_PROP_FOURCC, fourcc)
        self.camera1.set(cv2.CAP_PROP_FPS, 30)
        self.camera1.set(cv2.CAP_PROP_FRAME_WIDTH, cameraWIDTH)
        self.camera1.set(cv2.CAP_PROP_FRAME_HEIGHT, cameraHEIGHT)
        self.Timer1.start(1)
        self.timelb1 = time.clock()
        if self.camera1.isOpened() == False:
            self.DispLb_2.setText('摄像头未连接或打开失败，请检查')
        #
        # success, img = self.camera1.read()
        # if success:
        #     print(success)
        #     self.Image1 = img
        #     # cv2.waitKey(35)
        #     size = (950, np.uint16(950 / img.shape[1] * img.shape[0]))
        #     self.Image1 = cv2.resize(self.Image1, size, interpolation=cv2.INTER_NEAREST)
        #     img = cv2.cvtColor(self.Image1, cv2.COLOR_BGR2RGB)
        #     qimg = qimage2ndarray.array2qimage(img)
        #     self.DispLb_2.setPixmap(QPixmap(qimg))
        #     self.DispLb_2.show()
    # ========== 第一个 功能演示 ==========
    # def openDemo(self):
    #     self.StopBt_2.setEnabled(True)
    #     if self.ShowBt_2.text() == '开始' and self.ReFlag == 0: #flag=0 openfile
    #         self.StopBt_2.setEnabled(True)
    #         self.filename, self.filetype = QFileDialog.getOpenFileName(self, 'Choose file')
    #         self.ShowBt_2.setText('停止')
    #         self.ShowBt_2.setIcon(qta.icon('fa.stop-circle', scale_factor=1, color='#a2d7dd'))
    #         self.camera1 = cv2.VideoCapture(self.filename)
    #         self.Timer1.start(1)
    #         self.timelb1 = time.clock()
    #     elif self.ShowBt_2.text() == '开始' and self.ReFlag==1: #重播
    #         self.StopBt_2.setEnabled(True)
    #         self.ReFlag = 0
    #         self.ShowBt_2.setText('停止')
    #         self.ShowBt_2.setIcon(qta.icon('fa.stop-circle', scale_factor=1, color='#a2d7dd'))
    #         self.camera1 = cv2.VideoCapture(self.filename)
    #         self.Timer1.start(1)
    #         self.timelb1 = time.clock()
    #     elif self.ShowBt_2.text()=='停止':
    #         self.DispLb_2.setText("视频停止，请选择视频播放:)")
    #         self.ShowBt_2.setText('开始')
    #         self.StopBt_2.setIcon(qta.icon('fa.play', scale_factor=1, color='#a2d7dd'))
    #         self.DispLb_2.clear()
    #         self.Timer1.stop()
    #
    # def StopDemo(self):
    #     if self.StopBt_2.text() == '暂停':
    #         self.StopBt_2.setText('继续')
    #         self.StopBt_2.setIcon(qta.icon('fa.play', scale_factor=1, color='#a2d7dd'))
    #         # self.DispLb_2.setText("视频暂停:)")
    #         # print("demo视频暂停:)")
    #         self.Timer1.stop()
    #     elif self.StopBt_2.text() == '继续':
    #         self.StopBt_2.setIcon(qta.icon('fa.pause', scale_factor=1, color='#ffffff'))
    #         self.StopBt_2.setText('暂停')
    #         self.Timer1.start(1)


    # ============== 设置filepath的text名字 =================
    def SetFilePath(self):
        # self.RecordListWidget.clear()
        # self.cur_path = QFileDialog.getExistingDirectory(self, "选取文件夹", self.cur_path)
        self.RecordPath = QFileDialog.getExistingDirectory(self, "浏览", '.')
        for i in os.listdir(self.RecordPath):
            self.RecordListWidget.addItem(i)

    # ================ 2安全驾驶 实时的 ===================
    def TimerOutFun(self):
        success, img = self.camera.read()
        if success:
            # =============网络检测=================
            img, lane_alert, car_alert, person_alert, light_alert = video_detect(img)
            self.Image_r = img
            # cv2.waitKey(35)
            size = (701, np.uint16(701 / img.shape[1] * img.shape[0]))
            img = cv2.resize(img, size, interpolation=cv2.INTER_NEAREST)
            # ======================================
            self.Image = img  #  img 替换为abcd中的返回值 就是网络处理图像后得到的值
            img = cv2.cvtColor(self.Image, cv2.COLOR_BGR2RGB)
            cv2.waitKey(25)
            qimg = qimage2ndarray.array2qimage(img)
            self.DispLb.setPixmap(QPixmap(qimg))
            self.DispLb.show()
            self.Image_num += 1
            self.flag1 = self.flag1 + 1

            if self.RecordFlag == 1:
                self.video_writer.write(self.Image_r)
            if self.Image_num % 10 == 9:
                frame_rate = 10 / (time.clock() - self.timelb)
                self.FmRateLCD.display(frame_rate)
                self.timelb = time.clock()

            if car_alert == 1:
                col = "red"
                self.btnBoo.setIcon(qta.icon('fa.automobile', scale_factor=1, color=col))
            elif lane_alert == 1:
                col = 'red'
                self.btnTurn.setIcon(qta.icon('fa.ellipsis-v', scale_factor=1, color=col))
            elif light_alert == 1:
                col = "red"
                self.btnLig.setIcon(qta.icon('fa.circle-o', scale_factor=1, color=col))
            elif person_alert == 1:
                col = "red"
                self.btnPeo.setIcon(qta.icon('fa.user', scale_factor=1, color=col))
            else:
                col = "green"
                self.btnTurn.setIcon(qta.icon('fa.ellipsis-v', scale_factor=1, color=col))
                self.btnBoo.setIcon(qta.icon('fa.automobile', scale_factor=1, color=col))
                self.btnLig.setIcon(qta.icon('fa.circle-o', scale_factor=1, color=col))
                self.btnPeo.setIcon(qta.icon('fa.user', scale_factor=1, color=col))
                # self.btnTurn.setIcon(qta.icon('fa.star-o', scale_factor=1, color=col))
            if self.ShowBt.text() == '开始':
                self.DispLb.clear()
                self.ShowBt.setIcon(qta.icon('fa.play-circle', scale_factor=1, color='#a2d7dd'))
                self.StopBt.setEnabled(False)
                self.camera.release()


        else:
            self.Timer.stop()
            self.Image_num=0
            self.ShowBt.setText("开始")
            self.ShowBt.setIcon(qta.icon('fa.play-circle', scale_factor=1, color='#a2d7dd'))
            self.DispLb.clear()
            self.MsgTE.clear()
            self.MsgTE.setPlainText('图像获取失败')
            self.camera.release()
            self.DispLb.setText('摄像头打开失败')

    def StopCamera(self):
        if self.StopBt.text() == '暂停':
            self.StopBt.setText('继续')
            self.DispLb.clear()
            self.RecordBt.setText('保存')

            self.Timer.stop()
        elif self.StopBt.text() == '继续':
            self.StopBt.setText('暂停')
            self.RecordBt.setText('录像')

            self.Timer.start(1)

    def RecordCamera(self):
        tag = self.RecordBt.text()
        if tag == '保存':
            try:
                self.RecordBt.setIcon(QIcon('icon\icons8-停止-80.png'))
                image_name = 'image' + time.strftime('%Y%m%d%H%M%S',time.localtime(time.time())) + '.jpg'
                cv2.imwrite(image_name, self.Image_r)
                self.MsgTE.clear()
                self.MsgTE.setPlainText('Image saved.')
                self.RecordListWidget.addItem(image_name) #print(image_name)
            except Exception as e:
                self.MsgTE.clear()
                self.MsgTE.setPlainText(str(e))
        elif tag == '录像':
            self.RecordBt.setText('停止')
            self.RecordBt.setIcon(QIcon('icon\icons8-停止-80.png'))
            video_name = 'video' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + '.mp4'
            # video_name1 = 'video' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + '.mp4'
            # fps = self.FmRateLCD.value()
            size = (self.Image_r.shape[1], self.Image_r.shape[0])

            self.video_writer = cv2.VideoWriter(self.RecordPath+'/'+video_name, fourcc_record, self.camera.get(5), size)

            self.RecordFlag = 1
            self.MsgTE.setPlainText('Video recording...')
            self.RecordListWidget.addItem(video_name)
            self.StopBt.setEnabled(False)

        elif tag == '停止':
            self.RecordBt.setText('录像')
            self.RecordBt.setIcon(QIcon('icon\iconRecord.png'))
            self.video_writer.release()
            self.RecordFlag = 0
            self.MsgTE.setPlainText('Video saved.')
            self.StopBt.setEnabled(True)

    # ================ 功能展示 =================
    def TimerOutFun1(self):
        success, img = self.camera1.read()
        if success:
            cv2.line(img, (0, cameraHEIGHT // 2), (cameraWIDTH, cameraHEIGHT // 2), (0, 255, 0), 2)
            cv2.line(img, (cameraWIDTH // 2, 0), (cameraWIDTH // 2, cameraHEIGHT), (0, 255, 0), 2)
            self.Image1 = img
            cv2.waitKey(25)
            size = (950, np.uint16(950 / img.shape[1] * img.shape[0]))
            self.Image1 = cv2.resize(self.Image1, size, interpolation=cv2.INTER_NEAREST)
            img = cv2.cvtColor(self.Image1, cv2.COLOR_BGR2RGB)
            qimg = qimage2ndarray.array2qimage(img)
            self.DispLb_2.setPixmap(QPixmap(qimg))
            self.DispLb_2.show()

    # ============ 播放存储的行车记录 ==============
    def TimerOutFun2(self):
        success1, img = self.camera2.read()
        # print(success1)
        if success1:
            cv2.waitKey(40)
            size = (730, np.uint16(730 / img.shape[1] * img.shape[0]))
            img = cv2.resize(img, size, interpolation=cv2.INTER_NEAREST)
            self.Image2 = img
            img = cv2.cvtColor(self.Image2, cv2.COLOR_BGR2RGB)
            qimg = qimage2ndarray.array2qimage(img)
            self.Disp_lab3.setPixmap(QPixmap(qimg))
            self.Disp_lab3.show()
            self.Image_num2 += 1
            if self.ShowBt_3.text() == '播放':
                self.Disp_lab3.clear()
                self.ShowBt_3.setIcon(qta.icon('fa.play-circle', scale_factor=1, color='#a2d7dd'))
                self.StopBt_3.setEnabled(False)
        else:
            self.Image_num2=0
            self.Timer2.stop()
            #self.AgainBt_3.setEnabled(True)
            # if self.StopBt_3.text()=='继续':
            #     self.Disp_lab3.setText("视频暂停:)")
            #     print('记录播放暂停')
            # else:
            #     self.Disp_lab3.setText("视频播放完毕，请重新播放别的视频:)")
            #     self.ShowBt_3.setDisabled(False)
            self.Disp_lab3.setText("视频播放完毕:)")
            self.ShowBt_3.setText("播放")
            self.ShowBt_3.setIcon(qta.icon('fa.play-circle', scale_factor=1, color='#a2d7dd'))
            self.AgainBt_3.setEnabled(True)
            self.StopBt_3.setEnabled(False)
            self.StopBt_3.setText('暂停')
            self.StopBt_3.setIcon(qta.icon('fa.pause', scale_factor=1, color='#a2d7dd'))

    def ExitCamera(self):
        self.Timer.stop()
        # print(11)
        # self.DispLb.clear()
        self.camera.release()
        self.MsgTE.setPlainText('Exiting the application..')
        #QCoreApplication.quit()

    # =========== 初始化各种按钮的图标 ============
    def initIconBtn(self):
        icon1 = qta.icon('fa.cloud', scale_factor=1, color='#ffffff')  # fa.icon_name
        icon2 = qta.icon('fa.tv', scale_factor=1, color='#ffffff')
        icon3 = qta.icon('fa.video-camera', scale_factor=1, color='#ffffff')
        icon4 = qta.icon('fa.car', scale_factor=1, color='#ffffff')
        icon5 = qta.icon('fa.music', scale_factor=1, color='#ffffff')
        icon6 = qta.icon('fa.cog', scale_factor=1, color='#ffffff')
        self.bt1.setIcon(icon1)
        self.bt1.setIconSize(QSize(61, 61))
        self.bt2.setIcon(icon2)
        self.bt2.setIconSize(QSize(61, 61))
        self.bt3.setIcon(icon3)
        self.bt3.setIconSize(QSize(61, 61))
        self.bt4.setIcon(icon4)
        self.bt4.setIconSize(QSize(61, 61))
        self.bt5.setIcon(icon5)
        self.bt5.setIconSize(QSize(61, 61))
        self.bt6.setIcon(icon6)
        self.bt6.setIconSize(QSize(61, 61))
        self.bt1.setStyleSheet(
            '''
                QToolButton{background-color:#DAE8F3;border-radius:10px;padding:2px 4px;}
                QToolButton:hover{background-color:#ABBCDA;}
            ''')
        self.bt2.setStyleSheet(
            '''
                QToolButton{background-color:#e3e3e3;border-radius:10px;padding:2px 4px;}
                QToolButton:hover{background-color:#d3d3d3;}

            ''')
        self.bt3.setStyleSheet(
            '''
                QToolButton{background-color:#FBC3C8;border-radius:10px;padding:2px 4px;}
                QToolButton:hover{background-color:#F4ABB4;}

            ''')
        self.bt4.setStyleSheet(
            '''
                QToolButton{background-color:#F6DCD7;border-radius:10px;padding:2px 4px;}
                QToolButton:hover{background-color:#F4ABB4;}
            ''')
        self.bt5.setStyleSheet(
            '''
                QToolButton{background-color:#CFE1F7;border-radius:10px;padding:2px 4px;}
                QToolButton:hover{background-color:#ABBCDA;}

            ''')
        self.bt6.setStyleSheet(
            '''
                QToolButton{background-color:#7EABD0;border-radius:10px;padding:2px 4px;}
                QToolButton:hover{background-color:#ABBCDA;}
            ''')
        op = QGraphicsOpacityEffect()       # 设置主界面的按钮 透明度
        op.setOpacity(1)
        self.bt1.setGraphicsEffect(op)
        self.bt2.setGraphicsEffect(op)      # self.bt1.setWindOpacity(0.05)

        op.setOpacity(0.95)
        self.bt3.setGraphicsEffect(op)
        self.bt4.setGraphicsEffect(op)
        self.bt5.setGraphicsEffect(op)
        self.bt6.setGraphicsEffect(op)
        self.btnReturn.setIcon(qta.icon('fa.chevron-left', scale_factor=1, color='#BFDEEF'))
        self.btnReturn.setIconSize(QSize(61, 61))
        self.btnExit.setIcon(QIcon('icon\icons8-删除-480.png'))
        self.btnExit.setIconSize(QSize(61, 61))
        self.btnReturn.setStyleSheet(
            '''
                QPushButton{background:transparent;border-radius:10px;padding:2px 4px;}
                QPushButton:hover{background-color:#83bff3;}
            ''')
        self.btnExit.setStyleSheet(
            '''
                QPushButton{background:transparent;border-radius:10px;padding:2px 4px;}
                QPushButton:hover{background-color:#ee857a;}
            ''')

        icon12 = qta.icon('fa.pause', scale_factor=1, color='#a2d7dd')
        icon13 = qta.icon('fa.play-circle', scale_factor=1, color='#a2d7dd')
        icon14 = qta.icon('fa.folder-open-o', scale_factor=1, color='#a2d7dd')  #
        # self.StopBt_2.setIcon(icon12)
        self.StopBt_3.setIcon(icon12)
        self.StopBt.setIcon(icon12)
        # self.ShowBt_2.setIcon(icon13)
        self.ShowBt_3.setIcon(icon13)
        self.ShowBt.setIcon(icon13)
        self.FilePathBt.setIcon(icon14)
        self.exitBt.setIcon(qta.icon('fa.stop-circle-o', scale_factor=1, color='#a2d7dd'))
        self.setRe.setIcon(qta.icon('fa.chevron-left', scale_factor=1, color='#bce2e8'))

        self.FilePathBt_2.setIcon(qta.icon('fa.folder-open-o', scale_factor=1, color='#a2d7dd'))
        self.RecordBt.setIcon(QIcon(('icon\iconRecord.png')))
        self.AgainBt_3.setIcon(qta.icon('fa.undo', scale_factor=1, color='#a2d7dd'))
        # self.AgainBt_2.setIcon(qta.icon('fa.undo', scale_factor=1, color='#a2d7dd'))
        self.FilePathBt_2.setStyleSheet(
            '''
            QToolButton{border-radius:10px;padding:2px 4px}
            QToolButton:hover{background-color:#abced8;}

            ''')
        self.AgainBt_3.setStyleSheet('''
            QToolButton{border-radius:10px;padding:2px 4px}
            QToolButton:hover{background-color:#abced8;}

            ''')
        self.StopBt.setStyleSheet('''
            QToolButton{border-radius:10px;padding:2px 4px}
            QToolButton:hover{background-color:#abced8;}

            ''')
        # self.StopBt_2.setStyleSheet('''
        #     QToolButton{border-radius:10px;padding:2px 4px}
        #     QToolButton:hover{background-color:#abced8;}
        #     ''')
        self.StopBt_3.setStyleSheet('''
            QToolButton{border-radius:10px;padding:2px 4px}
            QToolButton:hover{background-color:#abced8;}

            ''')
        self.ShowBt.setStyleSheet('''
            QToolButton{border-radius:10px;padding:2px 4px}
            QToolButton:hover{background-color:#abced8;}

             ''')
        # self.ShowBt_2.setStyleSheet('''
        #     QToolButton{border-radius:10px;padding:2px 4px}
        #     QToolButton:hover{background-color:#abced8;}
        #
        #     ''')
        self.exitBt.setStyleSheet('''
            QToolButton{border-radius:10px;padding:2px 4px}
            QToolButton:hover{background-color:#abced8;}

            ''')
        self.ShowBt_3.setStyleSheet('''
            QToolButton{border-radius:10px;padding:2px 4px}
            QToolButton:hover{background-color:#abced8;}

            ''')
        # self.AgainBt_2.setStyleSheet(
        #     '''
        #     QToolButton{border-radius:10px;padding:2px 4px}
        #     QToolButton:hover{background-color:#abced8;}
        #
        #     ''')
        self.RecordBt.setStyleSheet(
            '''
            QToolButton{border-radius:10px;padding:2px 4px}
            QToolButton:hover{background-color:#abced8;}
            ''')
        self.FilePathBt.setStyleSheet(
            '''
                QToolButton{border-radius:10px;padding:2px 4px;}
                QToolButton:hover{border:1px solid #abced8;}
            ''')
        self.FilePathBt.setIconSize(QSize(35, 35))
        self.FilePathBt_2.setIconSize(QSize(35, 35))
        self.ShowBt.setIconSize(QSize(35, 35))
        self.StopBt.setIconSize(QSize(35, 35))
        self.RecordBt.setIconSize(QSize(35, 35))
        # self.ShowBt_2.setIconSize(QSize(35, 35))
        # self.StopBt_2.setIconSize(QSize(35, 35))
        # self.AgainBt_2.setIconSize(QSize(35, 35))
        self.ShowBt_3.setIconSize(QSize(35, 35))
        self.StopBt_3.setIconSize(QSize(35, 35))
        self.AgainBt_3.setIconSize(QSize(35, 35))
        self.exitBt.setIconSize(QSize(40,40))

        icon8 = qta.icon('fa.user', scale_factor=1, color='#abced8')
        icon9 = qta.icon('fa.circle-o', scale_factor=1, color='#abced8')
        icon10 = qta.icon('fa.ellipsis-v', scale_factor=1, color='#abced8')
        icon11 = qta.icon('fa.car', scale_factor=1, color='#abced8')
        self.btnPeo.setIcon(icon8)
        self.btnLig.setIcon(icon9)
        self.btnTurn.setIcon(icon10)
        self.btnBoo.setIcon(icon11)
        self.btnPeo.setStyleSheet("background:transparent")
        self.btnTurn.setStyleSheet("background:transparent")
        self.btnLig.setStyleSheet("background:transparent")
        self.btnBoo.setStyleSheet("background:transparent")
        self.MsgTE.setStyleSheet("background:transparent")

        self.setWindowOpacity(0.98)                     # 设置窗口透明度
        self.setWindowFlag(Qt.FramelessWindowHint)      # 隐藏边框 没看出什么效果

        #================= 初始化音乐模块里的声音图标 ===============
        self.voicebtlabel.setIcon(QIcon('icon/icons8-音量-disable.png'))
        self.preview_button.setIcon(QIcon('icon/icons8-快退-96.png'))
        self.next_button.setIcon(QIcon('icon/icons8-快进-96.png'))
        self.play_button.setIcon(qta.icon('fa.play-circle', scale_factor=1, color='#BFDEEF'))
        self.open_button.setIcon(QIcon('icon/icons8-音乐文件夹-80.png'))
        self.voicebtlabel.setIconSize(QSize(30,30))
        self.preview_button.setIconSize(QSize(50,50))
        self.play_button.setIconSize(QSize(165,165))
        self.next_button.setIconSize(QSize(50,50))
        self.open_button.setIconSize(QSize(50,50))
        self.preview_button.setStyleSheet(
            '''
                QToolButton{background:transparent;border-radius:10px;padding:2px 4px;}
                QToolButton:hover{background-color:#83bff3;}
            ''')
        self.play_button.setStyleSheet(
            '''
                QToolButton{background:transparent;border-radius:10px;padding:2px 4px;}
                QToolButton:hover{background-color:#83bff3;}
            ''')
        self.next_button.setStyleSheet(
            '''
                QToolButton{background:transparent;border-radius:10px;padding:2px 4px;}
                QToolButton:hover{background-color:#83bff3;}
            ''')
        self.open_button.setStyleSheet(
            '''
                QPushButton{background:transparent;border-radius:10px;padding:2px 4px;}
                QPushButton:hover{border:1px solid #83bff3;}
            ''')
        self.voicebtlabel.setStyleSheet(
            '''
                QToolButton{background:transparent;border-radius:10px;padding:2px 4px;}
                QToolButton:hover{background-color:#83bff3;}
            ''')
        self.music_label.setPixmap(QPixmap('img/music_pic1.png'))
        self.music_label.setScaledContents(True)
        self.musicListWidget.setStyleSheet('background:transparent')
        self.cmb.setItemIcon(0,QIcon('icon/icons8-播放列表-96.png'))
        self.cmb.setItemIcon(1,QIcon('icon/icons8-对齐-96.png'))
        self.cmb.setItemIcon(2, QIcon('icon/icons8-重复一个-96.png'))
        self.cmb.setItemIcon(3, QIcon('icon/icons8-随机-96.png'))
        self.cmb.setIconSize(QSize(40,40))
        self.cmb.setStyleSheet('border-radius:10px;padding:2px 4px;border:1px solid #ffffff')

        #================== 初始化天气模块 ====================
        self.weaLabel.setPixmap(QPixmap('icon/icons8-彩虹-96.png'))
        self.weaLabel.setScaledContents(True)
        self.searchWeather.setIcon(qta.icon('fa.search', scale_factor=1, color='#BFDEEF'))
        self.searchWeather.setIconSize(QSize(35, 35))
        self.searchWeather.setStyleSheet(
            '''
                QPushButton{background:transparent;border-radius:10px;padding:2px 4px;}
                QPushButton:hover{background-color:#83bff3;}
            ''')

        # self.searchWeather.setStyleSheet('background:transparent')
        self.weatherLineEdit.setStyle(QStyleFactory.create('Fusion'))

        #==================设置模块===================
        self.setRe.setStyle(QStyleFactory.create('Fusion'))
        self.bt11.setIcon(QIcon('icon/icons8-性别中性用户-96.png'))
        self.bt11.setIconSize(QSize(150,150))
        self.bt22.setIcon(QIcon('icon/icons8-帮助-96.png'))
        self.bt22.setIconSize(QSize(150, 150))
        self.bt33.setIcon(QIcon('icon/icons8-点亮-96.png'))
        self.bt33.setIconSize(QSize(150, 150))
        self.bt44.setIcon(QIcon('icon/icons8-下载更新-96.png'))
        self.bt44.setIconSize(QSize(150, 150))
        self.bt11.setStyleSheet(
            '''
               QToolButton{background:transparent;border-radius:10px;padding:2px 4px;}
               QToolButton:hover{font-size:26px;border-bottom:2px solid #00007f}
           ''')
        self.bt22.setStyleSheet(
            '''
               QToolButton{background:transparent;border-radius:10px;padding:2px 4px;}
               QToolButton:hover{font-size:26px;border-bottom:2px solid #00007f}
           ''')
        self.bt33.setStyleSheet(
            '''
               QToolButton{background:transparent;border-radius:10px;padding:2px 4px;}
               QToolButton:hover{font-size:26px;border-bottom:2px solid #00007f}
           ''')
        self.bt44.setStyleSheet(
            '''
               QToolButton{background:transparent;border-radius:10px;padding:2px 4px;}
               QToolButton:hover{font-size:26px;border-bottom:2px solid #00007f}
           ''')
        self.bt111.setStyleSheet(
            '''
               QPushButton{background:transparent;border-radius:10px;padding:2px 4px;text-color:#83bff3;}
               QPushButton:hover{background-color:#83bff3;}
           ''')
        self.bt222.setStyleSheet(
            '''
               QPushButton{background:transparent;border-radius:10px;padding:2px 4px;text-color:#83bff3;}
               QPushButton:hover{background-color:#83bff3;}
           ''')

        self.bt333.setStyleSheet(
             '''
                QPushButton{background:transparent;border-radius:10px;padding:2px 4px;text-color:#83bff3;}
                QPushButton:hover{background-color:#83bff3;}
            ''')
        self.setpic.setPixmap(QPixmap('img\背景.png'))
        self.setpic.setScaledContents(True)

        #=====默认是白天=====
        self.setPalette(QPalette(QColor('#ebf6f7')))
        self.music_label.setPixmap(QPixmap('img/music day.png'))
        self.movie = QMovie("img/gif2.gif")
        self.dayflag = 0
        #====== map ======
        self.mapSure.setStyleSheet(
             '''
                QPushButton{background-color:#CFE1F7;border-radius:10px;padding:2px 4px;text-color:#83bff3;}
                QPushButton:hover{background-color:#83bff3;}
            ''')
        self.mapcBox.setStyle(QStyleFactory.create('Fusion'))
        self.FontCbx.setStyle(QStyleFactory.create('Fusion'))
        self.FontSure.setStyleSheet(
             '''
                QPushButton{background-color:#CFE1F7;border-radius:10px;padding:2px 4px;text-color:#83bff3;}
                QPushButton:hover{background-color:#83bff3;}
            ''')
        self.colorCbx.setStyle(QStyleFactory.create('Fusion'))
        self.ColorSure.setStyleSheet(
             '''
                QPushButton{background-color:#CFE1F7;border-radius:10px;padding:2px 4px;text-color:#83bff3;}
                QPushButton:hover{background-color:#83bff3;}
            ''')
        self.fontSizeSld.setStyle(QStyleFactory.create('Fusion'))
        self.updatbt.setStyleSheet(
             '''
                QPushButton{background-color:#CFE1F7;border-radius:10px;padding:2px 4px;text-color:#83bff3;}
                QPushButton:hover{background-color:#83bff3;}
            ''')
        self.radioSld.hide()
        self.voiceTbn.hide()
        self.voiceSld.setStyle(QStyleFactory.create('Fusion'))
        # self.SetStackedWidget.setStyleSheet("background-color:#ffffff")
        op = QGraphicsOpacityEffect()  # 设置主界面的按钮 透明度
        op.setOpacity(0.51)
        self.setpic.setGraphicsEffect(op)
    # ================== 切换到对应的界面 ===================
    def slotBtnClicked(self):    # 6个大模块

        text = self.sender()
        text1 = text.text()
        self.labTitle.setText(text1)
        self.btnReturn.show()
        i = [u'相机校正', u'安全驾驶', u'行车记录', u'天气', u'音乐', u'设置'].index(text1)
        self.stackedWidget.setCurrentIndex(i + 1)
        if self.stackedWidget.currentIndex()==1:
            self.jiaozheng()

    def SetBtnClicked(self):     # 4个设置里的小模块
        text = self.sender()
        text1 = text.text()
        self.subtitle.setText(text1)
        self.setRe.show()
        i = [u'个性化设置', u'帮助中心',  u'更新',u'开发者信息'].index(text1) #u'个性化设置', u'帮助中心',  u'版本更新',u'开发者信息'
        self.SetStackedWidget.setCurrentIndex(i+1)


    def introBtnClicked(self):  # 应用介绍那里的模块
        text = self.sender()
        text1 = text.text()
        i = [u'功能介绍',u'应用介绍'].index(text1)
        self.helpStackedWidget.setCurrentIndex(i)

    # =========== 返回界面 =============
    def clickSetReturn(self):   # 返回帮助界面
        idx=self.SetStackedWidget.currentIndex()
        if idx != 0:
            self.subtitle.setText(' ')
            self.SetStackedWidget.setCurrentIndex(0)
            self.helpStackedWidget.setCurrentIndex(0)
            self.setRe.hide()


    def clickReturn(self):      # 返回主界面
        idx=self.stackedWidget.currentIndex()
        self.SetStackedWidget.setCurrentIndex(0)
        self.SetStackedWidget.setCurrentIndex(0)
        self.helpStackedWidget.setCurrentIndex(0)
        self.Timer1.stop()
        self.setRe.hide()
        self.subtitle.setText(' ')

        # print(self.camera.isOpened())
        try:
            if self.camera.isOpened()==True:
                self.camera.release()
        except Exception as  e:
            # self.DispLb.setText('e')
            pass

        if idx != 0:
                self.labTitle.setText('    司南驾驶系统')
                self.stackedWidget.setCurrentIndex(0)
                self.btnReturn.hide()

    # ========== 打开地图 功能 =============
    def openMap(self):
        self.mapLab=QWebEngineView()
        if self.mapcBox.currentText()=='百度地图':
            webbrowser.open('https://map.baidu.com/')
        elif self.mapcBox.currentText()=='高德地图':
            webbrowser.open('https://www.amap.com/')
        else:
            self.actionhint.setText('not open any website')

if __name__ == "__main__":  #""
    app = QApplication(argv)
    # app.setPalette(QPalette(QColor('#002060')))  # 背景颜色
    # app.setFont(QFont('宋体'))#Microsoft YaHei
    # app.set 就是设置全部的 最大 然后self.button/stackedwidget.set 就是有针对地设置
    # 然后把名字换成对应类的名称就好了 QLabel QStackedWidget这些 注意不要打错 打错了也不报错 不匹配也不报错"QToolButton{border-image: url(long.jpg)}"
    #app.setStyleSheet('''QPushButton:hover{background:white}''')
    win = MyMainWindow()
    win.setFixedSize(1000,800)
    win.show()
    exit(app.exec_())
