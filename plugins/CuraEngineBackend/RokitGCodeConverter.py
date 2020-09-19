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
                    'G0 Z40.0 C30.0\n' +\
                    'G0 A0.\n' +\
                    'G56 G0 X0.0 Y0.0\n' +\
                    'G1 E-1 F300 ; retract the Extruder for release some of the pressure\n' +\
                    'G90 ; absolute positioning\n' +\
                    'M308 0 0 0 0 0 0 27 ; set temperature\n' +\
                    'M109; wait for temperatur\n' +\
                    'M73 ; motor drive off\n' +\
                    'M176 ; embed compressor OFF'

        # 선택한 명령어
        self._current_index = -1  
        self._enabled_extruder_list = [] 

        self._previous_index = -1
        self._current_nozzle = ''

        self._accummulated_distance = 0
        self._is_retraction_moment = False

        self._last_E = 0.0
        self._retraction_index = -1
                
        self._current_layer = -1

        # *** G-code Line(command) 관리 변수
        self._gcode_list = []        
        self._last_extrusion_amount = 0


        self._is_shot_moment = True
        self._StartOfStartCodeIndex = -1
        self._EndOfStartCodeIndex = None

        self._hasAirCompressorOn = False
        self._extruderSetupCode = '' # 처음 나오는 extruder

    def setReplacedlist(self, gcode_list) -> None:
        self._gcode_list = gcode_list

    def getReplacedlist(self) -> str:
        return self._gcode_list

    def _setExtruder(self, gcode) -> str:
        self._previous_index = self._current_index
        self._current_index = self._P.getExtruderIndex(gcode)
        self._addToEnabledExtruders(self._current_index)       
        return self._Q.getVariantName(self._current_index)
    
    # 사용된 익스트루더 index 기록
    def _addToEnabledExtruders(self, current_index) -> None:
        if current_index not in self._enabled_extruder_list:
            self._enabled_extruder_list.append(current_index) # [0,1,2,3,4,5]

    def run(self) -> None:

        for index, gcodes in enumerate(self._gcode_list):
            modified_gcodes = gcodes

            if ';FLAVOR:Marlin' in gcodes:
                modified_gcodes = gcodes.replace(';FLAVOR:Marlin', ';F/W : 7.7.1.x')

            elif self.StartOfStartCode in gcodes:
                self._StartOfStartCodeIndex = index
                modified_gcodes = gcodes.replace('Cura_SteamEngine', 'OrganRegenerator_Engine')
                modified_gcodes = self._convertOneLayerGCode(modified_gcodes, isStartCode=True)     
                modified_gcodes = self._P.replaceLayerInfo(modified_gcodes)
                if self._Q.dispensor_enable:
                   modified_gcodes = self._P.replaceDispenserSetupCode(modified_gcodes)

            elif self.StartOfEndCode in gcodes:
                
                self._EndOfStartCodeIndex = index if self._EndOfStartCodeIndex is None else self._EndOfStartCodeIndex
                modified_gcodes = self.StartOfEndCode +\
                    gcodes[gcodes.find(self.StartOfEndCode)+len(self.StartOfEndCode):gcodes.rfind(self.EndOfEndCode)] +\
                    self.EndOfEndCode + '\n'

                modified_gcodes = self.getUVCode(self._current_index, self._current_layer) + '\n' + modified_gcodes.replace('{end_code}', self.END_CODE)

            elif gcodes.startswith(';LAYER:'):    
                modified_gcodes = self._convertOneLayerGCode(gcodes)

            elif self._P.G1_F_E.match(gcodes) is not None:
                self._EndOfStartCodeIndex = index
                modified_gcodes = self._convertOneLayerGCode(gcodes)

            self._gcode_list[index] = self._P.removeRedundencyGCode(modified_gcodes)

        startSetupCode = self._P.removeRedundencyGCode(self._extruderSetupCode)
        self._gcode_list[self._StartOfStartCodeIndex] += '\n;Start point\n{start_setup}; ==== setup end\n\n{well_num}'.format(
            start_setup = startSetupCode,
            well_num = ";Well Number: 0\n" if self._build_plate_type == 'Well Plate' else "")

        if self._build_plate_type == 'Well Plate':
            self._cloneWellPlate()

    def _getPressureOn(self, gcode, reverse=False) -> str:
        if self._hasAirCompressorOn == False:
            self._hasAirCompressorOn = True
            if reverse:
                gcode = self._G['M301'] + gcode
            else:
                gcode += self._G['M301']
        return gcode

    def _getPressureOff(self, gcode) -> str:
        if self._hasAirCompressorOn:
            gcode = self._G['M330'] + gcode
            self._hasAirCompressorOn = False
        return gcode

    # UV 명령어 삽입
    def getUVCode(self, extruder_index, layer_index) -> str:

        if self._Q.uv_enable_list[extruder_index] == True:
            per_layer = self._Q.uv_per_layer_list[extruder_index]
            start_layer = self._Q.uv_start_layer_list[extruder_index]
            layer = layer_index - start_layer + 1

            if layer >= 0 and (layer % per_layer) == 0:
                return ';UV - Layer:{layer}, start:{start_layer}, per:{per_layer}\n{uvcode}'.format(
                    layer=layer_index, 
                    start_layer=start_layer, 
                    per_layer=per_layer, 
                    uvcode=self._P.UV_Code(extruder_index))
        return ''

    # X Y를 인식하는 모든 부분에 추가함. (G1과 G0일 때의 x,y 좌표 수용)
    def _getTravelDistance(self, current_pos, next_pos):
        if current_pos is not None:
            self._accummulated_distance += distance.euclidean(current_pos, next_pos)
        if self._accummulated_distance > self._Q.retraction_min_travel[0]:
            self._is_retraction_moment = True
            self._accummulated_distance = 0
        return next_pos

    def _convertOneLayerGCode(self,gcodes,isStartCode=False) -> str:

        current_position = None
        before_layer_uvcode = ''
        uvcode =''
        have_first_extruder = False

        gcode_list = gcodes.split('\n')
        for index, gcode in enumerate(gcode_list):

            if self._P.MarlinCodeForRemoval.match(gcode) or\
                (self._current_nozzle.startswith('FFF') is False and gcode == 'G92 E0'):
                gcode_list[index] = self._P.RemovedMark
                continue

            if gcode.startswith(';LAYER:'):
                self._current_layer = self._P.getLayerIndex(gcodes)                
                if self._current_layer > 0:
                    uvcode = self.getUVCode(self._current_index, self._current_layer - 1)                    
                    if len(uvcode) > 1:
                        before_layer_uvcode = self._P.getWrappedUVCode(uvcode, self._current_index)
                        have_first_extruder = gcode_list[index+3].startswith('T') # danger op because we expect gcode list ;LAYER ...T0 
                continue

            if gcode.startswith(';'): # comment
                if self._current_nozzle.startswith('FFF'):
                    if self._retraction_index > 0 and self._retraction_index < index and self._is_retraction_moment:
                        gcode = self._insertBackRetraction(gcode) # Back-Retraction
                        gcode_list[self._retraction_index] = self._P.getRetractionCode(self._current_index, self._last_E) + gcode_list[self._retraction_index]
                        self._accummulated_distance = 0
                gcode_list[index] = gcode
                continue

            if gcode.startswith('T'): # Nozzle changed
                
                self._hasAirCompressorOn = False # reset shot-mode
                self._current_nozzle = self._setExtruder(gcode)

                extruder_setup_code = self._P.getExtruderSetupCode(self._previous_index, self._current_index, uvcode)
                if isStartCode:
                    self._extruderSetupCode = extruder_setup_code
                    gcode_list[index] = ''
                else:
                    gcode_list[index] = extruder_setup_code

                continue
            
            if isStartCode:
                match = self._P.getMatched(gcode, [self._P.G92_E0])
                if match:
                    gcode_list[index] = self._P.RemovedMark
                    self._extruderSetupCode += match.group(1) + '\n'
                    continue

            match = self._P.getMatched(gcode, [self._P.G1_F_E])
            if match:
                # remove itself when Dispensor
                if self._current_nozzle.startswith('Dispenser'):
                    gcode_list[index] = self._P.RemovedMark
                    continue
                elif self._current_nozzle.startswith('FFF'):
                    self._is_retraction_moment = False

                gcode = '{head} E{e:<.5f}\n'.format(
                    head = match.group(1),
                    e = float(match.group(2))
                )

                # add M301 when FFF and this is first M301
                if self._current_nozzle.startswith('FFF') and isStartCode == False:
                    gcode = self._getPressureOn(gcode)
                
                if isStartCode:
                    gcode_list[index] = self._P.RemovedMark
                    self._extruderSetupCode += gcode + '\n'
                else:
                    gcode_list[index] = gcode
                continue

            # Z 값 갱신하고 FFF가 아닐때 M330 추가
            match = self._P.getMatched(gcode, [self._P.G0_F_X_Y_Z, self._P.G1_F_Z])
            if match:
                gcode = self._P.update_Z_value(gcode, self._current_index, self._Q.Initial_layer0_list[self._current_index], match)
                if self._current_nozzle.startswith('FFF'):
                    if gcode.startswith('G0'):
                        current_position = self._getTravelDistance(current_position, self._getNextLocation(match)) # retract
                    else:
                        current_position = self._getNextLocation(match)
                else:
                    gcode = self._getPressureOff(gcode)
                
                gcode_list[index] = gcode
                continue

             # Z 값 갱신하고 FFF가 아닐때 M330 추가
            match = self._P.getMatched(gcode, [self._P.G0_F_X_Y])
            if match:
                gcode = self._P.prettyFormat(match)
                if self._current_nozzle.startswith('FFF'):
                    current_position = self._getTravelDistance(current_position, self._getNextLocation(match)) # retract
                    if not gcode_list[index-1].startswith('G0'):
                        self._retraction_index = index
                else:
                    gcode = self._getPressureOff(gcode)

                gcode_list[index] = gcode
                continue

            # add M330 
            match = self._P.getMatched(gcode, [self._P.G0_X_Y_Z])
            if match:
                gcode = self._P.update_Z_value(gcode, self._current_index, self._Q.Initial_layer0_list[self._current_index], match)                    
                if self._current_nozzle.startswith('FFF') is False:                    
                    gcode = self._getPressureOff(gcode) 
                gcode_list[index] = gcode
                continue 

            # add M301
            match = self._P.getMatched(gcode, [self._P.G1_F_X_Y_E])
            if match:
                gcode = self._P.pretty_XYE_Format(match)
                if self._current_nozzle.startswith('FFF'):
                    pressure_code = self._getPressureOn(gcode, reverse=True)
                    current_position = self._getNextLocation(match)
                    if self._retraction_index > 0 and self._retraction_index < index and self._is_retraction_moment:
                        gcode = self._insertBackRetraction(pressure_code) # Back-Retraction
                        gcode_list[self._retraction_index] = self._P.getRetractionCode(self._current_index, self._last_E) + gcode_list[self._retraction_index]
                    self._accummulated_distance = 0
                    self._last_E = float(match.group(4))
                else:
                    gcode = self._P.prettyFormat(match)
                    gcode = self._getPressureOn(gcode, reverse=True)

                gcode_list[index] = gcode
                continue

            # E 제거
            match = self._P.getMatched(gcode, [self._P.G1_X_Y_E])
            if match:
                if self._current_nozzle.startswith('FFF'):
                    gcode = self._P.pretty_XYE_Format(match)
                    current_position = self._getNextLocation(match)
                    self._accummulated_distance = 0
                    self._last_E = float(match.group(4))
                else:
                    gcode = self._P.prettyFormat(match)
                gcode_list[index] = gcode
                continue

            # 소숫점 자리 정리
            match = self._P.getMatched(gcode, [self._P.G0_X_Y])
            if match:
                if self._current_nozzle.startswith('FFF'):
                    current_position = self._getTravelDistance(current_position, self._getNextLocation(match)) # retract
                gcode_list[index] = self._P.prettyFormat(match)

            # 수소점 자리 정리 -1
            match = self._P.getMatched(gcode, [self._P.G1_X_Y])
            if match:
                if self._current_nozzle.startswith('FFF'):
                    current_position = self._getNextLocation(match) # retract
                gcode_list[index] = self._P.prettyFormat(match)  
                continue

        if uvcode != '' and have_first_extruder == False:
            gcode_list[0] = before_layer_uvcode + gcode_list[0]

        return '\n'.join(gcode_list)
        
    def _getNextLocation(self, match):
        return [float(match.group(2)), float(match.group(3))]

    def _insertBackRetraction(self, rear_code):
        self._is_retraction_moment = False
        return self._P.getBackRetractionCode(self._current_index, self._last_E) + rear_code


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
            gcode_spacing += self._G['G90_G0_C'].format(self._Q.Initial_layer0_list[self._current_index])
            gcode_spacing += self._G['G92_X0_Y0']
            gcode_spacing += ';Well Number: %d\n' % well_num

            gcode_clone.insert(0, gcode_spacing)
            self._gcode_list[self._EndOfStartCodeIndex:self._EndOfStartCodeIndex]= gcode_clone # put the clones in front of the end-code
            gcode_clone.remove(gcode_spacing)