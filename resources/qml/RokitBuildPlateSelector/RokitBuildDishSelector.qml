// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 2.3

import UM 1.2 as UM
import Cura 1.0 as Cura

Cura.ExpandablePopup {
    id: buildPlateSelector

    contentPadding: UM.Theme.getSize("default_lining").width
    contentAlignment: Cura.ExpandablePopup.ContentAlignment.AlignLeft

    UM.I18nCatalog {id: catalog;  name: "cura" }

    headerItem: Cura.IconWithText {
        text: "Build Plate"
        source: UM.Theme.getIcon("buildplate")
        font: UM.Theme.getFont("medium")
        iconColor: UM.Theme.getColor("machine_selector_printer_icon")
        iconSize: source != "" ? UM.Theme.getSize("machine_selector_icon").width: 0
    }

    contentItem: RokitBuildDishSetup {
        anchors.left: parent.left
        anchors.top: parent.top
    }
}
