## Invivo-4d6 GCode

* D1~D6: channel 선택
* M300 - status 읽기
* M301 - steady shot RUN
* M302 - time shot RUN
* M330 - shot stop
* G4 P4000 - 4sec delay


    G01 Z${coord.z - 8}.
    G04 P1000
    M301
    G04 P2000 
    M330
    G04 P500
    G01 Z${coord.z}.
    G01 X${coord.x} Y${coord.y} Z${coord.z} F700
    G01 A0.
    G01 B2.\n`
    
* G0 -> G1
* G1 - Coordinated Movement X Y Z E
* G2 - CW ARC
* G3 - CCW ARC
* G5 - MOVE ALL EXTRUDER (3 노즐의 경우 한번에 모든 extruder 동작용)
* G10 - retract filament according to setting of M207
* G11 - retract recover according to setting of M208
* G28 - Home all Axis

* G29 - Detailed Z-Probe, probes the bed at 3 or more points.
* G30 - Single Z Probe, probes bed at current XY location. : TODO
* G31 - Z축 Home을 오토레벨링 센서로 감지
* G32 - Z축 Home을 포토센서로 감지
* G90 - Use Absolute Coordinates
* G91 - Use Relative Coordinates
* G92 - Set current position to coordinates given
* G95 - 버퍼에 있는 모든 모션 동작을 다할때까지 대기

* M17 - Enable/Power all stepper motors
* M18 - Disable all stepper motors power

* M73 - Set the percent of printing
* M104 - Set extruder target temp
* M105 - Read current temp

* M106 - Fan 1..10 on (UV Cure-Led)
* M107 - Fan 1..10 off

* M109 - Wait for extruder current temp to reach target temp.
* M110 - Set Current Line Number TODO
* M111 - Set Debug level.

* M114 - Display current position in mm
* M115 - Capabilities string
* M119 - Show Endstop State : Min [X/Y/Z] [hited/open-chain]
* M140 - Set bed target temp
* M150 - Set Led light output, R<0~255>, G<0~255>, B<0~255>
  Fan_4, Fan_5, Fan_6
* M190 - Wait for bed current temp to reach target temp.

### Custom M Codes

* M20 - List SD files
* M21 - Init SD CARD : SDCARD AND USB MEMORY
* M22 - Release sd card
* M23 - select sd file - 미구현
* M24 - start/resume sd print - 미구현
* M25 - pause sd print - 미구현
* M26 - set sd position in bytes - 미구현
* M27 - report sd print status - 미구현
* M28 - begin write to sd file - 미구현
* M29 - stop writing sd file - 미구현
* M30 - Delete a file on the sd card or memory

* M80 - 출력시작전에 보내는 코드로, 출력중 파라미터 초기화 세팅

* M82 - Set E codes absolute (default)
* M83 - Set E codes relative while in Absolute Coordinates (G90) mode

* M84 - Disable steppers until next move,
* M84 -> blocking quit
* M84 S0 -> quit immediately - 출력 취소 또는 종료시 호출

* M85 - Set inactivity shutdown timer with parameter S<seconds>. 미구현

* M98 - set backslash for motor
* M92 - Set axis_steps_per_unit - same syntax as G92
* M93 - Send axis_steps_per_unit

* M176 - Fan 3 on
* M177 - Fan 3 off

* M200 - Set filament diameter ans set E axis units to cubic millimeters  미구현

* M201 - Set maximum acceleration in units/s^2 for print moves (M201 X1000 Y1000 Z100
E2000)
* M203 - Set maximum feedrate that your machine can sustain (M203 X200 Y200 Z300
E10000) in mm/sec
* M204 - Set default acceleration: S normal moves T filament only moves
 (M204 S3000 T7000) in mm/sec^2
* M205 - advanced settings: minimum travel speed S=while printing T=travel only,
 X=maximum xy jerk, Z=maximum Z jerk
* M206 - set additional homing offset

* M207 - Set retract length S[positive mm] F[feedrate mm/s] Z[addition zlift/hop],
 stays in mm regardless of M200 setting.
* M208 - Set recover/unretract length S[positive mm] F[feedrate mm/s].
* M209 - Enable automatic retract detect if the slicer did not support G10/G11, TODO
 - every normal extrude-only move will be classified as retract depending on the
direction.
*
* M210 - Set Homing Feedrate mm/min Xnnn Ynnn Znnn
* M218 - Set hotend offset in mm: T<extruder num> X<offset_on_x> Y<offset_on_y> TODO

* M220 - set speed factor override percentage S=factor in percent
* M221 - set extruder multiply factor S100 --> original Extrude Speed TODO
* M280 - Set servo position absolute. P: servo index, S: angle or microseconds. TODO

Note: M301, M303, M304 applies to currently selected extruder. Use T0 or T1 to
select.

* M301 - Set Heater parameters P, I, D, S (slope), B (y-intercept), W (maximum pwm)
* M303 - PID relay autotune S<temperature> sets the target temperature.
  (default target temperature = 150C) TODO
* M304 - Set Heater parameters P, I, D, S (slope), B (y-intercept), W (maximum pwm)

* M400 - Finish all moves
* M401 - Lower Z-probe for servo
* M402 - Raise Z-probe for servo
* M404 - Filament width TODO - 미구현
* M405 - Filament sensor on TODO - 미구현 - 다른데서 구현
* M406 - Filament sensor off TODO - 미구현 - 다른데서 구현
* M407 - Display filament diameter TODO - 미구현

* M500 - stores paramters in EEPROM
* M501 - reads parameters from EEPROM(if you need to reset them after you changed them temporarily).
* M502 - reverts to the default "factory settings". You still need to store them in EEPROM afterwards if you want to.
* M503 - Print settings currently in memory
* M504 - upgrade pru.bin firmware : 온도커브, 모션콘트롤
* M505 - Save Parameters to SD-Card : 미구현

* M510 - Invert axis, 0=false, 1=true (M510 X0 Y0 Z0 E1)
* M520 - Set maximum print area (M520 X200 Y200 Z150)

* M521 - Disable axis when unused (M520 X0 Y0 Z1 E0)
* M522 - Use software endstops I=min, A=max, 0=false, 1=true (M522 I0 A1)
* M523 - Enable min endstop input 1=true, -1=false (M523 X1 Y1 Z1)
* M524 - Enable max endstop input 1=true, -1=false (M524 X-1 Y-1 Z-1)
* M525 - Set homing direction 1=+, -1=- (M525 X-1 Y-1 Z-1)
* M526 - Invert endstop inputs 0=false, 1=true (M526 X0 Y0 Z0)

* M600 - Printing pause
* M601 - Printing resume
* M602 - load/unload filament (load/unload ,speed/length)

* M906 - Set motor current (mA)
 (M906 X1000 Y1000 Z1000 E1000 B1000) or set all (M906 S1000)
* M907 - Set motor current (raw)
 (M907 X128 Y128 Z128 E128 B128) or set all (M907 S128)

* M908 - Set feedrate multiply (M908 S200)
* M909 - has heat bed platform  S1 -> Yes, S0 -> No
* M910 - finish sending parameters
* M911 - Whether enable auto current adjust or not, S1 -> enable, S0 -> disable
* M912 - Whether enable auto slow down or not, S1 -> enable, S0 -> disable
* M913 - Machine type: S0 -> xyz, S1 -> delta, S2 -> corexy
* M914 - Set servo endstop angle, M914 S0 E90

* M1000 - Turn on/off relay1/relay2
* M1001 - Read Status(Value) of GPIO : Door ,Filament, Relay1, Relay2
* M1002 - Set Enable/Disable For Door_dection_Enable
* M1003 - Set Enable/Disable for Filament_Enable/Autoleveling_Enable
* M1004 - Read Status : Door_dection_Enable, Filament_Enable, Autoleveling_Enable
* M1009 - Read or Set for GPIO (M1009 G10 O1 L1 S1)
* M1010 - Ignore Z-EndStop
* M1012 - Trun On UV-LED (M1012 P0) -> M106으로 대체됨
* M1015 - Set Enable/Disable for retraction when cancelling (speed, length)
* M970 - Reset on software
* M972 - set time for realtime-clock
* M980 - Functions for NFC.. 현재 구현중

* T - Select Extruder : T0 T1 T2