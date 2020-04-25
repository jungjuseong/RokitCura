// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 2.3 as Controls2

import UM 1.2 as UM
import Cura 1.0 as Cura
import QtQuick.Layouts 1.3

import "../../Widgets"
import "./model"

BuildPlateSelector {
      
    Rectangle {
        width: UM.Theme.getSize("rokit_culture_slide").width
        height : UM.Theme.getSize("rokit_culture_slide").height
        anchors {
            centerIn: parent
        }
        color: UM.Theme.getColor("rokit_build_plate")
        border.width : 1
        border.color: UM.Theme.getColor("rokit_build_plate_border")
    }
    dishModel: CultureSlideModel {}
}
