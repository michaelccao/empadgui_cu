#!/bin/bash
gnome-terminal --working-directory=/home/empad/tvx_64/tvx/camera/camserver -e ./camserver
cd /home/empad/Desktop/empadgui_cu-master
python empadgui_cu.py
