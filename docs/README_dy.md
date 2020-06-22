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




# start code 
;(*** front of start-gcode for Rokit Healthcare ***)\n
M72 ; Motor enable 
M74 ;  Enabel IO 
M78 ; LED Light ON 
M176 ; Comp ON 
G21 ; Set unit to mm 
; Axis Home
M29 Y
M29 X
M29 Z
M29 C
M29 A
G78 B50.
M29 B
// G90
M311 ; Get shot time
M321 ; Get vaccum time
M313 ; Get interval time
M314 ; Get shot pressure
M315 ; Get vaccum pressure

M316 ; Get real temp
M317 ; Get set temp
M318 ; Get PID value
M319 ; Get toggle temp
G92 E0 ; Set E to 0 only FFF

; (1, 2, 3, 4, 5, EX, BED)
M303 0 0 0 0 0 0 ; Set shot time
M304 0 0 0 0 0 0 ; Set vaccum time
M305 0 0 0 0 0 0 ; Set interval time
M306 0 0 0 0 0 0 ; Set shot pressure
M307 0 0 0 0 0 0 ; Set vaccum pressure
M308 0 0 0 0 0 0 0 ; Set temp
M309 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ; Set PID value

M310 5 ; Set toggle level

M316 ; Get real temp 
; (M190 0 0 0 0 0 0 0 Wait for set temp)

; (G54 G00 X0. Y0. Z0. Set positioning to absolute right printing zone)
; (G55 G00 X0. Y0. Z0. Set positioning to absolute left printing zone)
;(*** back of start-gcode ***)


# end code
(**** start of end-gcode for Rokit Healthcare ****)
M73 P100 ;end progress
M104 T0 S0 ;extruder heater off
M140 S0 ;Turn-off bed
M75 ;IO dis 
M79 ; uv off
M177 ;comp off
;(*** end of end-gcode ***)