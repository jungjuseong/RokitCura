# Copyright (c) 2020 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from string import Formatter
from enum import IntEnum
from UM.Logger import Logger
from typing import Any, cast, Dict, List, Optional, Set
import re
import Arcus #For typing.

from cura.CuraApplication import CuraApplication
from cura.Machines.Models.RokitBuildDishModel import RokitBuildDishModel

class RokitPrintQuality:
    def __init__(self) -> None:    

        self._application = CuraApplication.getInstance()
        self._global_container_stack = self._application.getMachineManager().activeMachine

        # extruders info
        self._JoinSequence = [1,2,3,4,5,0] # - 데이터 조인 순서 : 조인만 하는 데이터에 사용

        self.ExtruderNames = ['D6','D1','D2','D3','D4','D5']

        self.Extruder_X_Position = [42.5, -42.5, -42.5, -42.5, -42.5, -42.5]
        self.LeftExtruder_X_Offset = 85.0
        self.A_AxisPosition = [0, 0, -72,  72, 144, -144] 

        # 프린트 온도 설정
        temperature_list = [self._getExtrudersProperty(index,'material_print_temperature') for index in self._JoinSequence] # - 데이터 조인 순서
        temperature_list.append(self.getGlobalContainerStackProperty('material_bed_temperature'))
        self.print_temperature = ' '.join(map(str, temperature_list))

        # get dispenser property from global stack
        self.dispensor_enable = self.getGlobalContainerStackProperty('dispensor_enable')

        self.shot_time_list = ' '.join(map(str,[self._getExtrudersProperty(index,'dispensor_shot') for index in self._JoinSequence]))
        self.vac_time_list = ' '.join(map(str,[self._getExtrudersProperty(index,'dispensor_vac') for index in self._JoinSequence]))
        self.interval_list = ' '.join(map(str,[self._getExtrudersProperty(index,'dispensor_int') for index in self._JoinSequence]))
        self.shot_power_list = ' '.join(map(str,[self._getExtrudersProperty(index,'dispensor_shot_power') for index in self._JoinSequence]))
        self.vac_power_list = ' '.join(map(str,[self._getExtrudersProperty(index,'dispensor_vac_power') for index in self._JoinSequence]))

        # UV 설정
        self.uv_enable_list = [False,False,False,False,False,False]
        self.uv_per_layer_list = [1,1,1,1,1,1]
        self.uv_start_layer_list = [1,1,1,1,1,1]

        self.uv_type_list = ['365','365','365','365','365','365']
        self.uv_time_list = [5,5,5,5,5,5]
        self.uv_dimming_list = [80,80,80,80,80,80]

        # Well Plate의 경우 UV는 출력이 안되게 함
        uv = self.getGlobalContainerStackProperty("uv"); 
        if uv:
            self.uv_enable_list = [self._getExtrudersProperty(index,'uv_enable') for index in range(6)]

        for index, uv_enable in enumerate(self.uv_enable_list):
            if uv_enable:
                self.uv_per_layer_list[index] = self._getExtrudersProperty(index,'uv_per_layers')
                self.uv_start_layer_list[index] = self._getExtrudersProperty(index,'uv_start_layer')
                self.uv_type_list[index] = self._getExtrudersProperty(index,'uv_type')
                self.uv_time_list[index] = self._getExtrudersProperty(index,'uv_time')
                self.uv_dimming_list[index] = self._getExtrudersProperty(index,'uv_dimming')

        # 쿨링
        self.cool_fan_enabled_list = [self._getExtrudersProperty(index,'cool_fan_enabled') for index in range(6)]

        # 리트렉션
        # self.retraction_enable_list = [self._getExtrudersProperty(index,'retraction_enable') for index in range(6)]
        # self.retraction_amount_list = [self._getExtrudersProperty(index,'retraction_amount') for index in range(6)]
        # self.retraction_speed_list = [self._getExtrudersProperty(index,'retraction_speed') for index in range(6)]
        # self.retraction_min_travel = [self._getExtrudersProperty(index,'retraction_min_travel') for index in range(6)]
        # self.retraction_extrusion_window = [self._getExtrudersProperty(index,'retraction_extrusion_window') for index in range(6)]

        # z좌표 관리
        self.layer_height_0 = self.getGlobalContainerStackProperty('layer_height_0')
        self.layer_height = self.getGlobalContainerStackProperty('layer_height')

        self.wall_thickness_list = ' '.join(map(str,[self._getExtrudersProperty(index,'wall_thickness') for index in self._JoinSequence]))
        self.infill_sparse_density_list = ' '.join(map(str,[self._getExtrudersProperty(index,'infill_sparse_density') for index in self._JoinSequence]))

    def _getExtrudersProperty(self, index, property):
        return self._global_container_stack.extruderList[index].getProperty(property,'value')

    def getGlobalContainerStackProperty(self, property):
        return self._global_container_stack.getProperty(property,'value')

    def getVariantName(self, index):
        variant = ''
        if index >= 0 and index < 6:
            variant = self._global_container_stack.extruderList[index].variant.getName()
        return variant
