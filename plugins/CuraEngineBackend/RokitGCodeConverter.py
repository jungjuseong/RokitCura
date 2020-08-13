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
        self._TraslateToGcode = self._gcode_model.TranslateToGCode # {}
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
        self._selected_extruder = None
        self._selected_extruder_index = None  # 0(left), 1, 2, 3, 4, 5
        self._selected_extruder_num_list = []   # [0(Left), 1, 2, 3, 4, 5]
        self._selected_extruder_list = []   # [D6(Left), D1, D2, D3, D4, D5]

        self._previous_extruder = None
        self._previous_extruder_index = None
        self._nozzle_type = ""
        
        self._layer_no = None
        self._uv_position = None        

        # 빌드 플레이트 타입
        self._build_plate = ""
        self._build_plate_type = ""

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

    def setReplacedlist(self, replaced_gcode_list) -> None:
        self._replaced_gcode_list = replaced_gcode_list

    def getReplacedlist(self):
        return self._replaced_gcode_list
        
    # 시작 (준비 작업)
    def run(self):
        # self._initialiizeConverter()
        self._getPrintProperty() # gcode 가져오기
        self._convertGCode() # 기본 변환
        self._setBuildPlateProperty() # 플레이트에 따라 변환 # 수정 필요

    def _getExtrudersProperty(self, index, property):
        return self._global_container_stack.extruderList[index].getProperty(property,"value")

    def _getGlobalContainerStackProperty(self, property):
        return self._global_container_stack.getProperty(property,"value")

    def _getVariantName(self, index):
        return self._global_container_stack.extruderList[index].variant.getName()

    def _getPrintProperty(self):
        # 프린트 온도 설정
        list =[self._getExtrudersProperty(index,"material_print_temperature") for index in self._JoinSequence] # - 데이터 조인 순서
        list.append(self._getGlobalContainerStackProperty("material_bed_temperature"))
        self._print_temperature = " ".join(map(str, list))
        # UV 사용 여부
        self._uv_enable_list = [self._getExtrudersProperty(index,"uv_enable") for index in self._ExtruderSequence]
        # Dispenser 사용 여부
        self._is_enable_dispensor = self._getGlobalContainerStackProperty("dispensor_enable")
        
    # Main
    def _convertGCode(self):
        for index, lines in enumerate(self._replaced_gcode_list): # lines(layer) 마다
            self._replaced_line = lines

            layer_command_list = lines.split("\n")
            for num, command_line in enumerate(layer_command_list): # Command 마다
                self._replaced_code = command_line
                self._removeUnnecessaryCode(command_line)
                self._parseSelectedExtruder(command_line) # *** 가장 먼저, 선택된 익스트루더를 확인해야함.

                if index != len(self._replaced_gcode_list) -1: # 마지막 엔드 코드는 고려 안함. # start 코드도 고려하게 안하게 수정해야함.
                    self._insertShotCommand(command_line)
                    self._convertZCommand(command_line)

                if self._replaced_code is not None:
                    layer_command_list[num] = self._replaced_code
                else:
                    layer_command_list[num] = ";{blank}"
            self._replaced_line = "\n".join(layer_command_list)

            self._addUVCommand(lines) # 레이어 주기에 맞춰 커맨드 삽입
            self._replaceSomeCommands() # 
            self._fillIntegerWithZero() # 정수를 0으로 채우기 함수
            
            self._replaceLayerInfo()

            self._replaceStartDispenserCode(index) # 조건 처리 필요 (index 1,2에서 다음의 함수가 필요)
            self._replaced_gcode_list[index] = self._replaced_line

    # Shot/Stop 명령어
    def _insertShotCommand(self, command_line) -> None:
        # command : 변하는 커맨드
        # command_line : 조건에 필요한 커맨드 (변하지 않는 커맨드)
        gcode = self._replaced_code
        if command_line.startswith("G1") :
            gcode = self._removeECommand(gcode) # E 값을 지우는 매소드
            
            if self._G1_F_X_Y_E.match(command_line) or self._G1_X_Y_E.match(command_line):
                if  self._is_shot_moment == True:
                    gcode = self._TraslateToGcode["StartShot"] + gcode
                    self._is_shot_moment = False
            else:
                if self._is_shot_moment == False:
                    gcode = self._TraslateToGcode["StopShot"] + gcode
                    self._is_shot_moment = True

        elif command_line.startswith("G0") and self._is_shot_moment == False:
                gcode = self._TraslateToGcode["StopShot"] + gcode
                self._is_shot_moment = True

        self._replaced_code = gcode

    def _removeUnnecessaryCode(self, code) -> None:
        # Marlin 커맨드 제거
        MarlinCodePattern = re.compile("M140|M190|M104|M109|M141|M205")

        if code.startswith("M"):
            for marlin_code in self._marlin_code_dic:
                if code.startswith(marlin_code):
                    self._replaced_code = None
                    return
        
        if code == "G92 E0":
            if not self._nozzle_type.startswith('FFF'):
                self._replaced_code = None

    # 기타 명령어 관리
    def _replaceSomeCommands(self):
        self._replaced_line = self._replaced_line\
            .replace("{print_temp}", self._TraslateToGcode["SetPrintTemperature"] % self._print_temperature)\
            .replace(";FLAVOR:Marlin", ";F/W : 7.7.1.x")\
            .replace("G92 E0\nG92 E0", "G92 E0")\
            .replace("M105\n", "")\
            .replace("M107\n", "")\
            .replace("M82 ;absolute extrusion mode\n", "")\
            .replace(";{blank}\n", "")   

    def _replaceLayerInfo(self) -> None:
        layer_height = " ".join(map(str,[self._getExtrudersProperty(index,"layer_height") for index in self._JoinSequence]))
        wall_thickness = " ".join(map(str,[self._getExtrudersProperty(index,"wall_thickness") for index in self._JoinSequence]))
        infill_sparse_density = " ".join(map(str,[self._getExtrudersProperty(index,"infill_sparse_density") for index in self._JoinSequence]))

        self._replaced_line = self._replaced_line\
            .replace("{layer_height}", layer_height)\
            .replace("{wall_thickness}", wall_thickness)\
            .replace("{infill_sparse_density}", infill_sparse_density)

    # 디스펜서 설정 - dsp_enable, shot, vac, int, shot.p, vac.p 
    def _replaceStartDispenserCode(self, layer_index) -> None:
        if layer_index != 1: # start 코드일때만 
            return
        if not self._is_enable_dispensor:
            return

        shot_time = " ".join(map(str,[self._getExtrudersProperty(index,"dispensor_shot") for index in self._JoinSequence]))
        vac_time = " ".join(map(str,[self._getExtrudersProperty(index,"dispensor_vac") for index in self._JoinSequence]))
        int_time = " ".join(map(str,[self._getExtrudersProperty(index,"dispensor_int") for index in self._JoinSequence]))
        shot_power = " ".join(map(str,[self._getExtrudersProperty(index,"dispensor_shot_power") for index in self._JoinSequence]))
        vac_power = " ".join(map(str,[self._getExtrudersProperty(index,"dispensor_vac_power") for index in self._JoinSequence]))

        self._replaced_line = self._replaced_line\
            .replace(";{shot_time}", self._TraslateToGcode['SetShotTime'] % shot_time)\
            .replace(";{vac_time}", self._TraslateToGcode['SetVacuumTime'] % vac_time)\
            .replace(";{interval}", self._TraslateToGcode['SetInterval'] % int_time)\
            .replace(";{shot_p}", self._TraslateToGcode['SetShotPressure'] % shot_power)\
            .replace(";{vac_p}", self._TraslateToGcode['SetVacuumPressure'] % vac_power)

    # 정수자리에 0을 삽입
    def _fillIntegerWithZero(self) -> None:
        self._replaced_line = self._replaced_line.replace("-.","-0.")

    # 익스트루더가 교체될 때마다 추가로 붙는 명령어 관리
    def _addExtruderSelectingCode(self,replaced): # FFF 예외처리 필요
        replaced += " ; Selected Nozzle\n; Nozzle type : %s\n" % self._nozzle_type
        if self.is_first_selectedExtruder:
            self.is_first_selectedExtruder = False
            return replaced
        a_command = self._TraslateToGcode["AAxisPosition"] 
        
        replaced += self._TraslateToGcode["MoveToBF"] % (0.0, 300)
        if self._selected_extruder == 'D6':
            # Right --> Left
            if self._previous_extruder != 'D6':
                replaced += self._TraslateToGcode["MoveToC"] % (40.0) # Right Extruder를 위로 올림
                replaced += self._TraslateToGcode["RMoveToXY"] % (-85.0, 0.0)
                replaced += self._TraslateToGcode["MoveToAxisOrigin"]
        else:
            replaced += self._TraslateToGcode["MoveToAF"] % (a_command[self._selected_extruder], 600)
            replaced += self._TraslateToGcode["GoToDetectedLimit"] # B좌표 끝까지 이동
            # Left --> Right
            if self._previous_extruder == 'D6':
                replaced += self._TraslateToGcode["MoveToZ"] % (40.0) # Left Extruder를 위로 올림
                replaced += self._TraslateToGcode["RMoveToXY"] % (85.0, 0.0)
                replaced += self._TraslateToGcode["MoveToAxisOrigin"]

        return replaced

    # 익스트루더 index 기록
    def _noteSelectedExtruder(self) -> None:
        if self._selected_extruder not in self._selected_extruder_list:
            self._selected_extruder_num_list.append(self._selected_extruder_index) # T 명령어 정보 (0,1,2,3,4,5)
            self._selected_extruder_list.append(self._selected_extruder) # T 명령어 정보 (0,1,2,3,4,5)
        
        self._previous_extruder_index = self._selected_extruder_index
        self._previous_extruder = self._selected_extruder

    # T 명령어를 통해 선택한 시린지 확인
    def _parseSelectedExtruder(self, gcode) -> None:
        m = self._replaced_code

        if gcode.startswith("T"):
            # 익스트루더 인덱스 및 이름 저장
            self._selected_extruder_index = int(m[-1]) # 현재 익스트루더의 인덱스
            self._nozzle_type = self._getVariantName(self._selected_extruder_index)
            # 익스트루더 이름 변환
            m = m.replace("T0","D6").replace("T","D")
            self._selected_extruder = m # 수정 필요* 함수로 바꿔서 String화
            # 익스트루더가 바뀔 때 변경되는 설정
            m = self._addExtruderSelectingCode(m) #*** (1)

            # if self._selected_extruder != 'D6': # Right Extruder
            #     self._affectCLocationWithHop() # 선택된 익스트루더의 Hop으로 인한 C좌표 변경 작업 (2)

            self._replaced_code = m # 멤버 변수에 저장 
            self._setUVCode() # 익스트루더가 바뀔떄 마다 호출 (3)
            self._noteSelectedExtruder() # 사용되는 익스트루더를 리스트에 저장

    # z좌표 관리
    def _convertZCommand(self, gcode):
        if gcode.startswith(('G0','G1')) and gcode.find("Z") != -1:
            try:
                self._current_z_value = float(gcode[gcode.find("Z") + 1:]) # ***

                if self._selected_extruder != 'D6': # Right
                    self._replaced_code = self._convertFromZToC() # C 좌표로 변환
            except Exception:
                Logger.logException("w","Could not convert from Z to C")
                pass

    # C 좌표로 변환
    def _convertFromZToC(self):
        replaced = self._replaced_code
        replaced = replaced[:replaced.find("Z")]
        replaced += "\nG0 C"+ str(self._current_z_value)
        return replaced

    # E 커맨드 제거
    def _removeECommand(self, gcode):
        if self._nozzle_type.startswith('FFF'): 
            return gcode
        if gcode.find("E") != -1:
            gcode = gcode[:gcode.find("E")-1]
        return gcode

#--------------------------------------------------------------------------------------------------------------------------------------------------------------

    # 선택된 실린지에 따라 UV '종류', '주기', '시간', '세기' 가 다름.
    def _setUVCode(self):
        index = self._selected_extruder_index
        self._uv_position = self._TraslateToGcode["UVDevicePosition"]
        self._uv_per_layers = self._getExtrudersProperty(index,"uv_per_layers")
        self._uv_type = self._getExtrudersProperty(index,"uv_type")
        self._uv_time = self._getExtrudersProperty(index,"uv_time")
        self._uv_dimming = self._getExtrudersProperty(index,"uv_dimming") # - 미구현
        
        # UV 타입에 따른 UV 명령어 선정        
        if self._uv_type == '365':
            self._uv_on_code = self._TraslateToGcode['UVCuringOn'] # UV type: Curing
            self._uv_off_code = self._TraslateToGcode['UVCuringOff'] # UV type: Curing
        elif self._uv_type == '405':
            self._uv_on_code = self._TraslateToGcode['UVDisinfectionOn'] # UV type: Disinfect
            self._uv_off_code = self._TraslateToGcode['UVDisinfectionOff'] # UV type: Disinfect
        
        x_position = self._LeftExtruderXPosition
        if (self._selected_extruder != "D6"):
            x_position = -x_position

        self._change_current_position_for_uv = self._TraslateToGcode['SetToNewAxis'] %  (x_position, 0)
        self._move_to_uv_position = self._TraslateToGcode['RMoveToXY'] % (x_position, 0)

    # Layer 주기를 기준으로 UV 명령어 삽입
    # dispenser 설정 명령어 삽입
    def _addUVCommand(self, lines) -> None:
        if lines.startswith(";LAYER:"):
            self._layer_no = int(lines[len(";LAYER:"):lines.find("\n")])
            if self._uv_enable_list[self._selected_extruder_index]:
                if self._current_z_value is None: # 예외 처리
                    Logger.log("w","No Current Z Value")
                    self._current_z_value = 0.00
                if (self._layer_no % self._uv_per_layers) == 0:
                    uv_part = ";UV\n"
                    uv_part += self._TraslateToGcode['MoveToOrigin']
                    uv_part += self._change_current_position_for_uv
                    uv_part += self._TraslateToGcode['RMoveToXY'] % (self._uv_position['x'], self._uv_position['y'])
                    uv_part += self._TraslateToGcode['MoveToZ'] % (self._uv_position['z'])
                    uv_part += self._uv_on_code # UV ON
                    uv_part += self._TraslateToGcode['UVTime'] % (self._uv_time * 1000)
                    uv_part += self._uv_off_code # UV Off
                    if self._selected_extruder != 'D6':
                        uv_part += self._TraslateToGcode['MoveToZ'] % (0.00)
                    else:
                        uv_part += self._TraslateToGcode['MoveToZ'] % (self._current_z_value)
                    uv_part += self._move_to_uv_position
                    uv_part += self._TraslateToGcode['SetToNewAxis'] % (0.00, 0.00)
                    self._replaced_line += uv_part

    # Well plate 복제 기능
    def _clonning(self, trip):
        clone_num = trip["well_number"] -1 # 본코드를 제외판 복제 코드는 전체에서 1개를 빼야함.
        line_seq = trip["line_seq"]
        # z_height = trip["z"]

        gcode_clone = self._replaced_gcode_list[2:-1]
        std_str = self._TraslateToGcode['MoveToOrigin']
        self._line_controller = 1 # forward

        gcode_body = []
        for i in range(1,clone_num): # Clone number ex) 1 ~ 96
            if i % line_seq ==0:
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
            gcode_spacing += self._TraslateToGcode['MoveToOrigin']
            gcode_spacing += self._TraslateToGcode['MoveTo'] % ('C', -4.0)
            gcode_spacing += self._TraslateToGcode['RMoveTo'] % (direction , distance)
            gcode_spacing += self._TraslateToGcode['MoveTo'] % ('C', self._start_coord['c'])
            gcode_spacing += self._TraslateToGcode['MoveToAxisOrigin']

            gcode_clone.insert(0,gcode_spacing)
            self._replaced_gcode_list[-2:-2]= gcode_clone  # put the clones in front of the end-code
            # gcode_body.append(gcode_clone)
            gcode_clone.remove(gcode_spacing)

    # start 코드 다음으로 붙는 준비 명령어
    def _setBuildPlateProperty(self):
        a_command = self._TraslateToGcode["AAxisPosition"]
        self._build_plate = self._getGlobalContainerStackProperty("machine_build_dish_type")
        self._build_plate_type = self._build_plate[:self._build_plate.find(':')]

        # 
        if (self._build_plate_type == "Culture Dish"):
            extruder_selecting = "\n;start point\n"
            if self._selected_extruder_list[0] is None: # 예외 처리
                self._selected_extruder_list.append("D6")

            if self._selected_extruder_list[0] == "D6":
                extruder_selecting += self._TraslateToGcode['RMoveToXY'] % (self._LeftExtruderXPosition, 0)
                extruder_selecting += self._TraslateToGcode["ResetAxis"] # G92 Z40
            else: # Right
                extruder_selecting += self._TraslateToGcode['RMoveToXY'] % (-self._LeftExtruderXPosition, 0)
                extruder_selecting += self._TraslateToGcode["MoveToAF"] % (a_command[self._selected_extruder_num_list[0]], 600)
                extruder_selecting += self._TraslateToGcode["ResetAxis"] # G92 C40
                extruder_selecting += self._TraslateToGcode["GoToDetectedLimit"]
                

            extruder_selecting += self._TraslateToGcode['MoveToAxisOrigin']
            self._replaced_gcode_list[1] += extruder_selecting
            # gcode_list.insert(-1,self._TraslateToGcode['SetToNewAxis'] % (11, start_point.y()))
            
            self._replaced_gcode_list.insert(-1,self._TraslateToGcode['MoveToZ'] % (40.0))
            self._replaced_gcode_list.insert(-1,self._TraslateToGcode['MoveToC'] % (40.0))
            self._replaced_gcode_list.insert(-1,self._TraslateToGcode['ResetZAxisToZeo'])
            self._replaced_gcode_list.insert(-1,self._TraslateToGcode['ResetCAxisToZeo'])
        
        elif (self._build_plate_type == "Well Plate"):
            # "trip": {"line_seq":96/8, "spacing":9.0, "z": 10.8, "start_point": QPoint(74,49.5)}})
            for index in range(self._build_dish_model.count):
                self._dish = self._build_dish_model.getItem(index)
                if self._dish['product_id'] == self._build_plate:
                    trip = self._dish['trip']
                    break

            start_point = trip["start_point"]
            # if self._nozzle_type.startsWith == "FFF" or self._nozzle_type.endswith("Nozzle"):
            # 원점 재설정 # 익스트루더 선택 (left, r1, r2, r3, r4, r5)
            extruder_selecting = "\n;start point\n"
            # 수정해야함. (left right 관련된 스타트 포인트가 없음.)
            extruder_selecting += self._TraslateToGcode['RMoveToXY'] % (start_point.x(), start_point.y())
            extruder_selecting += self._TraslateToGcode['MoveToAxisOrigin']
            if self._selected_extruder_list[0] != 'D6':
                extruder_selecting += self._TraslateToGcode["GoToDetectedLimit"] # G78 B50.
            self._replaced_gcode_list[1] += extruder_selecting
            self._clonning(trip)

