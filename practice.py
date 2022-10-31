from dataclasses import replace
from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys, serial, time, datetime, keyboard
import numpy as np

REFRESH_TIME = 50 # ms
RMSSD_TIME = 10 # s
IN_KEY = 'left arrow'
OUT_KEY = 'right arrow'

# initialize serial
ser = serial.Serial('COM4', 9600, timeout=0.01)
ser.reset_input_buffer()

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)
        self.minutes = int(input("Practise duration (minutes)"))

        self.start_time = time.time()

        self.HR = []
        self.hr = 0
        self.HRV = []
        self.hrv = 0
        self.HRV_RMSSD = []
        self.hrv_rmssd = 0
        self.BREATH = []
        self.T = []

        self.last_interval = 0

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(0, 0, 0), width=1)
        self.graphWidget.plotItem.getAxis('bottom').setPen(pen)
        self.graphWidget.plotItem.getAxis('left').setPen(pen)

        pen = pg.mkPen(color=(255, 0, 0), width=1)
        self.data_line1 =  self.graphWidget.plot(self.T, self.HR, pen=pen, name='HR (BPM)')
        pen = pg.mkPen(color=(0, 0, 255), width=1)
        self.data_line2 =  self.graphWidget.plot(self.T, self.HRV_RMSSD, pen=pen, name='HRV (ms)')
        pen = pg.mkPen(color=(0, 255, 0), width=1)
        self.data_line3 =  self.graphWidget.plot(self.T, self.BREATH, pen=pen, name='BREATH')
        self.graphWidget.setXRange(0, self.minutes, padding=0)
        self.graphWidget.setYRange(0, 150, padding=0)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(REFRESH_TIME)
        self.timer.timeout.connect(self.update_data)
        self.timer.start()

    def update_data(self):
        t = time.time() - self.start_time
        if ser.in_waiting > 0:
            while ser.in_waiting > 0:
                interval = int(ser.readline())
                if interval < 600:
                    break
                self.hr = round((1000.0/interval)*60, 0)
                self.hrv = self.last_interval - interval
                self.last_interval = interval
                if t > RMSSD_TIME:
                    slc = np.argwhere(np.array(self.T) > (t - RMSSD_TIME))
                    self.hrv_rmssd = np.sqrt(np.mean(np.power(np.array(self.HRV)[slc], 2)))
                else:
                    self.hrv_rmssd = 0

        if keyboard.is_pressed(IN_KEY):
            breath = 1
        elif keyboard.is_pressed(OUT_KEY):
            breath = -1
        else:
            breath = 0

        self.BREATH.append(breath)
        self.HR.append(self.hr)
        self.HRV.append(self.hrv)
        self.HRV_RMSSD.append(self.hrv_rmssd)
        self.T.append(t)

        x = np.array(self.T)/60.0
        self.data_line1.setData(x, self.HR)
        self.data_line2.setData(x, self.HRV_RMSSD)
        self.data_line3.setData(x, np.array(self.BREATH)*15 + np.mean(self.HR))

        if t > self.minutes*60:
            fname = 'practices/{}min {}.txt'.format(self.minutes, datetime.datetime.now()).replace(':', '.')
            with open(fname, 'w') as f:
                f.write('time;hr;hrv;hrv_rmssd;breath\n')
                for i in range(len(self.T)):
                    f.write('{};{};{};{};{}\n'.format(self.T[i], self.HR[i], self.HRV[i], self.HRV_RMSSD[i], self.BREATH[i]))
            sys.exit(app.exec_())

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())