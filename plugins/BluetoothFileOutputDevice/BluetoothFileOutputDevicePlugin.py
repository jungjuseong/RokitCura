# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Application import Application
from UM.OutputDevice.OutputDevicePlugin import OutputDevicePlugin
from UM.i18n import i18nCatalog
from .BluetoothFileOutputDevice import BluetoothFileOutputDevice

catalog = i18nCatalog("uranium")

class BluetoothFileOutputDevicePlugin(OutputDevicePlugin):
    """Implements an OutputDevicePlugin that provides a single instance of BluetoothFileOutputDevice"""

    def __init__(self):
        super().__init__()

        Application.getInstance().getPreferences().addPreference("bluetooth_file/last_used_type", "")
        Application.getInstance().getPreferences().addPreference("bluetooth_file/dialog_save_path", "")

    def start(self):
        self.getOutputDeviceManager().addOutputDevice(BluetoothFileOutputDevice())

    def stop(self):
        self.getOutputDeviceManager().removeOutputDevice("bluetooth_file")