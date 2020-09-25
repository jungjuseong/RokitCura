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

        # 선택한 명령어
        self._current_index = -1  
        self._previous_index = -1
                
        self._layer_no = 0
        self._current_layer = -1

        # *** G-code Line(command) 관리 변수
        self._gcode_list = []        

        self._StartOfStartCodeIndex = -1
        self._EndOfStartCodeIndex = None

        self._tool_index = -1
        self._tool_code = ''
        self._successive_uv = False

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

                modified_gcodes = self._P.getUVCode(self._previous_index,self._current_index, self._current_layer) + '\n' + modified_gcodes.replace('{end_code}', self.END_CODE)

            else:
                modified_gcodes = self._convertOneLayerGCode(modified_gcodes, isStartCode=True)     

            self._gcode_list[index] = self._P.removeRedundencyGCode(modified_gcodes)

        if self._build_plate_type == 'Well Plate':
            self._cloneWellPlate()


    def _getLayerNo(self, z_value, extruder_index) -> int:
        return int(round((z_value - self._Q.layer_height_0) / self._Q.layer_heights[extruder_index]))

    def _getDistance(self, last_pos, next_pos):
        print_distance = 0
        if last_pos is not None:
            print_distance = distance.euclidean(last_pos, next_pos)
        
        self._current_position = next_pos
        return print_distance

    def _getNextLocation(self, match):
        return [float(match.group(2)), float(match.group(3))]

    def _convertOneLayerGCode(self,gcodes,isStartCode=False) -> str:

        gcode_list = gcodes.split('\n')
        for index, gcode in enumerate(gcode_list):

            # tool changed
            extruder = self._P.getMatched(gcode, [self._P.D])
            if extruder:
                self._current_index = int(extruder.group(1))
                self._tool_code = self._P.getExtruderSetup(self._previous_index, self._current_index, self._layer_no)                
                self._tool_index = index

                if self._previous_index == -1: # first tool
                    gcode_list[index] = self._tool_code

                continue

            # layer changed
            layer = self._P.getMatched(gcode, [self._P.G0_Z_OR_C])
            if layer:
                self._current_layer = self._getLayerNo(float(layer.group(1)), self._current_index)

                uvcode = ''
                if self._current_layer > 0 or self._previous_index != -1:
                    uvcode = self._P.getUVCode(self._previous_index, self._current_index, self._current_layer)

                if self._previous_index != self._current_index: # tool changed
                    if self._previous_index != -1:
                        if self._successive_uv and uvcode != '':
                            uvcode = ''
                            self._successive_uv = False

                        gcode_list[self._tool_index] = '{uvcode}{tool}'.format(
                            uvcode=uvcode, 
                            tool=self._tool_code
                        )
                    self._previous_index = self._current_index
                else:
                    if uvcode != '':
                        gcode_list[index] = '{uvcode}{bed_pos}{layer}'.format(
                            uvcode=uvcode,
                            bed_pos=self._P.getBedPos(self._current_index),
                            layer=gcode_list[index]
                        )
                        self._successive_uv = True
                    else:
                        self._successive_uv = False
                
               
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