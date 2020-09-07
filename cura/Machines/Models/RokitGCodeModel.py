
class RokitGCodeModel():
    def __init__(self) -> None:
        self.GCODE = {
            'G90_G0_X_Y': 'G90 G0 X%.2f Y%.2f\n',
            'G90_G0_C_RESET': 'G90 G0 C-30.0\n',

            'G0': 'G0\n',
            'G0_Z': 'G0 Z%.2f\n',
            'G0_C0': 'G0 C0.00\n',
            'G0_C': 'G0 C{0: <10.2f}\n',
            'G0_C40': 'G0 C40.0\n',
            'G0_Z0': 'G0 Z0.00\n',
            'G0_Z40': 'G0 Z40.0\n',
            'G0_XY_ZERO': 'G0 X0.0 Y0.0\n',

            'G0_Z_RESET': 'G0 Z-40.0\n',
            'G0_X_Y': 'G0 X%.2f Y%.2f\n',
            
            'G91_G0_X_Y': 'G91 G0 X%.2f Y%.2f\n',
            'LEFT_G91_G0_X_Y': 'G55 X{left_x:.2f} Y{left_y:.2f}\n',
            'LEFT_G91_G0_X0_Y0': 'G55 X0.0 Y0.0\n',
            'RIGHT_G91_G0_X_Y': 'G54 X{right_x:.2f} Y{right_y:.2f}\n',
            'RIGHT_G91_G0_X0_Y0': 'G54 X0.0 Y0.0\n',

            'G92_X0_Y0': 'G92 X0.0 Y0.0\n',
            'G92_X_Y': 'G92 X%.2f Y%.2f\n',
            'G92_Z0': 'G92 Z0.0\n',
            'G92_E0': 'G92 E0.0\n',
            'G92_C0': 'G92 C0.0\n',

            'G0_X_Y': 'G0 X%.2f Y%.2f\n',
            'G0_A0_F600': 'G0 A0.00 F600\n',
            'G0_B0_F300': 'G0 B0.00 F300\n',
            'G0_A_F600': 'G0 A{a_axis:.2f} F600\n',

            'G0_B15_F300': 'G0 B15.0 F300\n',

            'M29_B': 'M29 B\n',
            'UV_A_Curing_Position': 'G59 X0.0 Y0.0\n',
            'UV_A_On': 'M172\n',
            'UV_Channel': 'M381 {uv_channel:d}\n',
            'UV_Dimming': 'M385 {uv_dimming:.1f}\n',
            'UV_Time': 'M386 {uv_time:.1f}\n',
            'TimerLED': 'M384\n',
            'P4_P': 'P4 P{uv_delay:d}\n',

            'UV_A_Off': 'M173\n',
            'UV_DisinfectionOn': 'M174\n',
            'UV_DisinfectionOff': 'M175\n',
            'UV_A_Position': 'G56 X0.0 Y0.0\n',

            'PRINT_TEMP': 'M308 %s',
            'WAIT_TEMP': 'M109',

            'SHOT': 'M303 %s',
            'VAC': 'M304 %s',
            'INT': 'M305 %s',
            'SET_P': 'M306 %s',
            'VAC_P': 'M307 %s',
            'StartShot': 'M301\n',
            'StopShot': 'M330\n'
        }
