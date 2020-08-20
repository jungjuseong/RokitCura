# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from UM.Logger import Logger
from PyQt5.QtCore import Qt, QPointF
import cura.CuraApplication  # Imported like this to prevent circular dependencies.

class RokitGCodeModel():

    GCODE = {
        "G90_G0_XY_ZERO": "G90 G0 X0.0 Y0.0\n",
        "G90_G0_X_Y": "G90 G0 X%.2f Y%.2f\n",
        
        "G90_G0_C": "G90 G0 C%.2f\n",
        "G0_C0": "G0 C0.00\n",
        "G90_G0_C_RESET": "G90 G0 C-30.0\n",

        "G0": "G0\n",
        "G0_Z": "G0 Z%.2f\n",
        "G0_Z0": "G0 Z0.00\n",
        "G0_Z_RESET": "G0 Z-40.0 C0.0\n",
        
        "G91_G0_X_Y": "G91 G0 X%.2f Y%.2f\n",
        "G91_G0_X": "G91 G0 X%.2f\n",
        "G91_G0_Y": "G91 G0 Y%.2f\n",

        "G92_X0_Y0": "G92 X0.0 Y0.0\n",
        "G92_X_Y": "G92 X%.2f Y%.2f\n",
        "G92_Z0": "G92 Z0.0\n",
        "G92_C0": "G92 C0.0\n",

        "G0_X_Y": "G0 X%.2f Y%.2f\n",
        "G0_A0_F600": "G0 A0.00 F600\n",
        "G0_B0_F300": "G0 B0.00 F300\n",
        "G0_A_F600": "G0 A%.2f F600\n",

        "M29_B": "M29 B\n",

        "G78_B15_F300": "G78 B50. F300\n",   
        
        "UV_A_On": "M172\n",
        "UV_A_Off": "M173\n",
        "UVDisinfectionOn": "M174\n",
        "UVDisinfectionOff": "M175\n",

        "UVChannel": "M381 %d\n",
        "TimerLED": "M384\n",
        "UVDimming": "M385 %.1f\n",
        "UVTime": "M386 %.1f\n",

        "SetPrintTemperature": "M308 %s",
        "SetWaitingTemperature": "M109 ; wait for temperature",

        "SetShotTime": "M303 %s",
        "SetVacuumTime": "M304 %s",
        "SetInterval": "M305 %s",
        "SetShotPressure": "M306 %s",
        "SetVacuumPressure": "M307 %s",

        "StartShot": "M301\n",
        "StopShot": "M330\n"
    }