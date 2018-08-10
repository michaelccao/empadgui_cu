#!/user/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 16:07:48 2015

@author: Michael Cao
"""

import kivy
kivy.require('1.8.0')

from kivy.config import Config
Config.set('graphics', 'window_state', 'visible')
Config.set('graphics', 'height', '550')
Config.set('graphics', 'width', '1175')
Config.write()

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.behaviors import DragBehavior
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.graphics import Line
from kivy.graphics import Color
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.properties import NumericProperty
from kivy.properties import ListProperty
from kivy.clock import Clock
from kivy.uix.spinner import Spinner

import sys
import socket

import os
import subprocess
import string

import time

import csv

import serial

import platform
if platform.system() == 'Windows':
    from ctypes import windll


xy_minx=5120
xy_maxx=60415
xy_miny=5120
xy_maxy=60415

expt=0.001
framet=0
num_fr=1

rangex = xy_maxx - xy_minx
rangey = xy_maxy - xy_miny

num_cps = 1
exposeOverhead = 2
hw_overhead = 0

serial_address = '/dev/ttyS4' #serial address of Keithley on current EMPAD computer, last updated 6/12/2018

try:
    ser = serial.Serial(serial_address, timeout = 1)
    ser.write('*RST\r')
    ser.write(':SOUR:FUNC VOLT\r')
    ser.write(':SOUR:VOLT:RANG:AUTO 1\r')
    ser.write(':SOUR:VOLT:LEV 120\r')
    ser.write(':SENS:CURR:PROT 200E-6\r')
    ser.write(':SENS:FUNC "CURR"\r')
    ser.write(':SENS:CURR:RANG:AUTO 1\r')
    ser.write(':ARM:COUN INF\r')
    ser.write(':OUTP ON\r')
    ser.write(':INIT\r')
    
    keithley_connected = True
except:
    keithley_connected = False

def Send_to_Cam(msg, recvflag = True):
    if not connected:
        raise Exception('NOT CONNECTED')
        return
    msg = msg.encode()
    
    sock.sendall(msg)
    if recvflag:
        print(sock.recv(4096).decode())
        
    time.sleep(0.010)


Builder.load_string("""

<DragPopup>:
    drag_rectangle: (self.x, self.y+self._container.height, self.width, self.height - self._container.height)
    drag_timeout: 10000000
    drag_distance: 0
    auto_dismiss: True
    title: 'DragPop'

""")

class DragPopup(DragBehavior, Popup):
    pass

class DragBox(DragBehavior, BoxLayout):

    def __init__(self, **kwargs):
        super(DragBox, self).__init__(**kwargs)
        
        with self.canvas:
            Color(1., 1., 1.)
            self.r = Line(rectangle = (self.x, self.y, self.width, self.height))
                           
    
        self.orientation = 'vertical'
        
        topbar = BoxLayout(height = 25, size_hint_y = None)
        self.topheight = topbar.height
        topbar.orientation = 'horizontal'
        self.add_widget(topbar)
        
        spacer = Widget(width = self.width-150, 
                        size_hint_x = None)
        bmin = Button(text = "Min", width = 50, size_hint_x = None)
        bmax = Button(text = "Max", width = 50, size_hint_x = None)
        close = Button(text= "Close", width = 50, size_hint_x = None)
        
        topbar.add_widget(spacer)
        topbar.add_widget(bmin)
        topbar.add_widget(bmax)
        topbar.add_widget(close)
        
        def closebox(self, *args):
            box = self.parent.parent
            lay = box.parent
            lay.remove_widget(box)
            
        close.bind(on_press=closebox)
        
        self.drag_rectangle = (self.x, self.y + self.height - self.topheight, 
                               self.width,
                               self.topheight)
        self.drag_timeout = 100000000
        self.drag_distance = 0

Builder.load_string("""
    
<SetMasks>:

    drag_rectangle: self.x, self.top-50, 100, 50
    drag_timeout: 100000000
    drag_distance: 0
    
    pos: 200, 200

    size: 405, 300
    size_hint_x: None
    size_hint_y: None
    do_default_tab: False
    
    outer_slider: outer_slider
    outer_value: outer_value
    
    inner_slider: inner_slider
    inner_value: inner_value
    
    x_slider: x_slider
    x_value: x_value
    
    y_slider: y_slider
    y_value: y_value
    
    masknum: masknum
    
    shape: shape
    
    ud: ud
    lr: lr
    
    gui: self
    
    def0: 0, 0, 20, 64, 'Annulus', 'down', 'down'
    def1: 0, 0, 2, 2, 'Rectangle', 'down', 'down'
    def2: 0, 0, 0, 0, 'Annulus', 'normal', 'normal'
    def3: 0, 0, 0, 0, 'Annulus', 'normal', 'normal'
    
    refresh: True

    TabbedPanelItem:
        text: 'Live Masks'
        on_touch_down: root.gui.put_on_top(root)
        
        BoxLayout:
            orientation: 'vertical'
            BoxLayout:
                orientation: 'horizontal'
                height: 205
                size_hint_y: None
    
                BoxLayout:
                    orientation: 'vertical'
                    
                        
                    BoxLayout:
                        orientation: 'horizontal'
                        height: 50
                        size_hint_y: None
                        BoxLayout:
                            orientation: 'vertical'
                            width: 130
                            size_hint_x: None
                            Label:
                                size: self.texture_size
                                size_hint: None, None
                                pos_hint: {'center_x':0.5}              
                                text: 'KX'
    
                            Slider:
                                id: x_slider
                                width: 130
                                height: 30
                                size_hint_x: None
                                size_hint_y: None
                                range: root.slider_range(shape.text, outer_slider.value, outer_slider.value)
                                step: 1
                                value: root.keep_in_range(self.value, self.range)
                        TextInput:
                            id: x_value
                            pos_hint: {'y':0.0}
                            multiline: False
                            height: 30
                            padding_x: 10
                            width: 70
                            size_hint: (None,None)
                            text: '%.0f' % x_slider.value
                            input_filter: 'int'
                            on_text_validate: root.update_slider(slider = 'x')
                            
                    BoxLayout:
                        orientation: 'horizontal'
                        height: 50
                        size_hint_y: None
                        BoxLayout:
                            orientation: 'vertical'
                            width: 130
                            size_hint_x: None
                            Label:
                                size: self.texture_size
                                size_hint: None, None
                                pos_hint: {'center_x':0.5}              
                                text: 'KY'
    
                            Slider:
                                id: y_slider
                                width: 130
                                height: 30
                                size_hint_x: None
                                size_hint_y: None
                                range: root.slider_range(shape.text, outer_slider.value, inner_slider.value)
                                step: 1
                                value: root.keep_in_range(self.value, self.range)
                        TextInput:
                            id: y_value
                            pos_hint: {'y':0.0}
                            multiline: False
                            height: 30
                            padding_x: 10
                            width: 70
                            size_hint: (None,None)
                            text: '%.0f' % y_slider.value
                            input_filter: 'int'
                            on_text_validate: root.update_slider(slider = 'y')
                        
                    BoxLayout:
                        orientation: 'horizontal'
                        height: 50
                        size_hint_y: None
                        BoxLayout:
                            orientation: 'vertical'
                            width: 130
                            size_hint_x: None
                            Label:
                                size: self.texture_size
                                size_hint: None, None
                                pos_hint: {'center_x':0.5}              
                                text: 'Inner Radius' if shape.text=='Annulus' else 'Height'
    
                            Slider:
                                id: inner_slider
                                width: 130
                                height: 30
                                size_hint_x: None
                                size_hint_y: None
                                range: (0, 64)
                                step: 1
                                
                                
                        TextInput:
                            id: inner_value
                            pos_hint: {'y':0.0}
                            multiline: False
                            height: 30
                            padding_x: 10
                            width: 70
                            size_hint: (None,None)
                            text: '%.0f' % inner_slider.value
                            input_filter: 'int'
                            on_text_validate: root.update_slider(slider = 'inner')
                    BoxLayout:
                        orientation: 'horizontal'
                        height: 50
                        size_hint_y: None
                        BoxLayout:
                            orientation: 'vertical'
                            width: 130
                            size_hint_x: None   
                            Label:
                                text: 'Outer Radius' if shape.text=='Annulus' else 'Width'
                                size: self.texture_size
                                size_hint: None, None
                                pos_hint: {'center_x':0.5}
                            Slider:
                                id: outer_slider
                                width: 130
                                height: 30
                                size_hint_x: None
                                size_hint_y: None
                                range: (0, 64)
                                step: 1
                                value: max(inner_slider.value, outer_slider.value) if shape.text=='Annulus' else outer_slider.value
                        TextInput:
                            id: outer_value
                            pos_hint: {'y':0.0}
                            multiline: False
                            height: 30
                            padding_x: 10
                            width: 70
                            size_hint: (None,None)
                            text: '%.0f' % outer_slider.value
                            input_filter: 'int'
                            on_text_validate: root.update_slider(slider = 'outer')
                    Widget:
                        name: 'spacer'
                        
                BoxLayout:
            Widget:
                name: 'spacer'
                height: 25
                size_hint_y: None
            BoxLayout:
                orientation: 'horizontal'
                Spinner:
                    id: masknum
                    size: 100, 25
                    size_hint: None, None
                    text: 'Mask 0'
                    values: 'Mask 0', 'Mask 1', 'Mask 2', 'Mask 3'
                    text: root.select_mask(self.text)
                Spinner:
                    id: shape
                    size: 100, 25
                    size_hint: None, None
                    text: 'Annulus'
                    values: 'Annulus', 'Rectangle'
                Button:
                    text: 'Center Mask'
                    size: 100, 25
                    size_hint: None, None
                    on_release: x_slider.value, y_slider.value = 0,0
                Button:
                    text: 'Apply Mask'
                    size: 100, 25
                    size_hint: None, None
                    on_release: root.apply_mask(masknum.text[-1])
                    
            BoxLayout:
                orientation: 'horizontal'
                height: 25
                size_hint_y: None
                ToggleButton:
                    id: ud
                    text: 'Up/Down'
                    size: 100, 25
                    size_hint: None, None
                    state: 'normal'
                ToggleButton:
                    id: lr
                    text: 'Left/Right'
                    size: 100, 25
                    size_hint: None, None
                    state: 'normal'
                ToggleButton:
                    id: flash
                    text: 'Flash'
                    size: 100, 25
                    size_hint: None, None
                    state: 'normal'
                    on_release: root.flash(self.state)
                    
                
            Widget:
            
                canvas:
                    Color:
                        rgb: 0, 0, 0
                    Rectangle:
                        pos: root.center_x, root.top - 248
                        size: 200, 200
                    
                    Color:
                        rgba: 1, 1, 1, (1 if shape.text == 'Annulus' else 0)
                    Ellipse:
                        pos: root.ellipse_pos(root.center_x, root.top, x_slider.value, y_slider.value, outer_slider.value)
                        size: root.ellipse_size(outer_slider.value)
                        
                    
                    Color:
                        rgba: 0, 0, 0, (1 if shape.text == 'Annulus' else 0)
                    Ellipse:
                        pos: root.ellipse_pos(root.center_x, root.top, x_slider.value, y_slider.value, inner_slider.value)
                        size: root.ellipse_size(inner_slider.value)
                    
                    Color:
                        rgba: 1, 1, 1, (1 if shape.text == 'Rectangle' else 0)
                    Rectangle:
                        pos: root.rect_pos(root.center_x, root.top, x_slider.value, y_slider.value, outer_slider.value, inner_slider.value)
                        size: max(0.001, 2*outer_slider.value/64.0*100), max(0.001, 2*inner_slider.value/64.0*100)
                    
                    
                        
""")
        
class SetMasks(DragBehavior, TabbedPanel):
    
    outer_slider = ObjectProperty(None)
    outer_value = ObjectProperty(None)
    
    inner_slider = ObjectProperty(None)
    inner_value = ObjectProperty(None)
    
    x_slider = ObjectProperty(None)
    x_value = ObjectProperty(None)
    
    y_slider = ObjectProperty(None)
    y_value = ObjectProperty(None)
    
    size_slider = ObjectProperty(None)
    size_value = ObjectProperty(None)
    
    event = 0
    
    def flash(self, flashing):
        def apply_mask_cb(*args):
            self.apply_mask(self.masknum.text[-1])
            
        if flashing == 'down':
            self.event = Clock.schedule_interval(apply_mask_cb, 2)
        if flashing == 'normal':
            Clock.unschedule(self.event)
            
        
            
    def keep_in_range(self, value, srange):
        if value >= srange[0] and value <= srange[1]:
            return value
        if value < srange[0]:
            return srange[0]
        if value > srange[1]:
            return srange[1]
    
    def slider_range(self, shape, w, h):
        if shape == 'Annulus':
            return (max(-64, -64 + w),min(64 - w, 64))
        else:
            return (max(-64, -64 + h), min(64, 64 - h))
    
    def ellipse_pos(self, rx, rt, x, y, size):
        
        #print('posarg',rx,rt,x,y,size)
        size = size*100/64.0       
        x = x*100/64.0
        y = y*100/64.0
        
        x0 = rx + 100 - size + x
        y0 = rt - 148 - size + y
        
        #print('pos',x0,y0)
        
        return (x0, y0)
    
    def rect_pos(self, rx, rt, x, y, w, h):
        w = w*100/64.0
        h = h*100/64.0
        x = x*100/64.0
        y = y*100/64.0
        
        x0 = rx + 100 - w + x
        y0 = rt - 148 - h + y
        
        return (x0, y0)
        
    def ellipse_size(self, size, *args):        
        size = 2*size*100/64.0

        #print('size',max(0.001, size), max(0.001, size))
        
        return max(0.001, size), max(0.001, size)
    
    def update_slider(self, **kwargs):            
        values = {
        'outer':self.outer_value, 
        'inner':self.inner_value,
        'x':self.x_value,
        'y':self.y_value
        }
        
        sliders = {
        'outer':self.outer_slider,
        'inner':self.inner_slider,
        'x':self.x_slider,
        'y':self.y_slider
        }
        
        value = values[kwargs['slider']]

        slider = sliders[kwargs['slider']]
        slider_max = slider.max
        slider_min = slider.min
        try:
            nvalue = float(value.text)
        except:
            nvalue = 0
        nvalue = max(slider_min, nvalue)
        nvalue = min(slider_max, nvalue)
        
        sliders[kwargs['slider']].value = nvalue
        value.text = '%.0f' % nvalue
    
    def apply_mask(self, text):
        if self.shape.text == 'Annulus':
            roitype = 'annulus'
        else:
            roitype = 'box'
        try:
            starting_index = int(text)*3
            
            padgui.active_masks[starting_index] = 'sum %d' % int(text)
            if self.ud.state == 'down' and self.lr.state == 'down':
                roitype = roitype + '_lr_ud'
                padgui.active_masks[starting_index+1] = 'lr %d' % int(text)
                padgui.active_masks[starting_index+2] = 'ud %d' % int(text)
            elif self.ud.state == 'down' and self.lr.state == 'normal':
                roitype = roitype + '_ud'
                padgui.active_masks[starting_index+1] = 'off'
                padgui.active_masks[starting_index+2] = 'ud %d' % int(text)
            elif self.ud.state == 'normal' and self.lr.state == 'down':
                roitype = roitype + '_lr'
                padgui.active_masks[starting_index+1] = 'lr %d' % int(text)
                padgui.active_masks[starting_index+2] = 'off'
            else:
                padgui.active_masks[starting_index+1] = 'off'
                padgui.active_masks[starting_index+2] = 'off'
            Send_to_Cam('padcom roimask %s %s %.0f %.0f %.0f %.0f\n' % (roitype, text, self.x_slider.value+64, -self.y_slider.value+64, self.inner_slider.value, self.outer_slider.value))
        except:
            pass
        
        defvalue = (self.x_slider.value, self.y_slider.value, self.inner_slider.value, self.outer_slider.value, self.shape.text, self.ud.state, self.lr.state)        
        
        if text=='0':
            self.def0 = defvalue
        if text=='1':
            self.def1 = defvalue
        if text=='2':
            self.def2 = defvalue
        if text=='3':
            self.def3 = defvalue
            
    
        
        
        
    def select_mask(self, text):
        if text == '':
            return 'Mask 0'
            
        defaults = {'Mask 0': self.def0, 'Mask 1': self.def1, 'Mask 2': self.def2, 'Mask 3': self.def3}

        self.refresh = False
        
        self.x_slider.value = defaults[text][0]
        self.y_slider.value = defaults[text][1]
        self.inner_slider.value = defaults[text][2]
        self.outer_slider.value = defaults[text][3]
        self.shape.text = defaults[text][4]
        self.ud.state = defaults[text][5]
        self.lr.state = defaults[text][6]
        
        self.refresh = True
        
        return text
        
Builder.load_file('changedir.kv')
Builder.load_file('newfolder.kv')

class NewFolder(DragPopup):
    path = ''
    def __init__(self, dpath):
        DragPopup.__init__(self)
        
        if dpath[-1] != os.sep:
            dpath = dpath + os.sep
        self.path = dpath

        print(self.path)
    
    def create_new_folder(self, fname):
        directory = self.path + fname
        print(directory)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except Exception as e:
                print(e)
        self.dismiss()
        Change_Dir.change_path(directory)
        Change_Dir.open()
        
    def close(self):
        self.dismiss()
        Change_Dir.open()

class ChangeDir(DragPopup):
    
    def __init__(self, rootpath):
        DragPopup.__init__(self)

        
        drives = []
        
        if platform.system() == 'Windows':
            bitmask = windll.kernel32.GetLogicalDrives()
            
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drives.append(letter + ':\\')
                bitmask >>= 1
                
                
        try:
            with open('last_state.csv', 'r') as file:
                reader = csv.reader(file, delimiter=' ', quotechar='|')
                params = []
                for row in reader:
                    params.append(row)
            sp = params[3][0]
        except:
            sp = os.sep
            
        
        if len(drives) != 0:
            self.drives.text = os.path.splitdrive(sp)[0] + os.sep#drives[0]
            self.fchoose.path = sp
#            self.drives.text = drives[0]
            self.drives.values = drives
        else:
            self.drives.text = rootpath
            self.drives.values = rootpath
        
        
    def new_folder(self, path):
        nf = NewFolder(path)
        self.dismiss()
        nf.open()
#        print(path)
    
    def change_path(self, path):
        self.fchoose.path = path



Change_Dir = ChangeDir(os.path.abspath(os.sep))

Builder.load_string("""
<SetScan>:   

    drag_rectangle: self.x, self.top-50, 200, 50
    drag_timeout: 100000000
    drag_distance: 0
    
    pos: 200, 0

    size: 410, 325
    size_hint_x: None
    size_hint_y: None
    do_default_tab: False
    
    x_slider: x
    x_slider2: x2
    x_value: x_value
    x_value2: x_value2
    
    y_slider: y
    y_slider2: y2
    y_value: y_value
    y_valu2: y_value2
    
    size_slider: size
    size_slider2: size2
    size_value: size_value
    size_value2: size_value2
        
    filename: filename
    filename2: filename2
    dockbtn: dockbtn
    dockbtn2: dockbtn2
    
    gui: self
    attach: self
    
    scanning: False
    saving: False
    savingto: savingto
    savingto2: savingto2
    
    acquire: acquire.__self__
    focus: focus.__self__
    acquire2: acquire2.__self__
    focus2: focus2.__self__
    
    aparam: False, False, False, False, False, False, False
    oparam: '','','','','','',''
    tparam: '','','','','','',''
    porders: 0,0,0,0,0,0,0
    
    
    
    exposure_time: exposure_time
    exposure_time2: exposure_time2
    xres: xres
    xres2: xres2
    
    acquiretab: acquiretab
    livetab: livetab
    
    TabbedPanelItem:
        text: 'Live'
        id: livetab
        on_touch_down: root.gui.put_on_top(root)
        BoxLayout:
            orientation: 'vertical'
            BoxLayout:
                orientation: 'horizontal'
                height: 200
                size_hint_y: None
                
                BoxLayout:
                    orientation: 'vertical'
                    Widget:
                        name: 'spacer'
                        
                    BoxLayout:
                        orientation: 'horizontal'
                        height: 50
                        size_hint_y: None
                        BoxLayout:
                            orientation: 'vertical'
                            width: 130
                            size_hint_x: None
                            Label:
                                text: 'X'
                                size: self.texture_size
                                size_hint: None, None
                                pos_hint: {'center_x':0.5}
                            Slider:
                                id: x
                                width: 130
                                height: 30
                                size_hint_x: None
                                size_hint_y: None
                                range: (0, 1)
                                step: 0.01
                                value: 0.5
                        TextInput:
                            id: x_value
                            pos_hint: {'y':0}
                            multiline: False
                            height: 30
                            padding_x: 10
                            width: 70
                            size_hint: (None,None)
                            text: '%4.2f' % x.value
                            on_text_validate: root.update_slider(slider = 'x')
                            input_filter: 'float'
                    
                    
                    BoxLayout:
                        orientation: 'horizontal'
                        height: 50
                        size_hint_y: None
                        BoxLayout:
                            orientation: 'vertical'
                            width: 130
                            size_hint_x: None
                            Label:
                                text: 'Y'
                                size: self.texture_size
                                size_hint: None, None
                                pos_hint: {'center_x':0.5}
                            Slider:
                                id: y
                                width: 130
                                height: 30
                                size_hint_x: None
                                size_hint_y: None
                                range: (0, 1)
                                step: 0.01
                                value: 0.5
                        TextInput:
                            id: y_value
                            pos_hint: {'y':0}
                            multiline: False
                            height: 30
                            padding_x: 10
                            width: 70
                            size_hint: (None,None)
                            text: '%4.2f' % y.value
                            on_text_validate: root.update_slider(slider = 'y')
                            input_filter: 'float'
                    BoxLayout:
                        orientation: 'horizontal'
                        height: 50
                        size_hint_y: None
                        BoxLayout:
                            orientation: 'vertical'
                            width: 130
                            size_hint_x: None                 
                            Label:
                                text: 'Size'
                                size: self.texture_size
                                size_hint: None, None
                                pos_hint: {'center_x':0.5}
                            Slider:
                                id: size
                                width: 130
                                height: 30
                                size_hint_x: None
                                size_hint_y: None
                                range: (0, 1)
                                step: 0.01
                                value: 1.0
                        TextInput:
                            id: size_value
                            pos_hint: {'y':0}
                            multiline: False
                            height: 30
                            padding_x: 10
                            width: 70
                            size_hint: (None,None)
                            text: '%4.2f' % size.value
                            on_text_validate: root.update_slider(slider = 'size')
                            input_filter: 'float'
                    GridLayout:
                        cols: 2
                        height: 60
                        size_hint_y: None
                        Label:
                            text: 'Pixels'
                            size: self.texture_size
                            
                        Label:
                            text: 'Exp. Time (ms)'
                            size: self.texture_size
                            
                    
                        TextInput:
                            id: xres
                            height: 30
                            text: '128'
                            input_filter: 'int'
                            multiline: False
                            padding_x: [self.width/2 - self._get_text_width(max(self._lines, key=len), self.tab_width, self._label_cached) / 2.0, 0] if self.text else [self.width/2, 0]
                        TextInput:
                            id: exposure_time
                            height: 30
                            text: '1'
                            input_filter: 'float'
                            multiline: False
                            padding_x: [self.width/2 - self._get_text_width(max(self._lines, key=len), self.tab_width, self._label_cached) / 2.0, 0] if self.text else [self.width/2, 0]
                    Widget:
                        name: 'spacer'
                BoxLayout:
                    id: canvas_space
            
            Widget:
                height: 3
                size_hint_y: None
            FNameInput:
                id: filename
                text: root.construct_filename(root.aparam, root.oparam, root.tparam, root.prefix, root.suffix)[0]
                multiline: False
                height: 30
                size_hint_y: None
                format: root.determine_format(self.text)
            
            BoxLayout:
                orientation: 'horizontal'
                height: 25
                size_hint_y: None
                
                Button:
                    id: focus
                    text: 'Stop Scan' if root.scanning else 'Live'
                    height: 25
                    width: 75
                    size_hint: None, None
                    on_release: root.scan(app.Save_Path, filename.text, x.value, y.value, size.value, xres.text, xres.text, focus, False, exposure_time.text)
                
                Button:
                    id: acquire
                    text: 'Acquire'
                    height: 25
                    width: 75
                    size_hint: None, None
                    pos_hint:{'x':0}
                    on_release: root.acquire_img(app.Save_Path, filename.text, x2.value, y2.value, size2.value, xres2.text, xres2.text, focus, True, exposure_time2.text)
                
                Button:
                    text: 'Change Dir'
                    height: 25
                    width: 80
                    size_hint: None, None
                    on_release: root.change_dir()
                
                Widget:
                
                ToggleButton:
                    id: dockbtn
                    text: '>>'
                    height: 25
                    width: 40
                    size_hint: None, None
                    on_release: root.gui.dock(self)
                
                                
            Label:
                id: savingto
                text: 'Saving to %s' % app.Save_Path
                size: self.texture_size
                size_hint: None, None
            
                
                
                                    
            Widget:
            
                canvas:
                    Color:
                        rgb: 0, 0, 0
                    Rectangle:
                        pos: root.center_x, root.top - 248
                        size: 200, 200
                        
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        pos: root.rect_pos(root.center_x, x.value, size.value, root.top, y.value)
                        size: root.rect_size(x.value, y.value, size.value)
    
    TabbedPanelItem:
        text: 'Acquire'
        id: acquiretab
        on_touch_down: root.gui.put_on_top(root)
        BoxLayout:
            orientation: 'vertical'
            BoxLayout:
                orientation: 'horizontal'
                height: 200
                size_hint_y: None
                
                BoxLayout:
                    orientation: 'vertical'
                    Widget:
                        name: 'spacer'
                        
                    BoxLayout:
                        orientation: 'horizontal'
                        height: 50
                        size_hint_y: None
                        BoxLayout:
                            orientation: 'vertical'
                            width: 130
                            size_hint_x: None
                            Label:
                                text: 'X'
                                size: self.texture_size
                                size_hint: None, None
                                pos_hint: {'center_x':0.5}
                            Slider:
                                id: x2
                                width: 130
                                height: 30
                                size_hint_x: None
                                size_hint_y: None
                                range: (0, 1)
                                step: 0.01
                                value: 0.5
                        TextInput:
                            id: x_value2
                            pos_hint: {'y':0}
                            multiline: False
                            height: 30
                            padding_x: 10
                            width: 70
                            size_hint: (None,None)
                            text: '%4.2f' % x2.value
                            on_text_validate: root.update_slider(slider = 'x2')
                            input_filter: 'float'
                    
                    
                    BoxLayout:
                        orientation: 'horizontal'
                        height: 50
                        size_hint_y: None
                        BoxLayout:
                            orientation: 'vertical'
                            width: 130
                            size_hint_x: None
                            Label:
                                text: 'Y'
                                size: self.texture_size
                                size_hint: None, None
                                pos_hint: {'center_x':0.5}
                            Slider:
                                id: y2
                                width: 130
                                height: 30
                                size_hint_x: None
                                size_hint_y: None
                                range: (0, 1)
                                step: 0.01
                                value: 0.5
                        TextInput:
                            id: y_value2
                            pos_hint: {'y':0}
                            multiline: False
                            height: 30
                            padding_x: 10
                            width: 70
                            size_hint: (None,None)
                            text: '%4.2f' % y2.value
                            on_text_validate: root.update_slider(slider = 'y2')
                            input_filter: 'float'
                    BoxLayout:
                        orientation: 'horizontal'
                        height: 50
                        size_hint_y: None
                        BoxLayout:
                            orientation: 'vertical'
                            width: 130
                            size_hint_x: None                 
                            Label:
                                text: 'Size'
                                size: self.texture_size
                                size_hint: None, None
                                pos_hint: {'center_x':0.5}
                            Slider:
                                id: size2
                                width: 130
                                height: 30
                                size_hint_x: None
                                size_hint_y: None
                                range: (0, 1)
                                step: 0.01
                                value: 1.0
                        TextInput:
                            id: size_value2
                            pos_hint: {'y':0}
                            multiline: False
                            height: 30
                            padding_x: 10
                            width: 70
                            size_hint: (None,None)
                            text: '%4.2f' % size2.value
                            on_text_validate: root.update_slider(slider = 'size2')
                            input_filter: 'float'
                    GridLayout:
                        cols: 2
                        height: 60
                        size_hint_y: None
                        Label:
                            text: 'Pixels'
                            size: self.texture_size
                            
                        Label:
                            text: 'Exp. Time (ms)'
                            size: self.texture_size
                            
                    
                        TextInput:
                            id: xres2
                            height: 30
                            text: '256'
                            input_filter: 'int'
                            multiline: False
                            padding_x: [self.width/2 - self._get_text_width(max(self._lines, key=len), self.tab_width, self._label_cached) / 2.0, 0] if self.text else [self.width/2, 0]
                        TextInput:
                            id: exposure_time2
                            height: 30
                            text: '1'
                            input_filter: 'float'
                            multiline: False
                            padding_x: [self.width/2 - self._get_text_width(max(self._lines, key=len), self.tab_width, self._label_cached) / 2.0, 0] if self.text else [self.width/2, 0]
                    Widget:
                        name: 'spacer'
                BoxLayout:
                    id: canvas_space
            
            Widget:
                height: 3
                size_hint_y: None
            FNameInput:
                id: filename2
                text: root.construct_filename(root.aparam, root.oparam, root.tparam, root.prefix, root.suffix)[0]
                multiline: False
                height: 30
                size_hint_y: None
                format: root.determine_format(self.text)
            
            BoxLayout:
                orientation: 'horizontal'
                height: 25
                size_hint_y: None
                
                Button:
                    id: focus2
                    text: 'Stop Scan' if root.scanning else 'Live'
                    height: 25
                    width: 75
                    size_hint: None, None
                    on_release: root.scan(app.Save_Path, filename.text, x.value, y.value, size.value, xres.text, xres.text, focus, False, exposure_time.text)
                
                Button:
                    id: acquire2
                    text: 'Acquire'
                    height: 25
                    width: 75
                    size_hint: None, None
                    pos_hint:{'x':0}
                    on_release: root.acquire_img(app.Save_Path, filename.text, x2.value, y2.value, size2.value, xres2.text, xres2.text, focus, True, exposure_time2.text)
                
                Button:
                    text: 'Change Dir'
                    height: 25
                    width: 80
                    size_hint: None, None
                    on_release: root.change_dir()
                
                Widget:
                
                ToggleButton:
                    id: dockbtn2
                    text: '>>'
                    height: 25
                    width: 40
                    size_hint: None, None
                    on_release: root.gui.dock(self)
                
                                
            Label:
                id: savingto2
                text: 'Saving to %s' % app.Save_Path
                size: self.texture_size
                size_hint: None, None
            
                
                
                                    
            Widget:
            
                canvas:
                    Color:
                        rgb: 0, 0, 0
                    Rectangle:
                        pos: root.center_x, root.top - 248
                        size: 200, 200
                        
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        pos: root.rect_pos(root.center_x, x2.value, size2.value, root.top, y2.value)
                        size: root.rect_size(x2.value, y2.value, size2.value)
                   
""")


        
class SetScan(DragBehavior, TabbedPanel):
    
    x_slider = ObjectProperty(None)
    x_value = ObjectProperty(None)
    
    y_slider = ObjectProperty(None)
    y_value = ObjectProperty(None)
    
    size_slider = ObjectProperty(None)
    size_value = ObjectProperty(None)
    
    filename = ObjectProperty(None)
    exposure_time = ObjectProperty(None)
    
    x_slider2 = ObjectProperty(None)
    x_value2 = ObjectProperty(None)
    
    y_slider2 = ObjectProperty(None)
    y_value2 = ObjectProperty(None)
    
    size_slider2 = ObjectProperty(None)
    size_value2 = ObjectProperty(None)
    
    filename2 = ObjectProperty(None)
    exposure_time2 = ObjectProperty(None)
    
    prefix = StringProperty('')
    suffix = StringProperty('')
    
    post_name = StringProperty('')
    
    fullname = StringProperty('')
    
    def determine_format(self, text):
        try:
            fname = self.construct_filename(self.aparam, self.oparam, self.tparam, self.prefix, self.suffix)[1]
            findex = text.index(fname)
            flen = len(fname)
            self.prefix = text[0:findex]
            self.suffix = text[findex+flen:]
#            print(self.prefix,self.suffix)
        except:
            pass
        return ''
    
    
    def construct_filename(self, ap, op, tp, prefix, suffix):
        order = self.attach.porders
        num_active = max(order)
        fname = ''
        for i in range(1, num_active+1):
            pindex = order.index(i)
            fname = fname + tp[pindex]
            if tp[pindex] != '':
                fname = fname + '_'
            
        displayname = ''
        displayname = self.prefix + fname[0:-1] + self.suffix
        
        if padgui.state_restored == True:
            padgui.save_state()
        else:
            print(padgui.state_restored)
        
        return displayname, fname[0:-1]
        
    def match_res(self, res1, foc, res2):
        if foc==False:
            res2.text = res1.text
        
    def rect_pos(self, rx, x, size, rt, y):
        x0 = max(rx, rx + 200*(1-x) - 100*size)
        y0 = max(rt-248, rt-248 + 200*y - 100*size)
        return (x0,y0)
        
    def rect_size(self, x, y, size):
        w = min(100*size + 200*x, 200*size, 200 - 200*x + 100*size)
        h = min(100*size + 200*y, 200*size, 200 - 200*y + 100*size)
        return (w,h)
    
    def change_dir(self):
        Change_Dir.open()
            
    def update_slider(self, **kwargs):            
        values = {
        'x':self.x_value,
        'y':self.y_value,
        'size':self.size_value,
        'x2':self.x_value2,
        'y2':self.y_value2,
        'size2':self.size_value2}
        
        sliders = {
        'x':self.x_slider,
        'y':self.y_slider,
        'size':self.size_slider,
        'x2':self.x_slider2,
        'y2':self.y_slider2,
        'size2':self.size_slider2}
        
        value = values[kwargs['slider']]

        slider = sliders[kwargs['slider']]
        slider_max = slider.max
        slider_min = slider.min
        try:
            nvalue = float(value.text)
        except:
            nvalue = 0
        nvalue = max(slider_min, nvalue)
        nvalue = min(slider_max, nvalue)
        
        sliders[kwargs['slider']].value = nvalue
        value.text = '%.2f' % nvalue
        
    
    def scan_finished(self, *args):    
        self.scanning = False
        self.acquire.disabled = False
        self.focus.disabled = False
        self.acquire2.disabled = False
        self.focus2.disabled = False
        
        self.acquire.text = 'Acquire'
        self.acquire.state = 'normal'
        
        self.acquire2.text = 'Acquire'
        self.acquire2.state = 'normal'

        self.num_iterate()
        
        #Restore name inputs
        self.filename.disabled = False                        
        self.attach.disabled = False
        
        self.filename2.disabled = False
    
    def restore_label(self, *args):
        self.savingto.text = 'Saving to %s' % padgui.Save_Path
        self.savingto2.text = 'Saving to %s' % padgui.Save_Path
    
    def acquire_img(self, savepath, fname, frac_x, frac_y, frac_t, xres, yres, btn, save, expt):
        
        if not self.scanning:
            self.scan(savepath, fname, frac_x, frac_y, frac_t, xres, yres, btn, save, expt)
            self.switch_to(self.acquiretab)
        else:
            if self.acquire.text == 'Save' or self.acquire2.text == 'Save':
                try:
                    Send_to_Cam('padcom scan_focus 0\n')
                    Send_to_Cam('filestore 1 5\n')
                    self.acquire.text = 'Saving...'
                    self.acquire.state = 'down'
                    self.acquire2.text = 'Saving...'
                    self.acquire2.state = 'down'
                    self.saving = True
                except Exception as e:
                    print(e)
            else:
                try:
                    Send_to_Cam('filestore 0 5\n')
                    self.acquire.text = 'Save'
                    self.acquire.state = 'normal'
                    self.acquire2.text = 'Save'
                    self.acquire2.state = 'normal'
                    self.saving = False
                except Exception as e:
                    print(e)
    def scan(self, savepath, fname, frac_x, frac_y, frac_t, xres, yres, btn, save, expt):
        
        expt = float(expt)/1000.0
        
        if not self.connected:
            print('Not connected to server')
            self.scanning = not self.scanning
            self.scanning = False
        if padgui.Busy:
            print('Busy')
            self.scanning = not self.scanning
            self.scanning = not self.scanning
        if self.connected and not padgui.Busy:
            
            if self.scanning:  #Stop scanning
                
                
                
                try:
                    Send_to_Cam('padcom scan_focus 0\n') #Finish off scan
                    self.savingto.text = 'ALLOW SCAN TO FINISH'
                    self.savingto2.text = 'ALLOW SCAN TO FINISH'
                    Clock.schedule_once(self.restore_label, 3)
                    self.scanning = False
                    self.acquire.text = 'Acquire'
                    self.acquire.state = 'normal'
                    self.acquire2.text = 'Acquire'
                    self.acquire2.state = 'normal'

#                    print(self.saving)

                    #Restore name inputs
                    self.filename.disabled = False
                    self.filename2.disabled = False
                    self.attach.disabled = False

                    self.num_iterate()
                except Exception as e:
                    print(e)
                
            else:  #Start new scan
                self.switch_to(self.livetab)
                self.saving = save
                xy_numx = int(xres)
                xy_numy = int(yres)

                if save: #Scan to acquire
                    try:
                        Send_to_Cam('padcom scan_focus 0\n') #Only do one scan
                        Send_to_Cam('filestore 1 5\n') #Save last scan
                        self.scanning = True
                        self.focus.disabled = True
                        self.acquire.text = 'Saving...'
                        self.acquire.state = 'down'
                        self.focus2.disabled = True
                        self.acquire2.text = 'Saving...'
                        self.acquire2.state = 'down'
                        
                        
                        
                        
                        timeout = max(2,xy_numx*xy_numy/1000.0 + 2)
                        Clock.schedule_once(self.scan_finished, timeout)
                    except Exception as e:
                        print(e)
                else:
                    try:
                        Send_to_Cam('padcom scan_focus 1\n') #Keep scanning
                        Send_to_Cam('filestore 0 5\n') #Don't save .raw files
                        self.scanning = True
                        self.acquire.text = 'Save'
                        self.acquire.state = 'normal'
                        self.acquire2.text = 'Save'
                        self.acquire2.state = 'normal'
                        
                        
                    except Exception as e:
                        print(e)
            
            
                            
                
                if frac_x < frac_t/2:
                    frac_x = frac_t/2
                if frac_x > 1 - frac_t/2:
                    frac_x = 1 - frac_t/2
                if frac_y < frac_t/2:
                    frac_y = frac_t/2
                if frac_y > 1 - frac_t/2:
                    frac_y = 1 - frac_t/2
                
                midx = int(rangex*frac_x) + xy_minx
                midy = int(rangey*frac_y) + xy_miny
                
                if xy_numx > 1:
                    xy_stepx = int(frac_t*rangex/xy_numx) + 1
                    xy_startx = int(midx - (xy_numx/2)*xy_stepx)
                    if xy_startx < xy_minx: xy_startx = xy_minx
                else:
                    xy_stepx = 1
                    xy_startx = midx
                    
                if xy_numy > 1:
                    xy_stepy = int(frac_t*rangey/xy_numy) + 1
                    xy_starty = int(midy - (xy_numy/2)*xy_stepy)
                    if xy_starty < xy_miny : xy_starty = xy_miny
                else:
                    xy_stepy = 1
                    xy_starty = midx
                
                
                try:    
                    Send_to_Cam(('Set_Take_n %.8f %.8f %d\n' % (expt, framet, num_fr)))
                    
                    Send_to_Cam(('SetScan %d %d %d %d %d %d\n' % (xy_startx,xy_stepx,xy_numx,xy_starty,xy_stepy,xy_numy)))
                    
                    self.post_name = '_%dx_%dy_%dz_%dstep' % (int(frac_x*100), int(frac_y*100), int(frac_t*100), xy_stepx)
                    
                    fullname = savepath + fname + self.post_name
                    
                    self.fullname = fname
                
                    Send_to_Cam(('Exposure %s\n' % fullname))
                    
                    #Name is fixed for this scan, Disable renaming
                    self.filename.disabled = True
                    self.filename2.disabled = True
                    self.attach.disabled = True
                except Exception as e:
                    print(e)
                
                padgui.Busy = True
                
                timeout = num_cps*num_fr*max(expt+0.00086,framet) + exposeOverhead+hw_overhead          
                #Round timeout up to nearest half second
                timeout = timeout*10
                if timeout % 5 != 0:
                    timeout = 5*(timeout//5) + 5
                timeout = timeout/10            
                Clock.schedule_once(padgui.Timeout, 0)
    
    def num_iterate(self):
        if self.attach.imnum.ptext.text.isdigit() and self.saving:
            self.gui.refresh_save_label()
            
#            try:
#                original = self.fullname
#                new_name = self.filename.text
#                
#                for filename in os.listdir(padgui.Save_Path):
#                    if filename.startswith(original):
#                        os.rename(filename, filename.replace(original, new_name, 1))
#                
#            except Exception as e:
#                print(e)            
            
            digits = len(self.attach.imnum.ptext.text)
            num = int(self.attach.imnum.ptext.text) + 1
            num = str(num)
            for i in range(0, digits-len(num)):
                num = '0' + num
            self.attach.imnum.ptext.text = num
            
            
#                os.rename()
            

Builder.load_file('fnameparam.kv')

class FNameInput(TextInput):
    acceptable_char = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    acceptable_char = acceptable_char + '1234567890-_'
    def insert_text(self, substring, from_undo=False):
        acceptable_char = self.acceptable_char
        if acceptable_char.find(substring) != -1:
            return super(FNameInput, self).insert_text(substring, from_undo=from_undo)
        else:
            return super(FNameInput, self).insert_text('', from_undo=from_undo)

class FNameParam(BoxLayout):
    
    num_order = [0, 0, 0, 0, 0, 0, 0]
    prev_check = [False, False, False, False, False, False, False]
    re_order_recursion = False
    
    def restore_state(self):
        padgui.FNP = self
        padgui.state_restored = False
            
        with open('last_state.csv', 'r') as file:
            reader = csv.reader(file, delimiter=' ', quotechar='|')
            params = []
            for row in reader:
                params.append(row)
                
            self.re_order_recursion = True 
            self.num_order = [int(i) for i in params[1]]
            params[1] = [i if i!= '0' else '' for i in params[1]]
            
            self.imnum.ptext.text = params[0][0]
            self.sample.ptext.text = params[0][1]
            self.mag.ptext.text = params[0][2]
            self.cam.ptext.text = params[0][3]
            self.ap.ptext.text = params[0][4]
            self.conv.ptext.text = params[0][5]
            self.spot.ptext.text = params[0][6]
            
            self.imnum.ord.text = params[1][0]
            self.sample.ord.text = params[1][1]
            self.mag.ord.text = params[1][2]
            self.cam.ord.text = params[1][3]
            self.ap.ord.text = params[1][4]
            self.conv.ord.text = params[1][5]
            self.spot.ord.text = params[1][6]
                   
            self.imnum.pcheck.active = bool(params[2][0]=='True')
            self.sample.pcheck.active = bool(params[2][1]=='True')
            self.mag.pcheck.active = bool(params[2][2]=='True')
            self.cam.pcheck.active = bool(params[2][3]=='True')
            self.ap.pcheck.active = bool(params[2][4]=='True')
            self.conv.pcheck.active = bool(params[2][5]=='True')

            self.re_order_recursion = False            
            
            self.spot.pcheck.active = bool(params[2][6]=='True')
            
            padgui.Save_Path = params[3][0]
        
        padgui.state_restored = True
        
        return None
    
    def re_order(self, checks, orders):
        if self.re_order_recursion:
            return self.num_order
            
        #Prevent program from re-curring while changing parameters            
        self.re_order_recursion = True
            
        param_orders = [self.imnum.ord, self.sample.ord, 
                        self.mag.ord, self.cam.ord, self.ap.ord, 
                        self.conv.ord, self.spot.ord]
                        
        numchecks = len(checks)
        actives = sum(checks)
        
               
        for i in range(0, numchecks):
                
            if self.num_order[i]==0 and checks[i]: #New parameter turned on
                self.num_order[i] = max(self.num_order)+1
                break
                
            if self.num_order[i]!=0 and not checks[i]: #Parameter turned off
                #All values above go down by one
                for j in range(self.num_order[i]+1, actives+2):
                    jindex = self.num_order.index(j)
                    self.num_order[jindex] = self.num_order[jindex] - 1
                    
                #Make turned off value 0
                self.num_order[i] = 0
                break
                
            if self.num_order[i] != (int(param_orders[i].text) if param_orders[i].text!='' else 0): #Change in values
                new_value = int(param_orders[i].text)
                orig_value = self.num_order[i]
                
                if new_value - orig_value > 0:
                    for j in range(orig_value+1, new_value+1):
                        jindex = self.num_order.index(j)
                        self.num_order[jindex] = self.num_order[jindex] - 1
                else:
                    for j in range(orig_value-1, new_value-1, -1):
                        jindex = self.num_order.index(j)
                        self.num_order[jindex] = self.num_order[jindex] + 1
                
                self.num_order[i] = new_value
                break
                
                
                
        
        
        for i in range(0, numchecks):
            param_orders[i].text = str(self.num_order[i]) if self.num_order[i]!= 0 else ''
            
        self.re_order_recursion = False
        return self.num_order
                        
    
    def activeparam(self, checks):
        active_parameters = 0
        if check1:
            active_parameters = active_parameters + 1
        print(active_parameters)
        print(self.active_param)
        return active_parameters
        


class Order(Spinner):
    
    def num_values(self, mvalue):
        values = []
        for i in range(0, mvalue):
            values.append(str(i+1))
#        print(values)
        return values
        

        
        
Builder.load_string("""
<Commands>:
    drag_rectangle: self.x, self.top-50, 200, 50
    drag_timeout: 100000000
    drag_distance: 0
    
    pos: 200, 0

    size: 350, 150
    size_hint_x: None
    size_hint_y: None
    do_default_tab: False
    vmode: False
    gui: self
    
    TabbedPanelItem:
        text: 'Commands'
        on_touch_down: root.gui.put_on_top(root)
        GridLayout:
            cols: 3
            spacing: 0
            Button:
                text: 'Next Image'
                on_release: root.next_image()
            ToggleButton:
                
                state: 'normal' if root.vmode == False else 'down'
                text: 'Video Mode On' if self.state == 'down' else 'Video Mode Off'
                on_release: root.v_mode()
            Button:
                text: 'Take BKG'
                on_release: root.takebkg()
            BoxLayout:
                orientation: 'horizontal'
                ToggleButton:
                    id: logbtn
                    text: 'Log'
                    on_release: root.Lin_Log(logbtn, linbtn)
                ToggleButton:
                    id: linbtn
                    text: 'Linear'
                    on_release: root.Lin_Log(linbtn, logbtn)
            Button:
                text: 'Scale Up'
                on_release: root.Scale((logbtn.state == 'down', linbtn.state == 'down'), 1)
            Button:
                text: 'Scale Down'
                on_release: root.Scale((logbtn.state == 'down', linbtn.state == 'down'), -1)
            BoxLayout:
                orientation: 'horizontal'
                Button:
                    text: 'Power'
                    on_release: root.Power_On()
                ToggleButton:
                    id: insertbtn
                    text: 'Insert'
                    on_release: root.insert_detector(insertbtn)
            Button:
                text: 'ADF'
                on_release: root.ADF()
            Button:
                text: 'BF'
                on_release: root.BF()
            
    TabbedPanelItem:
        text: 'Images'
        
        GridLayout:
            cols: 3
            
            Button:
                text: 'Mask 0 Sum'
                disabled: True if app.active_masks[0] == 'off' else False
                on_release: root.goto_image(0)
                
            Button:
                text: 'Mask 0 DPC X'
                disabled: True if app.active_masks[1] == 'off' else False
                on_release: root.goto_image(1)
            
            Button:
                text: 'Mask 0 DPC Y'
                disabled: True if app.active_masks[2] == 'off' else False
                on_release: root.goto_image(2)
                
            Button:
                text: 'Mask 1 Sum'
                disabled: True if app.active_masks[3] == 'off' else False
                on_release: root.goto_image(3)
                
            Button:
                text: 'Mask 1 DPC X'
                disabled: True if app.active_masks[4] == 'off' else False
                on_release: root.goto_image(4)
                
            Button:
                text: 'Mask 1 DPC Y'
                disabled: True if app.active_masks[5] == 'off' else False
                on_release: root.goto_image(5)
                
            Button:
                text: 'Mask 2 Sum'
                disabled: True if app.active_masks[6] == 'off' else False
                on_release: root.goto_image(6)
                
            Button:
                text: 'Mask 2 DPC X'
                disabled: True if app.active_masks[7] == 'off' else False
                on_release: root.goto_image(7)
            
            Button:
                text: 'Mask 2 DPC Y'
                disabled: True if app.active_masks[8] == 'off' else False
                on_release: root.goto_image(8)
                
            Button:
                text: 'Mask 3 Sum'
                disabled: True if app.active_masks[9] == 'off' else False
                on_release: root.goto_image(9)
                
            Button:
                text: 'Mask 3 DPC X'
                disabled: True if app.active_masks[10] == 'off' else False
                on_release: root.goto_image(10)
            
            Button:
                text: 'Mask 3 DPC Y'
                disabled: True if app.active_masks[11] == 'off' else False
                on_release: root.goto_image(11)
""")

Builder.load_file('takebkg.kv')

class TakeBKG(DragPopup):
    def takebkg(self, filename, numimages):
        self.dismiss()
        numimages = int(numimages)
        filename = filename.strip().replace(' ', '_')
        if filename == '':
            print('No filename given')
        elif numimages < 1:
            print('Number of images must be at least 1')
        else:
            filename = padgui.Save_Path + filename
            if padgui.Busy:
                print('PAD is busy')
                return
            try:
                Send_to_Cam('videomodeoff \n')
                
                Send_to_Cam('padcom milbacksub 0 \n')
                
                Send_to_Cam(('Set_Take_n %.8f %.8f %d\n' % (expt, framet, numimages)))
                
                Send_to_Cam(('SetAvgExp %s %d \n' % (filename, numimages)))
                
                Send_to_Cam(('Exposure %s\n' % filename), False)
                #Checking for recv later
                timeout = num_cps*numimages*max(expt+0.00086,framet) + exposeOverhead+hw_overhead
                print(timeout)
                #Round timeout up to nearest half second
                timeout = timeout*10
                if timeout % 5 != 0:
                    timeout = 5*(timeout//5) + 5
                timeout = timeout/10
                print(timeout)
                padgui.Busy = True
                Clock.schedule_once(padgui.Timeout, timeout)
                Clock.schedule_once(lambda x: self.setbackground(filename), timeout)
            except Exception as e:
                print(e)
    def setbackground(self, filename):
        try:
            
            #time.sleep(5)
            #sock.recv(4096)
            callback = sock.recv(4096).decode()
            #callback=''
            if callback[0:7]=='     OK':
                print('WE ARE OKAY')
            print(callback[0:7])
            print(callback)
            if True:
                
                Send_to_Cam(('Set_Take_n %.8f %.8f %d\n' % (expt, framet, num_fr)))
                
                Send_to_Cam(('padcom milbackimg %s_avg.tif \n' % filename))
                
                Send_to_Cam('padcom milbacksub 1 \n')
                
            
        except Exception as e:
            print(e)
            
takebkg = TakeBKG()
      
class Commands(DragBehavior, TabbedPanel):
    
    logscale = 7
    logoffset = 0
    nscale = 0
    noffset = 0
    
    def goto_image(self, num):
        try:
            padgui.current_active_mask = num
            Send_to_Cam('padcom scandisp %s\n' % padgui.active_masks[padgui.current_active_mask])
            
            gui = self.parent.parent
            
            live_masks = gui.im
            
            live_masks.masknum.text = 'Mask %d' % int(padgui.current_active_mask/3)
            
        except Exception as e:
            print(e)
    
    def ADF(self):
        try:
            padgui.current_active_mask = 0
            Send_to_Cam('padcom scandisp sum 0\n')
            
            gui = self.parent.parent
            
            live_masks = gui.im
            
            live_masks.masknum.text = 'Mask %d' % int(padgui.current_active_mask/3)
            
        except Exception as e:
            print(e)
            
    def BF(self):
        try:           
            padgui.current_active_mask = 3
            Send_to_Cam('padcom scandisp sum 1\n')
            
            gui = self.parent.parent
            
            live_masks = gui.im
            
            live_masks.masknum.text = 'Mask %d' % int(padgui.current_active_mask/3)
            
        except Exception as e:
            print(e)
            
    def Power_On(self):
        try:
            Send_to_Cam('ldcmndfile empad_power.cmd\n')
            
            Send_to_Cam('ldcmndfile empad_hvon.cmd\n')
            
            #Send_to_Cam('ldcmndfile empad_hvon.cmd\n')
            
        except Exception as e:
            print(e)    
    
    def Lin_Log(self, on, off):
        try:
            if on.text == 'Log' and on.state=='down':
                Send_to_Cam(('padcom loglin 1 %d %d\n' % (self.logscale, self.logoffset)))
                
            elif on.text == 'Linear' and on.state=='down':
                Send_to_Cam(('padcom loglin 0\n'))
                
                Send_to_Cam(('padcom mildisp %d 1 %d\n' % (self.nscale, self.noffset)))
                
            on.state = 'down'
            off.state = 'normal'

        except Exception as e:
            on.state = 'normal'
            off.state = 'normal'
            print(e)
    
    def Scale(self, loglin, shift):
        try:
            if loglin==(True, False): #Change logscale
                tempscale = self.logscale+shift
                tempscale = min(16, tempscale)
                tempscale = max(1, tempscale)
                Send_to_Cam(('padcom loglin 1 %d %d\n' % (tempscale, self.logoffset)))
                self.logscale = tempscale
                
            if loglin==(False, True): #Change linscale
                tempscale = self.nscale+shift
                tempscale = min(16, tempscale)
                tempscale = max(-5, tempscale)
                Send_to_Cam(('padcom mildisp %d 1 %d\n' % (tempscale, self.noffset)))
                self.nscale = tempscale
                
        except Exception as e:
            print(e)
            
    def next_image(self):
        try:
            
            while True:
                padgui.current_active_mask = int((padgui.current_active_mask + 1)%len(padgui.active_masks))
                image = padgui.active_masks[padgui.current_active_mask]
                
                if image != 'off':
                    break
                
            Send_to_Cam('padcom scandisp %s\n' % padgui.active_masks[padgui.current_active_mask])
            
            gui = self.parent.parent
            
            live_masks = gui.im
            
            live_masks.masknum.text = 'Mask %d' % int(padgui.current_active_mask/3)
            
        except Exception as e:
            print(e)
    def v_mode(self):
        if self.vmode:
            try:
                Send_to_Cam('videomodeoff\n')
                
                self.vmode = not self.vmode
            except:
                self.vmode = not self.vmode
                self.vmode = not self.vmode
        else:
            try:
                Send_to_Cam(('videomodeon %.8f\n' % expt))
                
                self.vmode = not self.vmode
            except:
                self.vmode = not self.vmode
                self.vmode = not self.vmode
    def takebkg(self):
        takebkg.open()
        
    def insert_detector(self, insertbtn):
        try:
            if insertbtn.state == 'down':
                Send_to_Cam('padcom insert 1\n')
            else:
                Send_to_Cam('padcom insert 0\n')
        except:
            try:
                Send_to_Cam('padcom insert 0\n')
            except:
                pass
            insertbtn.state = 'normal'

Builder.load_string("""

<Gui>:

    im: im.__self__
    imt: imt
    setac: setac.__self__
    setact: setact
    com: com.__self__
    comt: comt
    workspace: workspace
    serverpop: serverpop.__self__
    connect_status: connect_status
    file_open: file_open.__self__
    debug: debug.__self__
    fnp: fnp.__self__
    im_label: im_label.__self__
    recently_saved: recently_saved
    
    orientation: 'vertical'
        
    ActionBar:
        height: 25
        size_hint_y: None
        
        ActionView:
            
            ActionPrevious:
                width: 0
                height: 0
                size_hint: None, None
                with_previous: False
                
            ActionGroup:
                text: 'File'
                mode: 'spinner'
                
                ActionButton:
                    text: 'Open Raw'
                    on_release: file_open.open()

                ActionButton:
                    text: 'Quit'
                    on_release: app.stop()

            ActionGroup:
                text: '  Windows  '
                mode: 'spinner'

                ActionToggleButton:
                    id: imt
                    text: 'Masks'
                    state: 'down'
                    on_release: root.WindowToggle(window = 'im')
                
                ActionToggleButton:
                    id: setact
                    text: 'Scan'
                    state: 'down'
                    on_release: root.WindowToggle(window = 'setac')
                    
                ActionToggleButton:
                    id: comt
                    text: 'Commands'
                    state: 'down'
                    on_release: root.WindowToggle(window = 'com')

            ActionGroup:
                text: 'Server'
                mode: 'spinner'

                ActionButton:
                    text: 'Options'
                    on_release: serverpop.open()

                ActionToggleButton:
                    id: connect_status
                    state: 'normal' if not serverpop.connected else 'down'
                    text: 'Connect' if not serverpop.connected else 'Disconnect'
                    on_release: root.connect_to_server()
                    
                ActionButton:
                    text: 'Debug'
                    on_release: debug.open()
    
    ActionBar:
        height: 25
        size_hint_y: None

        ActionView:

            ActionPrevious:
                width: 0
                height: 0
                size_hint: None, None
                with_previous: False

            ActionButton:
                icon: 'Folder-128.png'
                on_press: file_open.open()

            ActionButton:
                icon: 'Gnome-Network-Server-64.png'
                on_press: root.connect_to_server()
            
            ActionButton:
                icon: 'camera.png'
                on_press: root.vmode()
            
        
        
    FloatLayout:
        id: workspace
        SetMasks:
            gui: root
            id: im
            pos: 715, 25
            
        SetScan:
            gui: root
            id: setac
            attach: fnp
            aparam: fnp.aparam
            oparam: fnp.oparam
            tparam: fnp.tparam
            pos: 0, 170
            connected: serverpop.connected
            
        Label:
            id: recently_saved
            fname: setac.filename.text
            text: 'Recently saved file:'
            size: self.texture_size
            size_hint: None, None
            pos: setac.x, setac.y-20
        FNameParam:
            id: fnp
            dock: setac
            pos: setac.right, setac.y
            
        Label:
            text: 'Connected to %s port %s' % (serverpop.ip, serverpop.port) if serverpop.connected else 'Not connected'
            pos_hint: {'right': 1, 'y': 0.0}
            size: self.texture_size
            size_hint: None, None
        Commands:
            gui: root
            id: com
            pos: 715, 350
            
        Label:
            id: im_label
            pos: com.x+10, com.y-25
            text: root.current_image(app.current_active_mask)
            size_hint: None, None
            size: self.texture_size
            halign: 'left'            
            
    DragPopup:
        id: serverpop
        title: 'Server Options'
        size: 400, 2*ipaddress.minimum_height + 100
        size_hint: None, None
        port: portnum.text
        ip: ipaddress.text
        connected: False
        BoxLayout:
            orientation: 'vertical'
            Widget:
                height: 10
                size_hint_y: None
            BoxLayout:
                orientation: 'horizontal'
                height: ipaddress.minimum_height
                size_hint_y: None
                Label:
                    text: 'IP'
                    width: 50
                    size_hint_x: None
                TextInput:
                    id: ipaddress
                    text: 'localhost'
                    multiline: False
                    height: 30
                    size_hint_y: None
            BoxLayout:
                orientation: 'horizontal'
                height: portnum.minimum_height
                size_hint_y: None
                Label:
                    text: 'Port'
                    width: 50
                    size_hint_x: None
                TextInput:
                    id: portnum
                    text: '41234'
                    multiline: False
                    height: 30
                    size_hint_y: None
            Button:
                text: 'Ok'
                size: 50, 25
                size_hint: None, None
                on_release: serverpop.dismiss()
                
    DragPopup:
        id: file_open
        title: 'Open File'
        size: 500, 500
        size_hint: None, None
        auto_dismiss: False
        drives: drives
        BoxLayout:
            orientation: 'vertical'
            FileChooserListView:
                id: fchoose
                filters: ['*.raw']
                rootpath: file_open.drives.text
                path: file_open.drives.text
            BoxLayout:
                orientation: 'horizontal'
                height: 50
                size_hint_y: None
                Spinner:
                    id: drives
                    size: 50, 50
                    size_hint: None, None
                Button:
                    size: 50, 50
                    size_hint: None, None
                    text: 'Load'
                    on_release: root.Load_File(fchoose)
                Button
                    size: 50, 50
                    size_hint: None, None
                    text: 'Close'
                    on_release: file_open.dismiss()
    DragPopup:
        id: debug
        title: 'Send Custom Commands'
        size: cmd.width + 25, cmd.minimum_height + 90
        size_hint: None, None
        BoxLayout:
            orientation: 'vertical'
            TextInput:
                id: cmd
                size: 300, 30
                size_hint: None, None
            BoxLayout:
                orientation: 'horizontal'
                Button:
                    text: 'Send'
                    size: 50, 25
                    size_hint: None, None
                    on_release: root.send_cmd(cmd)
                Button:
                    text: 'Close'
                    size: 50, 25
                    size_hint: None, None
                    on_release: debug.dismiss()
            
                        
""")

class Gui(BoxLayout):
    im = ObjectProperty(None)
    imt = ObjectProperty(None)
    setac = ObjectProperty(None)
    setact = ObjectProperty(None)
    com = ObjectProperty(None)    
    comt = ObjectProperty(None)
    workspace = ObjectProperty(None)
    serverpop = ObjectProperty(None)
    file_open = ObjectProperty(None)
    connect_status = ObjectProperty(None)
    fnp = ObjectProperty(None)
    
    def put_on_top(self, obj):
        
        self.workspace.remove_widget(obj)
        self.workspace.add_widget(obj)
        if obj == self.setac and self.setac.dockbtn.state == 'down':
            self.workspace.remove_widget(self.fnp)
            self.workspace.add_widget(self.fnp)
    
    def __init__(self, **kwargs):
        super(Gui, self).__init__(**kwargs)
        self.remove_widget(self.serverpop)
        self.remove_widget(self.file_open)
        self.remove_widget(self.debug)
        self.workspace.remove_widget(self.fnp)
        self.workspace.add_widget(self.fnp)
        self.setac.dockbtn.state = 'down'
        self.setac.dockbtn2.state = 'down'
        self.connect_to_server()
        
        drives = []
        
        rootpath = os.path.abspath(os.sep)
        
        if platform.system() == 'Windows':
            bitmask = windll.kernel32.GetLogicalDrives()
            
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drives.append(letter + ':\\')
                bitmask >>= 1
        
        if len(drives) != 0:
            self.file_open.drives.text = drives[0]
            self.file_open.drives.values = drives
        else:
            self.file_open.drives.text = rootpath
            self.file_open.drives.values = rootpath
            
    
    def current_image(self, active):      
        c_image = ['Mask 0 Sum', 'Mask 0 DPC X', 'Mask 0 DPC Y', 
                   'Mask 1 Sum', 'Mask 1 DPC X', 'Mask 1 DPC Y',
                   'Mask 2 Sum', 'Mask 2 DPC X', 'Mask 2 DPC Y',
                   'Mask 3 Sum', 'Mask 3 DPC X', 'Mask 3 DPC Y',]
                   
        print(padgui.current_active_mask)
        return 'Current Image: %s' % c_image[active]
        
    def dock(self, btn):
        if btn.state=='down':
            self.workspace.add_widget(self.fnp)
            self.setac.dockbtn.state = 'down'
            self.setac.dockbtn2.state = 'down'
        else:
            self.workspace.remove_widget(self.fnp)
            self.setac.dockbtn.state = 'normal'
            self.setac.dockbtn2.state = 'normal'
    
    def send_cmd(self, text):
        try:
            msg = text.text
            msg = msg + '\n'
            Send_to_Cam(msg)
            text.text = ''
        except Exception as e:
            print(e)
    
    def connect_to_server(self):
        server_address = (self.serverpop.ip, int(self.serverpop.port))
        global sock
        global connected
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        if self.serverpop.connected:   
            try:
                sock.close()
                self.serverpop.connected = False
                connected = False
            except:
                self.serverpop.connected = False
                connected = False
        else:
            try:
                sock.connect(server_address)
                self.serverpop.connected = True
                connected = True
                Send_to_Cam(('ldcmndfile empadstart_p2_01_2017_06_07.cmd\n'))
                
                Send_to_Cam(('padcom roimask annulus_lr_ud_ 0 64 64 20 64\n'))
                                
                Send_to_Cam(('filestore 1 5\n'))
                
                Send_to_Cam(('padcom roimask box_lr_ud_ 1 64 64 2 2\n'))
                
                
                
            except Exception as e:
                print(e)
                self.serverpop.connected = True
                self.serverpop.connected = False #need to change to update related attributes
                connected = False
            
    def WindowToggle(self, **kwargs):
        tbutton = {
                    'im' : self.imt,
                    'com' : self.comt,
                    'setac' : self.setact
                    }
                    
        wind = {
                'im': self.im,
                'setac': self.setac,
                'com': self.com}
                
        button = tbutton[kwargs['window']]
        windo = wind[kwargs['window']]
        
        if button.state == 'normal':
            self.workspace.remove_widget(windo)
            if windo == self.setac:
                try:
                    self.workspace.remove_widget(self.fnp)
                    self.workspace.remove_widget(self.recently_saved)
                finally:
                    pass
            if windo == self.com:
                try:
                    self.workspace.remove_widget(self.im_label)
                finally:
                    pass
        elif button.state == 'down':
            self.workspace.add_widget(windo)
            if windo == self.setac:
                self.setac.dockbtn.state='normal'
                self.workspace.add_widget(self.recently_saved)
            if windo == self.com:
                self.workspace.add_widget(self.im_label)
        
    def focus(self, **kwargs):
        try:
            Send_to_Cam('filestore 0 5\n')
            
            Send_to_Cam('padcom scan_focus 1\n')
            
        except:
            pass
    
    def vmode(self):
        if self.com.vmode:
            try:
                Send_to_Cam('videomodeoff\n')
                
                self.com.vmode = not self.com.vmode
            except:
                pass
        else:
            try:
                Send_to_Cam(('videomodeon %.8f\n' % expt))
                
                self.com.vmode = not self.com.vmode
            except:
                pass
    
    def Load_File(self, fchoose):
        try:
            fullpath = os.path.join(fchoose.path, fchoose.selection[0])
            subprocess.Popen([sys.executable,"4DBrowserV3_nocanny.py", "%s" % fullpath])
            self.file_open.dismiss()
        except Exception as e:
            print(e)
    
    def refresh_save_label(self):
        self.recently_saved.text = 'Recently saved: %s' % self.recently_saved.fname[0:30]

class PADGUI(App):
    
    Save_Path = StringProperty(os.path.abspath(os.sep))
    FNP = ''
    
    state_restored = False
    Busy = False
    
    active_masks = ListProperty(['sum 0', 'lr 0', 'ud 0', 'sum 1', 'lr 1', 'ud 1', 'off', 'off', 'off', 
                'off', 'off', 'off'])
                
    current_active_mask = NumericProperty(0)
    

    def save_state(self):
        with open('last_state.csv', 'w') as file:
            writer = csv.writer(file, delimiter = ' ', quotechar='|', quoting = csv.QUOTE_MINIMAL)
            writer.writerow(self.FNP.tparam)
            writer.writerow(self.FNP.num_order)
            writer.writerow(self.FNP.aparam)
            writer.writerow([self.Save_Path])
    def dummy(self):
        return self.Save_Path
    def change_save_path(self, pop, fchoose):
        self.Save_Path = fchoose.path
        if self.Save_Path[-1] != os.sep:
            self.Save_Path = self.Save_Path + os.sep
        print(self.Save_Path)
        if self.state_restored == True:
            self.save_state()
            
        pop.dismiss()
    
    def build(self):
        global gui
        self.Save_Path = os.path.dirname(os.path.abspath(__file__)) + os.sep
#        self.Save_Path = '/home/rack/data/temp/'
        #self.Save_Path = '/home/padme/data/guitest/'
        gui = Gui()
        return gui
    
    def on_stop(self, *args):
        sock.close()
        try:
            Send_to_Cam('padcom insert 0\n')
            ser.close()
        except:
            pass
        self.save_state()
        
    def Timeout(self, *args):
        self.Busy = False
#        print('No longer busy')
    
if __name__ == '__main__':
    padgui = PADGUI()
    padgui.run()
    
