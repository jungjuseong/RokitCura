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

        self.HOME_ALL_AXIS = '; Home all axis\n' +\
                    'M29 Z\n' +\
                    'M29 C\n' +\
                    'M29 B\n' +\
                    'G0 B15. F300\n' +\
                    'M29 B\n' +\
                    'G79\n' +\
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

    def getRetractionCode(self, extruder_index, last_e) -> str:
        if self._Q.retraction_enable_list[extruder_index]:
            return 'G1 F{f} E{e:<.5f} ;(Retraction_a)\n'.format(
                f = self._Q.retraction_speed_list[extruder_index] * 60, 
                e = last_e - self._Q.retraction_amount_list[extruder_index])
        return ''

    def getBackRetractionCode(self,extruder_index,last_e) -> str:
        if self._Q.retraction_enable_list[extruder_index]:
            return 'G1 F{f} E{e:<.5f} ;(Back-Retraction_a)\n'.format(
                f = self._Q.retraction_speed_list[extruder_index] * 60, 
                e = last_e)
        return ''

    # UV code
    def UV_Code(self, extruder_index) -> str:
        code = '{G59_G0_X0_Y0}{M172}{M381_CHANNEL}{M385_DIMMING}{M386_TIME}{M384}{P4_DURATION}'.format(**self._G)
        return code.format(
            channel = 0 if self._Q.uv_type_list[extruder_index] == '365' else 1, 
            dimming = self._Q.uv_dimming_list[extruder_index], 
            time = self._Q.uv_time_list[extruder_index], 
            duration = self._Q.uv_time_list[extruder_index] * 1000)

    def getWrappedUVCode(self, uvcode, extruder_index, layer_height) -> str:
        reset_height = self._G['G0_Z40_C40_F420']
        m29b = self._G['M29_B']
        left_bed= self._G['G54_G0_X0_Y0']
        right_bed= self._G['G55_G0_X0_Y0']
        bed_pos = left_bed if extruder_index == 0 else right_bed
        move_z = self._G['G0_C'] if extruder_index == 0 else self._G['G0_Z'] % layer_height 

        return '{reset_height}{m29b}{uvcode}{bed_pos}{move_z}'.format(
            reset_height = reset_height,
            m29b = m29b,
            uvcode = uvcode,
            bed_pos = bed_pos,
            move_z = move_z)

    # 익스트루더가 교체될 때마다 추가로 붙는 명령어
    def getExtruderSetupCode(self, previous_index, current_index, uvcode) -> str:

        current_nozzle = self._Q.getVariantName(current_index)
        previous_nozzle = self._Q.getVariantName(previous_index)

        aaxis = self._G['G0_A_F600'].format(a_axis = self._Q.A_AxisPosition[current_index])
        g0b15f300 = self._G['G0_B15_F300']
        reset_height = self._G['G0_Z40_C40_F420']
        m29b = self._G['M29_B']
        airoff = self._G['M330']
        airon = self._G['M301']
        left_bed= self._G['G54_G0_X0_Y0']
        right_bed= self._G['G55_G0_X0_Y0']
        g92e0 = self._G['G92_E0']

        extruder = self.getRokitExtruderName(current_index)

        DISPENSER_START = '{extruder}{aaxis}{bed_pos}{g0b15f300}'.format(
                extruder = extruder,
                aaxis = aaxis,
                bed_pos = right_bed if previous_index == -1 else '',
                g0b15f300 = g0b15f300
        )
        DISPENSER_END = '{airoff}{reset_height}{m29b}{uvcode}{bed_pos}'.format(
                airoff = airoff,
                reset_height = reset_height,
                m29b = m29b,
                uvcode = uvcode,
                bed_pos = left_bed if current_index == 0 else right_bed if uvcode != '' else ''
        )

        EXTRUDER_START = '{extruder}{bed_pos}'.format(
                extruder = extruder,
                bed_pos = left_bed if previous_index != 0 else '',  
                
        )
        EXTRUDER_END = '{reset_height}{m29b}{uvcode}{bed_pos}{airoff}'.format(
                reset_height = reset_height,
                m29b = m29b,
                uvcode = uvcode,
                bed_pos = right_bed if current_index > 0 else left_bed if uvcode != '' else '',
                airoff = airoff
        )

        HOtMELT_START = '{extruder}{bed_pos}'.format(
                extruder = extruder,
                bed_pos = left_bed if previous_index != 0 else ''       
        )
        HOTMELT_END = '{airoff}{reset_height}{m29b}{uvcode}{bed_pos}'.format(
                airoff = airoff,
                reset_height = reset_height,
                m29b = m29b,
                uvcode = uvcode,
                bed_pos = right_bed if current_index > 0 else left_bed if uvcode != '' else ''
        )

        code = ';{}'
        if previous_index == -1: # 처음 나온 Nozzle

            MESSAGE = '; <==== setup start from {p}\n'.format(p=current_nozzle)

            # D1~D5
            if current_index > 0:
                code = MESSAGE + '{start}\n'.format(start=DISPENSER_START)
            # D6 - FFF
            elif current_nozzle.startswith('Extruder'):
                code = MESSAGE + '{start}\n'.format(start=EXTRUDER_START)
            # D6 - Hot Melt
            elif current_nozzle.startswith('Hot Melt'):
                code = MESSAGE + '{start}\n'.format(start=HOtMELT_START)
        else:            
            MESSAGE = '; <==== setup start from {pr} to {cu}\n'.format(pr=previous_nozzle,cu=current_nozzle)

            # 3. D6(FFF)에서 D1~5로 변경된 경우
            if previous_nozzle.startswith('Extruder') and current_index > 0:              
                code = MESSAGE + '{end}\n{start}'.format(end=EXTRUDER_END, start=DISPENSER_START)
            # 4. D1~5에서 D6(FFF)로 변경된 경우
            elif previous_index > 0 and current_nozzle.startswith('Extruder'):
                code = MESSAGE + '{end}\n{start}'.format(end=DISPENSER_END, start=EXTRUDER_START)            

            # 5. D6(Hot Melt)에서 D1~5로 변경된 경우
            elif previous_nozzle.startswith('Hot Melt') and current_index > 0:
                code = MESSAGE + '{end}\n{start}'.format(end=HOTMELT_END, start=DISPENSER_START)            

            # 6. D1~D5에서 D6(Hot Melt)로 변경된 경우
            elif previous_index > 0 and current_nozzle.startswith('Hot Melt'):
                code = MESSAGE + '{end}\n{start}'.format(end=DISPENSER_END, start=HOtMELT_START)            

            # 7. D1~D5에서 D1~D5으로 변경된 경우
            elif previous_index > 0 and current_nozzle.startswith('Dispenser'):
                code = MESSAGE + '{end}\n{start}'.format(end=DISPENSER_END, start=DISPENSER_START)            

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

