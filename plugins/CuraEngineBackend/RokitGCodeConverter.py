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

class RokitGCodeConverter:
    def __init__(self) -> None:    

        self._pretty_format = True
        self._quality= RokitPrintQuality()

        self._G_model = RokitGCodeModel()        
        self._G = self._G_model.GCODE

        self._build_dish_model = RokitBuildDishModel()

        # 외부 dict
        self._dish = {}

        self._travel= {}
        build_plate = self._quality.getGlobalContainerStackProperty('machine_build_dish_type')
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
        self._retraction_speed = self._quality.retraction_speed_list[0] * 60

        self._last_E = 0.0
        self._retraction_index = -1
                
        self._current_layer_index = None

        # *** G-code Line(command) 관리 변수
        self._replaced_gcode_list = []        

        self._last_extrusion_amount = 0

        # startcode / endcode
        self._StartOfStartCode = '\n; (*** start of start code for Dr.Invivo 4D6)'
        self._EndOfStartCode = '\n; (*** end of start code for Dr.Invivo 4D6)'

        self._StartOfEndCode = '\n; (*** start of end code for Dr.Invivo 4D6)'
        self._EndOfEndCode = '\n; (*** end of end code for Dr.Invivo 4D6)'

        self._END_CODE = 'M330\n' +\
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

        self._HOME_ALL_AXIS = '; Home all axis\n' +\
                    'M29 Z\n' +\
                    'M29 C\n' +\
                    'M29 B\n' +\
                    'G0 B15. F300\n' +\
                    'M29 B\n' +\
                    'M29 A\n' +\
                    'M29 Y\n' +\
                    'M29 X\n' +\
                    'G79\n'

        self._DISH_LEVELING_PROCEDURE = '; Dish leveling procedure\n' +\
                    'G0 X0. Y0. F300\n' +\
                    'G29\n' +\
                    'G0 X15. F300\n' +\
                    'G29\n' +\
                    'G0 X0. Y15. F300 \n' +\
                    'G29\n' +\
                    'G0 X-15. Y0. F300\n' +\
                    'G29\n' +\
                    'G0 X0. Y-15. F300\n' +\
                    'G29\n' +\
                    'M420\n' +\
                    'G0 X0. Y0. F300\n'

        # match patterns
        self._Extruder_NO = re.compile(r'^T([0-9]+)')
        self._LAYER_NO = re.compile(r'^;LAYER:([0-9]+)')

        _FP = r'[+-]?\d*[.]?\d+'

        self._G0_or_G1 = re.compile(r'^G[0-1] ')
        self._G1_F_X_Y_E = re.compile(r'(G1 F{f}) X({x}) Y({y}) E({e})'.format(f=_FP,x=_FP,y=_FP,e=_FP))
        self._G1_X_Y_E = re.compile(r'(G1) X({x}) Y({y}) E({e})'.format(x=_FP,y=_FP,e=_FP))

        self._MarlinCodeForRemoval = re.compile(r'M(82|140|190|104 [TS]|109 [TS]|141|205|105|107)')
        self._RemovedMark = '; to-be-removed'

        self._G1_F_E = re.compile(r'^(G1 F{f}) E({e})'.format(f=_FP,e=_FP))

        self._G1_F_Z = re.compile(r'^(G1 F{f}) Z({z})'.format(f=_FP,z=_FP))
        self._G0_Z = re.compile(r'^(G0) Z({z})'.format(z=_FP))
        self._G0_F_X_Y_Z = re.compile(r'^(G0 F{f}) X({x}) Y({y}) Z({z})'.format(f=_FP,x=_FP,y=_FP,z=_FP))
        self._G0_F_X_Y = re.compile(r'^(G0 F{f}) X({x}) Y({y})'.format(f=_FP,x=_FP,y=_FP))

        self._G0_X_Y_Z = re.compile(r'^(G0) X({x}) Y({y}) Z({z})'.format(x=_FP,y=_FP,z=_FP))

        self._G0_X_Y = re.compile(r'^(G0) X({x}) Y({y})'.format(x=_FP,y=_FP))
        self._G1_X_Y = re.compile(r'^(G1) X({x}) Y({y})'.format(x=_FP,y=_FP))

        self._G1_F_G1_F = re.compile(r'^G1 F{f1}\n(G1 F{f2}\n)'.format(f1=_FP,f2=_FP))

        self._OnlyInteger = re.compile(r'([XYZ][-+]?\d+)')

        self._is_shot_moment = True
        self._index_of_StartOfStartCode = -1
        self._index_of_EndOfStartCode = None

        self._hasShot = False
        self._startExtruderSetupCode = '' # 처음 나오는 extruder
        self._back_retraction = False
        #self._initial_extruder_did_something = False # 처음의 D6와 D1~D5 사이에 G1 x y e 코드가 없는 경우

    def setReplacedlist(self, replaced_gcode_list) -> None:
        self._replaced_gcode_list = replaced_gcode_list

    def getReplacedlist(self) -> str:
        return self._replaced_gcode_list

    def _getLayerIndex(self, one_layer_gcode) -> int:
        return int(self._LAYER_NO.search(one_layer_gcode).group(1))

    def _setExtruder(self, gcode) -> str:
        self._previous_index = self._current_index
        self._current_index = self._getExtruderIndex(gcode)
        self._addToActivatedExtruders(self._current_index)       
        return self._quality.getVariantName(self._current_index)
    
    # 사용된 익스트루더 index 기록
    def _addToActivatedExtruders(self, current_index) -> None:
        if current_index not in self._activated_index_list:
            self._activated_index_list.append(current_index) # [0,1,2,3,4,5]

    def run(self) -> None:

        for index, one_layer_gcode in enumerate(self._replaced_gcode_list):
            modified_gcode = one_layer_gcode
            if ';FLAVOR:Marlin' in one_layer_gcode:
                modified_gcode = one_layer_gcode.replace(';FLAVOR:Marlin', ';F/W : 7.7.1.x')

            elif self._StartOfStartCode in one_layer_gcode:
                self._index_of_StartOfStartCode = index
                modified_gcode = one_layer_gcode.replace('Cura_SteamEngine', 'OrganRegenerator_Engine')
                modified_gcode = self._convertOneLayerGCode(modified_gcode, True)     
                modified_gcode = self._replaceLayerInfo(modified_gcode)
                if self._quality.dispensor_enable:
                   modified_gcode = self._replaceDispenserSetupCode(modified_gcode)

            elif self._StartOfEndCode in one_layer_gcode:
                self._index_of_EndOfStartCode = index if self._index_of_EndOfStartCode is None else self._index_of_EndOfStartCode
                modified_gcode = self._StartOfEndCode +\
                    one_layer_gcode[one_layer_gcode.find(self._StartOfEndCode)+len(self._StartOfEndCode):one_layer_gcode.rfind(self._EndOfEndCode)] +\
                    self._EndOfEndCode + '\n'

                modified_gcode = modified_gcode.replace('{end_code}', self._END_CODE)

            elif one_layer_gcode.startswith(';LAYER:'):
                self._current_layer_index = self._getLayerIndex(one_layer_gcode)
                modified_gcode = self._convertOneLayerGCode(one_layer_gcode, False)
                if self._current_layer_index > 0:
                    modified_gcode += self._add_UV_Code(self._current_index)                

            elif self._G1_F_E.match(one_layer_gcode) is not None:
                self._index_of_EndOfStartCode = index
                modified_gcode = self._convertOneLayerGCode(one_layer_gcode, False)

            self._replaced_gcode_list[index] = self._removeRedundencyGCode(modified_gcode)

        self._replaced_gcode_list[self._index_of_StartOfStartCode] += '\n;Start point\n' + self._startExtruderSetupCode + '\n'
        #self._setStartExtruderGcodeAfterStartGcode() 
    
    def _getExtruderIndex(self, gcode) -> int:
        matched = self._Extruder_NO.search(gcode)
        return int(matched.group(1))

    def _update_Z_value(self, gcode, matched) -> str:

        initial_layer0_height = self._quality.Initial_layer0_list[self._current_index]
        
        if len(matched.groups()) > 3:
            front_code = '{head} X{x:<.3f} Y{y:<.3f}'.format(head=matched.group(1), x=float(matched.group(2)), y=float(matched.group(3)))
            z_value = float(matched.group(4))
        else:
            front_code = matched.group(1)
            z_value = float(matched.group(2))        
        
        z_delta = z_value # - self._quality.layer_height_0
        new_z = z_delta + initial_layer0_height

        #if gcode.startswith('G0') and z_delta == 0:
        #    return front_code

        if self._nozzle_type.startswith('Dispenser'):
            z_value_form = '\nG0 C{:<.3f}'.format(new_z)
        else:
            z_value_form = ' Z{:<.3f}'.format(new_z)

        return front_code + z_value_form # ';' + str(matched.group(2))

    def _getMatched(self, gcode, patterns):
        for p in patterns:
            matched = p.match(gcode)
            if matched:
                return matched
        return None

    def _prettyFormat(self, match) -> str:
        return '{head} X{x:<.3f} Y{y:<.3f}'.format(head=match.group(1), x=float(match.group(2)), y=float(match.group(3)))

    def _pretty_XYE_Format(self, match) -> str:
        return '{head} X{x:<.3f} Y{y:<.3f} E{e:<.5f}'.format(head=match.group(1), x=float(match.group(2)), y=float(match.group(3)),e=float(match.group(4)))
        
    def _getPressureOn(self, gcode, reverse=False) -> str:
        if self._hasShot == False:
            self._hasShot = True
            if reverse:
                gcode = self._G['M301'] + gcode
            else:
                gcode += self._G['M301']
        return gcode

    def _getPressureOff(self, gcode) -> str:
        if self._hasShot:
            gcode = self._G['M330'] + gcode
            self._hasShot = False
        return gcode


    # X Y를 인식하는 모든 부분에 추가함. (G1과 G0일 때의 x,y 좌표 수용)
    def _getNextPosition(self, current_pos, next_pos):
        if current_pos is not None:
            self._accummulated_distance += distance.euclidean(current_pos, next_pos)

        if self._accummulated_distance > self._quality.retraction_min_travel[0]:
            self._is_retraction_moment = True # 리트렉션 코드가 삽입되는 트리거
            self._accummulated_distance = 0        
        return next_pos

    def _getRetractionCode(self) -> str:
        last_retraction_amount = self._last_E - self._quality.retraction_amount_list[0]
        return 'G1 F{f} E{e:<.5f} ;(retraction)\n'.format(
            f = self._retraction_speed, 
            e = last_retraction_amount)

    def _getBackRetractionCode(self) -> str:
        return 'G1 F{f} E{e:<.5f} ;(back retraction)\n'.format(f= self._retraction_speed, e= self._last_E)

    def _convertOneLayerGCode(self, one_layer_gcode, isStartCode=False) -> str:

        current_position = None

        gcode_list = one_layer_gcode.split('\n')
        for index, gcode in enumerate(gcode_list):

            if self._MarlinCodeForRemoval.match(gcode) or\
                (self._nozzle_type.startswith('FFF') is False and gcode == 'G92 E0'):
                gcode_list[index] = self._RemovedMark
                continue

            if gcode.startswith(';'): # comment
                gcode_list[index] = gcode
                continue

            if gcode.startswith('T'): # Nozzle changed
                self._hasShot = False # reset shot-mode
                self._nozzle_type = self._setExtruder(gcode)

                if isStartCode:
                    # gcode_list[index] = ''
                    self._startExtruderSetupCode = self._getExtruderSetupCode()
                else:
                    gcode_list[index] = self._getExtruderSetupCode()

                continue
            
            match = self._getMatched(gcode, [self._G1_F_E])
            if match:
                # remove Retraction when Dispensor
                if self._nozzle_type.startswith('Dispenser'):
                    gcode_list[index] = self._RemovedMark
                    continue

                # when FFF or Hot Melt
                gcode = '{head} E{e:<.5f} ;({comment}Retraction)\n'.format(
                    head = match.group(1),
                    e = float(match.group(2)),
                    comment = 'Back-' if self._back_retraction else ''
                )

                # add M301 when FFF and this is first M301
                if self._nozzle_type.startswith('FFF'):
                    gcode = self._getPressureOn(gcode)
                
                gcode_list[index] = gcode
                self._last_extrusion_amount = float(match.group(2)) # <<< 이때의 E값은 프린터할 때 나오는 E값이 아니므로 참조 x : (last_E 변수 참고)
                continue

            # Z 값 갱신하고 FFF가 아닐때 M330 추가
            match = self._getMatched(gcode, [self._G0_F_X_Y_Z, self._G1_F_Z])
            if match:
                gcode = self._update_Z_value(gcode, match)
                if self._nozzle_type.startswith('FFF') is False:
                    gcode = self._getPressureOff(gcode)
                else:
                    next_position = [float(match.group(2)), float(match.group(3))]
                    if gcode.startswith('G0'):
                        current_position = self._getNextPosition(current_position, next_position)
                    else:
                        current_position = next_position
                    #self._calculateLocation(gcode, float(match.group(2)), float(match.group(3))) # <<<

                gcode_list[index] = gcode
                continue

             # Z 값 갱신하고 FFF가 아닐때 M330 추가
            match = self._getMatched(gcode, [self._G0_F_X_Y])
            if match:
                gcode = self._prettyFormat(match)
                if self._nozzle_type.startswith('FFF') is False:
                    gcode = self._getPressureOff(gcode)
                else:
                    #self._calculateLocation(gcode, float(match.group(2)), float(match.group(3))) # <<<
                    next_position = [float(match.group(2)), float(match.group(3))]
                    current_position = self._getNextPosition(current_position, next_position)
                    if gcode_list[index-1].startswith('G1'):
                        self._retraction_index = index

                gcode_list[index] = gcode
                continue

            # add M330 
            match = self._getMatched(gcode, [self._G0_X_Y_Z])
            if match:
                gcode = self._update_Z_value(gcode, match)
                if self._nozzle_type.startswith('FFF') is False:
                    gcode = self._getPressureOff(gcode)  
                else:
                    #self._calculateLocation(gcode, float(match.group(2)), float(match.group(3))) # <<<
                    next_position = [float(match.group(2)), float(match.group(3))]
                    current_position = self._getNextPosition(current_position, next_position)
                    if gcode_list[index-1].startswith('G1'):
                        self._retraction_index = index
                gcode_list[index] = gcode
                continue 

            # add M301
            match = self._getMatched(gcode, [self._G1_F_X_Y_E])
            if match:
                gcode = self._pretty_XYE_Format(match)
                if self._nozzle_type.startswith('FFF'):
                    #self._calculateLocation(gcode, float(match.group(2)), float(match.group(3))) # <<<
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
                    gcode = self._prettyFormat(match)
                    gcode = self._getPressureOn(gcode, reverse=True)

                gcode_list[index] = gcode
                continue

            # E 제거
            match = self._getMatched(gcode, [self._G1_X_Y_E])
            if match:
                self._back_retraction = False
                
                if self._nozzle_type.startswith('FFF'):
                    current_position = [float(match.group(2)), float(match.group(3))]
                    gcode = self._pretty_XYE_Format(match)
                    # <<< retraction 추가
                    if self._retraction_index > 0 and self._retraction_index < index:
                        if self._is_retraction_moment:
                            gcode = self._getBackRetractionCode() + gcode
                            gcode_list[self._retraction_index] = self._getRetractionCode() + gcode_list[self._retraction_index]
                            self._is_retraction_moment = False

                    self._last_E = float(match.group(4))
                else:
                    gcode = self._prettyFormat(match)
                gcode_list[index] = gcode
                
                continue

            # 수소점 자리 정리
            match = self._getMatched(gcode, [self._G0_X_Y])
            if match:
                if self._nozzle_type.startswith('FFF'):
                    current_position = self._getNextPosition(current_position, [float(match.group(2)), float(match.group(3))])
                    if gcode_list[index-1].startswith('G1'):
                        self._retraction_index = index

                self._back_retraction = True
                gcode_list[index] = self._prettyFormat(match)
            
            match = self._getMatched(gcode, [self._G1_X_Y])
            if match:
                if self._nozzle_type.startswith('FFF'):
                    current_position = [float(match.group(2)), float(match.group(3))]
                self._back_retraction = False
                gcode_list[index] = self._prettyFormat(match)  
                continue
        return '\n'.join(gcode_list)

    def _removeRedundencyGCode(self, one_layer_gcode) -> str:
        # 중복 코드 제거
        modified_code = re.sub('G92 E0\nG92 E0', 'G92 E0', one_layer_gcode)

        # 중복된 G1 F000 코드 제거
        redundency_match = self._G1_F_G1_F.search(modified_code)
        if redundency_match is not None:
            modified_code = re.sub(pattern=redundency_match.group(0),\
                repl=redundency_match.group(1),\
                string=modified_code)
        
        modified_code = re.sub(self._RemovedMark + '\n', '', modified_code)
        return modified_code

    def _replaceLayerInfo(self, start_code) -> str:

        start_code =  start_code\
            .replace('{home_all_axis}',self._HOME_ALL_AXIS)\
            .replace('{dish_leveling_procedure}',self._DISH_LEVELING_PROCEDURE)

        return start_code\
            .replace('{print_temp}', self._G['PRINT_TEMP'] % self._quality.print_temperature)\
            .replace('{layer_height}', self._quality.layer_height_list)\
            .replace('{wall_thickness}', self._quality.wall_thickness_list)\
            .replace('{infill_sparse_density}', self._quality.infill_sparse_density_list)

    def _replaceDispenserSetupCode(self, start_code) -> str:
        return start_code\
            .replace(';{shot_time_list}', self._G['SHOT'] % self._quality.shot_time_list)\
            .replace(';{vac_time_list}', self._G['VAC'] % self._quality.vac_time_list)\
            .replace(';{interval_list}', self._G['INT'] % self._quality.interval_list)\
            .replace(';{shot_p_list}', self._G['SET_P'] % self._quality.shot_power_list)\
            .replace(';{vac_p_list}', self._G['VAC_P'] % self._quality.vac_power_list)

    # UV 명령어 삽입
    def _add_UV_Code(self, extruder_index) -> str:

        uv_per_layer = self._quality.uv_per_layer_list[extruder_index]
        start_layer = self._quality.uv_start_layer_list[extruder_index]
        layer = self._current_layer_index - start_layer + 1

        if layer >= 0 and (layer % uv_per_layer) == 0:
            return self._get_UV_Code(extruder_index)

        return ''

    # UV code
    def _get_UV_Code(self, extruder_index) -> str:
        if self._quality.uv_enable_list[extruder_index] is False:
            return ''

        code = ';UV\n{G59_G0_X0_Y0}{M172}{M381_CHANNEL}{M385_DIMMING}{M386_TIME}{M384}{P4_DURATION}'.format(**self._G)
        return code.format(
            channel = 0 if self._quality.uv_type_list[extruder_index] == '365' else 1, 
            dimming = self._quality.uv_dimming_list[extruder_index], 
            time = self._quality.uv_time_list[extruder_index], 
            duration = self._quality.uv_time_list[extruder_index] * 1000)

    def _getRokitExtruderName(self, index) -> str:
        return '{extruder_name} ; Selected Nozzle({nozzle_type})\n'.format(
            extruder_name = self._quality.ExtruderNames[index], 
            nozzle_type = self._quality.getVariantName(index))

    # 익스트루더가 교체될 때마다 추가로 붙는 명령어
    def _getExtruderSetupCode(self) -> str:

        previous_nozzle_type = self._quality.getVariantName(self._previous_index)
        g0af600 = self._G['G0_A_F600'].format(a_axis = self._quality.A_AxisPosition[self._current_index])
        g0b15f300 = self._G['G0_B15_F300']
        extruder = self._getRokitExtruderName(self._current_index)
        uvcode = self._get_UV_Code(self._previous_index)
        g0z40c40f420 = self._G['G0_Z40_C40_F420']
        m29b = self._G['M29_B']
        stopshot = self._G['M330']
        startshot = self._G['M301']
        g54g0x0y0= self._G['G54_G0_X0_Y0']
        g55g0x0y0= self._G['G55_G0_X0_Y0']
        g92e0 = self._G['G92_E0']

        code = ';{}'

        if self._previous_index == -1: # 처음나온 Nozzle
            # D1~D5
            if self._current_index > 0:
                code = '{extruder}{g0af600}{g54g0x0y0}{g0b15f300}'.format(
                        extruder = extruder,
                        g0af600 = g0af600,
                        g54g0x0y0 = g54g0x0y0,
                        g0b15f300 = g0b15f300
                    )
                code = '; <==== setup start when D1~5\n' + code + '; ==== setup end'
            # D6 - FFF
            elif self._nozzle_type.startswith('FFF'):
                code = '{extruder}{g54g0x0y0}{g92e0}'.format(
                        extruder = extruder,
                        g54g0x0y0 = g54g0x0y0,
                        g92e0 = g92e0,
                        g0b15f300 = g0b15f300
                    )
                code = '; <==== setup start when D6(Extruder)\n' + code + '; ==== setup end'
            # D6 - Hot Melt
            elif self._nozzle_type.startswith('Hot Melt'):
                code = '{extruder}{g54g0x0y0}{g92e0}'.format(
                        extruder = extruder,
                        g54g0x0y0 = g54g0x0y0,
                        g92e0 = g92e0
                    )
                code = '; <==== setup start when D6(Hot Melt)\n' + code + '; ==== setup end' 
        else:
            # 3. D6(Extruder)에서 D1~5로 변경된 경우
            if previous_nozzle_type.startswith('FFF') and self._current_index > 0:              
                code = '{g0z40c40f420}{m29b}{uvcode}{next_nozzle_pos}{stopshot}\n{extruder}{g0af600}{g54g0x0y0}{g0b15f300}'.format(
                        g0z40c40f420 = g0z40c40f420,
                        m29b = m29b,
                        uvcode = uvcode,
                        next_nozzle_pos = g55g0x0y0 if uvcode != '' else '',
                        stopshot = stopshot,
                        extruder = extruder,
                        g0af600 = g0af600,
                        g54g0x0y0 = g54g0x0y0,
                        g0b15f300 = g0b15f300
                    )
                code = '; <==== setup start when D6(Extruder)에서 D1~5\n' + code + '; ==== setup end' 
            # 4. D1~5에서 D6(Extruder)로 변경된 경우
            elif self._previous_index > 0 and self._nozzle_type.startswith('FFF'):                
                code = '{stopshot}{g0z40c40f420}{m29b}{uvcode}{next_nozzle_pos}\n{extruder}{g54g0x0y0}{g92e0}'.format(
                        stopshot = stopshot,
                        g0z40c40f420 = g0z40c40f420,
                        m29b = m29b,
                        uvcode = uvcode,
                        next_nozzle_pos = g54g0x0y0 if uvcode != '' else '',
                        extruder = extruder,
                        g54g0x0y0 = g54g0x0y0,
                        g92e0 = g92e0,
                        g0b15f300 = g0b15f300
                    )
                code = '; <==== setup start when D1~5에서 D6(Extruder)\n' + code + '; ==== setup end' 

            # 5. D6(Hot Melt)에서 D1~5로 변경된 경우
            elif previous_nozzle_type.startswith('Hot Melt') and self._current_index > 0:
                code = '{stopshot}{g0z40c40f420}{m29b}{uvcode}{next_nozzle_pos}\n{extruder}{g0af600}{g55g0x0y0}{g0b15f300}'.format(
                        stopshot = stopshot,
                        g0z40c40f420 = g0z40c40f420,
                        m29b = m29b,
                        uvcode = uvcode,
                        next_nozzle_pos = g55g0x0y0 if uvcode != '' else '',
                        extruder = extruder,
                        g0af600 = g0af600,
                        g55g0x0y0 = g55g0x0y0,
                        g0b15f300 = g0b15f300,
                    )
                code = '; <==== setup start when D6(Hot Melt)에서 D1~5\n' + code + '; ==== setup end' 

            # 6. 처음 또는 D1~D5에서 D6(Hot Melt)로 변경된 경우
            elif self._previous_index > 0 and self._nozzle_type.startswith('Hot Melt'):
                code = '{stopshot}{g0z40c40f420}{m29b}{uvcode}{next_nozzle_pos}\n{extruder}{g54g0x0y0}{g92e0}'.format(
                        stopshot = stopshot,
                        g0z40c40f420 = g0z40c40f420,
                        m29b = m29b,
                        uvcode = uvcode,
                        next_nozzle_pos = g54g0x0y0 if uvcode != '' else '',
                        extruder = extruder,
                        g54g0x0y0 = g54g0x0y0,
                        g92e0 = g92e0
                    )
                code = '; <==== setup start when D1~D5에서 D6(Hot Melt)\n' + code + '; ==== setup end' 

            # 7. 처음 또는 D1~D5에서 D1~D5으로 변경된 경우
            elif self._previous_index > 0 and self._current_index > 0:
                code = '{stopshot}{g0z40c40f420}{m29b}{uvcode}{next_nozzle_pos}\n{extruder}{g0af600}{g0b15f300}'.format(
                        stopshot = stopshot,
                        g0z40c40f420 = g0z40c40f420,
                        m29b = m29b,
                        uvcode = uvcode,
                        next_nozzle_pos = g55g0x0y0 if uvcode != '' else '',
                        extruder = extruder,
                        g0af600 = g0af600,
                        g0b15f300 = g0b15f300
                    )
                code = '; <==== setup start when D1~D5에서 D1~D5\n' + code + '; ==== setup end'
        return code

    # 사용된 익스트루더 index 기록
    def _addToActivatedExtruders(self, current_index) -> None:
        if current_index not in self._activated_index_list:
            self._activated_index_list.append(current_index) # T 명령어 정보 (0,1,2,3,4,5)

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
            gcode_spacing += self._G['G90_G0_C'].format(self._quality.Initial_layer0_list[self._current_index])
            gcode_spacing += self._G['G92_X0_Y0']
            gcode_spacing += ';Well Number: %d\n' % well_num

            gcode_clone.insert(0, gcode_spacing)
            self._replaced_gcode_list[self._index_of_EndOfStartCode:self._index_of_EndOfStartCode]= gcode_clone # put the clones in front of the end-code
            gcode_clone.remove(gcode_spacing)


    # start 코드 다음으로 붙는 준비 명령어
    def _setGcodeAfterStartGcode(self):

        start_codes = '\n' + self._startExtruderSetupCode + '\n;Start point\n'

        start_point = self._travel['start_point']
        if self._activated_index_list[0] == 0: # Left
            #if self._initial_extruder_did_something:
            start_codes += self._G['G54_G0_X0_Y0']
            if (self._build_plate_type == 'Well Plate'):
                start_codes += self._G['G90_G0_X_Y'] % (start_point.x(), start_point.y())

        else: # Right
            start_codes += self._G['G55_G0_X0_Y0']
            if (self._build_plate_type == 'Well Plate'):
                start_codes += self._G['G90_G0_X_Y'] % (start_point.x(), start_point.y())
            start_codes += self._G['G0_A_F600'].format(a_axis=self._quality.A_AxisPosition[self._activated_index_list[0]])
            start_codes += self._G['G0_B15_F300']
        
        if (self._build_plate_type == 'Well Plate'):
            start_codes += self._G['G92_X0_Y0']
            start_codes += ';Well Number: 0\n'
            self._cloneWellPlate()

        self._replaced_gcode_list[self._index_of_StartOfStartCode] += start_codes