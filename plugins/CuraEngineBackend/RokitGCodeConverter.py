# Copyright (c) 2020 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from string import Formatter
from enum import IntEnum
from UM.Logger import Logger
from typing import Any, cast, Dict, List, Optional, Set
import re
import Arcus #For typing.
from scipy.spatial import distance # <<< 거리를 계산하는 라이브러리 (점과 점사이의 거리) 

from cura.CuraApplication import CuraApplication
from cura.Machines.Models.RokitGCodeModel import RokitGCodeModel
from cura.Machines.Models.RokitBuildDishModel import RokitBuildDishModel
from .RokitPrintQuality import RokitPrintQuality
from .RokitPattern import RokitPattern

class RokitGCodeConverter:
    def __init__(self) -> None:    
      
        self._UV_TEST = False

        self._Q= RokitPrintQuality()
        self._P = RokitPattern()

        g_model = RokitGCodeModel()        
        self._G = g_model.GCODE

        self._build_dish_model = RokitBuildDishModel()

        # 외부 dict
        self._dish = {}

        self._travel= {}
        build_plate = self._Q.getGlobalContainerStackProperty('machine_build_dish_type')
        self._build_plate_type = build_plate[:build_plate.find(':')]
        for index in range(self._build_dish_model.count):
            self._dish = self._build_dish_model.getItem(index)
            if self._dish['product_id'] == build_plate:
                self._travel = self._dish['travel'] # Build plate가 정해짐
                break

        # startcode / endcode
        self.StartOfStartCode = '\n; (*** start of start code for Dr.Invivo 4D6)'
        self.EndOfStartCode = '\n; (*** end of start code for Dr.Invivo 4D6)'

        self.StartOfEndCode = '\n; (*** start of end code for Dr.Invivo 4D6)'
        self.EndOfEndCode = '\n; (*** end of end code for Dr.Invivo 4D6)'

        self.END_CODE = 'M330\n' +\
                    'M29 B\n' +\
                    'G0 Z40.0 C30.0 F460\n' +\
                    'G0 A0.\n' +\
                    'G56 G0 X0.0 Y0.0\n' +\
                    'D6\n' +\
                    'G1 E-1 F300 ; retract the Extruder for release some of the pressure\n' +\
                    'G90 ; absolute positioning\n' +\
                    'M308 27 27 27 27 27 27 27 ; set temperature'


        self._current_tool = -1  
        self._previous_tool = -1
                
        # *** G-code Line(command) 관리 변수
        self._gcode_list = []        

        self._StartOfStartCodeIndex = -1
        self._EndOfStartCodeIndex = None

        # for UV
        self._tool_initial_layers = [-1,-1,-1,-1,-1,-1] # 툴이 최초로 시작한 레이어 번호
        self._tool_index = -1
        self._logical_layer = 0
        self._real_layer = 0
        self._before_layer_use_uv = False

    def setReplacedlist(self, gcode_list) -> None:
        self._gcode_list = gcode_list

    def getReplacedlist(self) -> str:
        return self._gcode_list

    def run(self) -> None:

        for index, gcodes in enumerate(self._gcode_list):
            modified_gcodes = gcodes

            if self.StartOfStartCode in gcodes:
                self._StartOfStartCodeIndex = index
                modified_gcodes = self._convertOneLayerGCode(modified_gcodes, isStartCode=True)     
                modified_gcodes = self._P.replaceLayerInfo(modified_gcodes)
                if self._Q.dispensor_enable:
                   modified_gcodes = self._P.replaceDispenserSetupCode(modified_gcodes)
            
            elif self.StartOfEndCode in gcodes:                
                self._EndOfStartCodeIndex = index if self._EndOfStartCodeIndex is None else self._EndOfStartCodeIndex
                modified_gcodes = self.StartOfEndCode +\
                    gcodes[gcodes.find(self.StartOfEndCode)+len(self.StartOfEndCode):gcodes.rfind(self.EndOfEndCode)] +\
                    self.EndOfEndCode + '\n'

                modified_gcodes = self._P.getUVCode(self._current_tool, self._logical_layer,self._real_layer) +\
                     '\n' + modified_gcodes.replace('{end_code}', self.END_CODE)

            else:
                modified_gcodes = self._convertOneLayerGCode(modified_gcodes, isStartCode=True)     

            self._gcode_list[index] = self._P.removeRedundencyGCode(modified_gcodes)

        if self._build_plate_type == 'Well Plate':
            self._cloneWellPlate()


    def _getLayerNo(self, z_value, tool) -> int:
        return int(round((z_value - self._Q.layer_height_0) / self._Q.layer_heights[tool]))

    def _convertOneLayerGCode(self,gcodes,isStartCode=False) -> str:

        gcode_list = gcodes.split('\n')
        for index, gcode in enumerate(gcode_list):

            # tool changed
            tool_match = self._P.getMatched(gcode, [self._P.D])
            if tool_match:
                self._current_tool = int(tool_match.group(1))                    
                if (self._current_tool == 6):
                    self._current_tool = 0
                self._tool_index = index

                continue

            # layer changed
            layer_match = self._P.getMatched(gcode, [self._P.G0_Z_OR_C])
            if layer_match:
                self._real_layer = self._getLayerNo(float(layer_match.group(1)), self._current_tool)

                # 처음 툴이 나왔을 때 레이어를 기록
                if self._tool_initial_layers[self._current_tool] == -1:
                    self._tool_initial_layers[self._current_tool] = self._real_layer

                if self._previous_tool == -1:
                    self._previous_tool = self._current_tool
                    continue
                         
                if self._previous_tool != self._current_tool: # tool changed
                    self._logical_layer = self._real_layer - self._tool_initial_layers[self._previous_tool]
                    uvcode = self._P.getUVCode(self._previous_tool, self._logical_layer, self._real_layer)
                    if uvcode != '' and self._before_layer_use_uv == False:
                        gcode_list[self._tool_index] = uvcode + gcode_list[self._tool_index]
                    self._before_layer_use_uv = False
                    self._previous_tool = self._current_tool
                else: # layer changed
                    self._logical_layer = self._real_layer - self._tool_initial_layers[self._current_tool]
                    uvcode = self._P.getUVCode(self._current_tool, self._logical_layer - 1, self._real_layer - 1)
                    if uvcode != '':
                        gcode_list[index] = uvcode + '{bed_pos}{layer}'.format(bed_pos=self._P.getBedPos(self._current_tool),layer=gcode_list[index])
                        self._before_layer_use_uv = True
                    else:
                        self._before_layer_use_uv = False

               
        return '\n'.join(gcode_list)

    # Well plate 복제 기능
    def _cloneWellPlate(self):

        NumberOfWalls = self._travel['number_of_walls']
        NumberORows = self._travel['number_of_rows']
        HopHeight = self._travel['hop_height']
        ForwardSpaceing = self._travel['spacing']
        BackwardSpacing = -self._travel['spacing']

        self._EndOfStartCodeIndex -= len(self._gcode_list)
        
        from_index = self._StartOfStartCodeIndex + 1
        to_index = self._EndOfStartCodeIndex

        gcode_clone = self._gcode_list[from_index : to_index]
        travel_forward = True

        gcode_body = []
        for well_num in range(1, NumberOfWalls): # Clone number ex) 1 ~ 95
            if well_num % NumberORows == 0:
                direction = 'X'
                distance = ForwardSpaceing
                travel_forward = not travel_forward
            else:
                direction = 'Y'
                distance = BackwardSpacing if travel_forward else ForwardSpaceing

            (x,y) = (distance, 0.0) if direction == 'X' else (0.0, distance)
            gcode_spacing = ';hop_spacing\n' + self._G['G92_E0'] + self._G['G90_G0_C'].format(HopHeight)            
            gcode_spacing += self._G['G90_G0_X_Y'] % (x,y)
            gcode_spacing += self._G['G90_G0_C0']
            gcode_spacing += self._G['G92_X0_Y0']
            gcode_spacing += ';Well Number: %d\n' % well_num

            gcode_clone.insert(0, gcode_spacing)
            self._gcode_list[self._EndOfStartCodeIndex:self._EndOfStartCodeIndex]= gcode_clone # put the clones in front of the end-code
            gcode_clone.remove(gcode_spacing)