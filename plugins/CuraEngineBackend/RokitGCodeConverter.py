# Copyright (c) 2020 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from string import Formatter
from enum import IntEnum
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

# 
# 
# 
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
        self._dispensor_enable_list = [] 
        self._dispensor_shot_list = []
        self._dispensor_vac_list = []
        self._dispensor_int_list = []
        self._dispensor_shot_pressure_list = []
        self._dispensor_vac_pressure_list = []
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
        self._z_value = None
        self._to_c_value = None

        self._selected_extruder_index = None  # 0(left), 1, 2, 3, 4, 5
        self._previous_extruder_index = None
        self._selected_extruder_num_list = []   # 0(Left), 1, 2, 3, 4, 5
        self._nozzle_type = ""
        
        self._layer_no = None
        self._uv_position = None        

        # 빌드 플레이트 타입
        self._build_plate = ""
        self._build_plate_type = ""

        self._repalced_gcode_list = []        
        self._replaced_command = ""
        self._replaced_line = ""

    def setReplacedlist(self, replaced_gcode_list) -> None:
        self._repalced_gcode_list = replaced_gcode_list

    def getReplacedlist(self):
        return self._repalced_gcode_list

    # 전역 변수들 초기화
    def _initialiizeConverter(self):
        self._application = CuraApplication.getInstance()
        self._global_container_stack = self._application.getMachineManager().activeMachine

        self._command_model = RokitCommandModel()
        self._build_dish_model = RokitBuildDishModel()

        self._command_dic = self._command_model.ChangeStrings # {}
        self._marlin_command_dic = self._command_model.marlin["command"] # {}
        self._calculateCLocation()
        self._shot_flag = True
        
    # 시작 + local 변수 초기화
    def run(self):
        self._initialiizeConverter()

        self._getPrintProperty() # gcode 가져오기
        self._convertGCode() # 기본 변환
        self._setBuildPlateProperty() # 플레이트에 따라 변환
    
    # Main
    def _convertGCode(self):
        # 
        # parse Selected Extruder : 선택한 익스트루더를 파싱 --> (선택한 익스트루더의 1. 노즐타입,)
        # affect C Location With Hop
        # insert Shot Command
        # convert Z To C
        # 
        # set UVCommand
        # 
        for index, lines in enumerate(self._repalced_gcode_list): # lines(layer) 마다
            # if index == len(self._repalced_gcode_list) -1 :
            #     break 
            self._replaced_line = lines

            layer_command_list = lines.split("\n")
            for num, command_line in enumerate(layer_command_list): # Command 마다
                self._replaced_command = command_line

                self._parseSelectedExtruder(command_line) # *** 가장 먼저, 선택된 익스트루더를 확인해야함.
                self._insertShotCommand(command_line)
                self._convertZToC(command_line)
                self._remove_marlin_command(command_line)

                if self._replaced_command is not None:
                    layer_command_list[num] = self._replaced_command
                else:
                    # layer_command_list.remove(layer_command_list[num])
                    layer_command_list[num] = ";{blank}"

            self._replaced_line = "\n".join(layer_command_list)
            self._addUVCommand(lines) # 레이어 주기에 맞춰 커맨드 삽입
            self._replaceStartCode() # 리마크 처리 용
            self._fillIntegerWithZero() # 정수를 0으로 채우기 함수
            self._replaceStartDispenserCode() 

            self._repalced_gcode_list[index] = self._replaced_line

    def _remove_marlin_command(self, command) -> None:
        for marlin_command in self._marlin_command_dic:
            if command.startswith(marlin_command):
                self._replaced_command = None
                return

    # uv enabled 조건 처리 미완----
    def _getPrintProperty(self):
        self._data_join_sequence = [1,2,3,4,5,0] # - 데이터 조인 순서 : 조인만 하는 데이터에 사용
        self._extruder_sequence = [0,1,2,3,4,5] # - 익스트루더 순서 : 호출하는 데이터에 사용

        self._extruder_list = self._global_container_stack.extruderList

        # 프린트 온도 설정
        self._print_temperature_list =[self._extruder_list[index].getProperty("material_print_temperature","value") for index in self._data_join_sequence] # - 데이터 조인 순서
        self._print_temperature_list.append(self._global_container_stack.getProperty("material_bed_temperature","value"))
        self._print_temperature = " ".join(map(str,self._print_temperature_list))
        
        # UV 설정 # - 익스트루더 순서
        self._uv_enable_list = [self._extruder_list[index].getProperty("uv_enable","value") for index in self._extruder_sequence]


    def _replaceStartCode(self):
        replaced = self._replaced_line
        replaced = replaced.replace("{print_temp}", self._command_dic['printTemperature'] % self._print_temperature)
        replaced = replaced.replace(";FLAVOR:Marlin", ";F/W : 7.6.8.0")

        replaced = replaced.replace("G92 E0\nG92 E0", "G92 E0")
        replaced = replaced.replace("M105\n", "")
        replaced = replaced.replace(";{blank}\n", "")
        self._replaced_line = replaced
        
    # 디스펜서 설정 - dsp_enable, shot, vac, int, shot.p, vac.p   # - 데이터 조인 순서
    def _replaceStartDispenserCode(self) -> None:
        if self._nozzle_type == "FFF Extruder":
            return
        replaced = self._replaced_line
        self._dispensor_enable_list = [self._extruder_list[index].getProperty("dispensor_enable","value") for index in self._extruder_sequence] # - 익스트루더 순서
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


    def _addExtruderSelectCommand(self,replaced): # FFF 예외처리 필요
        a_command = self._command_dic["selected_extruders_A_location"] 
        replaced += " ;selected extruder\n;Nozzle type : %s\n" % self._nozzle_type
        replaced += self._command_dic["move_B_Coordinate"] % (0.0)
        replaced += self._command_dic["move_A_Coordinate"] % (a_command[self._selected_extruder], 600) if self._selected_extruder != 'D6' else ""
        replaced += self._command_dic["move_B_Coordinate"] % 20.0
        # replaced += self._command_dic["waitingTemperature"]       # M109
        return replaced
    
    # 중복되는 익스트루더 index 거르기
    def _checkSelectedExtruder(self, replaced_command) -> None:
        if self._previous_extruder_index != self._selected_extruder_index:
            self._selected_extruder_num_list.append(self._selected_extruder_index) # T 명령어 정보 (0,1,2,3,4,5)
        self._previous_extruder_index = self._selected_extruder_index
    
    def _setNozzleType(self, replaced_command) -> None:
        self._nozzle_type = self._extruder_list[self._selected_extruder_index].variant.getName()

    # T 명령어를 통해 선택한 시린지 확인
    def _parseSelectedExtruder(self, command_line) -> None:
        replaced_command = self._replaced_command
        if command_line.startswith("T"):
            self._selected_extruder_index = int(replaced_command[-1]) # 현재 익스트루더의 인덱스
            self._checkSelectedExtruder(replaced_command)  # 사용되는 익스트루더를 리스트에 저장
            self._setNozzleType(replaced_command)
            
            replaced_command = replaced_command.replace("T0","D6")
            replaced_command = replaced_command.replace("T","D")
            self._selected_extruder = replaced_command # 수정 필요

            if self._nozzle_type != "FFF Extruder":
                replaced_command = self._addExtruderSelectCommand(replaced_command)
                self._affectCLocationWithHop() # 선택되는 익스트루더가 바뀔 때 -> 선택된 익스트루더의 홉이 C좌표에 영향을 준다.
            self._replaced_command = replaced_command
            self._setUVCommand() # 익스트루더가 바뀔떄 마다 호출


    def _affectCLocationWithHop(self) -> None:
        selected_num = self._selected_extruder_num_list[0]
        self._retraction_hop_enabled = self._extruder_list[selected_num].getProperty("retraction_hop_enabled","value")
        self._retraction_hop_height = self._extruder_list[selected_num].getProperty("retraction_hop_after_extruder_switch_height","value")
        # self._retraction_hop_height = self._extruder_list[selected_num].getProperty("retraction_hop_after_extruder_switch","value")
        if self._retraction_hop_enabled == True:
            self._to_c_value = -20.0 - float(self._z_value) + self._retraction_hop_height
    
    def _calculateCLocation(self) -> None:
        self._first_z = self._repalced_gcode_list[2].find("Z")
        self._z_value = self._repalced_gcode_list[2][self._first_z + 1 : self._repalced_gcode_list[2].find("\n",self._first_z)]
        self._to_c_value = -20.0 - float(self._z_value)

    # C 좌표로 변환    
    def _convertZToC(self, command_line):
        if self._nozzle_type == "FFF Extruder": 
            return
        
        replaced = self._replaced_command
        if command_line.startswith("G") :
            if command_line.find("Z") != -1:
                z_value = command_line[command_line.find("Z") + 1:]
                j_location = float(z_value)+ self._to_c_value
                j_location = round(j_location,2)

                remove_z_value = command_line[:command_line.find("Z")]                

                replaced = replaced[:replaced.find("Z")]
                replaced += "\nG0 C"+ str(j_location) # 기존 z값
        self._replaced_command = replaced

    #Shot/Stop 명령어
    def _insertShotCommand(self, command_line):
        if self._nozzle_type == "FFF Extruder": 
            return

        replaced = self._replaced_command
        if command_line.startswith("G1") :
            if len(replaced.split()) > 4 and self._shot_flag == True:
                replaced = self._command_dic["shotStart"] + replaced
                self._shot_flag = False
        elif command_line.startswith("G0") :
            if self._shot_flag == False:
                replaced = self._command_dic["shotStop"] + replaced
                self._shot_flag =True
        self._replaced_command = replaced
#--------------------------------------------------------------------------------------------------------------------------------------------------------------

    def _setUVCommand(self):
        self._uv_per_layers = self._extruder_list[self._selected_extruder_num_list[0]].getProperty("uv_per_layers","value")
        self._uv_type = self._extruder_list[self._selected_extruder_num_list[0]].getProperty("uv_type","value")
        self._uv_time = self._extruder_list[self._selected_extruder_num_list[0]].getProperty("uv_time","value")
        self._uv_dimming = self._extruder_list[self._selected_extruder_num_list[0]].getProperty("uv_dimming","value") # - 미구현
        
        # UV 타입에 따른 UV 명령어 선정        
        if self._uv_type == '365':
            self._uv_command = self._command_dic['uvCuring'] # UV type: Curing
        elif self._uv_type == '405':
            self._uv_command = self._command_dic['uvDisinfect'] # UV type: Disinfect


    # Layer 주기를 기준으로 UV 명령어 삽입
    # dispenser 설정 명령어 삽입
    def _addUVCommand(self, lines) -> None:
        if lines.startswith(";LAYER:"):
            self._layer_no = int(lines[len(";LAYER:"):lines.find("\n")])
            self._uv_position = self._command_dic["static_uv_position"]

            if self._uv_enable_list[self._selected_extruder_num_list[0]] == True:
                if (self._layer_no % self._uv_per_layers) == 0:
                    uv_part = ";UV\n"
                    # uv_part += self._command_dic['moveToOriginCenter']
                    uv_part += self._command_dic['moveToRelativeZ'] % (self._uv_position['z'])
                    uv_part += self._command_dic['moveToRelativeXY'] % (self._uv_position['x'], self._uv_position['y'])
                    uv_part += self._uv_command['on'] # UV ON
                    uv_part += self._command_dic['uvTime'] % (self._uv_time * 1000)
                    uv_part += self._uv_command['off'] # UV Off
                    uv_part += self._command_dic['moveToRelativeXY'] % (self._uv_position['x'], -self._uv_position['y'])
                    uv_part += self._command_dic['moveToRelativeZ'] % (-self._uv_position['z'])
                    # uv_part += self._command_dic['moveToOriginCenter']
                    self._replaced_line += uv_part

    def _clonning(self, trip):
        # 복제 시스템 -------------------------> def로 변환

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
        self._build_plate = self._global_container_stack.getProperty("machine_build_dish_type", "value")
        self._build_plate_type = self._build_plate[:self._build_plate.find(':')]


        if (self._build_plate_type == "Culture Dish"):
            if self._nozzle_type != "FFF Extruder":
                extruder_selecting = "\n;start point\n"
                extruder_selecting += self._command_dic['moveToAbsoluteXY'] % (-42.5, 0.0)
                extruder_selecting += self._command_dic['changeAbsoluteAxisToCenter']
                extruder_selecting += self._command_dic["move_B_Coordinate"] % (20.0)

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
            if self._nozzle_type != "FFF Extruder":
                # 원점 재설정 # 익스트루더 선택 (left, r1, r2, r3, r4, r5)
                extruder_selecting = "\n;start point\n"
                extruder_selecting += self._command_dic['moveToAbsoluteXY'] % (start_point.x(), start_point.y())
                extruder_selecting += self._command_dic['changeAbsoluteAxisToCenter']
                extruder_selecting += self._command_dic["move_B_Coordinate"] % (20.0)
                self._repalced_gcode_list[1] += extruder_selecting

            self._clonning(trip)

