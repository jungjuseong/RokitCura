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

# class dishType():
#     def __init__(self, slice_message: Arcus.PythonMessage) -> None:
#
# 전체 익스트루더의 프린팅 온도
# 전체 익스트루더의 디스펜서 속성
# 선택된 익스트루더의 시린지 타입
# 선택된 익스트루더의 UV 타입
# 선택된 익스트루더의 Hop 속성
#
# FFF 예외처리 : 디스펜서 속성
# FFF 예외처리 : C좌표로 변환
# FFF 예외처리 : Shot/Stop 커맨드
#

class RokitGCodeConverter:
    def __init__(self) -> None:
        # super().__init__()

        self._start_coord = { 'c': -40.0, 'z': -40.0 }

        # 외부
        self._application = CuraApplication.getInstance()
        self._global_container_stack = self._application.getMachineManager().activeMachine
        self._extruder_list = None 

        # 필요
        self._gcode_model = RokitGCodeModel()        
        self._TranslateToGcode = self._gcode_model.TranslateToGCode # {}
        self._marlin_code_dic = self._gcode_model.marlin_codes # {}

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
        self._current_z_value = None

        # 선택한 명령어
        self._current_extruder_index = None  # 0(left), 1, 2, 3, 4, 5
        self._ExtruderNames = ["D6","D1","D2","D3","D4","D5"]
        self._activated_extruders = []   # [D6(Left), D1, D2, D3, D4, D5]

        self._previous_extruder = None
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
        self._G1_F_X_Y_E = re.compile('G1 F[0-9.]+ X[0-9.-]+ Y[0-9.-]+ E[0-9.-]')
        self._G1_X_Y_E = re.compile('G1 X[0-9.-]+ Y[0-9.-]+ E[0-9.-]')

        self._is_shot_moment = True
        self.is_first_selectedExtruder = True
        self._LeftExtruderXPosition = 42.5
        self._RightExtruderXPosition = -42.5


        self._MarlinCodePattern = re.compile("M(140|190|104|109 (S|T)|141|205|105|107)")
        self._UnnecessaryCodePattern = re.compile("M82 ;absolute extrusion mode|;;}")

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
        # get print temperature property from global stack
        print_temperature_list = [self._getExtrudersProperty(index,"material_print_temperature") for index in self._JoinSequence] # - 데이터 조인 순서
        print_temperature_list.append(self._getGlobalContainerStackProperty("material_bed_temperature"))
        self._print_temperature = " ".join(map(str, print_temperature_list))

        # get UV and dispenser property from global stack
        self._uv_enable_list = [self._getExtrudersProperty(index,"uv_enable") for index in self._ExtruderSequence]
        self._is_enable_dispensor = self._getGlobalContainerStackProperty("dispensor_enable")

        # 기본 변환
        self._convertGCode() 

        # 플레이트에 따라 변환 # 수정 필요
        self._setBuildPlateProperty() 

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
                modified_gcode = current_extruder + self._addExtraExtruderCode(current_extruder)

                x_position = self._LeftExtruderXPosition if (current_extruder != "D6") else self._RightExtruderXPosition
                self._set_UV_Code(self._current_extruder_index,x_position)

                self._addToActivatedExtruders(current_extruder)
                #if index == (len(gcode_list) - 1): # 마지막 end 코드는 고려 안함
                #    break
            elif gcode.startswith("G1"):
                modified_gcode = self._remove_E_Attribute(gcode)                
                if self._G1_F_X_Y_E.match(gcode) or self._G1_X_Y_E.match(gcode):
                    if  self._is_shot_moment == True:
                        modified_gcode = self._TranslateToGcode["StartShot"] + gcode
                        self._is_shot_moment = False
                else:
                    if self._is_shot_moment == False:
                        modified_gcode = self._TranslateToGcode["StopShot"] + gcode
                        self._is_shot_moment = True
            elif gcode.startswith("G0") and self._is_shot_moment == False:
                    modified_gcode = self._TranslateToGcode["StopShot"] + gcode
                    self._is_shot_moment = True    

            gcode_list[index] = ";ToBeDeleted" if modified_gcode is None else self._convert_Z_To_C(modified_gcode)
            
        return gcode_list

    def _convertGCode(self) -> None:
        for index, gcodes in enumerate(self._replaced_gcode_list): # line_per_layer
            modified_gcode_list = self._processGCodeToInvivoCode(gcodes)
                    
            joined_gcode = "\n".join(modified_gcode_list)

            if joined_gcode.startswith(";LAYER:"):
                if self._uv_enable_list[self._current_extruder_index]:
                    joined_gcode += self._get_UV_Code(line_per_layer) # 레이어 주기에 맞춰 커맨드 삽입
            
            joined_gcode = joined_gcode\
                .replace("{print_temp}", self._TranslateToGcode["SetPrintTemperature"] % self._print_temperature)\
                .replace(";FLAVOR:Marlin", ";F/W : 7.7.1.x")\
                .replace("G92 E0\nG92 E0", "G92 E0") \
                .replace(";ToBeDeleted\n","")

            joined_gcode.replace("-.","-0.") # 정수를 0으로 채우기 함수

            joined_gcode = self._replaceLayerInfo(joined_gcode)

            if index == 1 and self._is_enable_dispensor: # start 코드일때 만 
                joined_gcode = self._replaceStartDispenserCode(index, joined_gcode) # 조건 처리 필요 (index 1,2에서 다음의 함수가 필요)

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
            .replace(";{shot_time}", self._TranslateToGcode['SetShotTime'] % shot_time)\
            .replace(";{vac_time}", self._TranslateToGcode['SetVacuumTime'] % vac_time)\
            .replace(";{interval}", self._TranslateToGcode['SetInterval'] % int_time)\
            .replace(";{shot_p}", self._TranslateToGcode['SetShotPressure'] % shot_power)\
            .replace(";{vac_p}", self._TranslateToGcode['SetVacuumPressure'] % vac_power)


    # 익스트루더가 교체될 때마다 추가로 붙는 명령어 관리
    def _addExtraExtruderCode(self, current_extruder) -> str: # FFF 예외처리 필요
        extra_code = " ; Selected Nozzle\n; Nozzle type : %s\n" % self._nozzle_type

        if self.is_first_selectedExtruder:
            self.is_first_selectedExtruder = False
            return extra_code

        if current_extruder == 'D6':
            if self._previous_extruder != 'D6':
                extra_code += self._TranslateToGcode["MoveToXY"] % (85.0, 0.0) +\
                    self._TranslateToGcode["MoveToBF"] % (0.0, 300) +\
                    self._TranslateToGcode["Reset_Z_Axis"] +\
                    self._TranslateToGcode["ResetZAxisToZero"] +\
                    self._TranslateToGcode["SetAxisOrigin"]
        else:
            # Left --> Right
            if self._previous_extruder == 'D6':
                extra_code += self._TranslateToGcode["MoveToXY"] % (-85.0, 0.0) + \
                    self._TranslateToGcode["MoveToBF"] % (0.0, 300) + \
                    self._TranslateToGcode["Reset_C_Axis"] + \
                    self._TranslateToGcode["ResetCAxisToZero"]                     
                    
            axisCodes = self._TranslateToGcode["A_AxisPosition"]
            current_A_axis_pos = axisCodes[current_extruder]
            extra_code += self._TranslateToGcode["MoveToAF"] % (current_A_axis_pos, 600) + \
                        self._TranslateToGcode["GoToDetectedLimit"] + \
                        self._TranslateToGcode["SetAxisOrigin"]
        return extra_code

    # 익스트루더 index 기록
    def _addToActivatedExtruders(self, current_extruder) -> None:
        if current_extruder not in self._activated_extruders:
            self._activated_extruders.append(current_extruder) # T 명령어 정보 (0,1,2,3,4,5)
        self._previous_extruder = current_extruder

    # z좌표 관리
    def _convert_Z_To_C(self, gcode) -> str:
        if gcode.startswith(('G0','G1')) and gcode.find("Z") != -1:
            try:
                self._current_z_value = float(gcode[gcode.find("Z") + 1:]) # ***
                if self._current_extruder_index != '6':
                    gcode = self._convertFromZToC(gcode) # C 좌표로 변환
            except Exception:
                Logger.logException("w","Could not convert from Z to C")
                pass
        return gcode

    # C 좌표로 변환
    def _convertFromZToC(self, gcode) -> str:
       return gcode[:gcode.find("Z")] + "\nG0 C" + str(self._current_z_value)

    # E 커맨드 제거
    def _remove_E_Attribute(self, gcode) -> str:
        if self._nozzle_type.startswith('FFF'): 
            return gcode
        if gcode.find("E") != -1:
            gcode = gcode[:gcode.find("E")-1]
        return gcode

    # 선택된 실린지에 따라 UV '종류', '주기', '시간', '세기' 가 다름.
    def _set_UV_Code(self,index,x_position) -> None:
        self._uv_position = self._TranslateToGcode["UVDevicePosition"]
        self._uv_per_layers = self._getExtrudersProperty(index,"uv_per_layers")
        self._uv_type = self._getExtrudersProperty(index,"uv_type")
        self._uv_time = self._getExtrudersProperty(index,"uv_time")
        self._uv_dimming = self._getExtrudersProperty(index,"uv_dimming") # - 미구현
        
        # UV 타입에 따른 UV 명령어 선정        
        if self._uv_type == '365':
            self._uv_on_code = self._TranslateToGcode['UVCuringOn'] # UV type: Curing
            self._uv_off_code = self._TranslateToGcode['UVCuringOff'] # UV type: Curing
        elif self._uv_type == '405':
            self._uv_on_code = self._TranslateToGcode['UVDisinfectionOn'] # UV type: Disinfect
            self._uv_off_code = self._TranslateToGcode['UVDisinfectionOff'] # UV type: Disinfect
        


        self._change_current_position_for_uv = self._TranslateToGcode['SetToNewAxis'] %  (x_position, 0)
        self._move_to_uv_position = self._TranslateToGcode['RMoveToXY'] % (x_position, 0)

    # Layer 주기를 기준으로 UV 명령어 삽입
    # dispenser 설정 명령어 삽입
    def _get_UV_Code(self, line_per_layer) -> str:
        if self._current_z_value is None: # 예외 처리
                Logger.log("w","No Current Z Value")
                self._current_z_value = 0.0

        self._layer_no = int(line_per_layer[len(";LAYER:"):line_per_layer.find("\n")])
        if (self._layer_no % self._uv_per_layers) == 0:
            moveToCode = self._TranslateToGcode['MoveToZ'] % (0.00) if self._current_extruder_index != 0 else self._TranslateToGcode['MoveToZ'] % (self._current_z_value)
            uv_code = ";UV\n" + \
                self._TranslateToGcode['MoveToOrigin'] + \
                self._change_current_position_for_uv + \
                self._TranslateToGcode['RMoveToXY'] % (self._uv_position['x'], self._uv_position['y']) + \
                self._TranslateToGcode['MoveToZ'] % (self._uv_position['z']) + \
                self._uv_on_code + \
                self._TranslateToGcode['UVTime'] % (self._uv_time * 1000) + \
                self._uv_off_code + \
                moveToCode + \
                self._move_to_uv_position + \
                self._TranslateToGcode['SetToNewAxis'] % (0.00, 0.00)

            return uv_code

    # Well plate 복제 기능
    def _cloneWellPlate(self, trip):
        clone_num = trip["well_number"] -1 # 본코드를 제외판 복제 코드는 전체에서 1개를 빼야함.
        line_seq = trip["line_seq"]
        # z_height = trip["z"]

        gcode_clone = self._replaced_gcode_list[2:-1]
        std_str = self._TranslateToGcode['MoveToOrigin']
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
            gcode_spacing += self._TranslateToGcode['MoveToOrigin']
            gcode_spacing += self._TranslateToGcode['MoveTo'] % ('C', -4.0)
            gcode_spacing += self._TranslateToGcode['RMoveTo'] % (direction , distance)
            gcode_spacing += self._TranslateToGcode['MoveTo'] % ('C', self._start_coord['c'])
            gcode_spacing += self._TranslateToGcode['SetAxisOrigin']

            gcode_clone.insert(0,gcode_spacing)
            self._replaced_gcode_list[-2:-2]= gcode_clone  # put the clones in front of the end-code
            gcode_clone.remove(gcode_spacing)

    # start 코드 다음으로 붙는 준비 명령어
    # "trip": {"line_seq":96/8, "spacing":9.0, "z": 10.8, "start_point": QPoint(74,49.5)}})
    def _setBuildPlateProperty(self):
        trip= {}
        axi_code = self._TranslateToGcode["A_AxisPosition"]
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

        select_extruder = "\n;Start point\n" + \
            self._TranslateToGcode['MoveToXY'] % (x, start_point.y())

        if self._activated_extruders[0] == "D6": # Left
            select_extruder += self._TranslateToGcode["Reset_Z_Axis"] + self._TranslateToGcode["ResetZAxisToZero"]
        else:
            select_extruder += self._TranslateToGcode["Reset_C_Axis"] + self._TranslateToGcode["ResetCAxisToZero"]
    
            select_extruder += self._TranslateToGcode["MoveToAF"] % (axi_code[self._activated_extruders[0]], 600)
            select_extruder += self._TranslateToGcode["GoToDetectedLimit"] # G78 B50.
        
        if (build_plate_type == "Well Plate"):
            self._cloneWellPlate(trip)

        select_extruder += self._TranslateToGcode['SetAxisOrigin'] # "G92 X0.0 Y0.0 Z0.0 C0.0\n"
        self._replaced_gcode_list[1] += select_extruder
        self._replaced_gcode_list.insert(-1,self._TranslateToGcode['MoveToZ'] % (40.0))
        self._replaced_gcode_list.insert(-1,self._TranslateToGcode['MoveToC'] % (40.0))
        self._replaced_gcode_list.insert(-1,self._TranslateToGcode['ResetZAxisToZero'])
        self._replaced_gcode_list.insert(-1,self._TranslateToGcode['ResetCAxisToZero'])