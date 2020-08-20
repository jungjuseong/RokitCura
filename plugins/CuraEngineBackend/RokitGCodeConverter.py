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

class RokitGCodeConverter:
    def __init__(self) -> None:    

        # 외부
        self._application = CuraApplication.getInstance()
        self._global_container_stack = self._application.getMachineManager().activeMachine

        # 필요
        self._gcode_model = RokitGCodeModel()        
        self._GCODE = self._gcode_model.GCODE # {}

        self._build_dish_model = RokitBuildDishModel()

        # for naming extruders
        self._JoinSequence = [1,2,3,4,5,0] # - 데이터 조인 순서 : 조인만 하는 데이터에 사용
        self._ExtruderSequence = [0,1,2,3,4,5] # - 익스트루더 순서 : 호출하는 데이터에 사용

        # 프린트 온도 설정
        self._print_temperature = []

        # 디스펜서 설정 - dsp_enable, shot, vac, int, shot.p, vac.p
        self._is_enable_dispensor = None

        # UV 설정 - extruder에서 읽도록 바꿔야 함
        self._uv_enable_list = []
        self._uv_per_layers = []
        self._uv_type = []
        self._uv_time = []
        self._uv_dimming = []

        # 외부 dict
        self._dish = {}

        # z좌표 관리
        self._layer_height_0 = 0
        self._current_z_value = None
        self._InitialLayer0_C = -30
        self._InitialLayer0_Z = -40

        # 선택한 명령어
        self._current_extruder_index = None  # 0, 1, 2, 3, 4, 5
        self._ExtruderNames = ["D6","D1","D2","D3","D4","D5"]
        self._activated_extruders = []   # [D6, D1, D2, D3, D4, D5]

        self._previous_extruder_index = -1
        self._nozzle_type = ""
        
        self._layer_no = None
        self._uv_position = None

        # *** G-code Line(command) 관리 변수
        self._replaced_gcode_list = []        
        self._replaced_code = ""
        self._replaced_line = ""

        self._change_current_position_for_uv = None
        self._move_to_uv_position = None

        # match patterns
        self._G1_F_X_Y_E = re.compile(r'G1 F[0-9.]+ X[0-9.-]+ Y[0-9.-]+ E[0-9.-]')
        self._G1_X_Y_E = re.compile(r'G1 X[0-9.-]+ Y[0-9.-]+ E[0-9.-]')

        self._MarlinCodePattern = re.compile(r'M(140|190|104|109 [TS]|141|205|105|107)')
        self._UnnecessaryCodePattern = re.compile(r'M82 ;absolute extrusion mode|;;}')
        
        self._G1_F_Z = re.compile(r'(G1 F[0-9.]+) Z([0-9.]+)')
        self._G0_Z = re.compile(r'(G0) Z([0-9.]+)')
        self._G0_F_X_Y_Z = re.compile(r'(G0 F[0-9.]+) X([0-9.-]+) Y([0-9.-]+) Z([0-9.-]+)') # G0 F720 X2.13 Y1.057 Z0.3
        self._G1_F_G1_F = re.compile(r'\nG1 F[0-9.]+\n(G1 F[0-9.]+\n)')

        self._is_shot_moment = True
        self.is_first_selectedExtruder = True
        self._LeftExtruder_X_Position = 42.5
        self._RightExtruder_X_Position = -42.5
        self._LeftExtruder_X_Offset = 85.0

        self._A_AxisPosition = [0, 0, -72,  72, 144, 216]       
        self._UVDevicePosition = {"x" : 0.0,"y" : 62.0, "z" : 40.0 }


    def setReplacedlist(self, replaced_gcode_list) -> None:
        self._replaced_gcode_list = replaced_gcode_list

    def getReplacedlist(self) -> str:
        return self._replaced_gcode_list
    
    def _getExtrudersProperty(self, index, property):
        return self._global_container_stack.extruderList[index].getProperty(property,"value")

    def _getGlobalContainerStackProperty(self, property):
        return self._global_container_stack.getProperty(property,"value")

    def _getVariantName(self, index):
        return self._global_container_stack.extruderList[index].variant.getName()

    # 시작 (준비 작업)
    def run(self):
        self._layer_height_0 = self._getGlobalContainerStackProperty("layer_height_0")

        # get print temperature property from global stack
        print_temperature_list = [self._getExtrudersProperty(index,"material_print_temperature") for index in self._JoinSequence] # - 데이터 조인 순서
        print_temperature_list.append(self._getGlobalContainerStackProperty("material_bed_temperature"))
        self._print_temperature = " ".join(map(str, print_temperature_list))

        # get UV and dispenser property from global stack
        self._uv_enable_list = [self._getExtrudersProperty(index,"uv_enable") for index in self._ExtruderSequence]
        self._is_enable_dispensor = self._getGlobalContainerStackProperty("dispensor_enable")

        # 기본 변환
        self._convertGCode() 

        self._setGcodeAfterStartGcode() 

    def _processGCodeToInvivoCode(self, gcodes) -> str:
        gcode_list = gcodes.split("\n")
        for index, gcode in enumerate(gcode_list):
            modified_gcode = gcode
            if self._MarlinCodePattern.match(gcode) or self._UnnecessaryCodePattern.match(gcode) or \
                (gcode == "G92 E0" and self._nozzle_type.startswith('FFF') == False):
                modified_gcode = None
            elif gcode.startswith("T"): # select Extruder
                self._current_extruder_index = int(gcode[-1])
                self._nozzle_type = self._getVariantName(self._current_extruder_index)

                current_extruder =  self._ExtruderNames[self._current_extruder_index]
                modified_gcode = current_extruder + self._addExtraExtruderCode()

                x_position = self._LeftExtruder_X_Position\
                    if (self._current_extruder_index != 0) else self._RightExtruder_X_Position
                self._set_UV_Code(x_position)

                self._addToActivatedExtruders()
                #if index == (len(gcode_list) - 1): # 마지막 end 코드는 고려 안함
                #    break
            elif gcode.startswith("G1"):
                modified_gcode = gcode
                if not self._nozzle_type.startswith('FFF'): 
                    if gcode.find("E") != -1:
                        modified_gcode = self._remove_E_Attribute(modified_gcode)                
                if self._G1_F_X_Y_E.match(gcode) or self._G1_X_Y_E.match(gcode):
                    if  self._is_shot_moment == True:
                        modified_gcode = self._GCODE["StartShot"] + modified_gcode
                        self._is_shot_moment = False
                else:
                    if self._is_shot_moment == False:
                        modified_gcode = self._GCODE["StopShot"] + modified_gcode
                        self._is_shot_moment = True
            elif gcode.startswith("G0") and self._is_shot_moment == False:
                    modified_gcode = self._GCODE["StopShot"] + modified_gcode
                    self._is_shot_moment = True

            gcode_list[index] = ";ToBeDeleted" if modified_gcode is None else self._convert_Z_To_C(gcode, modified_gcode)
            
        return gcode_list

    # E 커맨드 제거 | E 값 | E 명령어
    def _remove_E_Attribute(self, gcode) -> str:
        modified_gcode = gcode[:gcode.find("E")-1]
        return modified_gcode

    def _convertGCode(self) -> None:
        for index, gcodes in enumerate(self._replaced_gcode_list): # line_per_layer
            modified_gcode_list = self._processGCodeToInvivoCode(gcodes)
                    
            joined_gcode = "\n".join(modified_gcode_list)

            if joined_gcode.startswith(";LAYER:"):
                if self._uv_enable_list[self._current_extruder_index]:
                    joined_gcode += self._get_UV_Code(gcodes) # 레이어 주기에 맞춰 커맨드 삽입
            
            joined_gcode = joined_gcode\
                .replace("{print_temp}", self._GCODE["SetPrintTemperature"] % self._print_temperature)\
                .replace(";FLAVOR:Marlin", ";F/W : 7.7.1.x")\
                .replace("G92 E0\nG92 E0", "G92 E0") \
                .replace(";ToBeDeleted\n","")

            joined_gcode.replace("-.","-0.") # 정수를 0으로 채우기 함수

            joined_gcode = self._replaceLayerInfo(joined_gcode)

            if index == 1 and self._is_enable_dispensor: # start 코드일때 만 
                joined_gcode = self._replaceStartDispenserCode(index, joined_gcode) # 조건 처리 필요 (index 1,2에서 다음의 함수가 필요)

            # 중복된 G1 F000 코드 제거
            redundency_code = self._G1_F_G1_F.search(joined_gcode)
            if redundency_code != None:
                joined_gcode = re.sub(pattern=redundency_code.group(0),\
                    repl=redundency_code.group(1),\
                    string=joined_gcode)

            self._replaced_gcode_list[index] = joined_gcode

    def _replaceLayerInfo(self, replaced) -> str:
        layer_height = " ".join(map(str,[self._getExtrudersProperty(index,"layer_height") for index in self._JoinSequence]))
        wall_thickness = " ".join(map(str,[self._getExtrudersProperty(index,"wall_thickness") for index in self._JoinSequence]))
        infill_sparse_density = " ".join(map(str,[self._getExtrudersProperty(index,"infill_sparse_density") for index in self._JoinSequence]))

        return replaced\
            .replace("{layer_height}", layer_height)\
            .replace("{wall_thickness}", wall_thickness)\
            .replace("{infill_sparse_density}", infill_sparse_density)

    # 디스펜서 설정 - dsp_enable, shot, vac, int, shot.p, vac.p 
    def _replaceStartDispenserCode(self, index, replaced) -> str:
        shot_time = " ".join(map(str,[self._getExtrudersProperty(index,"dispensor_shot") for index in self._JoinSequence]))
        vac_time = " ".join(map(str,[self._getExtrudersProperty(index,"dispensor_vac") for index in self._JoinSequence]))
        int_time = " ".join(map(str,[self._getExtrudersProperty(index,"dispensor_int") for index in self._JoinSequence]))
        shot_power = " ".join(map(str,[self._getExtrudersProperty(index,"dispensor_shot_power") for index in self._JoinSequence]))
        vac_power = " ".join(map(str,[self._getExtrudersProperty(index,"dispensor_vac_power") for index in self._JoinSequence]))
        return replaced\
            .replace(";{shot_time}", self._GCODE['SetShotTime'] % shot_time)\
            .replace(";{vac_time}", self._GCODE['SetVacuumTime'] % vac_time)\
            .replace(";{interval}", self._GCODE['SetInterval'] % int_time)\
            .replace(";{shot_p}", self._GCODE['SetShotPressure'] % shot_power)\
            .replace(";{vac_p}", self._GCODE['SetVacuumPressure'] % vac_power)


    # 익스트루더가 교체될 때마다 추가로 붙는 명령어 관리
    def _addExtraExtruderCode(self) -> str: # FFF 예외처리 필요
        extra_code = " ; Selected Nozzle(%s)\n" % self._nozzle_type

        if self.is_first_selectedExtruder:
            self.is_first_selectedExtruder = False
            return extra_code

        if self._current_extruder_index == 0:
            if self._previous_extruder_index != 0:
                extra_code += self._GCODE["G0_B0_F300"] +\
                            self._GCODE["G0_C0"] +\
                            self._GCODE["G91_G0_X_Y"] % (self._LeftExtruder_X_Offset, 0.0) +\
                            self._GCODE["G92_X0_Y0"]
        else:
            # Left --> Right
            if self._previous_extruder_index == 0:
                extra_code += self._GCODE["G0_Z0"] +\
                            self._GCODE["G91_G0_X_Y"] % (-self._LeftExtruder_X_Offset, 0.0) +\
                            self._GCODE["G92_X0_Y0"] +\
                            self._GCODE["G0_B0_F300"] +\
                            self._GCODE["G0_A0_F600"] +\
                            self._GCODE["G78_B15_F300"]               
            else:        
                current_A_axis_pos = self._A_AxisPosition[self._current_extruder_index]
                extra_code += self._GCODE["G0_B0_F300"] +\
                            self._GCODE["G0_A_F600"] % current_A_axis_pos + \
                            self._GCODE["G78_B15_F300"]

        return extra_code

    # 익스트루더 index 기록
    def _addToActivatedExtruders(self) -> None:
        if self._current_extruder_index not in self._activated_extruders:
            self._activated_extruders.append(self._current_extruder_index) # T 명령어 정보 (0,1,2,3,4,5)
        self._previous_extruder_index = self._current_extruder_index

    # Z 좌표 관리
    def _convert_Z_To_C(self, gcode, modified_gcode) -> str:

        initial_layer0 = self._InitialLayer0_Z if self._current_extruder_index == 0 else self._InitialLayer0_C
        axisName = " Z" if self._current_extruder_index == 0 else "C"

        matched_code = None
        if self._G1_F_Z.match(gcode):
            matched_code = self._G1_F_Z.search(gcode)
            self._current_z_value = float(matched_code.group(2))

            if self._current_extruder_index == 0:
                modified_gcode = matched_code.group(1) + axisName + str(self._current_z_value - self._layer_height_0 + initial_layer0)
            else:
                modified_gcode = matched_code.group(1) + "\n" 
                modified_gcode += "G0 " + axisName + str(self._current_z_value - self._layer_height_0 + initial_layer0)

        elif self._G0_F_X_Y_Z.match(gcode):
            matched_code = self._G0_F_X_Y_Z.search(gcode)
            self._current_z_value = float(matched_code.group(4))
            sub_height = self._current_z_value - self._layer_height_0

            if (sub_height == 0):
                return re.sub(r' Z([0-9.]+)','',gcode)
            elif self._current_extruder_index == 0:
                replaced_gcode = re.sub(r'Z([0-9.]+)','Z%.2f',gcode)
                modified_gcode = replaced_gcode % (sub_height + initial_layer0)
            else:
                modified_gcode = re.sub(r' Z([0-9.]+)','\n',gcode)
                modified_gcode += "G0 " + axisName + str(sub_height + initial_layer0)

        return modified_gcode

    # 선택된 실린지에 따라 UV '종류', '주기', '시간', '세기' 가 다름.
    def _set_UV_Code(self,x_position) -> None:
        self._uv_position = self._UVDevicePosition
        self._uv_per_layers = self._getExtrudersProperty(self._current_extruder_index,"uv_per_layers")
        self._uv_type = self._getExtrudersProperty(self._current_extruder_index,"uv_type")
        self._uv_time = self._getExtrudersProperty(self._current_extruder_index,"uv_time")
        self._uv_dimming = self._getExtrudersProperty(self._current_extruder_index,"uv_dimming") # - 미구현
        
        # UV 타입에 따른 UV 명령어 선정        
        if self._uv_type == '365':
            self._uv_on_code = self._GCODE['UVCuringOn'] # UV type: Curing
            self._uv_off_code = self._GCODE['UVCuringOff'] # UV type: Curing
        elif self._uv_type == '405':
            self._uv_on_code = self._GCODE['UVDisinfectionOn'] # UV type: Disinfect
            self._uv_off_code = self._GCODE['UVDisinfectionOff'] # UV type: Disinfect

        self._change_current_position_for_uv = self._GCODE['G92_X_Y'] %  (x_position, 0)
        self._move_to_uv_position = self._GCODE['G91_G0_X_Y'] % (x_position, 0)

    # Layer 주기를 기준으로 UV 명령어 삽입
    # dispenser 설정 명령어 삽입
    def _get_UV_Code(self, line_per_layer) -> str:
        if self._current_z_value is None: # 예외 처리
                Logger.log("w","No Current Z Value")
                self._current_z_value = 0.0

        self._layer_no = int(line_per_layer[len(";LAYER:"):line_per_layer.find("\n")])
        if (self._layer_no % self._uv_per_layers) == 0:
            moveToCode = self._GCODE['G0_Z'] % (0.00) if self._current_extruder_index != 0 else self._GCODE['G0_Z'] % (self._current_z_value)
            uv_code = ";UV\n" + \
                self._GCODE['G90_G0_XY_ZERO'] + \
                self._change_current_position_for_uv + \
                self._GCODE['G91_G0_X_Y'] % (self._uv_position['x'], self._uv_position['y']) + \
                self._GCODE['G0_Z'] % (self._uv_position['z']) + \
                self._uv_on_code + \
                self._GCODE['UVTime'] % (self._uv_time * 1000) + \
                self._uv_off_code + \
                moveToCode + \
                self._move_to_uv_position + \
                self._GCODE['G92_X_Y'] % (0.00, 0.00)

            return uv_code

    # Well plate 복제 기능
    def _cloneWellPlate(self, trip):
        clone_num = trip["well_number"] -1 # 본코드를 제외판 복제 코드는 전체에서 1개를 빼야함.
        line_seq = trip["line_seq"]
        # z_height = trip["z"]

        gcode_clone = self._replaced_gcode_list[2:-1]
        std_str = self._GCODE['G90_G0_XY_ZERO']
        self._line_controller = 1 # forward

        gcode_body = []
        for i in range(1,clone_num): # Clone number ex) 1 ~ 96
            if i % line_seq == 0:
                direction = 'X'
                distance = -trip["spacing"]
                self._line_controller = abs(self._line_controller - 1) # direction control
            else:
                if self._line_controller == 1:
                    direction = 'Y'
                    distance = -trip["spacing"]
                elif self._line_controller == 0:
                    direction = 'Y'
                    distance = trip["spacing"]

            # control spacing about build plate after printing one model
            gcode_spacing = ";hop_spacing\n"
            gcode_spacing += "G92 E0\n" 
            gcode_spacing += self._GCODE['G90_G0_XY_ZERO']
            gcode_spacing += self._GCODE['G90_G0_C'] % -4.0
            if direction == 'X':
                gcode_spacing += self._GCODE['G91_G0_X'] % distance
            else:
                gcode_spacing += self._GCODE['G91_G0_Y'] % distance

            gcode_spacing += self._GCODE['G90_G0_C'] % self._InitialLayer0_C
            gcode_spacing += self._GCODE['G92_X0_Y0']

            gcode_clone.insert(0,gcode_spacing)
            self._replaced_gcode_list[-2:-2]= gcode_clone  # put the clones in front of the end-code
            gcode_clone.remove(gcode_spacing)

    # start 코드 다음으로 붙는 준비 명령어
    # "trip": {"line_seq":96/8, "spacing":9.0, "z": 10.8, "start_point": QPoint(74,49.5)}})
    def _setGcodeAfterStartGcode(self):
        trip= {}
        build_plate = self._getGlobalContainerStackProperty("machine_build_dish_type")
        build_plate_type = build_plate[:build_plate.find(':')]
        for index in range(self._build_dish_model.count):
            self._dish = self._build_dish_model.getItem(index)
            if self._dish['product_id'] == build_plate:
                trip = self._dish['trip'] # Build plate가 정해짐
                break

        start_point = trip["start_point"]
        if self._activated_extruders[0] == 'D6':
            x = start_point.x()
        else:
            x = -start_point.x()

        start_codes = "\n;Start point\n" + \
            self._GCODE['G90_G0_X_Y'] % (x, start_point.y())

        if self._activated_extruders[0] == "D6": # Left
            start_codes += self._GCODE["G0_Z_RESET"]
        else:
            start_codes += self._GCODE["G90_G0_C_RESET"] +\
                self._GCODE["G92_C0"]
    
            start_codes += self._GCODE["G0_A_F600"] % (self._A_AxisPosition[self._activated_extruders[0]])
            start_codes += self._GCODE["G78_B15_F300"] # G78 B15.
        
        if (build_plate_type == "Well Plate"):
            self._cloneWellPlate(trip)

        start_codes += self._GCODE['G92_X0_Y0'] # "G92 X0.0 Y0.0 Z0.0 C0.0\n"

        self._replaced_gcode_list[1] += start_codes
        self._replaced_gcode_list.insert(-1,self._GCODE['G0_Z'] % (40.0))
        self._replaced_gcode_list.insert(-1,self._GCODE['G90_G0_C'] % (40.0))
        self._replaced_gcode_list.insert(-1,self._GCODE['G92_Z0'])
        self._replaced_gcode_list.insert(-1,self._GCODE['G92_C0'])
