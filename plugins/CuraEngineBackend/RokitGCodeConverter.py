# Copyright (c) 2020 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from string import Formatter
from enum import IntEnum
from UM.Logger import Logger
from typing import Any, cast, Dict, List, Optional, Set
import re
import Arcus #For typing.

from cura.CuraApplication import CuraApplication
from cura.Machines.Models.RokitCommandModel import RokitCommandModel
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

        # 외부
        self._application = None
        self._global_container_stack = None
        self._extruder_list = None 

        # 필요
        self._command_model = None
        self._build_dish_model = None
        self._data_join_sequence = []
        self._extruder_sequence = []
        
        # 프린트 온도 설정
        self._print_temperature_list = []

        # 디스펜서 설정 - dsp_enable, shot, vac, int, shot.p, vac.p
        self._is_enable_dispensor = None

        # UV 설정 - extruder에서 읽도록 바꿔야 함
        self._uv_enable_list = []
        self._uv_per_layers = []
        self._uv_type = []
        self._uv_time = []
        self._uv_dimming = []

        # 외부 dict
        self._command_dic = {}
        self._dish = {}

        # z를 c축으로
        self._first_z = None # firstZ
        self._first_z_value = None
        self._to_c_value = None
        self._current_z_value = None

        self._selected_extruder = None
        self._previous_extruder = None
        self._selected_extruder_index = None  # 0(left), 1, 2, 3, 4, 5
        self._previous_extruder_index = None
        self._selected_extruder_num_list = []   # [0(Left), 1, 2, 3, 4, 5]
        self._nozzle_type = ""
        
        self._layer_no = None
        self._uv_position = None        

        # 빌드 플레이트 타입
        self._build_plate = ""
        self._build_plate_type = ""

        self._repalced_gcode_list = []        
        self._replaced_command = ""
        self._replaced_line = ""

        self._change_current_position_for_uv = None
        self._move_to_uv_position = None

    def setReplacedlist(self, replaced_gcode_list) -> None:
        self._repalced_gcode_list = replaced_gcode_list

    def getReplacedlist(self):
        return self._repalced_gcode_list

    # 멤버 변수들 초기화
    def _initialiizeConverter(self):
        self._application = CuraApplication.getInstance()
        self._global_container_stack = self._application.getMachineManager().activeMachine

        self._command_model = RokitCommandModel()
        self._build_dish_model = RokitBuildDishModel()

        self._command_dic = self._command_model.ChangeStrings # {}
        self._marlin_command_dic = self._command_model.marlin["command"] # {}
        self._calculateCLocation()
        self._is_shot_moment = True
        self.is_first_selectedExtruder = True

    def _calculateCLocation(self) -> None:
        # -------------------------------------------------------------------------------------가장 처음 등장하는 Z값 찾기
        self._first_z = self._repalced_gcode_list[2].find("Z")
        self._first_z_value = self._repalced_gcode_list[2][self._first_z + 1 : self._repalced_gcode_list[2].find("\n",self._first_z)]
        self._to_c_value = -20.0 - float(self._first_z_value)
        
    # 시작 (준비 작업)
    def run(self):
        self._initialiizeConverter()

        self._getPrintProperty() # gcode 가져오기
        self._convertGCode() # 기본 변환
        self._setBuildPlateProperty() # 플레이트에 따라 변환 # 수정 필요

    def _getPrintProperty(self):
        self._data_join_sequence = [1,2,3,4,5,0] # - 데이터 조인 순서 : 조인만 하는 데이터에 사용
        self._extruder_sequence = [0,1,2,3,4,5] # - 익스트루더 순서 : 호출하는 데이터에 사용

        self._extruder_list = self._global_container_stack.extruderList

        # 프린트 온도 설정
        self._print_temperature_list =[self._extruder_list[index].getProperty("material_print_temperature","value") for index in self._data_join_sequence] # - 데이터 조인 순서
        self._print_temperature_list.append(self._global_container_stack.getProperty("material_bed_temperature","value"))
        self._print_temperature = " ".join(map(str,self._print_temperature_list))        
        # UV 사용 여부
        self._uv_enable_list = [self._extruder_list[index].getProperty("uv_enable","value") for index in self._extruder_sequence]
        # Dispenser 사용 여부
        self._is_enable_dispensor = self._global_container_stack.getProperty("dispensor_enable","value")
        
    # Main
    def _convertGCode(self): 
        for index, lines in enumerate(self._repalced_gcode_list): # lines(layer) 마다
            self._replaced_line = lines

            layer_command_list = lines.split("\n")
            for num, command_line in enumerate(layer_command_list): # Command 마다
                self._replaced_command = command_line
                self._removeMarlinCommand(command_line)
                self._parseSelectedExtruder(command_line) # *** 가장 먼저, 선택된 익스트루더를 확인해야함.

                if index != len(self._repalced_gcode_list) -1: # 마지막 엔드 코드는 고려 안함. # start 코드도 고려하게 수정해야함.
                    self._insertShotCommand(command_line)
                    self._convertZCommand(command_line)

                if self._replaced_command is not None:
                    layer_command_list[num] = self._replaced_command
                else:
                    layer_command_list[num] = ";{blank}"
            self._replaced_line = "\n".join(layer_command_list)

            self._addUVCommand(lines) # 레이어 주기에 맞춰 커맨드 삽입
            self._replaceStartCode() # 리마크 처리 용
            self._fillIntegerWithZero() # 정수를 0으로 채우기 함수
            self._replaceStartDispenserCode() # 조건 처리 필요 (index 1,2에서 다음의 함수가 필요)
            self._repalced_gcode_list[index] = self._replaced_line
            
    # Shot/Stop 명령어
    def _insertShotCommand(self, command_line) -> None:
        command = self._replaced_command
        if command_line.startswith("G1") :
            command = self._removeECommand(command)
            if len(command_line.split()) > 3 and self._is_shot_moment == True: # *******
                command = self._command_dic["shotStart"] + command
                self._is_shot_moment = False
        elif command_line.startswith("G0") :
            if self._is_shot_moment == False:
                command = self._command_dic["shotStop"] + command
                self._is_shot_moment =True
        self._replaced_command = command

    # Marlin 커맨드 제거
    def _removeMarlinCommand(self, command) -> None:
        for marlin_command in self._marlin_command_dic:
            if command.startswith(marlin_command):
                self._replaced_command = None
                return

    def _replaceStartCode(self):
        replaced = self._replaced_line
        replaced = replaced.replace("{print_temp}", self._command_dic['printTemperature'] % self._print_temperature)
        replaced = replaced.replace(";FLAVOR:Marlin", ";F/W : 7.6.8.0")

        replaced = replaced.replace("G92 E0\nG92 E0", "G92 E0")
        replaced = replaced.replace("M105\n", "")
        replaced = replaced.replace("M107\n", "")
        replaced = replaced.replace("M82 ;absolute extrusion mode\n", "")
        replaced = replaced.replace(";{blank}\n", "")
        self._replaced_line = replaced
        
    # 디스펜서 설정 - dsp_enable, shot, vac, int, shot.p, vac.p   # - 데이터 조인 순서
    def _replaceStartDispenserCode(self) -> None:
        if self._nozzle_type == "FFF Extruder" or self._nozzle_type.endswith("Nozzle") or not self._is_enable_dispensor:
            return
        replaced = self._replaced_line
        self._dispensor_shot_list = [self._extruder_list[index].getProperty("dispensor_shot","value") for index in self._data_join_sequence] 
        self._dispensor_vac_list = [self._extruder_list[index].getProperty("dispensor_vac","value") for index in self._data_join_sequence]
        self._dispensor_int_list = [self._extruder_list[index].getProperty("dispensor_int","value") for index in self._data_join_sequence]
        self._dispensor_shot_pressure_list = [self._extruder_list[index].getProperty("dispensor_shot_power","value") for index in self._data_join_sequence]
        self._dispensor_vac_pressure_list = [self._extruder_list[index].getProperty("dispensor_vac_power","value") for index in self._data_join_sequence]
        
        shot_times = " ".join(map(str,self._dispensor_shot_list))
        vac_times = " ".join(map(str,self._dispensor_vac_list))
        intervals = " ".join(map(str,self._dispensor_int_list))
        shot_pressures = " ".join(map(str,self._dispensor_shot_pressure_list))
        vac_pressures = " ".join(map(str,self._dispensor_vac_pressure_list))
        
        replaced = replaced.replace(";{shot_time}", self._command_dic['shotTime'] % shot_times)
        replaced = replaced.replace(";{vac_time}", self._command_dic['vacuumTime'] % vac_times)
        replaced = replaced.replace(";{interval}", self._command_dic['interval'] % intervals)
        replaced = replaced.replace(";{shot_p}", self._command_dic['shotPressure'] % shot_pressures)
        replaced = replaced.replace(";{vac_p}", self._command_dic['vacuumPressure'] % vac_pressures)
        self._replaced_line = replaced

    def _fillIntegerWithZero(self) -> None:
        self._replaced_line = self._replaced_line.replace("-.","-0.")
#--------------------------------------------------------------------------------------------------------------------------------------------
    # # 중복되는 익스트루더 index 거르기
    # def _checkSelectedExtruder(self, replaced_command) -> None:
    #     if self._previous_extruder_index != self._selected_extruder_index:
    #         self._selected_extruder_num_list.append(self._selected_extruder_index) # T 명령어 정보 (0,1,2,3,4,5)
    #     self._previous_extruder_index = self._selected_extruder_index

    def _addExtruderSelectingCommand(self,replaced): # FFF 예외처리 필요
        replaced += " ;selected extruder\n;Nozzle type : %s\n" % self._nozzle_type
        if self.is_first_selectedExtruder:
            self.is_first_selectedExtruder = False
            return replaced

        a_command = self._command_dic["selected_extruders_A_location"] 
        replaced += self._command_dic["move_B_Coordinate_with_speed"] % (0.0, 300) # Z축 초기화도 필요함. **
        
        if self._selected_extruder == 'D6':
            # Left --> Right
            if self._previous_extruder != 'D6':
                replaced += self._command_dic["moveToAbsoluteXY"] % (-85.0, 0.0)
        else:
            replaced += self._command_dic["move_A_Coordinate"] % (a_command[self._selected_extruder], 600)
            replaced += self._command_dic["goToLimitDetacted"]
            # Right --> Left
            if self._previous_extruder == 'D6':
                replaced += self._command_dic["moveToAbsoluteXY"] % (85.0, 0.0)
        replaced += self._command_dic["changeAbsoluteAxisToCenter"]
        # replaced += self._command_dic["waitingTemperature"]       # M109 Keep
        return replaced
    

    # 익스트루더 index 기록
    def _noteSelectedExtruder(self) -> None:
        self._previous_extruder = self._selected_extruder
    
    def _setNozzleType(self, replaced_command) -> None:
        self._nozzle_type = self._extruder_list[self._selected_extruder_index].variant.getName()

    # T 명령어를 통해 선택한 시린지 확인
    def _parseSelectedExtruder(self, command_line) -> None:
        replaced_command = self._replaced_command

        if command_line.startswith("T"):
            # -------------------------------------------------------------------------------------익스트루더 인덱스 및 이름 저장
            self._selected_extruder_index = int(replaced_command[-1]) # 현재 익스트루더의 인덱스
            # self._checkSelectedExtruder(replaced_command)  # 사용되는 익스트루더를 리스트에 저장
            self._setNozzleType(replaced_command)
            # -------------------------------------------------------------------------------------익스트루더 이름 변환
            replaced_command = replaced_command.replace("T0","D6")
            replaced_command = replaced_command.replace("T","D")
            self._selected_extruder = replaced_command # 수정 필요* 함수로 바꿔서 String화
            # -------------------------------------------------------------------------------------익스트루더가 바뀔 때 변경되는 설정작업
            replaced_command = self._addExtruderSelectingCommand(replaced_command) #*** (1)
            if self._selected_extruder != 'D6': # <Right Extruder>
                self._affectCLocationWithHop() # 선택된 익스트루더의 Hop으로 인한 C좌표 변경 작업 (2)
            self._replaced_command = replaced_command # 멤버 변수에 저장 
            self._setUVCommand() # 익스트루더가 바뀔떄 마다 호출 (3)
            self._noteSelectedExtruder()

    def _affectCLocationWithHop(self) -> None:
        selected_num = self._selected_extruder_index
        self._retraction_hop_enabled = self._extruder_list[selected_num].getProperty("retraction_hop_enabled","value")
        self._retraction_hop_height = self._extruder_list[selected_num].getProperty("retraction_hop_after_extruder_switch_height","value")
        if self._retraction_hop_enabled == True:
            self._to_c_value = -20.0 - float(self._first_z_value) + self._retraction_hop_height

    def _convertZCommand(self, command_line):
        if command_line.startswith("G") and command_line.find("Z") != -1:
            try:
                self._current_z_value = float(command_line[command_line.find("Z") + 1:])
                c_location = self._current_z_value + self._to_c_value
                c_location = round(c_location,2)

                if self._selected_extruder != 'D6': # Right일 때만 C좌표로 변환.
                    self._replaced_command = self._convertFromZToC(c_location)
            except Exception:
                Logger.logException("w","Could not convert from Z to C")
                pass

    # C 좌표로 변환    
    def _convertFromZToC(self, c_location):
        replaced = self._replaced_command
        replaced = replaced[:replaced.find("Z")]
        replaced += "\nG0 C"+ str(c_location) # 기존 z값
        return replaced

    # E 커맨드 제거
    def _removeECommand(self, command_line):
        if command_line.find("E") != -1:
            command_line = command_line[:command_line.find("E")-1]
        return command_line

#--------------------------------------------------------------------------------------------------------------------------------------------------------------

    # 선택된 실린지에 따라 UV '종류', '주기', '시간', '세기' 가 다름.
    def _setUVCommand(self):
        self._uv_position = self._command_dic["static_uv_position"]
        
        self._uv_per_layers = self._extruder_list[self._selected_extruder_index].getProperty("uv_per_layers","value")
        self._uv_type = self._extruder_list[self._selected_extruder_index].getProperty("uv_type","value")
        self._uv_time = self._extruder_list[self._selected_extruder_index].getProperty("uv_time","value")
        self._uv_dimming = self._extruder_list[self._selected_extruder_index].getProperty("uv_dimming","value") # - 미구현
        
        # UV 타입에 따른 UV 명령어 선정        
        if self._uv_type == '365':
            self._uv_command = self._command_dic['uvCuring'] # UV type: Curing
        elif self._uv_type == '405':
            self._uv_command = self._command_dic['uvDisinfect'] # UV type: Disinfect

        if self._selected_extruder == "D6": # Left
            self._change_current_position_for_uv = self._command_dic['changeToNewAbsoluteAxis'] % (-42.50, 0.00)
            self._move_to_uv_position = self._command_dic['moveToAbsoluteXY'] % (-42.50, 0.00)
        else: # Right
            self._change_current_position_for_uv = self._command_dic['changeToNewAbsoluteAxis'] % (42.50, 0.00)
            self._move_to_uv_position = self._command_dic['moveToAbsoluteXY'] % (42.50, 0.00)


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
                    uv_part += self._command_dic['moveToOriginCenter']
                    uv_part += self._change_current_position_for_uv
                    uv_part += self._command_dic['moveToAbsoluteXY'] % (self._uv_position['x'], self._uv_position['y'])
                    uv_part += self._command_dic['moveToAbsoluteZ'] % (self._uv_position['z'])
                    uv_part += self._uv_command['on'] # UV ON
                    uv_part += self._command_dic['uvTime'] % (self._uv_time * 1000)
                    uv_part += self._uv_command['off'] # UV Off
                    if self._selected_extruder != 'D6':
                        uv_part += self._command_dic['moveToAbsoluteZ'] % (0.00)
                    else:
                        uv_part += self._command_dic['moveToAbsoluteZ'] % (self._current_z_value)
                    uv_part += self._move_to_uv_position
                    uv_part += self._command_dic['changeToNewAbsoluteAxis'] % (0.00, 0.00)
                    self._replaced_line += uv_part

    # Well plate 복제 기능
    def _clonning(self, trip):
        clone_num = trip["well_number"] -1 # 본코드를 제외판 복제 코드는 전체에서 1개를 빼야함.
        line_seq = trip["line_seq"]
        # z_height = trip["z"]

        gcode_clone = self._repalced_gcode_list[2:-1]
        std_str = self._command_dic['moveToOriginCenter']
        self._line_controller = 1 # forward

        gcode_body = []
        for i in range(1,clone_num): # Clone number ex) 1 ~ 96
            if i % line_seq ==0:
                direction = 'X'
                distance = -trip["spacing"]
                self._line_controller = abs(self._line_controller-1) # direction control
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
            gcode_spacing += self._command_dic['moveToOriginCenter']
            gcode_spacing += self._command_dic['moveToAbsolute'] % ('C', -4.0)
            gcode_spacing += self._command_dic['moveToRelative'] % (direction , distance)
            gcode_spacing += self._command_dic['moveToAbsolute'] % ('C', -20.0)
            gcode_spacing += self._command_dic['changeAbsoluteAxisToCenter']

            gcode_clone.insert(0,gcode_spacing)
            self._repalced_gcode_list[-2:-2]= gcode_clone  # put the clones in front of the end-code
            # gcode_body.append(gcode_clone)
            gcode_clone.remove(gcode_spacing)

        # self._repalced_gcode_list.insert(-1,self._command_dic['changeToNewAbsoluteAxis'] % (11, start_point.y()))

    def _setBuildPlateProperty(self):
        # 빌드 플레이트 타입
        # start 코드 다음으로 붙는 준비 명령어
        a_command = self._command_dic["selected_extruders_A_location"]
        self._build_plate = self._global_container_stack.getProperty("machine_build_dish_type", "value")
        self._build_plate_type = self._build_plate[:self._build_plate.find(':')]


        if (self._build_plate_type == "Culture Dish"):
            extruder_selecting = "\n;start point\n"
            if self._selected_extruder == "D6": # Left
                extruder_selecting += self._command_dic['moveToAbsoluteXY'] % (-42.5, 0.0)
            else: # Right
                extruder_selecting += self._command_dic['moveToAbsoluteXY'] % (42.5, 0.0)
                extruder_selecting += self._command_dic["move_A_Coordinate"] % (a_command[self._selected_extruder], 600)
                extruder_selecting += self._command_dic["goToLimitDetacted"]
            extruder_selecting += self._command_dic['changeAbsoluteAxisToCenter']
            self._repalced_gcode_list[1] += extruder_selecting
            # gcode_list.insert(-1,self._command_dic['changeToNewAbsoluteAxis'] % (11, start_point.y()))
        elif (self._build_plate_type == "Well Plate"):
            # "trip": {"line_seq":96/8, "spacing":9.0, "z": 10.8, "start_point": QPoint(74,49.5)}})
            for index in range(self._build_dish_model.count):
                self._dish = self._build_dish_model.getItem(index)
                if self._dish['product_id'] == self._build_plate:
                    trip = self._dish['trip']
                    break

            start_point = trip["start_point"]
            # if self._nozzle_type == "FFF Extruder" or self._nozzle_type.endswith("Nozzle"):
            # 원점 재설정 # 익스트루더 선택 (left, r1, r2, r3, r4, r5)
            extruder_selecting = "\n;start point\n"
            # 수정해야함. (left right 관련된 스타트 포인트가 없음.)
            extruder_selecting += self._command_dic['moveToAbsoluteXY'] % (start_point.x(), start_point.y())
            extruder_selecting += self._command_dic['changeAbsoluteAxisToCenter']
            if self._selected_extruder != 'D6':
                extruder_selecting += self._command_dic["goToLimitDetacted"]
            self._repalced_gcode_list[1] += extruder_selecting
            self._clonning(trip)

