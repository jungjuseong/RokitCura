// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.3

import UM 1.3 as UM
import Cura 1.0 as Cura

Item
{
    property string enabledText: catalog.i18nc("@label:Should be short", "On")
    property string disabledText: catalog.i18nc("@label:Should be short", "Off")

    Cura.IconWithText
    {
        source: UM.Theme.getImage("stage_mark")
        text: catalog.i18nc("@label", "Layers")

        font: UM.Theme.getFont("medium")
        elide: Text.ElideMiddle

        UM.SettingPropertyProvider
        {
            id: rokit_generic
            containerStack: Cura.MachineManager.activeStack
            key: "rokit_generic"
            watchedProperties: ["value"]
        }
    }
}