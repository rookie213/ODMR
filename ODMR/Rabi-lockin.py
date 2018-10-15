# -*- coding: utf-8 -*-
# @Author: Yanff
# @Date:   2018-09-21 11:11:07
# @Last Modified by:   Yanff
# @Last Modified time: 2018-09-24 10:31:08
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from pyqtgraph.dockarea import *
import OperationCode as OptC
import spinapi as spinpy
import unit
import Config,time
import ButtonStyle
import constant as spinconst
import visa,clr

#connect to the MW generator and SR830
clr.FindAssembly('mcl_gen64.dll')
from mcl_gen64 import *

gen = usb_gen()
SN = gen.Connect()
SN = gen.SetPowerON()



# if (SN == 1 or SN == 2):
#     print('generator worked well')
# else:
#     print('generator is disabled')
#     exit()


# rm = visa.ResourceManager()
# SR850 = rm.open_resource('GPIB0::8::INSTR')

#Define operating words for SpinCore

wordPumping=Config.SpinCoreGenWord({
    "AOM730":True,
    })
wordOperating=Config.SpinCoreGenWord({
    "MW"        :True
    
    })
wordIdle=Config.SpinCoreGenWord({
    "AOM730"     :False
    }) 


Pumping =   [wordPumping,OptC.CONTINUE,0,3*unit.us]
Operating=  [wordOperating,OptC.CONTINUE,0,1*unit.us]
Detecting=  [wordPumping,OptC.CONTINUE,0,3*unit.us]
Idle = [wordIdle,OptC.CONTINUE,0,1*unit.us]
Idle2 = [wordIdle,OptC.CONTINUE,0,0.2*unit.us]

Fill = [wordIdle,OptC.CONTINUE,0,1*unit.us]

TimeList=None


def Rabi(start,stop,N):
	global TimeList
	tempa=np.array(range(N))
	step=float(stop-start)/N
	TimeList=start+step*tempa
	InstListArray=[]
	
	for j in range(N):
		InstListArray.append([])
		t=TimeList[j]
		Operating[3]=t*unit.us  # Ramesy Time Change
        #InstListArray.append(Cooling)
		Fill[3]=(stop-t)*unit.us
		InstListArray[j].append(tuple(Pumping))
		InstListArray[j].append(tuple(Idle))
		InstListArray[j].append(tuple(Operating))# pi/2
		InstListArray[j].append(tuple(Fill))
        #InstListArray[0].append(tuple(Fill))
		InstListArray[j].append(tuple(Idle2))
		InstListArray[j].append(tuple(Detecting))
		InstListArray[j].append((wordIdle,OptC.BRANCH,0,0.01*unit.us)) #制造pump下调沿,实现计数采集,并开始下一序列循环
		
	return InstListArray 

def setSpincore(InstList):
	self.spinpy.pb_stop()
	self.spinpy.pb_start_programming(spinconst.PULSE_PROGRAM)
	for Inst in InstList:
		self.spinpy.pb_inst_pbonly(*Inst)
	self.spinpy.pb_stop_programming()
	spinpy.pb_start()




def startRabi(updatetime = 3000):
	global num,cyc,Intetime,start,end,pointN,data,AList
	OnTimeSettingChange()

	SN = gen.SetFreq(fre,0)   #set frequence
	SN = gen.SetPower(Power,0)
	# if (SN == 1 or SN == 2):
	# 	print('generator is woked well')
	# else:
	# 	print('generator is disable')
	# 	exit()

	Plotting.stop()
	spinpy.pb_init()
	spinpy.pb_set_clock(500.0 *unit.MHz)
	data = np.zeros(N,dtype = float)
	num = 0
	cyc = 0
	if BtnStart.isChecked():
		BtnStart.setStyleSheet(ButtonStyle.stylle_quit)
		AList=Rabi(start,end,pointN)

		setSpincore(AList[num])
		
		
		BtnStart.setText("Stop")
		Plotting.start(Intetime)
	else:
		BtnStart.setStyleSheet(ButtonStyle.style_button_highlight)
		BtnStart.setText("Start")
		num = 0
		cyc = 0
		spinpy.stop()


def update():
	global num,data,pointN,AList,TimeList

	if BtnStart.isChecked():
		Vol = num
		# Vol = float(SR850.query('OUTR? 1\n'))
		data[num] =data[num] + Vol
		curve.setData(y=data,x=TimeList)       
		w2.setXRange(TimeList[0], TimeList[-1])
		num = +1
		num = num %pointN
		setSpincore(AList[num])

	else: # 完成任务后Start按钮弹回
		curve.setData(y=data,x=TimeList)
		w2.setXRange(TimeList[0], TimeList[-1])
		BtnStart.setChecked(False)
		startRabi()   #Finish the Rabi task
		print('Finished a measurement')
		Plotting.stop() 

def SaveData():
	return 0

def OnTimeSettingChange():  #############Setting###########
	global Contime,Intetime,Power,fre,start,end,pointN,pump,detect
	#Cooling[3]=SpinBoxCooling.value()*unit.ms
	Contime = SpinBoxconstanttime.value()*unit.s
	Intetime = SpinBoxIntegraltime.value()*unit.s
	Power = SpinBoxMWpower.value()*unit.dBm
	fre = SpinBoxMWfre.value()*unit.MHz
	start = SpinBoxstarttime.value()*unit.us
	end = SpinBoxstoptime.value()*unit.us
	pointN = SpinBoxpointNum.value()
	pump = SpinBoxpumptime.value()*unit.us
	detect = SpinBoxdetecttime.value()*unit.us



#set GUI
app = QtGui.QApplication([])
win = QtGui.QMainWindow() 
area = DockArea()
win.setCentralWidget(area)
win.resize(800,500)
win.setWindowTitle('pyRabi')

## Create docks, place them into the window one at a time.
d1 = Dock("Setting", size=(200, 300))     ## give this dock the minimum possible size
d2 = Dock("Ploting", size=(500,300))
area.addDock(d1, 'left')      ## place d1 at left edge of dock area (it will fill the whole space since there are no other docks yet)
area.addDock(d2, 'right')     ## place d2 at right edge of dock area

w1 = pg.LayoutWidget()

Lockin_constanttime= QtGui.QLabel('time constant')
lockin_Integraltime= QtGui.QLabel('Integral time')

pumptime = QtGui.QLabel('pumping time')
detecttime = QtGui.QLabel('detect time')
start_time= QtGui.QLabel('start time')
stop_time= QtGui.QLabel('stop time')
pointNum= QtGui.QLabel('point number')

MWpower= QtGui.QLabel('MW Power')
MWfre= QtGui.QLabel('MW Frequence')

SpinBoxconstanttime = pg.SpinBox(value=3.0,suffix=' s',dec=True,
	step=1.0,minStep=0.1,bounds=[0.1, 100])
SpinBoxIntegraltime = pg.SpinBox(value=3.0,suffix=' s',dec=True,
	step=1.0,minStep=0.1,bounds=[0.1, 100])
SpinBoxpumptime = pg.SpinBox(value=3.0,suffix=' us',dec=True,
	step=1.0,minStep=0.01,bounds=[0.01, 1000])
SpinBoxdetecttime = pg.SpinBox(value=3.0,suffix=' us',dec=True,
	step=1.0,minStep=0.01,bounds=[0.01, 1000])
SpinBoxstarttime = pg.SpinBox(value=0.01,suffix=' us',dec=True,
	step=0.1,minStep=0.001,bounds=[0.01, 1000])
SpinBoxstoptime = pg.SpinBox(value=1.01,suffix=' us',dec=True,
	step=0.1,minStep=0.001,bounds=[0.01, 1000])
SpinBoxpointNum = pg.SpinBox(value=100,int=True,dec=True,
	step=1,minStep=1)
SpinBoxMWpower = pg.SpinBox(value=-30,suffix=' dBm',dec=True,
	step=0.1,minStep=0.001,bounds=[-60, 0])
SpinBoxMWfre = pg.SpinBox(value=1374.5,suffix=' MHz',dec=True,decimals=5,
	step=0.1,minStep=0.001,bounds=[1, 3000])


BtnSave = QtGui.QPushButton('Save')
BtnStart = QtGui.QPushButton('Start')
BtnStart.setCheckable(True)
BtnStart.setChecked(False)
BtnStart.setStyleSheet(ButtonStyle.style_button_highlight)
BtnStart.setMinimumSize(QtCore.QSize(0, 30))

labelSpace1=QtGui.QLabel('Lock-in setup')
irow=0
w1.addWidget(labelSpace1, row=irow, col=0)
irow+=1
w1.addWidget(Lockin_constanttime, row=irow, col=0)
w1.addWidget(SpinBoxconstanttime, row=irow, col=1)
irow+=1
w1.addWidget(lockin_Integraltime, row=irow, col=0)
w1.addWidget(SpinBoxIntegraltime, row=irow, col=1)

labelSpace2=QtGui.QLabel('Rabi constant')
irow+=2
w1.addWidget(labelSpace2, row=irow, col=0)

irow+=1
w1.addWidget(pumptime, row=irow, col=0)
w1.addWidget(SpinBoxpumptime, row=irow, col=1)
irow+=1
w1.addWidget(detecttime, row=irow, col=0)
w1.addWidget(SpinBoxdetecttime, row=irow, col=1)
irow+=1
w1.addWidget(start_time, row=irow, col=0)
w1.addWidget(SpinBoxstarttime, row=irow, col=1)
irow+=1
w1.addWidget(stop_time, row=irow, col=0)
w1.addWidget(SpinBoxstoptime, row=irow, col=1)
irow+=1
w1.addWidget(pointNum, row=irow, col=0)
w1.addWidget(SpinBoxpointNum, row=irow, col=1)

labelSpace2=QtGui.QLabel('MW constant')
irow+=2
w1.addWidget(labelSpace2, row=irow, col=0)

irow+=1
w1.addWidget(MWfre, row=irow, col=0)
w1.addWidget(SpinBoxMWfre, row=irow, col=1)
irow+=1
w1.addWidget(MWpower, row=irow, col=0)
w1.addWidget(SpinBoxMWpower, row=irow, col=1)


labelSpace2=QtGui.QLabel('')
irow+=2
w1.addWidget(labelSpace2, row=irow, col=0)
irow+=1
w1.addWidget(BtnStart, row=irow, col=0)
w1.addWidget(BtnSave, row=irow, col=1)

d1.addWidget(w1)
BtnSave.clicked.connect(SaveData)
BtnStart.clicked.connect(startRabi)






##Plot window
w2 = pg.PlotWidget(title="Ploting")
curve = w2.plot(pen='y')
w2.setLabel('left', 'Vol', units='mV')
w2.setLabel('bottom', 'Frequence', units='MHz')
d2.addWidget(w2)
Plotting = QtCore.QTimer()
Plotting.timeout.connect(update)

if __name__=="__main__": 
    win.show()
    app.exec_()
    print("Exit")

# Inst = Rabi(1,11,10)
# print(Inst[0])