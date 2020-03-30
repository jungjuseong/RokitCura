// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 2.3

import UM 1.2 as UM
import Cura 1.0 as Cura

import "RokitBuildVolumeContents"

Cura.ExpandablePopup
{
    id: buildPlateSelector

    contentPadding: UM.Theme.getSize("default_lining").width
    contentAlignment: Cura.ExpandablePopup.ContentAlignment.AlignLeft
    // width: UM.Theme.getSize("rokit_buildvolume_setup_widget").width - 2 * UM.Theme.getSize("default_margin").width

    UM.I18nCatalog
    {
        id: catalog
        name: "cura"
    }

    headerItem: Cura.IconWithText
    {
        text: "Build Plate"
        source: UM.Theme.getIcon("printer_single")
        font: UM.Theme.getFont("medium")
        iconColor: UM.Theme.getColor("machine_selector_printer_icon")
        iconSize: source != "" ? UM.Theme.getSize("machine_selector_icon").width: 0
    }

    contentItem: RokitBuildVolumeSetup
    {
        id: rokitBuildVolumeSetup
        anchors
        {
            left: parent.left
            //right: parent.right
            top: parent.top
        }
        visible: true
    }

    // 임의 설정 창
    //contentItem: RokitBuildVolumeSetting
    // {
    //     id: rokitBuildVolumeSetting
    //     anchors
    //     {
    //         left: parent.left
    //         right: parent.right
    //         top: rokitBuildVolumeSetup.bottom
    //         topMargin: UM.Theme.getSize("wide_margin").width
    //     }
    // }

// <<<<<<< HEAD:resources/qml/RokitBuildVolumeSelector/RokitBuildVolumeSelector.qml
//     =======
//     contentItem: RokitBuildPlateSetting
//     {
//         id: rokitBuildPlateSetting
// >>>>>>> a6436bd61c80abb34610fba17c988c661ab5390d:resources/qml/RokitBuildPlateSelector/RokitBuildPlateSelector.qml

}
