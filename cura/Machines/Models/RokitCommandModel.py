# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from UM.Logger import Logger
from PyQt5.QtCore import Qt, QPointF
import cura.CuraApplication  # Imported like this to prevent circular dependencies.

class RokitCommandModel():

    # ChangeAtZ 참고
    ChangeStrings = {
        "moveToOriginCenter": "G90 G0 X0.0 Y0.0\n",
        "moveToAbsoluteXY": "G90 G0 X%.2f Y%.2f\n",
        "moveToAbsolute": "G90 G0 %c%.2f\n",

        "moveToRelativeXY": "G91 G0 X%.2f Y%.2f\n",
        "moveToRelative": "G91 G0 %c%.2f\n",

        "changeAbsoluteAxisToCenter": "G92 X0.0 Y0.0\n",
        "changeToNewAbsoluteAxis": "G92 X%.2f Y%.2f\n",
        "csetNewAbsoluteAxis": "G92 E0\n",

        "uvCuringOn": "M172\n",
        "uvCuringOff": "M173\n",
        "uvDisinfectOn": "M174\n",
        "uvDisinfectOff": "M175\n",
        
        "uvCuring" : {'on' : "M172\n", 'off' : "M173\n"},
        "uvDisinfect" : {'on' : "M174\n", 'off' : "M175\n"},

        "uvTime": "G4 P%d\n",

        "printTemperature": "M308 %s",
        "waitingTemperature": "M109",

        "shotTime": "M303 %s",
        "vacuumTime": "M304 %s",
        "interval": "M305 %s",
        "shotPressure": "M306 %s",
        "vacuumPressure": "M307 %s",

        "shotStart": "M301\n",
        "shotStop": "M330\n",

        "move_A_Coordinate": "G0 A%.2f F%d\n",
        "move_B_Coordinate": "G0 B%.2f\n",
        
        "selectRightExtruder": "D",
        "selectLeftExtruder": "D6",        

        "originCenter": "X0.0 Y0.0",
        "restoreToOriginState": "G0 X0 Y0 Z0 A0 F800\n",


        "speed": "M220 S%f\n",
        "flowrate": "M221 S%f\n",
        "flowrateOne": "M221 T0 S%f\n",
        "flowrateTwo": "M221 T1 S%f\n",
        "bedTemp": "M140 S%f\n",
        "extruderOne": "M104 S%f T0\n",
        "extruderTwo": "M104 S%f T1\n",
        "fanSpeed": "M106 S%d\n",

        "default_speed" : 10,
        "move_speed" : 20,

        "selected_extruder" : { "D1" : 0, "D2" : 72, "D3" : -72, "D4" : -144, "D5" : -216 },       

        "static_uv_position" : QPointF(42.5 , 0.0)
    }



    # target_values = {
    #     "speed": self.getSettingValueByKey("e2_speed"),
    #     "printspeed": self.getSettingValueByKey("f2_printspeed"),
    #     "flowrate": self.getSettingValueByKey("g2_flowrate"),
    #     "flowrateOne": self.getSettingValueByKey("g4_flowrateOne"),
    #     "flowrateTwo": self.getSettingValueByKey("g6_flowrateTwo"),
    #     "bedTemp": self.getSettingValueByKey("h2_bedTemp"),
    #     "extruderOne": self.getSettingValueByKey("i2_extruderOne"),
    #     "extruderTwo": self.getSettingValueByKey("i4_extruderTwo"),
    #     "fanSpeed": self.getSettingValueByKey("j2_fanSpeed")}

    # extruder = {
    # }

    old = {
        "speed": -1, 
        "flowrate": 100, 
        "flowrateOne": -1, 
        "flowrateTwo": -1, 
        "platformTemp": -1, 
        "extruderOne": -1,
        "extruderTwo": -1, 
        "bedTemp": -1, 
        "fanSpeed": -1, 
        "state": -1}
    # twLayers = self.getSettingValueByKey("d_twLayers")

    # self.setItems(item_list)
