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

        self._info = RokitExtrudersInfo()
        self._G_model = RokitGCodeModel()        
        self._G = self._G_model.GCODE

        self._build_dish_model = RokitBuildDishModel()

        # 외부 dict
        self._dish = {}
        self._current_z_value = None

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
        self._LAYER_NO = re.compile(r';LAYER:([0-9]+)')

        self._G0_or_G1 = re.compile(r'^G[0-1] ')
        self._G1_F_X_Y_E = re.compile(r'^G1 F[0-9.]+ X[0-9.-]+ Y[0-9.-]+ E[0-9.-]')
        self._G1_X_Y_E = re.compile(r'^G1 X[0-9.-]+ Y[0-9.-]+ E[0-9.-]')

        self._MarlinCodeForRemove = re.compile(r'M(140|190|104 [TS]|109 [TS]|141|205|105|107)')
        self._RemovedMark = '; to-be-removed'

        self._G1_F_E = re.compile(r'(G1 F[0-9.]+) E([0-9.-]+)')

        self._G1_F_Z = re.compile(r'(G1 F[0-9.]+) Z([0-9.]+)')
        self._G0_Z = re.compile(r'(G0) Z([0-9.]+)')
        self._G0_F_X_Y_Z = re.compile(r'(G0 F[0-9.]+) X([0-9.-]+) Y([0-9.-]+) Z([0-9.-]+)')
        self._G1_F_G1_F = re.compile(r'G1 F[0-9.]+\n(G1 F[0-9.]+\n)')

        self._DigitWithoutFloatingPoint = re.compile(r'([XYZ][0-9]+) ')

        self._is_shot_moment = True

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

    def _addFloatingPoint(self, gcode) -> str:         
        matched = self._DigitWithoutFloatingPoint.search(gcode)
        if matched:
            return gcode.replace(matched.group(1), matched.group(1) + '.0 ')
        return gcode

    def run(self) -> None:
        for index, one_layer_gcode in enumerate(self._replaced_gcode_list):
            modified_gcode = one_layer_gcode
            if ';FLAVOR:Marlin' in one_layer_gcode:
                modified_gcode = one_layer_gcode.replace(';FLAVOR:Marlin', ';F/W : 7.7.1.x')
            elif '*** start of start code' in one_layer_gcode:
                start_code = one_layer_gcode[one_layer_gcode.find(self._StartOfStartCode)+len(self._StartOfStartCode):one_layer_gcode.rfind(self._EndOfStartCode)]

                self._nozzle_type = self._setExtruder(one_layer_gcode)
                modified_gcode = self._info.ExtruderNames[self._current_index] + ' ; Selected Nozzle(%s)\n' % self._nozzle_type
                modified_gcode += self._replaceLayerInfo(start_code)

                if self._info.dispensor_enable: # start 코드일때 만 
                    modified_gcode = self._StartOfStartCode + '\n' +\
                        self._replaceDispenserSetupCode(modified_gcode) + self._EndOfStartCode + '\n'

            elif '*** start of end code' in one_layer_gcode:
                modified_gcode = self._StartOfEndCode +\
                    one_layer_gcode[one_layer_gcode.find(self._StartOfEndCode)+len(self._StartOfEndCode):one_layer_gcode.rfind(self._EndOfEndCode)] +\
                    self._EndOfEndCode + '\n'

            elif one_layer_gcode.startswith(';LAYER:'):
                self._current_layer_index = self._getLayerIndex(one_layer_gcode)
                modified_gcode = self._convertOneLayerGCode(one_layer_gcode)          

                modified_gcode = self._removeRedundencyGCode(modified_gcode)
                modified_gcode = re.sub('-\.', '-0.', modified_gcode) # 정수를 0으로 채우기
                modified_gcode += self._get_UV_Code(self._current_index) + '\n'


            elif re.match(self._G1_F_E, one_layer_gcode) is not None:
                modified_gcode = self._convertOneLayerGCode(one_layer_gcode)

            self._replaced_gcode_list[index] = modified_gcode
        self._setGcodeAfterStartGcode() 
    
    def _getExtruderIndex(self, gcode) -> int:
        extruderRe = re.compile(r'T([0-5]+)')
        return int(extruderRe.search(gcode).group(1))
    
    # shot 커맨드 관리
    def _controlShotCode(self, gcode):
        if (self._G1_F_X_Y_E.match(gcode) or self._G1_X_Y_E.match(gcode)) and self._is_shot_moment:
            self._is_shot_moment = False
            return self._G['StartShot'] + gcode # modified_gcode = self._controlShotCode(modified_gcode)
        elif re.match(self._G0_or_G1,gcode) is not None and self._is_shot_moment is False:
            self._is_shot_moment = True
            return self._G['StopShot'] + gcode

    def _convertOneLayerGCode(self, one_layer_gcode) -> str:
        gcode_list = one_layer_gcode.split('\n')
        for index, gcode in enumerate(gcode_list):
            modified_gcode = gcode

            if self._MarlinCodeForRemove.match(gcode) or\
                self._nozzle_type.startswith('FFF') is False and gcode == 'G92 E0':
                modified_gcode = self._RemovedMark
            elif gcode.startswith('T'): # Nozzle changed
                self._nozzle_type = self._setExtruder(gcode)
                modified_gcode = '{uv_code}\n{extruder_name}{nozzle}{extruder_setup_code}'.format(
                    uv_code = self._get_UV_Code(self._previous_index),
                    extruder_name = self._info.ExtruderNames[self._current_index],
                    nozlle = ' ; Selected Nozzle(%s)\n' % self._nozzle_type,
                    extruder_setup_code = self._getExtraExtruderCode())
            elif gcode.startswith('G'):
                # remove E command
                if gcode.startswith('G1') and self._nozzle_type.startswith('FFF') is False and 'E' in gcode:
                    modified_gcode = modified_gcode[:modified_gcode.find('E')-1]
                # control shot command
                modified_gcode = self._addFloatingPoint(modified_gcode)
                # convert z command
                modified_gcode = self._convert_Z_To_C(gcode, modified_gcode)
                modified_gcode = self._controlShotCode(modified_gcode)

            gcode_list[index] = modified_gcode
        return '\n'.join(gcode_list)

    def _removeRedundencyGCode(self, one_layer_gcode) -> str:
        # 중복 코드 제거
        modified_code = re.sub('G92 E0\nG92 E0', 'G92 E0', one_layer_gcode)

        # 중복된 G1 F000 코드 제거
        redundency_match = self._G1_F_G1_F.search(modified_code)
        if redundency_match != None:
            modified_code = re.sub(pattern=redundency_match.group(0),\
                repl=redundency_match.group(1),\
                string=modified_code)
        
        modified_code = re.sub(self._RemovedMark + '\n', '', modified_code)
        return modified_code

    def _replaceLayerInfo(self, replaced) -> str:
        print_temp = self._info.print_temperature
        layer_height_list = self._info.layer_height_list
        wall_thickness_list = self._info.wall_thickness_list
        infill_sparse_density_list = self._info.infill_sparse_density_list

        return replaced\
            .replace('{print_temp}', self._G['PRINT_TEMP'] % print_temp)\
            .replace('{layer_height}', layer_height_list)\
            .replace('{wall_thickness}', wall_thickness_list)\
            .replace('{infill_sparse_density}', infill_sparse_density_list)

    def _replaceDispenserSetupCode(self, replaced) -> str:
        shot_time_list = self._info.shot_time_list
        vac_time_list = self._info.vac_time_list
        interval_list = self._info.interval_list
        shot_power_list = self._info.shot_power_list
        vac_power_list = self._info.vac_power_list

        return replaced\
            .replace(';{shot_time_list}', self._G['SHOT'] % shot_time_list)\
            .replace(';{vac_time_list}', self._G['VAC'] % vac_time_list)\
            .replace(';{interval_list}', self._G['INT'] % interval_list)\
            .replace(';{shot_p_list}', self._G['SET_P'] % shot_power_list)\
            .replace(';{vac_p_list}', self._G['VAC_P'] % vac_power_list)

    # UV 명령어 삽입
    def _get_UV_Code(self, index) -> str:

        uv_per_layer = self._info.uv_per_layer_list[index]
        if self._info.uv_enable_list[index] and (index % uv_per_layer) == 0:
            return 'UV\n{UV_A_Position}{UV_A_On}{UVChannel}{UVDimming}{UVTime}{TimerLED}{P4_P}{ToWorkingLayer}'.format(**self._G,
                uv_channel = 0 if self._info.uv_type_list[index] == '405' else 1, 
                uv_dimming = self._info.uv_dimming_list[index], 
                uv_time = self._info.uv_time_list[index], 
                uv_delay = self._info.uv_time_list[index] *1000)
        return ''

    # 익스트루더가 교체될 때마다 추가로 붙는 명령어
    def _getExtraExtruderCode(self) -> str:

        extra_code = ''
        if self._current_index == 0:
            if self._previous_index != 0:
                extra_code += self._G['M29_B'] +\
                              self._G['G0_C0'] +\
                              self._G['LEFT_G91_G0_X_Y'] % (self._info.LeftExtruder_X_Offset, 0.0) +\
                              self._G['G92_X0_Y0']
        else:
            # Left --> Right
            if self._previous_index == 0:
                extra_code += self._G['G0_Z0'] +\
                              self._G['RIGHT_G91_G0_X_Y'] % (-self._info.LeftExtruder_X_Offset, 0.0) +\
                              self._G['G92_X0_Y0'] +\
                              self._G['M29_B'] +\
                              self._G['G0_A0_F600'] +\
                              self._G['G0_B15.0_F300']               
            else:        
                current_A_axis_pos = self._info.A_AxisPosition[self._current_index]
                extra_code += self._G['M29_B'] +\
                              self._G['G0_A_F600'] % current_A_axis_pos +\
                              self._G['G0_B15.0_F300']

        return extra_code

    # 사용된 익스트루더 index 기록
    def _addToActivatedExtruders(self, current_index) -> None:
        if current_index not in self._activated_index_list:
            self._activated_index_list.append(current_index) # T 명령어 정보 (0,1,2,3,4,5)

    # Z 좌표 관리
    def _convert_Z_To_C(self, gcode, modified_gcode) -> str:

        if self._current_index == 0:
            initial_layer0 = self._info.InitialLayer0_Z
            axisName = ' Z'
        else:
            initial_layers0 = self._info.InitialLayer0_C
            axisName = 'C'

        matched_code = None
        if self._G1_F_Z.match(gcode):
            matched_code = self._G1_F_Z.search(gcode)
            self._current_z_value = float(matched_code.group(2))

            if self._current_index == 0:
                modified_gcode = matched_code.group(1) + axisName + str(self._current_z_value - self._info.layer_height_0 + initial_layer0)
            else:
                modified_gcode = matched_code.group(1) + '\n' 
                modified_gcode += 'G0 ' + axisName + str(self._current_z_value - self._info.layer_height_0 + initial_layer0)

        elif self._G0_F_X_Y_Z.match(gcode):
            matched_code = self._G0_F_X_Y_Z.search(gcode)
            self._current_z_value = float(matched_code.group(4))
            sub_height = self._current_z_value - self._info.layer_height_0

            if (sub_height == 0):
                return re.sub(r' Z([0-9.]+)','',gcode)
            elif self._current_index == 0:
                replaced_gcode = re.sub(r'Z([0-9.]+)','Z%.2f',gcode)
                modified_gcode = replaced_gcode % (sub_height + initial_layer0)
            else:
                modified_gcode = re.sub(r' Z([0-9.]+)','\n',gcode)
                modified_gcode += 'G0 ' + axisName + str(sub_height + initial_layer0)

        return modified_gcode

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
            self._replaced_gcode_list[-2:-2]= gcode_clone  # put the clones in front of the end-code
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
        if self._activated_index_list[0] == 0:
            x = start_point.x()
        else:
            x = -start_point.x()

        start_codes = '\n;Start point\n' + self._G['LEFT_G91_G0_X_Y'] % (0,0) 

        if self._activated_index_list[0] == 0: # Left
            start_codes += self._G['G0_Z_RESET']
        else:
            start_codes += self._G['G90_G0_C_RESET'] +\
                self._G['G0_A_F600'] % (self._info.A_AxisPosition[self._activated_index_list[0]]) +\
                self._G['G0_B15.0_F300'] # G78 B15.

        start_codes += self._G['G92_X0_Y0'] # 'G92 X0.0 Y0.0 Z0.0 C0.0\n'
        
        if (build_plate_type == 'Well Plate'):
            start_codes += ';Well Number: 0\n'
            self._cloneWellPlate(trip)

        self._replaced_gcode_list[1] += start_codes
        self._replaced_gcode_list.insert(-1,self._G['G92_Z0'])
        self._replaced_gcode_list.insert(-1,self._G['G92_C0'])
