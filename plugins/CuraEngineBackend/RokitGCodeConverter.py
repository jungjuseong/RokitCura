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

        self._G_model = RokitGCodeModel()        
        self._G = self._G_model.GCODE

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

        # 선택한 명령어
        self._current_index = -1  
        self._activated_index_list = [] 

        self._previous_index = -1
        self._nozzle_type = ''

        self._accummulated_distance = 0
        self._is_retraction_moment = False
        self._retraction_speed = self._Q.retraction_speed_list[0] * 60

        self._last_E = 0.0
        self._retraction_index = -1
                
        self._current_layer_index = None

        # *** G-code Line(command) 관리 변수
        self._replaced_gcode_list = []        
        self._last_extrusion_amount = 0


        self._is_shot_moment = True
        self._index_of_StartOfStartCode = -1
        self._index_of_EndOfStartCode = None

        self._hasAirCompressorOn = False
        self._startExtruderSetupCode = '' # 처음 나오는 extruder

    def setReplacedlist(self, replaced_gcode_list) -> None:
        self._replaced_gcode_list = replaced_gcode_list

    def getReplacedlist(self) -> str:
        return self._replaced_gcode_list

    def _setExtruder(self, gcode) -> str:
        self._previous_index = self._current_index
        self._current_index = self._P.getExtruderIndex(gcode)
        self._addToActivatedExtruders(self._current_index)       
        return self._Q.getVariantName(self._current_index)
    
    # 사용된 익스트루더 index 기록
    def _addToActivatedExtruders(self, current_index) -> None:
        if current_index not in self._activated_index_list:
            self._activated_index_list.append(current_index) # [0,1,2,3,4,5]

    def run(self) -> None:

        for index, one_layer_gcode in enumerate(self._replaced_gcode_list):
            modified_gcode = one_layer_gcode

            if ';FLAVOR:Marlin' in one_layer_gcode:
                modified_gcode = one_layer_gcode.replace(';FLAVOR:Marlin', ';F/W : 7.7.1.x')

            elif self._P.StartOfStartCode in one_layer_gcode:
                self._index_of_StartOfStartCode = index
                modified_gcode = one_layer_gcode.replace('Cura_SteamEngine', 'OrganRegenerator_Engine')
                modified_gcode = self._convertOneLayerGCode(modified_gcode, True)     
                modified_gcode = self._P.replaceLayerInfo(modified_gcode)
                if self._Q.dispensor_enable:
                   modified_gcode = self._P.replaceDispenserSetupCode(modified_gcode)

            elif self._P.StartOfEndCode in one_layer_gcode:
                
                self._index_of_EndOfStartCode = index if self._index_of_EndOfStartCode is None else self._index_of_EndOfStartCode
                modified_gcode = self._P.StartOfEndCode +\
                    one_layer_gcode[one_layer_gcode.find(self._P.StartOfEndCode)+len(self._P.StartOfEndCode):one_layer_gcode.rfind(self._P.EndOfEndCode)] +\
                    self._P.EndOfEndCode + '\n'

                modified_gcode = self._add_UV_Code(self._current_index) + '\n' + modified_gcode.replace('{end_code}', self._P.END_CODE)

            elif one_layer_gcode.startswith(';LAYER:'):
                self._current_layer_index = self._P.getLayerIndex(one_layer_gcode)
                modified_gcode = self._convertOneLayerGCode(one_layer_gcode, False)            

            elif self._P.G1_F_E.match(one_layer_gcode) is not None:
                self._index_of_EndOfStartCode = index
                modified_gcode = self._convertOneLayerGCode(one_layer_gcode, False)

            self._replaced_gcode_list[index] = self._P.removeRedundencyGCode(modified_gcode)

        startSetupCode = self._P.removeRedundencyGCode(self._startExtruderSetupCode)
        self._replaced_gcode_list[self._index_of_StartOfStartCode] += '\n;Start point\n{start_setup}; ==== setup end\n\n{well_num}'.format(
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


    # X Y를 인식하는 모든 부분에 추가함. (G1과 G0일 때의 x,y 좌표 수용)
    def _getNextPosition(self, current_pos, next_pos):
        if current_pos is not None:
            self._accummulated_distance += distance.euclidean(current_pos, next_pos)

        if self._accummulated_distance > self._Q.retraction_min_travel[0]:
            self._is_retraction_moment = True # 리트렉션 코드가 삽입되는 트리거
            self._accummulated_distance = 0        
        return next_pos

    def _getRetractionCode(self) -> str:
        last_retraction_amount = self._last_E - self._Q.retraction_amount_list[0]
        return 'G1 F{f} E{e:<.5f} ;(Retraction_a)\n'.format(
            f = self._retraction_speed, 
            e = last_retraction_amount)

    def _getBackRetractionCode(self) -> str:
        return 'G1 F{f} E{e:<.5f} ;(Back-Retraction_a)\n'.format(f= self._retraction_speed, e= self._last_E)

    def _convertOneLayerGCode(self, one_layer_gcode, isStartCode=False) -> str:

        current_position = None

        gcode_list = one_layer_gcode.split('\n')
        for index, gcode in enumerate(gcode_list):

            if self._P.MarlinCodeForRemoval.match(gcode) or\
                (self._nozzle_type.startswith('FFF') is False and gcode == 'G92 E0'):
                gcode_list[index] = self._P.RemovedMark
                continue

            if gcode.startswith(';'): # comment
                gcode_list[index] = gcode
                continue

            if gcode.startswith('T'): # Nozzle changed
                self._hasAirCompressorOn = False # reset shot-mode
                self._nozzle_type = self._setExtruder(gcode)

                if isStartCode:
                    gcode_list[index] = ''
                    self._startExtruderSetupCode = self._P.getExtruderSetupCode(self._previous_index, self._current_index)
                else:
                    gcode_list[index] = self._P.getExtruderSetupCode(self._previous_index, self._current_index)

                continue
            
            if isStartCode:
                match = self._P.getMatched(gcode, [self._P.G92_E0])
                if match:
                    gcode_list[index] = self._P.RemovedMark
                    self._startExtruderSetupCode += match.group(1) + '\n'
                    continue

            match = self._P.getMatched(gcode, [self._P.G1_F_E])
            if match:
                # remove Retraction code itself when Dispensor
                if self._nozzle_type.startswith('Dispenser'):
                    gcode_list[index] = self._P.RemovedMark
                    continue
                elif self._nozzle_type.startswith('FFF'):
                    # <<< retraction 추가 - G0에서 G1로 바뀌는 시점
                    if self._retraction_index > 0 and self._retraction_index < index:
                        self._is_retraction_moment = False
                        self._accummulated_distance = 0

                gcode = '{head} E{e:<.5f}\n'.format(
                    head = match.group(1),
                    e = float(match.group(2))
                )

                # add M301 when FFF and this is first M301
                if self._nozzle_type.startswith('FFF') and isStartCode == False:
                    gcode = self._getPressureOn(gcode)
                
                if isStartCode:
                    gcode_list[index] = self._P.RemovedMark
                    self._startExtruderSetupCode += gcode + '\n'
                else:
                    gcode_list[index] = gcode
                self._last_extrusion_amount = float(match.group(2)) # <<< 이때의 E값은 프린터할 때 나오는 E값이 아니므로 참조 x : (last_E 변수 참고)
                continue

            # Z 값 갱신하고 FFF가 아닐때 M330 추가
            match = self._P.getMatched(gcode, [self._P.G0_F_X_Y_Z, self._P.G1_F_Z])
            if match:
                gcode = self._P.update_Z_value(gcode, self._nozzle_type, self._Q.Initial_layer0_list[self._current_index], match)
                if self._nozzle_type.startswith('FFF') is False:
                    gcode = self._getPressureOff(gcode)
                else:
                    next_position = [float(match.group(2)), float(match.group(3))]
                    if gcode.startswith('G0'):
                        current_position = self._getNextPosition(current_position, next_position)
                    else:
                        current_position = next_position

                gcode_list[index] = gcode
                continue

             # Z 값 갱신하고 FFF가 아닐때 M330 추가
            match = self._P.getMatched(gcode, [self._P.G0_F_X_Y])
            if match:
                gcode = self._P.prettyFormat(match)
                if self._nozzle_type.startswith('FFF') is False:
                    gcode = self._getPressureOff(gcode)
                else:
                    next_position = [float(match.group(2)), float(match.group(3))]
                    current_position = self._getNextPosition(current_position, next_position)
                    if not gcode_list[index-1].startswith('G0'):
                        self._retraction_index = index

                gcode_list[index] = gcode
                continue

            # add M330 
            match = self._P.getMatched(gcode, [self._P.G0_X_Y_Z])
            if match:
                gcode = self._P.update_Z_value(gcode, self._nozzle_type, self._Q.Initial_layer0_list[self._current_index], match)
                if self._nozzle_type.startswith('FFF') is False:
                    gcode = self._getPressureOff(gcode)  
                else:
                    next_position = [float(match.group(2)), float(match.group(3))]
                    current_position = self._getNextPosition(current_position, next_position)
                    if not gcode_list[index-1].startswith('G0'):
                        self._retraction_index = index
                gcode_list[index] = gcode
                continue 

            # add M301
            match = self._P.getMatched(gcode, [self._P.G1_F_X_Y_E])
            if match:
                gcode = self._P.pretty_XYE_Format(match)
                if self._nozzle_type.startswith('FFF'):
                    current_position = [float(match.group(2)), float(match.group(3))]
                    pressure_code = self._getPressureOn(gcode, reverse=True)
                    # <<< retraction 추가 - G0에서 G1로 바뀌는 시점
                    if self._retraction_index > 0 and self._retraction_index < index:
                        if self._is_retraction_moment:
                            gcode = self._getBackRetractionCode() + pressure_code
                            gcode_list[self._retraction_index] = self._getRetractionCode() + gcode_list[self._retraction_index]
                            self._is_retraction_moment = False

                    self._last_extrusion_amount = float(match.group(4))
                    self._last_E = float(match.group(4)) # <<<
                else:
                    gcode = self._P.prettyFormat(match)
                    gcode = self._getPressureOn(gcode, reverse=True)

                gcode_list[index] = gcode
                continue

            # E 제거
            match = self._P.getMatched(gcode, [self._P.G1_X_Y_E])
            if match:
                
                if self._nozzle_type.startswith('FFF'):
                    current_position = [float(match.group(2)), float(match.group(3))]
                    gcode = self._P.pretty_XYE_Format(match)
                    # <<< retraction 추가
                    if self._retraction_index > 0 and self._retraction_index < index:
                        if self._is_retraction_moment:
                            gcode = self._getBackRetractionCode() + gcode
                            gcode_list[self._retraction_index] = self._getRetractionCode() + gcode_list[self._retraction_index]
                            self._is_retraction_moment = False

                    self._last_E = float(match.group(4))
                else:
                    gcode = self._P.prettyFormat(match)
                gcode_list[index] = gcode
                
                continue

            # 수소점 자리 정리
            match = self._P.getMatched(gcode, [self._P.G0_X_Y])
            if match:
                if self._nozzle_type.startswith('FFF'):
                    current_position = self._getNextPosition(current_position, [float(match.group(2)), float(match.group(3))])
                    if not gcode_list[index-1].startswith('G0'):
                        self._retraction_index = index

                gcode_list[index] = self._P.prettyFormat(match)
            
            match = self._P.getMatched(gcode, [self._P.G1_X_Y])
            if match:
                if self._nozzle_type.startswith('FFF'):
                    current_position = [float(match.group(2)), float(match.group(3))]
                gcode_list[index] = self._P.prettyFormat(match)  
                continue

        return '\n'.join(gcode_list)

    # UV 명령어 삽입
    def _add_UV_Code(self, extruder_index) -> str:

        if self._Q.uv_enable_list[extruder_index] == True:
            uv_per_layer = self._Q.uv_per_layer_list[extruder_index]
            start_layer = self._Q.uv_start_layer_list[extruder_index]
            layer = self._current_layer_index - start_layer + 1

            if layer >= 0 and (layer % uv_per_layer) == 0:
                return self._P.get_UV_Code(extruder_index)

        return ''

    # Well plate 복제 기능
    def _cloneWellPlate(self):

        NumberOfWalls = self._travel['number_of_walls']
        NumberORows = self._travel['number_of_rows']
        HopHeight = self._travel['hop_height']
        ForwardSpaceing = self._travel['spacing']
        BackwardSpacing = -self._travel['spacing']

        self._index_of_EndOfStartCode -= len(self._replaced_gcode_list)
        
        from_index = self._index_of_StartOfStartCode + 1
        to_index = self._index_of_EndOfStartCode

        gcode_clone = self._replaced_gcode_list[from_index : to_index]
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
            self._replaced_gcode_list[self._index_of_EndOfStartCode:self._index_of_EndOfStartCode]= gcode_clone # put the clones in front of the end-code
            gcode_clone.remove(gcode_spacing)