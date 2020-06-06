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



# start code 
;(*** front of start-gcode for Rokit Healthcare ***)\n
M74 ; IO
{uv_on} ;M78 ; uv 
M176 ; mini comp
G21; set units to mm
G90; set positioning to absolute
{print_temp} ; include bed_temp
{shot_p} ; shot 압력
{vac_p} ; vac 압력
{interval} ; int(흡입 주기) 간격
G0 X0 Y0 Z0 A0. B0. C0.
G0 B0 ; 선택한 실린지 하강
{phys_slct_extruder} ; 물리적으로 익스트루더가 선택됨.
G0 B9. ; 선택한 실린지 하강
{select_extruder} ; 기계가 익스트루더를 인식함.(선택)
G0 C20 ; 실린지 묶음 하강
G92 E0 ;(Set E to 0 again) ; only fff
G0 Z10
;(*** back of start-gcode ***)



self._global_container_stack.getProperty("dispensor_shot","value")
self._global_container_stack.getProperty("dispensor_vac","value")


# end code
(**** start of end-gcode for Rokit Healthcare ****)
M73 P100 ;end progress
M104 T0 S0 ;extruder heater off
M140 S0 ;Turn-off bed
M75 ;IO dis 
M79 ; uv off
M177 ;comp off
;(*** end of end-gcode ***)