# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from UM.Logger import Logger
from PyQt5.QtCore import Qt, QPointF
import cura.CuraApplication  # Imported like this to prevent circular dependencies.

class RokitGCodeModel():

    TranslateToGCode = {
        "MoveToOrigin": "G90 G0 X0.0 Y0.0\n",
        "MoveToXY": "G90 G0 X%.2f Y%.2f\n",
        "MoveToZ": "G90 G0 Z%.2f\n",
        "MoveToC": "G90 G0 C%.2f\n",
        "MoveTo": "G90 G0 %c%.2f\n",
        "ResetAxis": "G90 G0 Z-40.0 C-40.0\n",

        "RMoveToXY": "G91 G0 X%.2f Y%.2f\n",
        "RMoveToZ": "G91 G0 Z%.2f\n",
        "RMoveTo": "G91 G0 %c%.2f\n",

        "SetAxisOrigin": "G92 X0.0 Y0.0\n",
        "SetToNewAxis": "G92 X%.2f Y%.2f\n",
        "ResetZAxisToZeo": "G92 Z0.0\n",
        "setZAxisToBed": "G92 Z40.0\n",
        "ResetCAxisToZeo": "G92 C0.0\n",
        "setCAxisToBed": "G92 C30.0\n",

        "MoveToAF": "G0 A%.2f F%d\n",
        "MoveToBF": "G0 B%.2f F%d\n",
        "MoveToB": "G0 B%.2f\n",
        "SetNewAxis": "G92 E0\n",
        "GoToDetectedLimit": "G78 B15.3 F300\n",   
        
        "UVCuringOn": "M172\n", 
        "UVCuringOff": "M173\n",
        "UVDisinfectionOn": "M174\n",
        "UVDisinfectionOff": "M175\n",

        "UVTime": "G4 P%d\n",

        "SetPrintTemperature": "M308 %s",
        "SetWaitingTemperature": "M109",

        "SetShotTime": "M303 %s",
        "SetVacuumTime": "M304 %s",
        "SetInterval": "M305 %s",
        "SetShotPressure": "M306 %s",
        "SetVacuumPressure": "M307 %s",

        "StartShot": "M301\n",
        "StopShot": "M330\n",

        "A_AxisPosition" : { "D1": 0, "D2": -72, "D3": 72, "D4": 144, "D5": 216, "D6": 0 },       
        "UVDevicePosition" : {"x" : 0.0,"y" : 62.0,"z" : 40.0 }
    }

    marlin_codes =  ["M140", "M190", "M104", "M109", "M141", "M205"]
