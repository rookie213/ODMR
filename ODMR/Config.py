# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 10:55:22 2014

@author: jmcui
"""
import configparser
# Serial COM Configration

ShutterControllerCOM='com4'
PowerControllerCOM='com6'
DcVoltCOM='com8'

#SpinCore Pin Configuration

SpinCorePin={}
SpinCorePin["AOM730"]=1  #引脚1 
SpinCorePin["MW"]=2
SpinCorePin["CounterGate"]=3


SpinCoreInvertedPins=[] #低电平为开启的引脚
'''
Note! On/Off state of a pin  can't been directly map to High/Low Level of TTL,
there's a configuration in  SpinCoreInvertedPins. 
If the key is listed in SpinCoreInvertedPins, corresponding 'On'(True) state 
is Low Level. 
'''


#####Functions#####
##Generate control word from a dict
def SpinCoreGenWord(wordDict):
    '''
    Generate a spincore word from a human readable wordDict
    a wordDict is a dict as following:
    {
    'DetectAOM': False,
    'DetectEOM': On,
    .....
    }
    where the dict key is a pin defined in dict SpinCorePin
    You can put any number of elements in wordDict. Pins unlist in a wordDict will 
    take the default value: False, which means an OFF operation 
    '''
    word=0
    # print(wordDict)
    for key in wordDict:
        # print(key)
        if wordDict[key]:
            word+=1<<(SpinCorePin[key]-1)
    mask=0
    for key in SpinCoreInvertedPins:
        mask+=1<<(SpinCorePin[key]-1)
    # print(word)
    # print(mask)
    word=word^mask
    # print(word)
    return word
###

#File Operation

ConfigINI = configparser.ConfigParser()
ConfigINI.read('Config.ini')

def GetOption(section,key):
    global ConfigINI
    if ConfigINI.has_option(section,key):
        return ConfigINI.get(section,key)
    else:
        return None
        
def SaveOption(section,key,value):
    global ConfigINI
    if ConfigINI.has_section(section)==False:
        ConfigINI.add_section(section)
    ConfigINI.set(section,key,value)
    cfgfile=open('Config.ini','w')
    ConfigINI.write(cfgfile)
    cfgfile.close()
