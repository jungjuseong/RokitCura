# Copyright (c) 2020 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from string import Formatter
from enum import IntEnum
from UM.Logger import Logger
from typing import Any, cast, Dict, List, Optional, Set
import re
import copy
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
        self._build_plate = self._Q.getGlobalContainerStackProperty('machine_build_dish_type')
        self._build_plate_type = self._build_plate[:self._build_plate.find(':')]

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

        # for UV
        self._tool_initial_layers = [-1,-1,-1,-1,-1,-1] # 툴이 최초로 시작한 레이어 번호
        self._tool_index = -1
        self._logical_layer = 0
        self._real_layer = 0
        self._before_layer_use_uv = False

        self._hopping_list = []
        self._clone_list = []

        self.StartCodeBegin = ';(*** start of start code for Dr.Invivo 4D6)'
        self.StartCodeEnd = ';(*** end of start code for Dr.Invivo 4D6)'

        self.EndCodeBegin = ';(*** start of end code for Dr.Invivo 4D6)'
        self.EndCodeEnd = ';(*** end of end code for Dr.Invivo 4D6)'

    def findKeyword(self, list, keyword) -> int:
        for index, word in enumerate(list): 
            if keyword in word:
                return index
        return -1

    def getHoppingList(self,number_of_walls,number_of_rows,spacing):

        travel_forward = True

        self._hopping_list.append(";NO_HOPPING\n")
        for well in range(1, number_of_walls): # (6,12,24,48,96)
            if well % number_of_rows == 0:
                direction = 'X'
                distance = spacing
                travel_forward = not travel_forward
            else:
                direction = 'Y'
                distance = -spacing if travel_forward else spacing

            (x,y) = (distance, 0.0) if direction == 'X' else (0.0, distance)

            hopping = ';HOPPING - {comment}{g0c30}{g0xy}{g92x0y0};END'.format(
                    comment=';Well No: %d\n' % well,
                    g0c30=self._G['G0_C30'],
                    g0xy=self._G['G0_X_Y'] % (x,y),
                    g92x0y0=self._G['G92_X0_Y0']
                )                        
            self._hopping_list.append(hopping.strip())

        return self._hopping_list

    def cloneWellPlate(self, gcode_list, travel):

        number_of_walls = int(travel['number_of_walls'])
        number_of_rows = int(travel['number_of_rows'])
        spacing = travel['spacing']

        chunk_list = []
        insert_here = -1
        for index, line in enumerate(gcode_list):
            if self.EndCodeBegin in line:
                insert_here = index
            chunk_list.extend(line.split('\n'))

        start_position = self.findKeyword(chunk_list,';BODY_START') + 1
        end_position = self.findKeyword(chunk_list, self.EndCodeBegin)
        body = '\n'.join(chunk_list[start_position:end_position]).strip()

        hopping_list = self.getHoppingList(number_of_walls,number_of_rows,spacing)

        for well in range(1, number_of_walls): # (6,12,24,48,96)
            self._clone_list.append(hopping_list[well] + '\n' + body)

        gcode_list[insert_here] = '\n'.join(self._clone_list) + gcode_list[insert_here]
        
    def run(self, gcode_list):

        for index, gcodes in enumerate(gcode_list):
            m_code = gcodes

            if self.StartCodeBegin in gcodes:
                m_code = self._convertOneLayerGCode(m_code)     
                m_code = self._P.replaceLayerInfo(m_code)
                if self._Q.dispensor_enable:
                   m_code = self._P.replaceDispenserSetupCode(m_code)
            elif self.EndCodeBegin in gcodes:                
                m_code = gcodes[gcodes.find(self.EndCodeBegin):gcodes.rfind(self.EndCodeEnd)] + self.EndCodeEnd
                m_code = '\n' + m_code.replace('{end_code}', self.END_CODE)
                gcode_list[index-1] += self._P.getUVCode(self._current_tool, self._logical_layer,self._real_layer)
            else:
                m_code = self._convertOneLayerGCode(m_code)     

            gcode_list[index] = self._P.removeRedundencyGCode(m_code)

        if self._build_plate_type == 'Well Plate':
            travel = {}
            for index in range(self._build_dish_model.count):
                dish = self._build_dish_model.getItem(index)
                if dish['product_id'] == self._build_plate:
                   travel = dish['travel'] # Build plate가 정해짐
                   break
            
            self.cloneWellPlate(gcode_list, travel)

    def _getLayerNo(self, z_value, tool) -> int:
        return int(round((z_value - self._Q.layer_height_0) / self._Q.layer_heights[tool]))

    def _convertOneLayerGCode(self,gcodes) -> str:

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
                    bed_pos = self._P.getBedPos(self._current_tool)
                    reset_height = (self._G['G0_Z40_C30_F420'] + self._G['M29_B']) #if self._current_tool > 0 else ''

                    if uvcode != '' and self._before_layer_use_uv == False:
                        gcode_list[self._tool_index] = uvcode + bed_pos + gcode_list[self._tool_index]
                    else:
                        gcode_list[self._tool_index] = reset_height + bed_pos + gcode_list[self._tool_index]
                    self._before_layer_use_uv = False
                    self._previous_tool = self._current_tool
                else: # layer changed
                    new_logical_layer = self._real_layer - self._tool_initial_layers[self._current_tool]
                    if self._logical_layer != new_logical_layer:
                        self._logical_layer = new_logical_layer
                        uvcode = self._P.getUVCode(self._current_tool, self._logical_layer - 1, self._real_layer - 1)
                        if uvcode != '':
                            gcode_list[index] = uvcode + '{bed_pos}{lower_b_axis}{layer}'.format(
                                bed_pos = self._P.getBedPos(self._current_tool),
                                lower_b_axis = self._G['G0_B15_F300'] if self._current_tool > 0 else '',
                                layer = gcode_list[index])
                            self._before_layer_use_uv = True
                    else:
                        self._before_layer_use_uv = False
               
        return '\n'.join(gcode_list)
    