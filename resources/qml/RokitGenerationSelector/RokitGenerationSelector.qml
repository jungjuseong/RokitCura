// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 2.0

import UM 1.3 as UM
import Cura 1.0 as Cura

Cura.ExpandablePopup // 팝업 형태로 변경
{
    id: rokitGenerationSelector

    //dragPreferencesNamePrefix: "view/settings"

    //property bool preSlicedData: PrintInformation !== null && PrintInformation.preSliced

    contentPadding: UM.Theme.getSize("default_lining").width
    //contentHeaderTitle: catalog.i18nc("@label", "Generation")
    enabled: !preSlicedData

    UM.I18nCatalog
    {
        id: catalog
        name: "cura"
    }

    headerItem: Cura.IconWithText
    {
        text: "Generation"
        source: UM.Theme.getIcon("printer_single")
        font: UM.Theme.getFont("medium")
        iconColor: UM.Theme.getColor("machine_selector_printer_icon")
        iconSize: source != "" ? UM.Theme.getSize("machine_selector_icon").width: 0
    }

    property var extrudersModel: CuraApplication.getExtrudersModel()

    contentItem: RokitGenerationContents {}

    onExpandedChanged: UM.Preferences.setValue("view/settings_visible", expanded)
    Component.onCompleted: expanded = UM.Preferences.getValue("view/settings_visible")
}
