// Copyright (c) 2019 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.6
import QtQuick.Controls 2.0

import Cura 1.0 as Cura
import UM 1.3 as UM

Label {
    property string name: "Label"

    text: name
    verticalAlignment: Text.AlignVCenter
    font: base.labelFont
    color: UM.Theme.getColor("text")
    height: parent.height
    width: base.textWidth
    renderType: Text.NativeRendering
}