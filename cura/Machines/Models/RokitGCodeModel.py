class RokitGCodeModel():
    def __init__(self) -> None:
        self.GCODE = {
            'G0_C30': 'G0 C30.0\n',
            'G0_Z40_C30_F420': 'G0 Z40.0 C30.0 F420\n',
            'G0_X_Y': 'G0 X%.3f Y%.3f\n',
            
            'G54_G0_X0_Y0': 'G54 G0 X0.0 Y0.0 ;(HOTMELT/EXTRUDER)\n',
            'G55_G0_X0_Y0': 'G55 G0 X0.0 Y0.0 ;(ROTARY)\n',
            'G56_G0_X0_Y0': 'G56 G0 X0.0 Y0.0 ;(LOADING/UNLOADING, MICROSCOPE)\n',
            'G57_G0_X0_Y0': 'G57 G0 X0.0 Y0.0 ;(FORK SENSOR)\n',
            'G58_G0_X0_Y0': 'G55 G0 X0.0 Y0.0 ;(ORIGIN)\n',
            'G59_G0_X0_Y0': 'G59 G0 X0.0 Y0.0 ;(UV-A)\n',

            'G92_X0_Y0': 'G92 X0.0 Y0.0\n', 
            'G92_E0': 'G92 E0.0\n',

            'G0_A_F600': 'G0 A{a_axis:<.3f} F600\n',
            'G0_B15_F300': 'G0 B15.0 F300 ;(ADD)\n',

            'M29_B': 'M29 B\n',
            'M172': 'M172\n',
            'M381_CHANNEL': 'M381 {channel:d}\n',
            'M385_DIMMING': 'M385 {dimming:<.1f}\n',
            'M386_TIME': 'M386 {time:<.1f}\n',
            'M384': 'M384\n',
            'G4_DURATION': 'G4 P{duration:d}\n',

            'M173': 'M173\n',
            'M174': 'M174\n',
            'M175': 'M175\n',

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