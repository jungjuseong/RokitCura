// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 2.3 as Controls2
import QtQuick.Controls 2.0
import QtQuick.Controls 1.1 as OldControls
import UM 1.2 as UM
import Cura 1.0 as Cura
import QtQuick.Layouts 1.3

import "../../Widgets"
import "./model"

Item {
    id: base

    anchors.fill: parent
    UM.I18nCatalog { id: catalog; name: "cura" }

    property var extrudersModel: Cura.ExtrudersModel {}
    
    property var dishModel: []
    property var category: "####"

    //{"product_id": "96", "shape": "elliptic", "volume": QVector3D(6.5, 6.5, 10.8)}

    Item {
        id: buildPlate
        
        height: UM.Theme.getSize("rokit_build_plate_content_widget").height
        anchors {
            left: parent.left
            right: parent.right
        } 
        
        Text {
            id: title
            anchors {
                bottom: selectDish.top
                left: parent.left
                leftMargin: UM.Theme.getSize("default_margin").width
                bottomMargin: UM.Theme.getSize("default_margin").width
            }
            text: catalog.i18nc("@label", "Product No.") 
            font: UM.Theme.getFont("medium")
            width: base.width / 3
        }

        OldControls.ToolButton {
            id: selectDish
            text: buildDishType.properties.value
            tooltip: text
            height: parent.height
            width: parent.width
            style: UM.Theme.styles.print_setup_header_button
            activeFocusOnPress: true
            menu: Cura.RokitBuildDishMenu {  }
        }
        
        // "Build dish type"
        UM.SettingPropertyProvider {
            id: buildDishType
            containerStack: Cura.MachineManager.activeMachine
            key: "machine_build_dish_type"
            watchedProperties: [ "value" ]
            storeIndex: 0
        }
    }
}