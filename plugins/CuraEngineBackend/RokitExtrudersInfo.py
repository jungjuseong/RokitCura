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

class RokitExtrudersInfo:
    def __init__(self) -> None:    

        self._application = CuraApplication.getInstance()
        self._global_container_stack = self._application.getMachineManager().activeMachine

        # extruders info
        self._JoinSequence = [1,2,3,4,5,0] # - 데이터 조인 순서 : 조인만 하는 데이터에 사용
        self._ExtruderSequence = [0,1,2,3,4,5] # - 데이터 조인 순서 : 조인만 하는 데이터에 사용

        self.ExtruderNames = ["D6","D1","D2","D3","D4","D5"]

        self.Extruder_X_Position = [42.5, -42.5, -42.5, -42.5, -42.5, -42.5]
        self.LeftExtruder_X_Offset = 85.0
        self.A_AxisPosition = [0, 0, -72,  72, 144, -144] 

        # 프린트 온도 설정
        temperature_list = [self._getExtrudersProperty(index,"material_print_temperature") for index in self._JoinSequence] # - 데이터 조인 순서
        temperature_list.append(self.getGlobalContainerStackProperty("material_bed_temperature"))
        self.print_temperature = " ".join(map(str, temperature_list))

        # get UV and dispenser property from global stack
        self.uv_enable_list = [self._getExtrudersProperty(index,"uv_enable") for index in self._ExtruderSequence]
        self.dispensor_enable = self.getGlobalContainerStackProperty("dispensor_enable")

        self.shot_time_list = " ".join(map(str,[self._getExtrudersProperty(index,"dispensor_shot") for index in self._JoinSequence]))
        self.vac_time_list = " ".join(map(str,[self._getExtrudersProperty(index,"dispensor_vac") for index in self._JoinSequence]))
        self.interval_list = " ".join(map(str,[self._getExtrudersProperty(index,"dispensor_int") for index in self._JoinSequence]))
        self.shot_power_list = " ".join(map(str,[self._getExtrudersProperty(index,"dispensor_shot_power") for index in self._JoinSequence]))
        self.vac_power_list = " ".join(map(str,[self._getExtrudersProperty(index,"dispensor_vac_power") for index in self._JoinSequence]))

        # UV 설정 - extruder에서 읽도록 바꿔야 함
        self.uv_per_layer_list = [0,0,0,0,0,0]
        self.uv_type_list = ['365','365','365','365','365','365']
        self.uv_time_list = [5,5,5,5,5,5]
        self.uv_dimming_list = [80,80,80,80,80,80]

        for index, uv_enable in enumerate(self.uv_enable_list):
            if uv_enable:
                self.uv_per_layer_list[index] = self._getExtrudersProperty(index,"uv_per_layers")
                self.uv_type_list[index] = self._getExtrudersProperty(index,"uv_type")
                self.uv_time_list[index] = self._getExtrudersProperty(index,"uv_time")
                self.uv_dimming_list[index] = self._getExtrudersProperty(index,"uv_dimming")

        # z좌표 관리
        self.layer_height_0 = self.getGlobalContainerStackProperty("layer_height_0")        
        self.InitialLayer0_C = -30
        self.InitialLayer0_Z = 0

        self.layer_height_list = " ".join(map(str,[self._getExtrudersProperty(index,"layer_height") for index in self._JoinSequence]))
        self.wall_thickness_list = " ".join(map(str,[self._getExtrudersProperty(index,"wall_thickness") for index in self._JoinSequence]))
        self.infill_sparse_density_list = " ".join(map(str,[self._getExtrudersProperty(index,"infill_sparse_density") for index in self._JoinSequence]))

    def _getExtrudersProperty(self, index, property):
        return self._global_container_stack.extruderList[index].getProperty(property,"value")

    def getGlobalContainerStackProperty(self, property):
        return self._global_container_stack.getProperty(property,"value")

    def getVariantName(self, index):
        variant = ''
        if index >= 0 and index < 6:
            variant = self._global_container_stack.extruderList[index].variant.getName()
        return variant
