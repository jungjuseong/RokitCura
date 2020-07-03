Rokit Cura
====
### ChangeLog
------------

- 2020.06.04.
96 well plate에 대한 gcode 파일 출력 구현
start code 정리, 재구조화
print 출력 순서 변경

- 2020.06.05.
설정 값(온도, uv, dispenser 등) 적용
실린지 선택 적용(미완)

- 2020.06.08.

- 2020.06.11.
Organ Regeneration --> Organ Regenerator
syringe 전체 적용과 syringe 각각 적용 구분
T 명령어 --> D 명령어 




### 미완성 기능
Dimming 설정 -- 명령어 생성이 안됨
Left first 기능
그림자 제거
print Temp. 범위 재설정 --> (-10 ~ 350)
G- code 필요없는 명령어 제거
* Build 플레이트 맡는 명령어 적용 및 재구조화


# GCodeWriter.py // End 코드 뒤에 SETTING 문자열
# Serialise the current container stack and put it at the end of the file. // 
    if not has_settings:
        settings = self._serialiseSettings(Application.getInstance().getGlobalContainerStack()
        stream.write(settings)

- 06.22
left syringe 이미지
초반의 익스트루더 b ,c위치 조절
spacing 코드 수정 c좌표로 **
axis control 뒤에 실린지 선택 설정 **
UV의 'layer주기'부분 수정
travel 속도 1200, 600 변경
M303, 디스펜서 명령어 실린지 순서 변경 ***
소수값에 정수부분 0 추가하기
로딩창 regenator로 이름 수정 
M301, M303 코드 적용 ****
uv start layer 항목 추가

# extruder_stack = self._global_container_stack.extruders.get(str(self._extruder_position))
# if not extruder_stack:
#     return
# nozzle_name = extruder_stack.variant.getName()

- 06.22
M301/M330 시퀀스 변경
start point (.0)처리**
G0 변질 문제 해결하기
E 명령어 --> 다른 표시로 변경
Z축을 C축으로 수정


- 06.27
# build volume 구별
# syringe 또는 fff, hot melt 구별
# 슬라이싱에 참여하는 노즐을 구별
# operation = GroupedOperation()
# node = SceneNode
# adfas = ExtruderManager.getInstance()
# active_extruder = node.callDecoration("getActiveExtruder")


<디스펜서 임시 디폴드 값>
M303 5 5 5 5 5 5
M304 0.3 0.3 0.3 0.3 0.3 0.3
M305 0 0 0 0 0 0
M306 90 90 90 90 90 90
M307 90 90 90 90 90 90
M308 30 30 30 30 30 30 30


# 슬라이스에 참여하는 익스트루더 active_extruder
# a = self._global_container_stack.extruderList[1].getId()
asdf = self._application.getMachineManager()
# asdf = self._application.getMachineManager().getInstance().getActiveExtruderStacks()
# asdf = self._application.getMachineManager().activeMachine
# asdh = self._application.getMachineManager().activeStack
# akjdl = self._application.getMachineActionManager()
# machine_nozzle_id = self._global_container_stack.extruderList[0].getMetaDataEntry("varient", "value")
# akjdl = self._application.getMachineManager().

# container_registry = ContainerRegistry.getInstance()
# my_metadata = container_registry.findContainersMetadata(id = "global_variant")[0]
# self.preferred_variant_name = my_metadata.get("preferred_variant_name", "")


1) Left or Right 노즐
2) 슬라이스에 참여하는 익스트루더
3) Left 노즐에서의 익스트루더 타입
4) 


# replaced += "G90 G0 X0.0 Y0.0\nG91 G0 X42.5 Y0.0\n"+ uv_command[0]+"; UV ON\nG4 P" + str(self._uv_time_list[0]*1000) + "\n" + uv_command[1] + "; UV OFF\nG90 G0 X0.0 Y0.0\n\n"
