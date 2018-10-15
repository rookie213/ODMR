# -*- coding: utf-8 -*-
# @Author: Yanff
# @Date:   2018-08-24 10:26:59
# @Last Modified by:   Yanff
# @Last Modified time: 2018-08-31 13:13:43

import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg 
from pyqtgraph.dockarea import *
import ButtonStyle
import unit,time
# import sys
# import warnings
# warnings.simplefilter("ignore", UserWarning)
# sys.coinit_flags = 2
import clr,visa

clr.FindAssembly('mcl_gen64.dll')
from mcl_gen64 import *


gen = usb_gen()
SN = gen.Connect()
    
if (SN == 1 or SN == 2):
    print('generator worked well')
else:
    print('generator is disabled')
    exit()
SN = gen.SetPowerON()
if (SN == 1 or SN == 2):
    print('generator is power on')
else:
    print('generator is power off')
    exit()
rm = visa.ResourceManager()
SR850 = rm.open_resource('GPIB0::8::INSTR')

#set GUI
app = QtGui.QApplication([])
# print(1)
win = QtGui.QMainWindow() 

area = DockArea()
win.setCentralWidget(area)
win.resize(800,500)
win.setWindowTitle('PyODMR')
## Create docks, place them into the window one at a time.
d1 = Dock("Setting", size=(150, 300))     ## give this dock the minimum possible size
d2 = Dock("Ploting", size=(500,300))
area.addDock(d1, 'left')      ## place d1 at left edge of dock area (it will fill the whole space since there are no other docks yet)
area.addDock(d2, 'right')     ## place d2 at right edge of dock area

w1 = pg.LayoutWidget()

Lockin_constanttime= QtGui.QLabel('time constant')
lockin_Integraltime= QtGui.QLabel('Integral time')
MWstartfr= QtGui.QLabel('start frequence')
MWendfr= QtGui.QLabel('end frequence')
MWstep= QtGui.QLabel('step')
MWpower= QtGui.QLabel('Power')



SpinBoxconstanttime = pg.SpinBox(value=3.0, suffix=' ms', 
                                 dec=True, 
                                 step=1.0, minStep=0.01, 
                                 bounds=[0.01, 1000])
SpinBoxIntegraltime = pg.SpinBox(value=3.0, suffix=' s', 
                                 dec=True, 
                                 step=1.0, minStep=0.01, 
                                 bounds=[0.01, 1000])
SpinBoxstartfr = pg.SpinBox(value=1000.0, suffix=' MHz', 
                                 dec=True, 
                                 step=1.0, minStep=0.01, 
                                 bounds=[0.01, 3000])
SpinBoxendfr = pg.SpinBox(value=1600.0, suffix=' MHz', 
                                 dec=True, 
                                 step=1.0, minStep=0.01, 
                                 bounds=[0.01, 3000])
SpinBoxstep = pg.SpinBox(value=1.0, suffix=' MHz', 
                                 dec=True, 
                                 step=1.0, minStep=0.01, 
                                 bounds=[0.01, 100])
SpinBoxpower = pg.SpinBox(value= -20.0, suffix=' dBm', 
                                 dec=True, 
                                 step=1.0, minStep=0.01, 
                                 bounds=[-30, 10])


BtnSave = QtGui.QPushButton('Save')
BtnStart = QtGui.QPushButton('Start')
BtnStart.setCheckable(True)
BtnStart.setChecked(False)
BtnStart.setStyleSheet(ButtonStyle.style_button_highlight)
BtnStart.setMinimumSize(QtCore.QSize(0, 30))

labelSpace1=QtGui.QLabel('Lock-in setup')
irow=2
w1.addWidget(labelSpace1, row=irow, col=0)
irow+=1
w1.addWidget(Lockin_constanttime, row=irow, col=0)
w1.addWidget(SpinBoxconstanttime, row=irow, col=1)
irow+=1
w1.addWidget(lockin_Integraltime, row=irow, col=0)
w1.addWidget(SpinBoxIntegraltime, row=irow, col=1)
labelSpace2=QtGui.QLabel('MW generator setup')
irow+=2
w1.addWidget(labelSpace2, row=irow, col=0)
irow+=1
w1.addWidget(MWstartfr, row=irow, col=0)
w1.addWidget(SpinBoxstartfr, row=irow, col=1)
irow+=1
w1.addWidget(MWendfr, row=irow, col=0)
w1.addWidget(SpinBoxendfr, row=irow, col=1)
irow+=1
w1.addWidget(MWstep, row=irow, col=0)
w1.addWidget(SpinBoxstep, row=irow, col=1)
irow+=1
w1.addWidget(MWpower, row=irow, col=0)
w1.addWidget(SpinBoxpower, row=irow, col=1)
labelSpace3=QtGui.QLabel('')
irow+=2
w1.addWidget(labelSpace3, row=irow, col=0)
irow+=1
w1.addWidget(BtnStart, row=irow, col=0)
w1.addWidget(BtnSave, row=irow, col=1)

d1.addWidget(w1)


def ODMR(start,stop,step):
    global Frelist,data
    N = int((stop - start)//step)
    tempa = np.array(range(N+1))
    Frelist = start + step*tempa
    data=np.zeros(len(Frelist),dtype = float)
    return Frelist


def SaveData():
    global BtnSave,data,Frelist
    fileFormat='dat'
    filetime=time.strftime("%Y-%m-%d",time.localtime())
    initialPath = QtCore.QDir.currentPath() +'/ODMR_' + filetime+'.'+fileFormat
    fileName = QtGui.QFileDialog.getSaveFileName(BtnSave, "Save As",
                                                 initialPath, 
                                                 "%s Files (*.%s);;All Files (*)" % (fileFormat.upper(), fileFormat))
    if fileName:
        with open(fileName, 'w') as myFile:
            #myFile.write('# CoolingTime:%f ms\n'%SpinBoxCooling.value())
            myFile.write('# PumpingTime:%f us\n'%SpinBoxPumping.value())
            myFile.write('# MW length:%f us\n'%SpinBoxOperate.value())
            myFile.write('# CountTime:%f ms\n'%SpinBoxDetect.value())
            myFile.write('# Cycles:%d \n' %Operator.RepeatedCycles)
            myFile.write('time,counts \n')
            Data=data
            index=np.array(range(0,len(Data),1))
            Y=Data[index]
            # Ref=Data[index+1]
            # RelY=Y-Ref
            for t,y in zip(Frelist,Y):
                myFile.write('%f, %ld \n' % (t,y))

# def Data(fre = 1000,power = -20,constanttime = 3):
#     SN = gen.SetPower(power)
#     if SN == 1 or 2:
#         print('Power is %f dbm' % power)
#     else:
#         print('Power setting is disabled')
#     SN = gen.SetFreq(fre)
    
#     if SN == 1 or 2:
#         print('Fre is %f MHz' % fre)
#     else:
#         print('Fre setting is disabled')
#         exit()

#     time.sleep(constanttime)
#     Vol = SR850.query('OUTR? 1\n')

#     return Vol







def StartODMR(updatetime=1000): # default plotting udate time is 1.0 second
    global Intetime,startfre,endfre,step,Power,i

    Plotting.stop()
    # gen = usb_gen()
    # SN = gen.Connect()

    OnTimeSettingChange()
    if BtnStart.isChecked():
        BtnStart.setStyleSheet(ButtonStyle.stylle_quit)
        AList=ODMR(startfre,endfre,step)

        SN = gen.SetPower(Power,0)    #set power
        if SN[0] == 1 or 2:
            print('Power is %f dbm' % Power)
        else:
            print('Power setting is disabled')
            exit()

        SN = gen.SetFreq(AList[i],0)   #set first frequence
        if (SN[0] == 1 or  2):
            print('Frequence is %f MHz' % Frelist[i])
        else:
            print('generator is disable')
            exit()





        # print(Contime)
        BtnStart.setText("Stop")
        Plotting.start(Intetime)
    else:
        BtnStart.setStyleSheet(ButtonStyle.style_button_highlight)
        # Operator.stop()
        BtnStart.setText("Start")
 


BtnSave.clicked.connect(SaveData)
BtnStart.clicked.connect(StartODMR)
##Plot window
w2 = pg.PlotWidget(title="Ploting")
curve = w2.plot(pen='y')
w2.setLabel('left', 'Vol', units='mV')
w2.setLabel('bottom', 'Frequence', units='MHz')
d2.addWidget(w2)



#==============================================================================
def update():
    global curve,BtnStart,w2,data,i,Frelist



    if BtnStart.isChecked():

        Vol =  float(SR850.query('OUTR? 1\n'))
        # print(Vol)
        # print(i)
        # print(data[i]+Vol)

        data[i] =data[i] + Vol
        # SN = gen.SetFreq(AList[i])   #set  frequence

        # print('1---',time.localtime(time.time()))
        curve.setData(y=data,x=Frelist)       
        w2.setXRange(Frelist[0], Frelist[-1])

        i+=1
        i=i%len(Frelist)
        SN = gen.SetFreq(Frelist[i],0)   #set  frequence
        if (SN[0] == 1 or 2):
            print('Frequence is %f MHz' % Frelist[i])
        else:
            print('generator is disabled')
            exit()
        # print(Frelist[i])
        # print('2---',time.localtime(time.time()))
        # print(Frelist)
        # print(i)       


        # strCycles="Cyecles:%d"%Operator.RepeatedCycles
        # labelSpace2.setText(strCycles)
    else: # 完成任务后Start按钮弹回
        curve.setData(y=Data,x=Frelist)
        w2.setXRange(Frelist[0], Frelist[-1])
        BtnStart.setChecked(False)
        StartODMR()   #Finish the Rabi task
        print('Finished a measurement')
        Data.finished=False  #Prepare for next task
        Plotting.stop()  
   

def OnTimeSettingChange():  #############Setting###########
    global Contime,Intetime,Power,startfre,endfre,step
    #Cooling[3]=SpinBoxCooling.value()*unit.ms
    startfre = SpinBoxstartfr.value()*unit.MHz
    endfre = SpinBoxendfr.value()*unit.MHz
    step = SpinBoxstep.value()*unit.MHz

    Contime = SpinBoxconstanttime.value()*unit.ms
    Intetime = SpinBoxIntegraltime.value()*unit.s

    Power=SpinBoxpower.value()*unit.dBm


Plotting = QtCore.QTimer()
Plotting.timeout.connect(update)

i=0


if __name__=="__main__": 
    win.show()
    app.exec_()
    print("Exit")


