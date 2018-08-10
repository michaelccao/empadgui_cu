# empadgui_cu
GUI for the Electron Microscope Pixel Array Detector (EMPAD) with Python and Kivy

Packages required:

Kivy

PySerial

Installation:
This is assuming you are installing on the rack computer that FEI provides with the EMPAD.  Software should work out of the box once you have the correct python packages.

1) Download repository and extract empadgui_cu-master folder to the Desktop
2) Move the LaunchPADGUI.desktop icon from inside the folder to the Desktop
3) Double click the LaunchPADGUI shortcut to start the software

Possible adjustments that need to be made:

1) Serial port of the Keithley may be different than what's stored in the code.  If it needs to be changed, go to line 70 and change "serial_address = '/dev/ttyS4'" to "serial_address = 'insert_port_address'"
2) Power On procedure may vary.  Camserver loads two files "empad_power.cmd" and "empad_hvon.cmd" to power the chip.  These files may have slightly different instructions than what FEI is using.  These files are stored in /home/empad/tvx_64/tvx/camera/camserver and FEI software will most likely load different versions of these files.  You can either load those files instead or create your own.  Then change lines 1935 and 1936 from:
  
  Send_to_Cam('ldcmndfile empad_power.cmd\n')
            
  Send_to_Cam('ldcmndfile empad_hvon.cmd\n')
  
to the correct file names.

Using the GUI:
1) Launch using the desktop shortcut
2) Press Power to power the chip.  Process takes about 1-2 minutes.  Watch camserver log to make sure all commands are done executing
3) Press TakeBKG to take background images
4) Press Change Dir button to change save directory.  This is very important on the first run after installation as the current save directory will be wrong.
5) BEFORE DOING THIS, MAKE SURE NO OTHER DETECTOR IS IN THE WAY.  THIS SOFTWARE DOES NOT STOP YOU FROM CRASHING THE EMPAD INTO AN ALREADY PRESENT DETECTOR UNLIKE THE FEI SOFTWARE.  Press Insert to insert detector
6) Press either Live for a continuous scan or Acquire for a single scan that will be saved
6a) While scanning, you can always change whether to stop the scan or save the current ongoing scan.
6b) Never start a new scan until current scan is finished.  Doing so will result in weird data.
