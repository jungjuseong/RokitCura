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

class RokitPattern:
    def __init__(self) -> None:    

        self._Q = RokitPrintQuality()
        self._G = RokitGCodeModel().GCODE

        g_model = RokitGCodeModel()        
        self._G = g_model.GCODE

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

        self.HOME_ALL_AXIS = '; Home all axis\n' +\
                    'M29 Z\n' +\
                    'M29 C\n' +\
                    'M29 B\n' +\
                    'G0 B15. F300\n' +\
                    'M29 B\n' +\
                    'M29 A\n' +\
                    'M29 Y\n' +\
                    'M29 X\n' +\
                    'G79\n'

        self.DISH_LEVELING_PROCEDURE = '; Dish leveling procedure\n' +\
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
        self.Extruder_NO = re.compile(r'^T([0-9]+)')
        self.LAYER_NO = re.compile(r'^;LAYER:([0-9]+)')

        _FP = r'[+-]?\d*[.]?\d+'

        self.G0_or_G1 = re.compile(r'^G[0-1] ')
        self.G92_E0 = re.compile(r'^(G92 E0$)')

        self.G1_F_X_Y_E = re.compile(r'(G1 F{f}) X({x}) Y({y}) E({e})'.format(f=_FP,x=_FP,y=_FP,e=_FP))
        self.G1_X_Y_E = re.compile(r'(G1) X({x}) Y({y}) E({e})'.format(x=_FP,y=_FP,e=_FP))

        self.MarlinCodeForRemoval = re.compile(r'M(82|140|190|104 [TS]|109 [TS]|141|205|105|107)')
        self.RemovedMark = '; to-be-removed'

        self.G1_F_E = re.compile(r'^(G1 F{f}) E({e})'.format(f=_FP,e=_FP))
        self.G1_F_Z = re.compile(r'^(G1 F{f}) Z({z})'.format(f=_FP,z=_FP))
        self.G0_Z = re.compile(r'^(G0) Z({z})'.format(z=_FP))
        self.G0_F_X_Y_Z = re.compile(r'^(G0 F{f}) X({x}) Y({y}) Z({z})'.format(f=_FP,x=_FP,y=_FP,z=_FP))
        self.G0_F_X_Y = re.compile(r'^(G0 F{f}) X({x}) Y({y})'.format(f=_FP,x=_FP,y=_FP))
        self.G0_X_Y_Z = re.compile(r'^(G0) X({x}) Y({y}) Z({z})'.format(x=_FP,y=_FP,z=_FP))

        self.G0_X_Y = re.compile(r'^(G0) X({x}) Y({y})'.format(x=_FP,y=_FP))
        self.G1_X_Y = re.compile(r'^(G1) X({x}) Y({y})'.format(x=_FP,y=_FP))

        self.G1_F_G1_F = re.compile(r'^G1 F{f1}\n(G1 F{f2}\n)'.format(f1=_FP,f2=_FP))
        self.OnlyInteger = re.compile(r'([XYZ][-+]?\d+)')

    def getLayerIndex(self, one_layer_gcode) -> int:
        return int(self.LAYER_NO.search(one_layer_gcode).group(1))

    def getExtruderIndex(self, gcode) -> int:
        matched = self.Extruder_NO.search(gcode)
        return int(matched.group(1))

    def getRokitExtruderName(self, index) -> str:
        return '{extruder_name} ; Selected Nozzle({nozzle_type})\n'.format(
            extruder_name = self._Q.ExtruderNames[index], 
            nozzle_type = self._Q.getVariantName(index))

    # UV code
    def get_UV_Code(self, extruder_index) -> str:
        code = ';UV\n{G59_G0_X0_Y0}{M172}{M381_CHANNEL}{M385_DIMMING}{M386_TIME}{M384}{P4_DURATION}'.format(**self._G)
        return code.format(
            channel = 0 if self._Q.uv_type_list[extruder_index] == '365' else 1, 
            dimming = self._Q.uv_dimming_list[extruder_index], 
            time = self._Q.uv_time_list[extruder_index], 
            duration = self._Q.uv_time_list[extruder_index] * 1000)

    # 익스트루더가 교체될 때마다 추가로 붙는 명령어
    def getExtruderSetupCode(self, previous_index, current_index) -> str:

        current_nozzle_type = self._Q.getVariantName(current_index)
        previous_nozzle_type = self._Q.getVariantName(previous_index)
        
        g0af600 = self._G['G0_A_F600'].format(a_axis = self._Q.A_AxisPosition[current_index])
        g0b15f300 = self._G['G0_B15_F300']
        extruder = self._P.getRokitExtruderName(current_index)
        uvcode = self._get_UV_Code(previous_index)
        g0z40c40f420 = self._G['G0_Z40_C40_F420']
        m29b = self._G['M29_B']
        stopshot = self._G['M330']
        startshot = self._G['M301']
        G64G0X0Y0= self._G['G54_G0_X0_Y0']
        G55G0X0Y0= self._G['G55_G0_X0_Y0']
        g92e0 = self._G['G92_E0']

        code = ';{}'

        if previous_index == -1: # 처음나온 Nozzle
            # D1~D5
            if current_index > 0:
                code = '{extruder}{g0af600}{g54g0x0y0}{g0b15f300}'.format(
                        extruder = extruder,
                        g0af600 = g0af600,
                        g54g0x0y0 = G64G0X0Y0,
                        g0b15f300 = g0b15f300
                    )
                code = '; <==== setup start when D1~5\n' + code + '\n'
            # D6 - FFF
            elif nozzle_type.startswith('FFF'):
                code = '{extruder}{g54g0x0y0}'.format(
                        extruder = extruder,
                        g54g0x0y0 = G64G0X0Y0,                        
                        g0b15f300 = g0b15f300
                    )
                code = '; <==== setup start when D6(Extruder)\n' + code + '\n'
            # D6 - Hot Melt
            elif nozzle_type.startswith('Hot Melt'):
                code = '{extruder}{g54g0x0y0}{g92e0}'.format(
                        extruder = extruder,
                        g54g0x0y0 = G64G0X0Y0,
                        g92e0 = g92e0
                    )
                code = '; <==== setup start when D6(Hot Melt)\n' + code + '\n' 
        else:
            # 3. D6(Extruder)에서 D1~5로 변경된 경우
            if previous_nozzle_type.startswith('FFF') and self._current_index > 0:              
                code = '{g0z40c40f420}{m29b}{uvcode}{next_nozzle_pos}{stopshot}\n{extruder}{g0af600}{g55g0x0y0}{g0b15f300}'.format(
                        g0z40c40f420 = g0z40c40f420,
                        m29b = m29b,
                        uvcode = uvcode,
                        next_nozzle_pos = G55G0X0Y0 if uvcode != '' else '',
                        stopshot = stopshot,
                        extruder = extruder,
                        g0af600 = g0af600,
                        g55g0x0y0 = G55G0X0Y0 if uvcode == '' else '',
                        g0b15f300 = g0b15f300
                    )
                code = '; <==== setup start when D6(Extruder)에서 D1~5\n' + code + '\n' 
            # 4. D1~5에서 D6(Extruder)로 변경된 경우
            elif previous_index > 0 and nozzle_type.startswith('FFF'):                
                code = '{stopshot}{g0z40c40f420}{m29b}{next_nozzle_pos}\n{extruder}{g92e0}'.format(
                        stopshot = stopshot,
                        g0z40c40f420 = g0z40c40f420,
                        m29b = m29b,                        
                        next_nozzle_pos = G64G0X0Y0 if uvcode != '' else '',
                        extruder = extruder,
                        g92e0 = g92e0,
                        g0b15f300 = g0b15f300
                    )
                code = '; <==== setup start when D1~5에서 D6(Extruder)\n' + code + '\n'

            # 5. D6(Hot Melt)에서 D1~5로 변경된 경우
            elif previous_nozzle_type.startswith('Hot Melt') and self._current_index > 0:
                code = '{stopshot}{g0z40c40f420}{m29b}{uvcode}{next_nozzle_pos}\n{extruder}{g0af600}{g55g0x0y0}{g0b15f300}'.format(
                        stopshot = stopshot,
                        g0z40c40f420 = g0z40c40f420,
                        m29b = m29b,
                        uvcode = uvcode,
                        next_nozzle_pos = G55G0X0Y0 if uvcode != '' else '',
                        extruder = extruder,
                        g0af600 = g0af600,
                        g55g0x0y0 = G55G0X0Y0,
                        g0b15f300 = g0b15f300,
                    )
                code = '; <==== setup start when D6(Hot Melt)에서 D1~5\n' + code + '\n' 

            # 6. 처음 또는 D1~D5에서 D6(Hot Melt)로 변경된 경우
            elif previous_index > 0 and nozzle_type.startswith('Hot Melt'):
                code = '{stopshot}{g0z40c40f420}{m29b}{uvcode}{next_nozzle_pos}\n{extruder}{g54g0x0y0}{g92e0}'.format(
                        stopshot = stopshot,
                        g0z40c40f420 = g0z40c40f420,
                        m29b = m29b,
                        uvcode = uvcode,
                        next_nozzle_pos = G64G0X0Y0 if uvcode != '' else '',
                        extruder = extruder,
                        g54g0x0y0 = G64G0X0Y0,
                        g92e0 = g92e0
                    )
                code = '; <==== setup start when D1~D5에서 D6(Hot Melt)\n' + code + '\n'

            # 7. 처음 또는 D1~D5에서 D1~D5으로 변경된 경우
            elif previous_index > 0 and self._current_index > 0:
                code = '{stopshot}{g0z40c40f420}{m29b}{uvcode}{next_nozzle_pos}\n{extruder}{g0af600}{g0b15f300}'.format(
                        stopshot = stopshot,
                        g0z40c40f420 = g0z40c40f420,
                        m29b = m29b,
                        uvcode = uvcode,
                        next_nozzle_pos = G55G0X0Y0 if uvcode != '' else '',
                        extruder = extruder,
                        g0af600 = g0af600,
                        g0b15f300 = g0b15f300
                    )
                code = '; <==== setup start when D1~D5에서 D1~D5\n' + code + '\n'
        return code

    def getMatched(self, gcode, patterns):
        for p in patterns:
            matched = p.match(gcode)
            if matched:
                return matched
        return None

    def prettyFormat(self, match) -> str:
        return '{head} X{x:<.3f} Y{y:<.3f}'.format(head=match.group(1), x=float(match.group(2)), y=float(match.group(3)))

    def pretty_XYE_Format(self, match) -> str:
        return '{head} X{x:<.3f} Y{y:<.3f} E{e:<.5f}'.format(head=match.group(1), x=float(match.group(2)), y=float(match.group(3)),e=float(match.group(4)))

    def removeRedundencyGCode(self, one_layer_gcode) -> str:
        # 중복 코드 제거
        gcode = re.sub('G92 E0\nG92 E0', 'G92 E0', one_layer_gcode)

        # 중복된 G1 F000 코드 제거
        redundency_match = self.G1_F_G1_F.search(gcode)
        if redundency_match is not None:
            gcode = re.sub(pattern=redundency_match.group(0),\
                repl=redundency_match.group(1),\
                string=gcode)
        
        gcode = re.sub(self.RemovedMark + '\n', '', gcode)
        return gcode

    def replaceLayerInfo(self, start_code) -> str:

        start_code =  start_code\
            .replace('{home_all_axis}',self.HOME_ALL_AXIS)\
            .replace('{dish_leveling_procedure}',self.DISH_LEVELING_PROCEDURE)

        return start_code\
            .replace('{print_temp}', self._G['PRINT_TEMP'] % self._Q.print_temperature)\
            .replace('{layer_height}', self._Q.layer_height_list)\
            .replace('{wall_thickness}', self._Q.wall_thickness_list)\
            .replace('{infill_sparse_density}', self._Q.infill_sparse_density_list)

    def replaceDispenserSetupCode(self, start_code) -> str:
        return start_code\
            .replace(';{shot_time_list}', self._G['SHOT'] % self._Q.shot_time_list)\
            .replace(';{vac_time_list}', self._G['VAC'] % self._Q.vac_time_list)\
            .replace(';{interval_list}', self._G['INT'] % self._Q.interval_list)\
            .replace(';{shot_p_list}', self._G['SET_P'] % self._Q.shot_power_list)\
            .replace(';{vac_p_list}', self._G['VAC_P'] % self._Q.vac_power_list)

    def update_Z_value(self, gcode, nozzle_type, initial_layer0_height, matched) -> str:
        
        if len(matched.groups()) > 3:
            front_code = '{head} X{x:<.3f} Y{y:<.3f}'.format(head=matched.group(1), x=float(matched.group(2)), y=float(matched.group(3)))
            z_value = float(matched.group(4))
        else:
            front_code = matched.group(1)
            z_value = float(matched.group(2))        
        
        z_delta = z_value
        new_z = z_delta + initial_layer0_height

        if nozzle_type.startswith('Dispenser'):
            z_value_form = '\nG0 C{:<.3f}'.format(new_z)
        else:
            z_value_form = '\nG0 Z{:<.3f}'.format(new_z)

        return front_code + z_value_form # ';' + str(matched.group(2))