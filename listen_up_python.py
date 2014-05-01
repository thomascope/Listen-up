# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 14:34:45 2014

@author: Thomas Cope

listen_up_task reimplemented in Python from Matlab

Required modules: Numpy, psychopy
"""

import codecs
from psychopy.iohub import EventConstants, launchHubServer
from psychopy import visual, core, data, event, logging, sound, gui
from numpy import sin, cos, tan, log, log10, pi, average, sqrt, std, deg2rad, rad2deg, linspace, asarray
from numpy.random import random, randint, normal, shuffle
import numpy
import wx
import time
import csv
from tec_toolboxes import MyBetterDlg, readList_listen_up
from cleanuptools import errorhandling
#import os



#set experiment parameters
info = {} #a dictionary of experiment parameters
info['ParticipantName'] = ''
info['RespMethod'] = ['Keyboard', 'Mouse', 'USBBox']
info['Faces'] = ['Aliens']
info['Fullscreen'] = ['False','True']
info['HorizResolution'] = 800
info['VertResolution'] = 700
info['StepSize'] = 0.16
info['StartPoint']= 0.00
info['Levitt'] = ['1, 3']
info['ScaleFactor']=1/sqrt(2)
info['TargetMorph']=0.00
info['Stopping']=8
info['StablePoint']=4
info['MinStep']=0.04
info['Ignore']=2
info['StudyTemplate']=['child_lexicality']
info['TargetType']=['ListenAndSee']
#info['Participant'] = ''
#info['Participant'] = ''
#present dialog to collect info
dlg = MyBetterDlg(info, order=['ParticipantName','RespMethod','Faces','StudyTemplate','StepSize','StartPoint','ScaleFactor'])
if dlg.OK == False: core.quit() #User pressed cancel in the GUI
info['NameOfStudy'] = 'listen_up_Python'

#print(info['ParticipantName'])
#print(len(info['ParticipantName']))
#print(info['RespMethod'])

if len(info['ParticipantName']) < 1:
    error = "you didn't specify a participant name!"
    print error
    errorhandling(error,info['NameOfStudy'])
    
if info['StartPoint'] > 0.49:
    error = 'start point is described from the 0 end of the continua'
    print error
    errorhandling(error,info['NameOfStudy'])
    
if info['Stopping'] < info['StablePoint']:
    error ='stable has to be less than or equal to the stopping criterion'
    print error
    errorhandling(error,info['NameOfStudy'])
    
#tell Python where to look for everything
path_List = 'Lists\%s.csv' %(info['StudyTemplate'])
path_Sounds = 'sounds\%s' %(info['StudyTemplate'])

#Create a CSV file in which to store participant responses
StartTime = time.strftime("%H_%M_%S")
StartDate = time.strftime("%d_%b_%Y")
OutFile = 'results\long_' + info['TargetType'] + '_' + info['ParticipantName'] + '_' + StartTime + '_' + StartDate + '.csv'
OutFileSum = 'results\short_' + info['TargetType'] + '_' + info['ParticipantName'] + '_' + StartTime + '_' + StartDate + '.csv'

#Setup writing objects
writer = csv.writer(open(OutFile, 'wb'))
writerSum = csv.writer(open(OutFileSum, 'wb'))

writer.writerow(['trial','target','foil1','foil2','answer','response','track','correct?','trackPosition','turnAbout','trackPositionDiff','currentStepSize','countTrack','change','time m','expt'])
writerSum.writerow(['experiment','participantCode','levitt','startPoint','stepSize','ScaleFactor','minLevel','FreeTrials','StoppingCriterion','stablePoint','TargetMorph'])
writerSum.writerow([info['StudyTemplate'],info['ParticipantName'],info['Levitt'],info['StartPoint'],info['StepSize'],info['ScaleFactor'],info['MinStep'],info['Ignore'],info['Stopping'],info['StablePoint'],info['TargetMorph']])

target=[];
foil1=[];
foil2=[];
order = numpy.zeros((0,2))
soundFolder=[];
images=[];
key=[];
trialTrack=[];

#The task has a variable length dependent on how participant does
#to stop running out of trials this is a temporary measure so that the list
#is randomised and addended eight times
#for the real version there should be enough trials as a buffer
for count in range(8):
    #this is the function that reads in from a .csv file the trial
    #structure - i.e. what is a target, what are the distractors, which
    #tracks they belong to
    target_it,foil1_it,foil2_it,order_it,soundFolder_it,images_it,key_it,noTracks,trialTrack_it,trackLabel=readList_listen_up(path_List,info['StartPoint'],info['TargetMorph']);
    
    target += target_it
    foil1 += foil1_it
    foil2 += foil2_it
    order = numpy.append(order,order_it,0)
    soundFolder += soundFolder_it
    images += images_it
    key += key_it
    trialTrack += trialTrack_it
    
# print noTracks # for debug

#%intiates empty parameters for later use for each track
trackItemNo = []
stepSize = []
errorz = []
change = []
turnAbout = []
correctTrack = []
noAllTurns = []
con_correct = []
con_incorrect = []
minStepReached = []
foil_adj_value=[]
counterAtBoundary = []
free_trials = []
for count in range(len(noTracks)):
    #%modulates difficulty of each trial based on adaptive track
    #%trackStep(i)=0;
    
    trackItemNo+=[0]
    
    #%step size reduces as experiment goes on - i.e. the size of change in
    #%difficulty is modulated during course of experiment
    stepSize += [info['StepSize']]
    
    errorz += [0];
    #%important variable for deciding when there is a change in direction of
    #%the track - starts with down i.e. assumes subject got the last response
    #%correct
    change += ['down']
    
    #%tracks
    turnAbout += [0]
    
    #%how many did they get right
    correctTrack += [0]
    
    noAllTurns += [0]
    
    #%a way to understand when to change difficulty - if there are three
    #%consecutive correct response make it harder, if they make one error make
    #%it easier
    con_correct += [0]
    con_incorrect += [0] 
    minStepReached += [0]
    
    foil_adj_value += [info['StartPoint']]
    
    counterAtBoundary += [0]
    free_trials += [info['Ignore']]

trackItemNo = [trackItemNo]
stepSize = [stepSize]
errorz = [errorz]
change = [change]
turnAbout = [turnAbout]
correctTrack = [correctTrack]
noAllTurns = [noAllTurns]
con_correct = [con_correct]
con_incorrect = [con_incorrect]
minStepReached = [minStepReached]
foil_adj_value=[foil_adj_value]
counterAtBoundary = [counterAtBoundary]
free_trials = [free_trials]

 #Create a window to draw in:
myWin = visual.Window([info['HorizResolution'], info['VertResolution']], allowGUI=False, color=(-1,-1,-1), monitor='testMonitor', units='pix', fullscr=(info['Fullscreen']==True))
##for debug only
#fixation = visual.Circle(myWin, size = 25, lineColor = 'DarkOrchid', fillColor = 'Fuchsia', lineWidth = 3.0)
#fixation.draw()
#myWin.flip()
#core.wait(5))

# Preload faces for presentation:
pictureVertPosition = info['VertResolution']/6
pictureHorizPosition = 0
facesVertPosition = -info['VertResolution']/4.5
leftFaceHorizPosition = -info['HorizResolution']/4.5
rightFaceHorizPosition = info['HorizResolution']/4.5


leftFaceClosed=visual.ImageStim(myWin,image='faces\%s' %(info['Faces']) + '\Closed.jpg', mask=None,pos=(leftFaceHorizPosition,facesVertPosition),size=(177.0,177.0))
rightFaceClosed=visual.ImageStim(myWin,image='faces\%s' %(info['Faces']) + '\Closed.jpg', mask=None,pos=(rightFaceHorizPosition,facesVertPosition),size=(177.0,177.0))
######## I am up to here!        

faceOpen=imread([pwd,'\faces\',faces,'\Open.jpg']);
faceCorrect=imread([pwd,'\faces\',faces,'\Smile.jpg']);
faceIncorrect=imread([pwd,'\faces\',faces,'\Frown.jpg']);

#%set up while loop and intialise trial counter
x=-1;
trial=0;

#setup timing
respClock = core.Clock()
expClock = core.Clock()

while x < 0:
    #%count for trials in while loop
    trial=trial+1
    
    #%check whether converged on this track; if you have ignore this trial
    if noAllTurns[-1][int(trialTrack[trial])-1] < info['Stopping']:
        
        #%keep track of how many of each track type have happened
        trackItemNo[-1][int(trialTrack[trial])-1]+=1
        
        # %adjust difficulty - foil_adj_value subsitituted in
        if float(foil1[trial][-8:-4]) > float(foil2[trial][-8:-4])
            foil1_t = foil1[trial][:-8] + '%0.2f' %(1-foil_adj_value[-1][int(trialTrack[trial])-1]) + foil1[trial][-4:]  
            foil2_t = foil2[trial][:-8] + '%0.2f' %(foil_adj_value[-1][int(trialTrack[trial])-1]) + foil2[trial][-4:]  
        else:
            foil1_t = foil1[trial][:-8] + '%0.2f' %(foil_adj_value[-1][int(trialTrack[trial])-1]) + foil1[trial][-4:]  
            foil2_t = foil2[trial][:-8] + '%0.2f' %(1-foil_adj_value[-1][int(trialTrack[trial])-1]) + foil2[trial][-4:]  
        
        ## IF WE WANT TO INTRODUCE CUES OTHER THAN IMAGES,THIS WOULD BE THE PLACE TO DO IT
        targetImage=visual.ImageStim(myWin,image='images\%s' %(info['StudyTemplate']) + '\%s.jpg' %(images[trial-1]),mask=None,pos=(0.0,pictureVertPosition),size=(250.0,250.0))

#        
#        #%faces data for presentation on each trial for corrective feedback and to
#        #%animate speaking
#        faceClosed=imread([pwd,'\faces\',faces,'\Closed.jpg']);
#        faceOpen=imread([pwd,'\faces\',faces,'\Open.jpg']);
#        faceCorrect=imread([pwd,'\faces\',faces,'\Smile.jpg']);
#        faceIncorrect=imread([pwd,'\faces\',faces,'\Frown.jpg']);
#        %
#        
#        trial_trialTrack=trialTrack(trial);
#        %make note of the level of difficulty of each trial
#        track_position{trialTrack(trial)}(trackItemNo(:,trialTrack(trial)))=1-foil_adj_value(trialTrack(trial));
#        track_position_diff{trialTrack(trial)}(trackItemNo(:,trialTrack(trial)))=abs((1-foil_adj_value(trialTrack(trial)))-foil_adj_value(trialTrack(trial)));
#        
#      
#        %trial information presented as a gui
#        [response(trial),planetz,spaceStarCount]=trialByTrial(target{trial},foil1_t,foil2_t,...
#            soundFolder{trial},NameOfStudy,images,targetImage,faceClosed,faceOpen,...
#            trial_trialTrack,trial,size(target,1),correctTrack,key(trial),faceCorrect,faceIncorrect,planetz,spaceStar,spaceStarCount,debugz,stepSize,TargetType,ResponseMethod);
#        
#        %decide whether the response was correct or not
#        if response(trial) == key(trial)
#            correctTrack(trial,trialTrack(trial))=1;
#            errorz_record{trialTrack(trial)}(trackItemNo(:,trialTrack(trial)))=0;
#        else
#            correctTrack(trial,trialTrack(trial))=0;
#            
#            %record first error when it occurs
#            errorz(:,trialTrack(trial))=errorz(:,trialTrack(trial))+1;
#            
#            errorz_record{trialTrack(trial)}(trackItemNo(:,trialTrack(trial)))=1;
#        end
#        
#        
#        
#        %if trial was correct evaluate whether a certain number have been correct
#        %or incorrect in a row and adjust accordingly
#        
#        %if statement 1 - is trial correct or not
#        if  correctTrack(trial,trialTrack(trial))
#            
#            %if statement 2
#            %if first error has already occured provide opportunity to reduce
#            %step size
#            if (trackItemNo(:,trialTrack(trial)) > free_trials(:,trialTrack(trial))) || (errorz(:,trialTrack(trial)) > 0);
#                
#                %keep score
#                con_correct(:,trial_trialTrack)=con_correct(:,trial_trialTrack)+1;
#                
#                %if statement 3
#                %does it meet Levitt criterion for a change but is not
#                %a change in direction i.e. 'down' and 'down'
#                if con_correct(:,trial_trialTrack) >= Levitt(:,2) && strcmp(change{trial_trialTrack},'down');%1 something that indicates change is true
#                    
#                    %record not a turning point
#                    turnAbout{trialTrack(trial)}(trackItemNo(:,trialTrack(trial)))=0;
#                    
#                    %safety - make sure stepsize is not less then
#                    %minimium allowed
#                    if stepSize(:,trial_trialTrack) < min_level
#                        stepSize(:,trial_trialTrack)=min_level;
#                    end
#                    
#                    %this is what keeps track of which trial to
#                    %play next
#                    foil_adj_value(:,trial_trialTrack)=foil_adj_value(:,trial_trialTrack)+stepSize(:,trial_trialTrack);
#                    
#                    
#                    %stop from crossing over and ping it up if
#                    %three consecutive at lowest level i.e. 48 and
#                    %52
#                    if foil_adj_value(:,trial_trialTrack) > 0.479
#                        foil_adj_value(:,trial_trialTrack)=0.48;
#                        
#                        counterAtBoundary(:,trial_trialTrack)=counterAtBoundary(:,trial_trialTrack)+1;
#                        
#                        
#                        %if three correct in a row at 0.48
#                        if  counterAtBoundary(:,trial_trialTrack) >= 4
#                            
#                            %reduce stepsize as if it was an
#                            %error turning point
#                            stepSize(:,trial_trialTrack)=str2num(sprintf('%.2f',stepSize(:,trial_trialTrack)*scale_factor));
#                            
#                            %fix it to make sure that the step size doesn't get
#                            %smaller than the minimum level
#                            if stepSize(:,trial_trialTrack) <= min_level
#                                %adjust track step size
#                                stepSize(:,trial_trialTrack)=min_level;
#                                
#                                %record the fact that it is at minimum
#                                minStepReached(trackItemNo(:,trialTrack(trial)),trial_trialTrack)=1;
#                            end
#                            
#                            foil_adj_value(:,trial_trialTrack)=0.48-stepSize(:,trial_trialTrack);
#                            %reset counter
#                            counterAtBoundary(:,trial_trialTrack)=0;
#                            turnAbout{trialTrack(trial)}(trackItemNo(:,trialTrack(trial)))=1;
#                            
#                            %make sure recording this is an
#                            %error - so a consecutive error does
#                            %not become a turning point
#                            change{trial_trialTrack}='up';
#                            
#                        end
#                        
#                    end
#                    
#                    %reset counter
#                    con_correct(:,trial_trialTrack)=0;
#                    con_incorrect(:,trial_trialTrack)=0;
#                    
#                    
#                    %else if for statement 3
#                    %does it meet levitt and also represent a change in
#                    %direction
#                elseif con_correct(:,trial_trialTrack) >= Levitt(:,2) && strcmp(change{trial_trialTrack},'up');
#                    
#                    %record the fact that this was a change in direction
#                    turnAbout{trialTrack(trial)}(trackItemNo(:,trialTrack(trial)))=1;
#                    
#                    %note change in direction
#                    change{trial_trialTrack}='down';
#                    
#                    %reduce step size by scaled factor because it was a
#                    %change in direction
#                    stepSize(:,trial_trialTrack)=str2num(sprintf('%.2f',stepSize(:,trial_trialTrack)*scale_factor));
#                    
#                    %fix it to make sure that the step size doesn't get
#                    %smaller than the minimum level
#                    if stepSize(:,trial_trialTrack) <= min_level
#                        %adjust track step size
#                        stepSize(:,trial_trialTrack)=min_level;
#                        
#                        %record the fact at minimum
#                        minStepReached(trackItemNo(:,trialTrack(trial)),trial_trialTrack)=1;
#                    end
#                    
#                    
#                    
#                    foil_adj_value(:,trial_trialTrack)=foil_adj_value(:,trial_trialTrack)+stepSize(:,trial_trialTrack);
#                    %stop from crossing over and ping it up if
#                    %three consecutive at lowest level
#                    if foil_adj_value(:,trial_trialTrack) > 0.479
#                        
#                        foil_adj_value(:,trial_trialTrack)=0.48;
#                        
#                        counterAtBoundary(:,trial_trialTrack)=counterAtBoundary(:,trial_trialTrack)+1;
#                        
#                        if  counterAtBoundary(:,trial_trialTrack) >= 4
#                            stepSize(:,trial_trialTrack)=str2num(sprintf('%.2f',stepSize(:,trial_trialTrack)*scale_factor));
#                            
#                            %fix it to make sure that the step size doesn't get
#                            %smaller than the minimum level
#                            if stepSize(:,trial_trialTrack) <= min_level
#                                %adjust track step size
#                                stepSize(:,trial_trialTrack)=min_level;
#                                
#                                %record the fact at minimum
#                                minStepReached(trackItemNo(:,trialTrack(trial)),trial_trialTrack)=1;
#                            end
#                            
#                            foil_adj_value(:,trial_trialTrack)=0.48-stepSize(:,trial_trialTrack);
#                            counterAtBoundary(:,trial_trialTrack)=0;
#                            
#                            change{trial_trialTrack}='up';
#                        end
#                    end
#                    %reset counters
#                    con_correct(:,trial_trialTrack)=0;
#                    con_incorrect(:,trial_trialTrack)=0;
#                    
#                    
#                    %else for statement 3
#                else
#                    
#                    %if neither reached levitt or matching correct
#                    %direction keep going and don't change the levels - one
#                    %error has been made so not in free trial section
#                    %anylonger - here waiting for more correct trials to
#                    %reach levitt
#                    
#                    turnAbout{trialTrack(trial)}(trackItemNo(:,trialTrack(trial)))=0;
#                    
#                    if foil_adj_value(:,trial_trialTrack) > 0.479
#                        foil_adj_value(:,trial_trialTrack)=0.48;
#                        
#                        counterAtBoundary(:,trial_trialTrack)=counterAtBoundary(:,trial_trialTrack)+1;
#                        
#                        if  counterAtBoundary(:,trial_trialTrack) >= 4
#                            stepSize(:,trial_trialTrack)=str2num(sprintf('%.2f',stepSize(:,trial_trialTrack)*scale_factor));
#                            
#                            %fix it to make sure that the step size doesn't get
#                            %smaller than the minimum level
#                            if stepSize(:,trial_trialTrack) <= min_level
#                                %adjust track step size
#                                stepSize(:,trial_trialTrack)=min_level;
#                                
#                                %record the fact at minimum
#                                minStepReached(trackItemNo(:,trialTrack(trial)),trial_trialTrack)=1;
#                            end
#                            
#                            foil_adj_value(:,trial_trialTrack)=0.48-stepSize(:,trial_trialTrack);
#                            counterAtBoundary(:,trial_trialTrack)=0;
#                            turnAbout{trialTrack(trial)}(trackItemNo(:,trialTrack(trial)))=1;
#                            
#                            change{trial_trialTrack}='up';
#                        end
#                    end
#                    
#                end
#                
#            else %else for statement 2
#                %if an error has not occured keep original step size and reset
#                %counts of correct/incorrect - this is the initial punishment free
#                %stage
#                
#                foil_adj_value(:,trial_trialTrack)=foil_adj_value(:,trial_trialTrack)+stepSize(:,trial_trialTrack);
#                %not a turnabout
#                turnAbout{trialTrack(trial)}(trackItemNo(:,trialTrack(trial)))=0;
#                
#                if foil_adj_value(:,trial_trialTrack) > 0.479
#                    foil_adj_value(:,trial_trialTrack)=0.48;
#                    
#                    counterAtBoundary(:,trial_trialTrack)=counterAtBoundary(:,trial_trialTrack)+1;
#                    
#                    if  counterAtBoundary(:,trial_trialTrack) >= 4
#                        stepSize(:,trial_trialTrack)=str2num(sprintf('%.2f',stepSize(:,trial_trialTrack)*scale_factor));
#                        
#                        %fix it to make sure that the step size doesn't get
#                        %smaller than the minimum level
#                        if stepSize(:,trial_trialTrack) <= min_level
#                            %adjust track step size
#                            stepSize(:,trial_trialTrack)=min_level;
#                            
#                            %record the fact at minimum
#                            minStepReached(trackItemNo(:,trialTrack(trial)),trial_trialTrack)=1;
#                        end
#                        
#                        foil_adj_value(:,trial_trialTrack)=0.48-stepSize(:,trial_trialTrack);
#                        counterAtBoundary(:,trial_trialTrack)=0;
#                        turnAbout{trialTrack(trial)}(trackItemNo(:,trialTrack(trial)))=1;
#                        errorz(:,trialTrack(trial))=1;
#                        change{trial_trialTrack}='up';
#                    end
#                end
#                
#                %counters
#                con_incorrect(:,trial_trialTrack)=0;
#                con_correct(:,trial_trialTrack)= 0;
#                
#                
#            end %statement 2 - end of if they have made an error
#        end %statement 1 - end of if trial is correct
#        
#        %if it is incorrect
#        %if statment 1
#        if ~correctTrack(trial,trialTrack(trial))
#            %reset consecuitive low point counter
#            counterAtBoundary(:,trial_trialTrack)=0;
#            %if statement 2 - if error been made (by definition) and outside of
#            %free trial period
#            if trackItemNo(:,trialTrack(trial)) > free_trials(:,trialTrack(trial))
#                %keep score
#                con_incorrect(:,trial_trialTrack)=con_incorrect(:,trial_trialTrack)+1;
#                
#                %if statement 3
#                %does it meet levitts criteria for a change but not a change in
#                %direction
#                if con_incorrect(:,trial_trialTrack) >= Levitt(:,1) && strcmp(change{trial_trialTrack},'up');
#                    
#                    con_incorrect(:,trial_trialTrack)=0;
#                    con_correct(:,trial_trialTrack)=0;
#                    
#                    if stepSize(:,trial_trialTrack) <= min_level
#                        %adjust track step size
#                        stepSize(:,trial_trialTrack)=min_level;
#                        minStepReached(trackItemNo(:,trialTrack(trial)),trial_trialTrack)=1;
#                    end
#                    
#                    %change value on continuum
#                    foil_adj_value(:,trial_trialTrack)=foil_adj_value(:,trial_trialTrack)-stepSize(:,trial_trialTrack);
#                    
#                    if foil_adj_value(:,trial_trialTrack)< 0
#                        foil_adj_value(:,trial_trialTrack)=0;
#                    end
#                    
#                    turnAbout{trialTrack(trial)}(trackItemNo(:,trialTrack(trial)))=0;
#                    change{trial_trialTrack}='up';
#                    
#                    
#                    %else for statement 3
#                    %change in levitt and direction
#                else con_incorrect(:,trial_trialTrack) >= Levitt(:,1) && strcmp(change{trial_trialTrack},'down');
#                    %reord that it is turnabout
#                    turnAbout{trialTrack(trial)}(trackItemNo(:,trialTrack(trial)))=1;
#                    
#                    %change step size by a factor
#                    stepSize(:,trial_trialTrack)=str2num(sprintf('%.2f',stepSize(:,trial_trialTrack)*scale_factor));
#                    
#                    %keep counters
#                    con_incorrect(:,trial_trialTrack)=0;
#                    con_correct(:,trial_trialTrack)=0;
#                    
#                    if stepSize(:,trial_trialTrack) <= min_level
#                        %adjust track step size
#                        
#                        stepSize(:,trial_trialTrack)=min_level;
#                        
#                        minStepReached(trackItemNo(:,trialTrack(trial)),trial_trialTrack)=1;
#                    end
#                    
#                    foil_adj_value(:,trial_trialTrack)=foil_adj_value(:,trial_trialTrack)-stepSize(:,trial_trialTrack);
#                    
#                    if foil_adj_value(:,trial_trialTrack)< 0
#                        foil_adj_value(:,trial_trialTrack)=0;
#                    end
#                    
#                    change{trial_trialTrack}='up';
#                    
#                end %end statement 3
#                
#            else %else statement 2
#                turnAbout{trialTrack(trial)}(trackItemNo(:,trialTrack(trial)))=0;
#                
#            end %end statement 2
#            
#        end %end of statement 1 - was trial incorrect
#        
#        fout = fopen(OutFile, 'at');
#        
#        fprintf(fout, '\n%d,%s,%s,%s,%d,%d,%d,%d,%0.2f,%d,%0.2f,%0.2f,%d,%s,%s,%s',...
#            trial,target{trial},foil1_t,foil2_t,key(trial),...
#            response(trial),trial_trialTrack, correctTrack(trial,trialTrack(trial)),track_position{trialTrack(trial)}(trackItemNo(:,trialTrack(trial))),turnAbout{trialTrack(trial)}(trackItemNo(:,trialTrack(trial))),track_position_diff{trialTrack(trial)}(trackItemNo(:,trialTrack(trial))),stepSize(:,trial_trialTrack),trackItemNo(:,trialTrack(trial)),change{trial_trialTrack},num2str(toc/60),TargetType) ;
#        record_step{trialTrack(trial)}(trackItemNo(:,trialTrack(trial)))=stepSize(:,trial_trialTrack);
#        fclose(fout);
#        
#        clear trial_target trial_foil1 trial_foil2
#        
#        
#        for z=1:max(noTracks)
#            noAllTurns(z)=sum(turnAbout{z});
#        end
#        
#    else
#        continue
#    end
#    
#    if sum(noAllTurns >= stoppingCriterion)/size(noTracks,1) == 1
#        x=1;
#    else
#        %do neither of the above and just continue as normal until one of the
#        %two conditions above is met
#    end
#    
#end
