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
                    'G56 G92.1\n' +\
                    'G0 X0.0 Y0.0\n' +\
                    'G1 E-1 F300 ; retract the Extruder for release some of the pressure\n' +\
                    'G90 ; absolute positioning\n' +\
                    'M308 27 27 27 27 27 27 27 ; set temperature'

        # 선택한 명령어
        self._current_index = -1  
        self._enabled_extruder_list = [] 

        self._previous_index = -1
        self._current_nozzle = ''
        self._last_position = 0
        self._is_retraction_moment = False
        self._is_shot_moment = False

        self._last_E = 0.0
        self._shot_index = -1
        self._retraction_index = -1
                
        self._layer_no = 0

        # *** G-code Line(command) 관리 변수
        self._gcode_list = []        
        self._last_extrusion_amount = 0

        self._StartOfStartCodeIndex = -1
        self._EndOfStartCodeIndex = None

        self._hasAirCompressorOn = False
        self._extruderSetupCode = ''

        self._initial_layer0_list = [0, 0, 0, 0, 0, 0]

    def setReplacedlist(self, gcode_list) -> None:
        self._gcode_list = gcode_list

    def getReplacedlist(self) -> str:
        return self._gcode_list
    
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

                modified_gcodes = self._P.getUVCode(self._current_index, self._layer_no) + '\n' + modified_gcodes.replace('{end_code}', self.END_CODE)

            elif gcodes.startswith(';LAYER:'):    
                modified_gcodes = self._convertOneLayerGCode(gcodes)

            elif self._P.G1_F_E.match(gcodes) is not None:
                self._EndOfStartCodeIndex = index
                modified_gcodes = self._convertOneLayerGCode(gcodes)

            self._gcode_list[index] = self._P.removeRedundencyGCode(modified_gcodes)

        startSetupCode = self._P.removeRedundencyGCode(self._extruderSetupCode)
        self._gcode_list[self._StartOfStartCodeIndex] += '\n;Start Point\n{start_setup};Start Point end\n\n{well_num}'.format(
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

    def _getZform(self, front_code, z_value, extruder_index) -> str:
        return '{front_code}\nG0 {axis_name}{height:<.3f}'.format(
            front_code = front_code,
            axis_name = 'C' if extruder_index > 0 else 'Z',
            height = z_value - self._Q.layer_height_0
        )

    def _update_Z(self, gcode, matched) -> str:
        
        layer_uvcode = ''
        front_code = '{head} X{x:<.3f} Y{y:<.3f}'.format(head=matched.group(1), x=float(matched.group(2)), y=float(matched.group(3)))
        z_value = float(matched.group(4))
        
        if self._layer_no >= 0:
           layer_uvcode = self._P.getUVCode(self._current_index, self._layer_no)

        if layer_uvcode != '':
           layer_uvcode = '\n' + layer_uvcode

        return self._getZform(front_code +  layer_uvcode, z_value, self._current_index)

    def _update_Z3(self, gcode, matched) -> str:        
        front_code = '{head} X{x:<.3f} Y{y:<.3f}'.format(head=matched.group(1), x=float(matched.group(2)), y=float(matched.group(3)))
        z_value = float(matched.group(4))
        return self._getZform(front_code, z_value, self._current_index)

    def _update_Z2(self, gcode, matched) -> str:        
        front_code = matched.group(1)
        z_value = float(matched.group(2))
        return self._getZform(front_code, z_value, self._current_index)

    def _haveToolOnJustNext(self, gcode_list) -> bool:
        for j in range(1,5):
            if gcode_list[j].startswith('T'):
                return True
        return False

    def _getDistance(self, last_pos, next_pos):
        print_distance = 0
        if last_pos is not None:
            print_distance = distance.euclidean(last_pos, next_pos)
        
        self._last_position = next_pos
        return print_distance

    def _getNextLocation(self, match):
        return [float(match.group(2)), float(match.group(3))]

    def _convertOneLayerGCode(self,gcodes,isStartCode=False) -> str:
        self._last_position = None
        before_layer_uvcode = ''
        accumulated_travel_distance = 0
        accumulated_shot_distance = 0

        gcode_list = gcodes.split('\n')
        for index, gcode in enumerate(gcode_list):
            # Layer
            if gcode.startswith(';LAYER:'):
                self._layer_no = self._P.getLayerIndex(gcodes)
                self._retraction_index = 0
                self._shot_index = 0
                continue
            # Marlin
            if self._P.MarlinCodeForRemoval.match(gcode) or\
                (self._current_nozzle.startswith('FFF') is False and gcode == 'G92 E0'):
                gcode_list[index] = self._P.RemovedMark
                continue
            #
            if isStartCode:
                match = self._P.getMatched(gcode, [self._P.G92_E0])
                if match:
                    gcode_list[index] = self._P.RemovedMark
                    self._extruderSetupCode += match.group(1) + '\n'
                    continue

            # 주석문
            if gcode.startswith(';'): # comment
                if gcode.startswith(';TYPE:') == False:
                    if self._current_nozzle.startswith('FFF'): # retraction
                        if (accumulated_travel_distance > self._Q.retraction_min_travel[self._current_index]):
                            if (self._retraction_index > 0 and self._retraction_index < index):
                                gcode = self._P.getBackRetractionCode(self._current_index, self._last_E) + gcode
                                gcode_list[self._retraction_index] = self._P.RemovedMark if self._UV_TEST else self._P.getRetractionCode(self._current_index, self._last_E) + gcode_list[self._retraction_index]
                    else:
                        if accumulated_shot_distance > self._Q.retraction_extrusion_window[self._current_index]: # shot 조건
                            if (self._shot_index > 0 and self._shot_index < index ):
                                gcode = "M330\n" + gcode
                                gcode_list[self._shot_index] = self._P.RemovedMark if self._UV_TEST else "M301\n" + gcode_list[self._shot_index]
                gcode_list[index] = gcode 
                continue

            # add [M301], [Back-retraction] # Retraction
            match = self._P.getMatched(gcode, [self._P.G1_F_X_Y_E])
            if match:
                gcode = self._P.pretty_XYE_Format(match)
                # shot index 구하기
                if gcode_list[index-1].startswith('G1') == False or ('X' and 'Y' not in gcode_list[index-1]):
                    self._shot_index = index
                    if self._current_nozzle.startswith('FFF') and self._Q.retraction_enable_list[0]: # retraction
                        if (accumulated_travel_distance > self._Q.retraction_min_travel[self._current_index]):
                            if (self._retraction_index > 0 and self._retraction_index < index):
                                gcode = self._P.getBackRetractionCode(self._current_index, self._last_E) + gcode
                                gcode_list[self._retraction_index] = self._P.RemovedMark if self._UV_TEST else self._P.getRetractionCode(self._current_index, self._last_E) + gcode_list[self._retraction_index]
                if self._current_nozzle.startswith('FFF'):
                    self._last_E = float(match.group(4))
                else:
                    gcode = self._P.RemovedMark if self._UV_TEST else self._P.prettyFormat(match)
                accumulated_shot_distance = 0
                accumulated_shot_distance += self._getDistance(self._last_position, self._getNextLocation(match)) # 밑에 있어야 함**
                gcode_list[index] = self._P.RemovedMark if self._UV_TEST else gcode
                continue

             # add [M330], [Retraction] # Shot
            match = self._P.getMatched(gcode, [self._P.G0_F_X_Y])
            if match:
                gcode = self._P.prettyFormat(match)
                if gcode_list[index-1].startswith('G0') == False:
                    self._retraction_index = index
                if gcode_list[index-1].startswith('G1'):
                    if self._current_nozzle.startswith('FFF') == False: # shot
                        if accumulated_shot_distance > self._Q.retraction_extrusion_window[self._current_index]:
                            if (self._shot_index > 0 and self._shot_index < index ):
                                gcode = "M330\n" + gcode
                                gcode_list[self._shot_index] = self._P.RemovedMark if self._UV_TEST else "M301\n" + gcode_list[self._shot_index]
                accumulated_travel_distance = 0
                accumulated_travel_distance += self._getDistance(self._last_position, self._getNextLocation(match)) # 밑에 있어야 함**
                gcode_list[index] = self._P.RemovedMark if self._UV_TEST else gcode
                continue
            
            # Z 값 갱신하고 FFF가 아닐때 M330 추가
            match = self._P.getMatched(gcode, [self._P.G0_F_X_Y_Z])
            if match:
                gcode = self._update_Z(gcode, match)
                accumulated_travel_distance += self._getDistance(self._last_position, self._getNextLocation(match))
                gcode_list[index] = self._P.RemovedMark if self._UV_TEST else gcode
                continue

            # 디버깅 필요
            match = self._P.getMatched(gcode, [self._P.G0_X_Y_Z])
            if match:
                gcode = self._update_Z3(gcode, match)
                accumulated_travel_distance += self._getDistance(self._last_position, self._getNextLocation(match))
                gcode_list[index] = self._P.RemovedMark if self._UV_TEST else gcode
                continue 

            # E 제거
            match = self._P.getMatched(gcode, [self._P.G1_X_Y_E])
            if match:
                if self._current_nozzle.startswith('FFF'):
                    gcode = self._P.pretty_XYE_Format(match)
                    self._last_E = float(match.group(4))
                else:
                    gcode = self._P.prettyFormat(match)
                accumulated_shot_distance += self._getDistance(self._last_position, self._getNextLocation(match))
                gcode_list[index] = self._P.RemovedMark if self._UV_TEST else gcode
                continue

            # 소숫점 자리 정리
            match = self._P.getMatched(gcode, [self._P.G0_X_Y])
            if match:
                accumulated_travel_distance += self._getDistance(self._last_position, self._getNextLocation(match))
                gcode_list[index] = self._P.RemovedMark if self._UV_TEST else self._P.prettyFormat(match)

            # 수소점 자리 정리 -1
            match = self._P.getMatched(gcode, [self._P.G1_X_Y])
            if match:
                accumulated_shot_distance += self._getDistance(self._last_position, self._getNextLocation(match))
                gcode_list[index] = self._P.RemovedMark if self._UV_TEST else self._P.prettyFormat(match) 
                continue

            # 리트렉션 코드 관리
            match = self._P.getMatched(gcode, [self._P.G1_F_E])
            if match:
                # remove itself when Dispensor
                accumulated_travel_distance = 0 # 리트렉션 중복을 막기 위함.
                if self._current_index > 0 or isStartCode:
                    gcode_list[index] = self._P.RemovedMark
                    continue

                gcode = '{head} E{e:<.5f}\n'.format(head = match.group(1),e = float(match.group(2)))

                # add M301 when FFF and this is first M301
                # if self._current_nozzle.startswith('FFF') and isStartCode == False:
                #     gcode = self._getPressureOn(gcode)
                
                if isStartCode:
                    gcode_list[index] = self._P.RemovedMark
                    self._extruderSetupCode += gcode + '\n'
                else:
                    gcode_list[index] = self._P.RemovedMark if self._UV_TEST else gcode
                continue

            # Z 값 갱신하고 FFF가 아닐때 M330 추가
            match = self._P.getMatched(gcode, [self._P.G1_F_Z])
            if match:
                gcode = self._update_Z2(gcode, match)
                gcode_list[index] = self._P.RemovedMark if self._UV_TEST else gcode
                continue

            # T0~T5
            match = self._P.getMatched(gcode, [self._P.T])
            if match: # Nozzle changed
                self._current_index = int(match.group(1))
                self._hasAirCompressorOn = False

                extruder_setup = self._P.getExtruderSetupCode(self._previous_index, self._current_index, self._layer_no)
                if isStartCode:
                    self._extruderSetupCode = extruder_setup
                    gcode_list[index] = ''
                else:
                    gcode_list[index] = extruder_setup
                
                self._previous_index = self._current_index
                self._addToEnabledExtruders(self._current_index)
                self._current_nozzle = self._Q.getVariantName(self._current_index)
                continue

        if before_layer_uvcode != '':
            gcode_list[0] = before_layer_uvcode + gcode_list[0]

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
            gcode_spacing += self._G['G90_G0_C'].format(self._initial_layer0_list[self._current_index])
            gcode_spacing += self._G['G92_X0_Y0']
            gcode_spacing += ';Well Number: %d\n' % well_num

            gcode_clone.insert(0, gcode_spacing)
            self._gcode_list[self._EndOfStartCodeIndex:self._EndOfStartCodeIndex]= gcode_clone # put the clones in front of the end-code
            gcode_clone.remove(gcode_spacing)