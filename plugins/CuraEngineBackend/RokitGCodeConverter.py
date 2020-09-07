# Copyright (c) 2020 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from string import Formatter
from enum import IntEnum
from UM.Logger import Logger
from typing import Any, cast, Dict, List, Optional, Set
import re
import Arcus #For typing.

from cura.CuraApplication import CuraApplication
from cura.Machines.Models.RokitGCodeModel import RokitGCodeModel
from cura.Machines.Models.RokitBuildDishModel import RokitBuildDishModel
from .RokitExtrudersInfo import RokitExtrudersInfo

class RokitGCodeConverter:
    def __init__(self) -> None:    

        self._pretty_format = True
        self._info = RokitExtrudersInfo()
        self._G_model = RokitGCodeModel()        
        self._G = self._G_model.GCODE

        self._build_dish_model = RokitBuildDishModel()

        # 외부 dict
        self._dish = {}

        # 선택한 명령어
        self._current_index = None  
        self._activated_index_list = [] 

        self._previous_index = -1
        self._nozzle_type = ''
        
        self._current_layer_index = None

        # *** G-code Line(command) 관리 변수
        self._replaced_gcode_list = []        

        # startcode / endcode
        self._StartOfStartCode = '\n; (*** start of start code for Dr.Invivo 4D6)'
        self._EndOfStartCode = '\n; (*** end of start code for Dr.Invivo 4D6)'

        self._StartOfEndCode = '\n; (*** start of end code for Dr.Invivo 4D6)'
        self._EndOfEndCode = '\n; (*** end of end code for Dr.Invivo 4D6)'

        # match patterns
        self._Extruder_NO = re.compile(r'^T([0-9]+)')
        self._LAYER_NO = re.compile(r'^;LAYER:([0-9]+)')

        _FP = r'[+-]?[0-9]*[.]?[0-9]+'

        self._G0_or_G1 = re.compile(r'^G[0-1] ')
        self._G1_F_X_Y_E = re.compile(r'^(G1 F{f}) X({x}) Y({y}) E({e})'.format(f=_FP,x=_FP,y=_FP,e=_FP))
        self._G1_X_Y_E = re.compile(r'^(G1) X({x}) Y({y}) E({e})'.format(x=_FP,y=_FP,e=_FP))

        self._MarlinCodeForRemoval = re.compile(r'M(82|140|190|104 [TS]|109 [TS]|141|205|105|107)')
        self._RemovedMark = '; to-be-removed'

        self._G1_F_E = re.compile(r'^()G1 F{f} E{e}'.format(f=_FP,e=_FP))

        self._G1_F_Z = re.compile(r'^(G1 F{f}) Z({z})'.format(f=_FP,z=_FP))
        self._G0_Z = re.compile(r'^(G0) Z({z})'.format(z=_FP))
        self._G0_F_X_Y_Z = re.compile(r'^(G0 F{f}) X({x}) Y({y}) Z({z})'.format(f=_FP,x=_FP,y=_FP,z=_FP))
        self._G0_X_Y_Z = re.compile(r'^(G0) X({x}) Y({y}) Z({z})'.format(x=_FP,y=_FP,z=_FP))

        self._G01_X_Y = re.compile(r'^(G0|G1) X({x}) Y({y})'.format(x=_FP,y=_FP))

        self._G1_F_G1_F = re.compile(r'^G1 F{f1}\n(G1 F{f2}\n)'.format(f1=_FP,f2=_FP))

        self._OnlyInteger = re.compile(r'([XYZ][-+]?\d+)')

        self._is_shot_moment = True
        self._index_of_start_code = -1

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
        return self._info.getVariantName(self._current_index)
    
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
                self._index_of_start_code = index
                modified_gcode = self._convertOneLayerGCode(one_layer_gcode, True)     
                modified_gcode = self._replaceLayerInfo(modified_gcode)
                if self._info.dispensor_enable:
                   modified_gcode = self._replaceDispenserSetupCode(modified_gcode)

            elif self._StartOfEndCode in one_layer_gcode:
                modified_gcode = self._StartOfEndCode +\
                    one_layer_gcode[one_layer_gcode.find(self._StartOfEndCode)+len(self._StartOfEndCode):one_layer_gcode.rfind(self._EndOfEndCode)] +\
                    self._EndOfEndCode + '\n'

            elif one_layer_gcode.startswith(';LAYER:'):
                self._current_layer_index = self._getLayerIndex(one_layer_gcode)

                modified_gcode = self._convertOneLayerGCode(one_layer_gcode)     
                modified_gcode += self._get_UV_Code(self._current_index) + '\n'

            elif self._G1_F_E.match(one_layer_gcode) is not None:
                modified_gcode = self._convertOneLayerGCode(one_layer_gcode)

            self._replaced_gcode_list[index] = self._removeRedundencyGCode(modified_gcode)
        self._setGcodeAfterStartGcode() 
    
    def _getExtruderIndex(self, gcode) -> int:
        matched = self._Extruder_NO.search(gcode)
        return int(matched.group(1))

    def _shotControl(self, gcode) -> str:
        gcode = self._G['StartShot' if self._is_shot_moment else 'StopShot'] + gcode
        self._is_shot_moment = not self._is_shot_moment

        return gcode

    def _update_Z_value(self, gcode, matched) -> str:
        if matched is None:
            return

        initial_layer0_height = self._info.Initial_layer0_list[self._current_index]
        
        if len(matched.groups()) > 3:
            front_code = '{head} X{x:<.2f} Y{y:.2f}'.format(head=matched.group(1), x=float(matched.group(2)), y=float(matched.group(3)))
            z_value = float(matched.group(4))
        else:
            front_code = matched.group(1)
            z_value = float(matched.group(2))        
        
        z_delta = z_value - self._info.layer_height_0

        if gcode.startswith('G0') and z_delta == 0:
            return front_code
        
        new_z_value = z_delta + initial_layer0_height

        if self._nozzle_type.startswith('Dispenser'):
            z_value_form = '\nG0 C{new_z_value:<.2f}'.format(new_z_value=new_z_value)
        else:
            z_value_form = ' Z{new_z_value:<.2f}'.format(new_z_value=new_z_value)

        return front_code + z_value_form # ';' + str(matched.group(2))

    def _getMatched(self, gcode, patterns):
        for p in patterns:
            matched = p.match(gcode)
            if matched:
                return matched
        return None

    def _convertOneLayerGCode(self, one_layer_gcode, isStartCode=False) -> str:
        gcode_list = one_layer_gcode.split('\n')
        for index, gcode in enumerate(gcode_list):

            if self._MarlinCodeForRemoval.match(gcode) or\
                (self._nozzle_type.startswith('FFF') is False and gcode == 'G92 E0'):
                gcode_list[index] = self._RemovedMark

            elif gcode.startswith('T'): # Nozzle changed
                self._nozzle_type = self._setExtruder(gcode)
                extruder_setup_code = '' if isStartCode else self._getExtraExtruderCode()
                gcode_list[index] = '{extruder_name} ; Selected Nozzle({nozzle_type})\n{extruder_setup_code}'.format(
                    extruder_name = self._info.ExtruderNames[self._current_index],
                    nozzle_type=self._nozzle_type,
                    extruder_setup_code = extruder_setup_code)

            elif gcode.startswith('G1') or gcode.startswith('G0'):

                # remove retraction when Dispensor
                m = self._getMatched(gcode, [self._G1_F_E])
                if m:
                    if self._nozzle_type.startswith('Dispenser'):
                        gcode_list[index] = self._RemovedMark
                    continue

                # update Z value
                m = self._getMatched(gcode, [self._G0_X_Y_Z, self._G0_F_X_Y_Z, self._G1_F_Z])
                if m:
                    gcode_list[index] = self._update_Z_value(gcode, m)
                    continue
               
                # add Start Shot/ Stop shot code
                m = self._getMatched(gcode, [self._G1_F_X_Y_E, self._G1_X_Y_E])
                if m:
                    gcode = '{head} X{x:<.2f} Y{y:<.2f}'.format(head=m.group(1), x=float(m.group(2)), y=float(m.group(3)))
                    if self._nozzle_type.startswith('FFF'):
                        gcode += ' E{e}'.format(e=m.group(4))

                    gcode_list[index] = self._shotControl(gcode) if self._is_shot_moment else gcode
                    continue

                # pretty format
                m = self._getMatched(gcode, [self._G01_X_Y])
                if m:
                    gcode = '{head} X{x:<.2f} Y{y:<.2f}'.format(head=m.group(1), x=float(m.group(2)), y=float(m.group(3)))
                   
                gcode_list[index] = gcode if self._is_shot_moment else self._shotControl(gcode)

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
            .replace('{home_all_axis}','M29 Z\nM29 C\nM29 B\nG0 B15. F300\nM29 B\nM29 Y\nM29 X\nG79\nM29 A\n')\
            .replace('{dish_leveling_procedure}','G0 X0. Y0. F300\nG29\nG0 X15. F300\nG29\nG0 X-15. Y15. F300\nG29\nG0 X-30. Y0. F300\nG29\nG0 X0. Y-15. F300\nG29\nM420\nG0 X0. Y0. F300\n')

        return start_code\
            .replace('{print_temp}', self._G['PRINT_TEMP'] % self._info.print_temperature)\
            .replace('{layer_height}', self._info.layer_height_list)\
            .replace('{wall_thickness}', self._info.wall_thickness_list)\
            .replace('{infill_sparse_density}', self._info.infill_sparse_density_list)

    def _replaceDispenserSetupCode(self, start_code) -> str:
        return start_code\
            .replace(';{shot_time_list}', self._G['SHOT'] % self._info.shot_time_list)\
            .replace(';{vac_time_list}', self._G['VAC'] % self._info.vac_time_list)\
            .replace(';{interval_list}', self._G['INT'] % self._info.interval_list)\
            .replace(';{shot_p_list}', self._G['SET_P'] % self._info.shot_power_list)\
            .replace(';{vac_p_list}', self._G['VAC_P'] % self._info.vac_power_list)


    # UV 명령어 삽입
    def _get_UV_Code(self, index) -> str:
        if self._current_layer_index == 0 or self._info.uv_enable_list[index] is False:
            return ''

        uv_per_layer = self._info.uv_per_layer_list[index]
        uv_code = ''
        if (self._current_layer_index % uv_per_layer) == 0:
            uv_code = ';UV\n{M29_B}{UV_A_Curing_Position}{G0_Z40}{UV_A_On}{UV_Channel}{UV_Dimming}{UV_Time}{TimerLED}{P4_P}{G0_B15_F300}'.format(**self._G)
            uv_code = uv_code.format(
                uv_channel = 0 if self._info.uv_type_list[index] == '405' else 1, 
                uv_dimming = self._info.uv_dimming_list[index], 
                uv_time = self._info.uv_time_list[index], 
                uv_delay = self._info.uv_time_list[index] * 1000)

        return uv_code

    # 익스트루더가 교체될 때마다 추가로 붙는 명령어
    def _getExtraExtruderCode(self) -> str:

        extra_code = ''
        # Right --> Left
        if self._current_index == 0 and self._previous_index != 0:
            extra_code = '{M29_B}{G0_C0}{LEFT_G91_G0_X_Y}{G92_X0_Y0}'.format(**self._G)
            extra_code = extra_code.format(left_x = self._info.LeftExtruder_X_Offset, left_y = 0.0) # LEFT_G91_G0_X_Y
        # Left --> Right
        elif self._current_index != 0 and self._previous_index == 0:
            extra_code = '{G0_Z0}{RIGHT_G91_G0_X_Y}{G92_X0_Y0}{M29_B}{G0_A0_F600}{G0_B15_F300}'.format(**self._G)
            extra_code = extra_code.format(right_x = self._info.LeftExtruder_X_Offset, right_y = 0.0) # RIGHT_G91_G0_X_Y
        # Right --> Right
        elif self._current_index != 0 and self._previous_index != 0:
            extra_code = '{M29_B}{G0_A_F600}{G0_B15_F300}'.format(**self._G)
            extra_code = extra_code.format(a_axis = self._info.A_AxisPosition[self._current_index]) # A axis

        return extra_code

    # 사용된 익스트루더 index 기록
    def _addToActivatedExtruders(self, current_index) -> None:
        if current_index not in self._activated_index_list:
            self._activated_index_list.append(current_index) # T 명령어 정보 (0,1,2,3,4,5)

    # Well plate 복제 기능
    def _cloneWellPlate(self, trip):
        clone_num = trip['well_number'] # 본코드를 제외한 복제 코드는 전체에서 1개를 빼야함.
        line_seq = trip['line_seq']
        # z_height = trip['z']

        gcode_clone = self._replaced_gcode_list[2:-1] # 수정 필요 *** (수로 범위를 설정하면 안됨)
        std_str = self._G['G90_G0_XY_ZERO']
        travel_forward = True

        gcode_body = []
        for i in range(1,clone_num): # Clone number ex) 1 ~ 96
            if i % line_seq == 0:
                direction = 'X'
                distance = -trip['spacing']
                travel_forward = not travel_forward
            else:
                if travel_forward:
                    direction = 'Y'
                    distance = -trip['spacing']
                elif not travel_forward:
                    direction = 'Y'
                    distance = trip['spacing']

            gcode_spacing = ';hop_spacing\n' +\
                self._G['G92_E0'] +\
                self._G['G90_G0_XY_ZERO'] +\
                self._G['G90_G0_C'].format(-4.0)
            if direction == 'X':
                gcode_spacing += self._G['G91_G0_X'] % distance 
            else:
                gcode_spacing += self._G['G91_G0_Y'] % distance
            gcode_spacing += self._G['G90_G0_C'].format(self._info.InitialLayer0_C)
            gcode_spacing += self._G['G92_X0_Y0']
            gcode_spacing += ';Well Number: %d\n' % i

            gcode_clone.insert(0,gcode_spacing)
            self._replaced_gcode_list[-2:-2]= gcode_clone # put the clones in front of the end-code
            gcode_clone.remove(gcode_spacing)

    # start 코드 다음으로 붙는 준비 명령어
    # 'trip': {'line_seq':96/8, 'spacing':9.0, 'z': 10.8, 'start_point': QPoint(74,49.5)}})
    def _setGcodeAfterStartGcode(self):
        trip= {}
        build_plate = self._info.getGlobalContainerStackProperty('machine_build_dish_type')
        build_plate_type = build_plate[:build_plate.find(':')]
        for index in range(self._build_dish_model.count):
            self._dish = self._build_dish_model.getItem(index)
            if self._dish['product_id'] == build_plate:
                trip = self._dish['trip'] # Build plate가 정해짐
                break

        start_point = trip['start_point']

        start_codes = '\n;Start point\n'
        if self._activated_index_list[0] == 0: # Left
            start_codes += self._G['LEFT_G91_G0_X0_Y0']
            start_codes += self._G['G0_Z_RESET']
            start_codes += self._G['G92_Z0']
        else:
            start_codes += self._G['RIGHT_G91_G0_X0_Y0']
            start_codes += self._G['G90_G0_C_RESET']
            start_codes += self._G['G92_C0']

            start_codes += self._G['G0_A_F600'] % (self._info.A_AxisPosition[self._activated_index_list[0]])
            start_codes += self._G['G0_B15_F300'] 
        
        
        if (build_plate_type == 'Well Plate'):
            start_codes += ';Well Number: 0\n'
            self._cloneWellPlate(trip)

        self._replaced_gcode_list[self._index_of_start_code] += start_codes

        if self._current_index > 0:
            self._replaced_gcode_list.insert(-1,self._G['G92_C0'])
        else:
            self._replaced_gcode_list.insert(-1,self._G['G92_Z0'])
