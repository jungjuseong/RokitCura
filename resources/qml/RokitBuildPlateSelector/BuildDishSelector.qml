// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 1.1 as OldControls

import QtQuick.Layouts 1.1

import UM 1.2 as UM
import Cura 1.0 as Cura

Item {
    id: base

    Cura.RokitBuildDishMenu {
        id: wellPlateMenu
        category: "Well Plate"
    }

    Cura.RokitBuildDishMenu {
        id: cultureDishMenu
        category: "Culture Dish"
    }

    Cura.RokitBuildDishMenu {
        id: cultureSlideMenu
        category: "Culture Slide"
    }

    property string category: ""

    UM.I18nCatalog { id: catalog; name: "cura" }

    anchors.fill: parent
    anchors.top : parent.top
    width: parent.width

    DishPreview {
        id: preview
    }

    OldControls.ToolButton {
        id: toolButton
        anchors.top: preview.bottom
        anchors.topMargin: UM.Theme.getSize("thick_margin").height * 2

        text: buildDishType.properties.value
        tooltip: text
        height: UM.Theme.getSize("rokit_build_plate_content_widget").height
        width: parent.width
        style: UM.Theme.styles.print_setup_header_button
        activeFocusOnPress: true
        menu: {
            if (category === "Well Plate")
                return wellPlateMenu
            if (category === "Culture Slide")
                return cultureSlideMenu
            if (category === "Culture Dish")
                return cultureDishMenu
        }
    }

    UM.SettingPropertyProvider {
        id: buildDishType
        containerStack: Cura.MachineManager.activeMachine
        key: "machine_build_dish_type"
        watchedProperties: [ "value" ]
        storeIndex: 0
    }
}