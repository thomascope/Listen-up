# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 16:46:35 2014
Toolboxes
@author: Thomas
"""

import codecs
from psychopy.iohub import EventConstants, launchHubServer
from psychopy import visual, core, data, event, logging, sound, gui
from numpy import sin, cos, tan, log, log10, pi, average, sqrt, std, deg2rad, rad2deg, linspace, asarray
from numpy.random import random, randint, normal, shuffle
import numpy
import wx
import csv


class MyBetterDlg(gui.DlgFromDict):
    def addField(self, label='', initial='', color='', choices=None, tip=''):
        """
        Adds a (labelled) input field to the dialogue box, optional text color
        and tooltip. Returns a handle to the field (but not to the label).
        If choices is a list or tuple, it will create a dropdown selector.
        """
        self.inputFieldNames.append(label)
        if choices:
            self.inputFieldTypes.append(str)
        else:
            self.inputFieldTypes.append(type(initial))
        if type(initial)==numpy.ndarray:
            initial=initial.tolist() #convert numpy arrays to lists
        container=wx.GridSizer(cols=2, hgap=10)
        #create label
        #labelLength = wx.Size(200,25)#was 8*until v0.91.4
        labelLength = wx.Size(9*len(label)+16,25)#was 8*until v0.91.4
        inputLabel = wx.StaticText(self,-1,label,
                                        size=labelLength,
                                        style=wx.ALIGN_RIGHT)
        if len(color): inputLabel.SetForegroundColour(color)
        container.Add(inputLabel, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        #create input control
        if type(initial)==bool:
            inputBox = wx.CheckBox(self, -1)
            inputBox.SetValue(initial)
        elif not choices:
            inputLength = wx.Size(max(50, 5*len(unicode(initial))+16), 25)
            inputBox = wx.TextCtrl(self,-1,unicode(initial),size=inputLength)
        else:
            inputBox = wx.Choice(self, -1, choices=[unicode(option) for option in list(choices)])
            # Somewhat dirty hack that allows us to treat the choice just like
            # an input box when retrieving the data
            inputBox.GetValue = inputBox.GetStringSelection
            initial = choices.index(initial) if initial in choices else 0
            inputBox.SetSelection(initial)
        if len(color): inputBox.SetForegroundColour(color)
        if len(tip): inputBox.SetToolTip(wx.ToolTip(tip))

        container.Add(inputBox,1, wx.ALIGN_CENTER_VERTICAL)
        self.sizer.Add(container, 1, wx.ALIGN_CENTER)

        self.inputFields.append(inputBox)#store this to get data back on OK
        return inputBox

#a specific function for reading in a list of stumuli for the listen_up task
def readList_listen_up(path_List,startPoint,targetMorph):
    trialdata = csv.reader(open(path_List,'rb'))
    alldatalist = []    
    for row in trialdata:
        alldatalist += [row]
        #        print row
        
    # which tracks are there?
    allnumbers = []
    for count in range(len(alldatalist)):
        allnumbers += alldatalist[count][5]
    noTracks = set(allnumbers)
    
    #extract label for each track for later plotting
    alllabels = []    
    for count in range(len(alldatalist)):
        alllabels += [alldatalist[count][1]]
    trackLabels=set(alllabels)
    
    #%keep randomising whole list until there are not 5 stimuli from the same track in a row 
    suitableshuffle = 0
    maxnumberofiterations = 1000
    shufflekey = numpy.arange(0,len(alldatalist),1)    
#    print shufflekey # for debugging
    while suitableshuffle <1:
        for count in range(maxnumberofiterations):    
            shuffle(shufflekey)
            alldatalist = [alldatalist[numpy.asscalar(i)] for i in shufflekey]
#            print shufflekey   # for debugging         
#            print alldatalist
            allnumbers = []        
            for i in range(len(alldatalist)):
                allnumbers += alldatalist[i][5]
            
            def is_sublist(a,b):
                if a == []: return True
                if b == []: return False
                return b[:len(a)]==a or is_sublist(a,b[1:])
                
            onesequence = ['1','1','1','1','1']
            twosequence = ['2','2','2','2','2']
            if not is_sublist(onesequence,allnumbers) and not is_sublist(twosequence,allnumbers):
                suitableshuffle += 1
                break
            
            if count == maxnumberofiterations-1 and suitableshuffle == 0:
                    error ='after 1000 random iterations the stimulus list still did not meet criteria -> something went wrong'
                    print error
                    errorhandling(error,info['readList_listen_up'])
                    
        
    #make sure target appears at both buttons equal number of times
    orderz = numpy.tile(numpy.array([[1,2],[2,1]]),(len(alldatalist)/2,1))
    shuffle(orderz)
# above to replicate: app=repmat([[1 2],[2, 1],size(data{1},1)/2,1);    
#    %now randomise order of when target appears at position one and two
#    orderz=app(randperm(size(app,1)),:);
#    
#    %apply randomised order from above while loop to identify order of trials, images, tracktype
    target=[]
    list1=[]
    list2=[]
    images = []
    trialTrack=[]
    for count in range(len(alldatalist)):
        target += [alldatalist[count][1]]
        list1 += [alldatalist[count][2]]
        list2 += [alldatalist[count][3]]
        images += [alldatalist[count][9]]
        trialTrack += [alldatalist[count][5]]
    
    distractor_start=[]
    target_start=[]    
    for count in range(len(target)):
#       %define target sound using target morph paramter also helps to work
#       %out which end of the continua to select sound
        if target[count]==list1[count]:
            target[count] = [list1[count] + '.wav_' + list2[count] + '.wav_td_' + '%0.2f.wav' %(targetMorph)]                
        #       %define target starting point by using startpoint parameter
            target_start += [list1[count] + '.wav_' + list2[count] + '.wav_td_' + '%0.2f.wav' %(startPoint)]            
         #       %define distractor
            distractor_start +=[list1[count] + '.wav_' + list2[count] + '.wav_td_' + '%0.2f.wav' %(1-startPoint)]
        else:
            target[count] = [list1[count] + '.wav_' + list2[count] + '.wav_td_' + '%0.2f.wav' %(1-targetMorph)]                
        #       %define target starting point by using startpoint parameter
            target_start += [list1[count] + '.wav_' + list2[count] + '.wav_td_' + '%0.2f.wav' %(1-startPoint)]            
         #       %define distractor
            distractor_start +=[list1[count] + '.wav_' + list2[count] + '.wav_td_' + '%0.2f.wav' %(startPoint)]

    key =[]
    foil1 = []    
    foil2 = []
    for count in range(len(orderz)):
        if orderz[count][0] == 1:
            key += [1]
            foil1 += [target_start[count]]
            foil2 += [distractor_start[count]]
        else:
            key += [2]
            foil2 += [target_start[count]]
            foil1 += [distractor_start[count]]         
    
    #label sound folder to help find files later    
    soundFolder = []
    for count in range(len(list1)):
        soundFolder += [list1[count] + '_' + list2[count]]
        
    #print alldatalist
    #end the function by returning the specific listen up data
    return target,foil1,foil2,orderz,soundFolder,images,key,noTracks,trialTrack,trackLabels
    