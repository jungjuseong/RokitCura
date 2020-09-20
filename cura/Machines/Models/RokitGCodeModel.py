class RokitGCodeModel():
    def __init__(self) -> None:
        self.GCODE = {
            'G90_G0_X_Y': 'G90 G0 X%.3f Y%.3f\n',
            'G90_G0_C_RESET': 'G90 G0 C-30.0\n',
            'G90_G0_C': 'G90 G0 C{0: <.3f}\n',

            'G0': 'G0\n',
            'G0_Z': 'G0 Z%.3f\n',
            'G0_C0': 'G0 C0.00\n',
            'G0_C': 'G0 C{0: <.3f}\n',
            'G0_C30': 'G0 C30.0\n',
            'G0_Z0': 'G0 Z0.00\n',
            'G0_Z40': 'G0 Z40.0\n',
            'G0_Z40_C40_F420': 'G0 Z40.0 C40.0 F420\n',
            'G0_Z_RESET': 'G0 Z-40.0\n',
            
            'G1_F_E':'G1 F{f:d} E{e:<.3f} ;(Back Retraction)\n',

            'G54_X_Y': 'G54 X{x:<.3f} Y{y:<.3f} ;(HOTMELT/EXTRUDER)\n',
            'G55_X_Y': 'G55 X{x:<.3f} Y{y:<.3f} ;(ROTARY)\n',

            'G54_G0_X0_Y0': 'G54 G92 1 ;(HOTMELT/EXTRUDER)\nG0 X0.0 Y0.0\n',
            'G55_G0_X0_Y0_ROTARY': 'G55 G92 1 ;(ROTARY)\nG0 X0.0 Y0.0\n',
            'G56_G0_X0_Y0': 'G56 G92 1 ;(LOADING/UNLOADING, MICROSCOPE)\nG0 X0.0 Y0.0\n',
            'G57_G0_X0_Y0': 'G57 G92 1 ;(FORK SENSOR)\nG0 X0.0 Y0.0\n',

            'G55_G0_X0_Y0': 'G55 G92 1 ;(ORIGIN)\nG0 X0.0 Y0.0\n',
            'G59_G0_X0_Y0': 'G59 G92 1 ;(UV-A)\nG0 X0.0 Y0.0\n',

            'G92_X0_Y0': 'G92 X0.0 Y0.0\n',
            'G92_Z0': 'G92 Z0.0\n',
            'G92_E0': 'G92 E0.0\n',
            'G92_C0': 'G92 C0.0\n',

            'G0_A0_F600': 'G0 A0.00 F600\n',
            'G0_B0_F300': 'G0 B0.00 F300\n',
            'G0_A_F600': 'G0 A{a_axis:<.3f} F600\n',

            'G0_B15_F300': 'G0 B15.0 F300\n',

            'M29_B': 'M29 B\n',
            'M172': 'M172\n',
            'M381_CHANNEL': 'M381 {channel:d}\n',
            'M385_DIMMING': 'M385 {dimming:<.1f}\n',
            'M386_TIME': 'M386 {time:<.1f}\n',
            'M384': 'M384\n',
            'P4_DURATION': 'P4 P{duration:d}\n',

            'M173': 'M173\n',
            'M174': 'M174\n',
            'M175': 'M175\n',
            'G56_G0_X0_Y0': 'G56 G0 X0.0 Y0.0\n',

            'PRINT_TEMP': 'M308 %s',
            'WAIT_TEMP': 'M109',

            'SHOT': 'M303 %s',
            'VAC': 'M304 %s',
            'INT': 'M305 %s',
            'SET_P': 'M306 %s',
            'VAC_P': 'M307 %s',
            'M301': 'M301\n',
            'M330': 'M330\n'
        }