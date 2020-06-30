# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Application import Application
from UM.OutputDevice.OutputDevicePlugin import OutputDevicePlugin
from UM.i18n import i18nCatalog
from .FourDConvertOuputDevice import FourDConvertOuputDevice

catalog = i18nCatalog("uranium")

class FourDConvertOuputDevicePlugin(OutputDevicePlugin):
    """Implements an OutputDevicePlugin that provides a single instance of FourDConvertOuputDevice"""

    def __init__(self):
        super().__init__()

        Application.getInstance().getPreferences().addPreference("four_d_converter/last_used_type", "")
        Application.getInstance().getPreferences().addPreference("four_d_converter/dialog_save_path", "")

    def start(self):
        self.getOutputDeviceManager().addOutputDevice(FourDConvertOuputDevice())

    def stop(self):
        """Implements an OutputDevicePlugi"""
        self.getOutputDeviceManager().removeOutputDevice("four_d_file")