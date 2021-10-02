from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pydub import AudioSegment
from PIL import Image, ImageDraw
import numpy as np
import threading
from scipy.io.wavfile import read
from numpy import fft
import pygame, sys, time
import os



class Window(QtWidgets.QMainWindow):
    '''Initializarea ferestrei'''
    def __init__(self, title):
        super(Window, self).__init__()
        '''Initializarea ferestrei principale'''
        self.v_box = QtWidgets.QVBoxLayout()
        self.setGeometry(550, 230, 800, 600)
        self.setFixedSize(800,600)
        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon("app_icon.ico"))

        '''Initializarea meniului File -> Open'''
        openFile1 = QtWidgets.QAction("Open an audio file", self)
        openFile1.setShortcut("Ctrl+O")
        openFile1.setStatusTip("Open an audio file")
        openFile1.triggered.connect(self.open_dialog)

        '''Initializarea meniului de schimbare a temei'''
        self.themeBox = QtWidgets.QComboBox(self)
        self.themeBox.addItem("Default")
        self.themeBox.addItem("Gray")
        self.themeBox.addItem("Purple")
        self.themeBox.addItem("Blue")
        self.themeBox.move(550, 50)
        self.themeBox.activated[str].connect(self.theme_choice)

        '''Initializarea meniului de schimbare a animatiilor'''
        self.animationBox = QtWidgets.QComboBox(self)
        self.animationBox.addItem("Wave")
        self.animationBox.addItem("Mirrored waves")
        self.animationBox.addItem("Circle")
        self.animationBox.addItem("All effects")
        self.animationBox.move(680, 50)
        self.animationBox.activated[str].connect(self.animation_choice)
        self.animationBox.setCurrentIndex(3)

        '''Initializarea meniului de schimbare a melodiilor'''
        self.playlistBox = QtWidgets.QComboBox(self)
        self.playlistBox.move(420, 50)
        self.playlist = []
        self.playlistBox.activated[str].connect(self.song_choice)






        '''Initializarea meniului pentru deschis fisiere'''

        self.statusBar()

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu("&File")
        fileMenu.addAction(openFile1)


        self.home()
        pygame.init()




    '''In aceasta metoda se initializeaza elementele din fereastra: butonul, label-ul cu imagine si text'''

    def home(self):

        '''Initializarea variabilelor pentru animatii'''
        self.circleOn = True
        self.leftWaveOn = True
        self.rightWaveOn = True


        self.color1 = QColor(255, 255, 255)
        self.color2 = QColor(255, 255, 255)

        self.isPlaying = False
        self.firstPause = False

        self.playIcon = QIcon("play.png")
        self.pauseIcon = QIcon("pause.png")
        self.loadIcon = QIcon('loadIcon.png')


        #Initializarea textului "No audio loaded"

        self.defaultLabel = QtWidgets.QLabel('No audio loaded', self)
        self.defaultLabel.move(290,200)
        self.defaultLabel.setFixedSize(200,100)
        self.defaultFont = QtGui.QFont('Times', 14, QtCore.Qt.green)
        self.defaultLabel.setFont(self.defaultFont)


        #Initializarea imaginii care o sa contina forma de unda

        self.waveForm = QtWidgets.QLabel(self)
        self.waveForm.setFixedSize(700, 300)
        self.waveForm.move(50, 100)
        self.waveForm.raise_()

        #Initializarea formei de unda din partea de jos
        self.waveForm2 = QtWidgets.QLabel(self)
        self.waveForm2.setFixedSize(700, 300)
        self.waveForm2.move(50, 450)
        self.waveForm2.raise_()

        #Initializarea slider-ului de volum

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.slider.move(150, 320)
        self.slider.setFixedSize(100, 100)
        self.slider.setMinimum(1)
        self.slider.setMaximum(10)
        self.slider.setValue(5)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setVisible(False)
        self.slider.valueChanged.connect(self.change_volume)


        #Initializarea butonului de play/pauza

        self.playButton = QtWidgets.QPushButton(self)
        self.playButton.setIcon(self.playIcon)
        self.playButton.resize(self.playButton.minimumSizeHint())
        self.playButton.clicked.connect(self.start_audio)
        self.playButton.setVisible(False)
        self.playButton.move(50, 350)

        #Initializarea butonului de play/pauza de pe canalul secundar
        self.playButton2 = QtWidgets.QPushButton(self)
        self.playButton2.setIcon(self.playIcon)
        self.playButton2.resize(self.playButton2.minimumSizeHint())
        self.playButton2.clicked.connect(self.start_audio2)
        self.playButton2.setVisible(False)
        self.playButton2.move(50, 650)

        #Initializarea butonului de incarcat melodia de sus
        self.loadButton1 = QtWidgets.QPushButton(self)
        self.loadButton1.setIcon(self.loadIcon)
        self.loadButton1.resize(self.loadButton1.minimumSizeHint())
        self.loadButton1.clicked.connect(self.open_dialog)
        self.loadButton1.move(600, 250)
        self.loadButton1.setVisible(True)

        #Initializarea butonului de incarcat melodia de jos
        self.loadButton2 = QtWidgets.QPushButton(self)
        self.loadButton2.setIcon(self.loadIcon)
        self.loadButton2.resize(self.loadButton1.minimumSizeHint())
        self.loadButton2.clicked.connect(self.open_dialog2)
        self.loadButton2.move(600, 600)
        self.loadButton2.setVisible(True)



        #Initializarea textului care o sa indice numele melodiei curente

        self.nameLabel = QtWidgets.QLabel(self)
        self.nameLabel.move(50, 30)
        self.nameLabel.setFixedSize(200, 300)
        self.nameFont = QtGui.QFont('Times', 12, QtCore.Qt.green)
        self.nameLabel.setFont(self.nameFont)
        self.nameLabel.setVisible(True)
        self.smallFont = QtGui.QFont('Times', 8, QtCore.Qt.green)

        #Initializarea textului care o sa indice numele melodiei de jos
        self.nameLabel2 = QtWidgets.QLabel(self)
        self.nameLabel2.move(50, 500)
        self.nameLabel2.setFont(self.nameFont)
        self.nameLabel2.setVisible(False)


        '''Initializarea scrisului cu "Choose theme"'''
        self.themeLabel = QtWidgets.QLabel(self)
        self.themeLabel.move(550,20)
        self.themeLabel.setText("Choose theme")
        self.themeLabel.setFont(self.smallFont)

        '''Initializarea scrisului cu "Effects type"'''
        self.animationLabel = QtWidgets.QLabel(self)
        self.animationLabel.move(680, 20)
        self.animationLabel.setText("Effects type")
        self.animationLabel.setFont(self.smallFont)

        '''Initializarea scrisului cu Playlist'''
        self.playlistLabel = QtWidgets.QLabel(self)
        self.playlistLabel.move(420, 20)
        self.playlistLabel.setText("Song playlist")
        self.playlistLabel.setFont(self.smallFont)


        #self.setLayout(v_box)

        '''Initializarea temei ferestrei '''
        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
        self.p = QPalette()
        self.gradient = QLinearGradient(0, 0, 0, 400)
        self.gradient.setColorAt(0.0, self.color1)
        self.gradient.setColorAt(1.0, self.color2)
        self.p.setBrush(QPalette.Window, QBrush(self.gradient))
        self.setPalette(self.p)
        self.show()

    '''Functia cu care se alege un fisier audio din calculator'''

    def open_dialog(self):
        try:
            name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open an audio file')
            self.songName = name[0].split("/")
            self.songName = self.songName[-1]
            self.songName = (self.songName.lstrip()).rstrip()
            self.open_audio()
        except:
            pass

    '''Functia cu care se alege un fisier audio din calculator pentru wave form-ul din partea de jos'''
    def open_dialog2(self):
        try:
            name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open a secondary audio file')
            name = name[0].split("/")
            name = name[-1]
            name = (name.lstrip()).rstrip()
            self.open_audio2(name)
            print('Song 2 name:')
            print(name)
        except:
            pass



    #Functia care se apeleaza cand se deschide un fisier audio
    def open_audio(self):
        try:
            self.isPlaying = False
            self.firstPause = False
            self.playButton.setIcon(self.playIcon)
            print(self.songName)
            self.isPlaying = False
            self.firstPause = False
            if self.songName in self.playlist:
                pass
            else:
                self.playlist.append(self.songName)
                self.playlistBox.addItem(self.songName)

            self.generate_wave(self.songName)
        except:
            pass

    def open_audio2(self, name):
        try:
            src = name
            self.secondaryPlaying = False
            self.secondaryFirstPause = False
            self.audio2 = AudioSegment.from_file(src)
            data = np.fromstring(self.audio2._data, np.int16)
            fs = self.audio2.frame_rate
            self.secondarySound = pygame.mixer.Sound(name)

            self.channelTwo = pygame.mixer.Channel(1)

            if name in self.playlist:
                pass
            else:
                self.playlist.append(name)
                self.playlistBox.addItem(name)
        except:
            pass

        BARS = 100
        BAR_HEIGHT = 60
        LINE_WIDTH = 5

        length = len(data)
        RATIO = length / BARS

        count = 0
        maximum_item = 0
        max_array = []
        highest_line = 0

        for d in data:
            if count < RATIO:
                count = count + 1

                if abs(d) > maximum_item:
                    maximum_item = abs(d)
            else:
                max_array.append(maximum_item)

                if maximum_item > highest_line:
                    highest_line = maximum_item

                maximum_item = 0
                count = 1
        line_ratio = highest_line / BAR_HEIGHT
        im = Image.new('RGBA', (BARS * LINE_WIDTH, BAR_HEIGHT), (255, 255, 255, 1))
        draw = ImageDraw.Draw(im)

        current_x = 1
        for item in max_array:
            item_height = item / line_ratio

            current_y = (BAR_HEIGHT - item_height) / 2
            draw.line((current_x, current_y, current_x, current_y + item_height), fill=(255, 0, 0), width=2)

            current_x = current_x + LINE_WIDTH

        # Configurarea elementelor de interfata dupa ce se genereaza forma de unda

        self.waveForm2.setPixmap(im.toqpixmap())
        self.nameLabel2.setVisible(True)
        self.nameLabel2.setText(name)
        self.playButton2.setVisible(True)




    #Functia care genereaza forma de unda pe baza fisierului audio incarcat si o reprezinta sub forma de imagine


    def generate_wave(self, name):
        src = name
        self.audio = AudioSegment.from_file(src)
        self.t = threading.Thread(target=self.play_audio, name='Audio play thread')
        self.t.setDaemon(True)
        data = np.fromstring(self.audio._data, np.int16)
        fs = self.audio.frame_rate

        BARS = 100
        BAR_HEIGHT = 60
        LINE_WIDTH = 5

        length = len(data)
        RATIO = length / BARS

        count = 0
        maximum_item = 0
        max_array = []
        highest_line = 0

        for d in data:
            if count < RATIO:
                count = count + 1

                if abs(d) > maximum_item:
                    maximum_item = abs(d)
            else:
                max_array.append(maximum_item)

                if maximum_item > highest_line:
                    highest_line = maximum_item

                maximum_item = 0
                count = 1
        line_ratio = highest_line / BAR_HEIGHT
        im = Image.new('RGBA', (BARS * LINE_WIDTH, BAR_HEIGHT), (255, 255, 255, 1))
        draw = ImageDraw.Draw(im)

        current_x = 1
        for item in max_array:
            item_height = item / line_ratio

            current_y = (BAR_HEIGHT - item_height) / 2
            draw.line((current_x, current_y, current_x, current_y + item_height), fill=(0, 255, 0), width=2)

            current_x = current_x + LINE_WIDTH


        #Configurarea elementelor de interfata dupa ce se genereaza forma de unda

        self.waveForm.setPixmap(im.toqpixmap())
        self.defaultLabel.setVisible(False)
        self.playButton.setVisible(True)
        self.slider.setVisible(True)
        self.nameLabel.setVisible(True)
        self.nameLabel.setText(self.songName)
        self.visualizer()



    #Functia care porneste melodia

    def play_audio(self):
        pygame.mixer.music.play()

    #Functia care se apeleaza cand se incearca inchiderea aplicatiei
    def closeEvent(self, event):
        choice = QtWidgets.QMessageBox.question(self, 'Exiting', "Are you sure you want to exit?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            print('Exiting now')
            event.accept()
            sys.exit()
        else:
            event.ignore()

    #Functia care se apeleaza la apasarea butonului Play/Pause
    def start_audio(self):
            if self.isPlaying == False and self.firstPause == False:
                self.channelOne.play(self.mainSound)
                self.isPlaying = True
                self.playButton.setIcon(self.pauseIcon)
            elif self.isPlaying == True:
                self.channelOne.pause()
                self.firstPause = True
                self.playButton.setIcon(self.playIcon)
                self.isPlaying = False
            elif self.isPlaying == False and self.firstPause == True:
                self.channelOne.unpause()
                self.playButton.setIcon(self.pauseIcon)
                self.isPlaying = True

    #Functia care se apeleaza la apasarea butonului Play/Pause de jos
    def start_audio2(self):
        if self.secondaryPlaying == False and self.secondaryFirstPause == False:
            self.channelTwo.play(self.secondarySound)
            self.secondaryPlaying = True
            self.playButton2.setIcon(self.pauseIcon)
        elif self.secondaryPlaying == True:
            self.channelTwo.pause()
            self.secondaryFirstPause = True
            self.playButton2.setIcon(self.playIcon)
            self.secondaryPlaying = False
        elif self.secondaryPlaying == False and self.secondaryFirstPause == True:
            self.channelTwo.unpause()
            self.playButton2.setIcon(self.pauseIcon)
            self.secondaryPlaying = True



    #Functia care se apeleaza pentru comutarea volumului intre cele doua canale
    def change_volume(self):
        try:
            self.channelTwo.set_volume(1 - self.slider.value()/10)
            self.channelOne.set_volume(self.slider.value()/10)
        except:
            pass

    #Functia care genereaza animatiile sincronizate cu melodia

    def visualizer(self):
        # Dimensiunile ferestrei cu animatii
        width, height = 420, 360
        center = [int(width / 2), int(height / 2)]

        # Se citeste fisierul audio, apoi se citeste amplitudinea si frecventa, cu pasul determinat de frame_skip
        file_name = self.songName
        frame_rate, amplitude = read(file_name)
        frame_skip = 96
        amplitude = amplitude[:, 0] + amplitude[:, 1]
        amplitude = amplitude[::frame_skip]
        frequency = list(abs(fft.fft(amplitude)))

        # Amplitudinea este setata in functie de inaltimea ferestrei grafice
        max_amplitude = max(amplitude)
        for i in range(len(amplitude)):
            amplitude[i] = float(amplitude[i]) / max_amplitude * height / 4 + height / 2
        amplitude = [int(height / 2)] * width + list(amplitude)

        # Se seteaza pozitia de start a ferestrei si se initializeaza
        x = 1350
        y = 472
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)

        '''Initializarea mixerului audio'''
        self.firstPlay = True
        if (self.firstPlay == True):
            screen = pygame.display.set_mode([width, height])
            bg = pygame.image.load("background.jpg")
            #pygame.mixer.music.play()
        self.firstPlay = False
        now = time.time()

        #Initializare pygame mixer

        self.channelOne = pygame.mixer.Channel(0)
        self.mainSound = pygame.mixer.Sound(file_name)

        # Realizarea animatiilor
        for i in range(len(amplitude[width:])):

            screen.fill([0, 0, 0])
            screen.blit(bg, (0, 0))

            # Realizarea cercului de pe ecran, raza depinde de amplitudine iar culoarea acestuia de frecventa
            try:
                if self.circleOn == True:
                    pygame.draw.circle(screen,
                                       [(frequency[i] * 2) % 255, (frequency[i] * 3) % 255, (frequency[i] * 5) % 255],
                                       center, amplitude[i], 1)
            except ValueError:
                pass

            #   Se genereaza forma de unda corespunzatoare amplitudinii si este desenata de doua ori, in oglinda
            prev_x, prev_y = 0, amplitude[i]
            for x, y in enumerate(amplitude[i + 1:i + 1 + width][::5]):

                if self.leftWaveOn == True:
                    pygame.draw.line(screen, [0, 255, 0], [prev_x * 5, prev_y], [x * 5, y], 1)
                if self.rightWaveOn == True:
                    pygame.draw.line(screen, [0, 255, 0], [(prev_x * 5 - width / 2) * -1 + width / 2, prev_y],
                                 [(x * 5 - width / 2) * -1 + width / 2, y], 1)
                prev_x, prev_y = x, y
                pygame.event.poll()

            # Functia are asigura un anumit frame refresh rate pentru animatie
            while time.time() < now + 1.0000000000 / frame_rate * frame_skip:
                time.sleep(.00000000001)
            now = time.time()
            if self.isPlaying == True:
                pygame.display.flip()
            if i == len(amplitude)-width-1:
                self.open_dialog()


    '''Functia de schimbare a temei'''

    def theme_choice(self, text):
        if text == "Default":
            self.color1 = QColor(255, 255, 255)
            self.color2 = QColor(255, 255, 255)
        elif text == "Gray":
            self.color1 = QColor(128, 128, 128)
            self.color2 = QColor(64, 64, 64)
        elif text == "Purple":
            self.color1 = QColor(178, 102, 255)
            self.color2 = QColor(153, 51, 255)
        elif text == "Blue":
            self.color1 = QColor(102, 178, 255)
            self.color2 = QColor(51, 153, 255)
        self.gradient = QLinearGradient(0, 0, 0, 400)
        self.gradient.setColorAt(0.0, self.color1)
        self.gradient.setColorAt(1.0, self.color2)
        self.p.setBrush(QPalette.Window, QBrush(self.gradient))
        self.setPalette(self.p)

    '''Functia de schimbare a elementelor vizuale'''

    def animation_choice(self, text):
        if text == "Wave":
            self.circleOn = False
            self.leftWaveOn = True
            self.rightWaveOn = False
        elif text == "Mirrored waves":
            self.circleOn = False
            self.leftWaveOn = True
            self.rightWaveOn = True
        elif text == "Circle":
            self.circleOn = True
            self.leftWaveOn = False
            self.rightWaveOn = False
        elif text == "All effects":
            self.circleOn = True
            self.leftWaveOn = True
            self.rightWaveOn = True

    '''Functia de schimbare a melodiei print intermediul playlist-ului'''

    def song_choice(self, text):
        self.songName = text
        self.open_audio()





#Functia care se apeleaza cand porneste aplicatia si creaza un obiect de tip fereastra si unul de tip aplicatie


def run():
    app = QtWidgets.QApplication(sys.argv)
    GUI = Window('Audio mixer')
    GUI.setFixedSize(800,800)
    sys.exit(app.exec_())

'''Apelul metodei run(), care porneste aplicatia'''
run()

