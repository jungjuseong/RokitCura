// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 1.1 as OldControls

import UM 1.3 as UM
import Cura 1.6 as Cura
import QtQuick.Layouts 1.3

Item {
    height: UM.Theme.getSize("rokit_build_plate_setting_widget").height + 2 * padding
    width: UM.Theme.getSize("rokit_build_plate_setting_widget").width - 2 * UM.Theme.getSize("wide_margin").width
    
    property real padding: UM.Theme.getSize("thick_margin").width
    property real sidePadding: UM.Theme.getSize("thin_margin").width

    property string tabName: ""

    Item {
        id: tabSpace

        UM.I18nCatalog { id: catalog; name: "cura" }
        anchors {
            top: parent.top
            left: parent.left
            leftMargin: parent.sidePadding
            right: parent.right
            rightMargin: parent.sidePadding
        }
        height: childrenRect.height  
        
        Label {
            id: buildPlateTitle
            anchors{
                top: parent.top
                topMargin: UM.Theme.getSize("default_margin").height
                left: parent.left
            } 
            height: contentHeight
            text: "Build Plate Settings"
            font: UM.Theme.getFont("medium")
            color: UM.Theme.getColor("small_button_text")
            renderType: Text.NativeRendering
            elide: Text.ElideRight
            verticalAlignment: Text.AlignVCenter
        }

        UM.TabRow {
            id: tabBar

            anchors {
                top: buildPlateTitle.bottom
                topMargin: UM.Theme.getSize("default_margin").width
                left: parent.left
                right: parent.right
            }
            Repeater {
                model: ListModel {
                    ListElement { name: "Culture Dish" }
                    ListElement { name: "Well Plate" }
                    ListElement { name: "Culture Slide" }
                }                
                delegate: UM.TabRowButton {
                    Text {
                        text: catalog.i18nc("@label", name)
                        anchors.centerIn: parent
                    }
                    onClicked: { 
                        tabName = name
                        toolButton.category = name
                    }       
                }

            }            
        }        
        Rectangle {
            id: borderLine
            anchors {
                top: tabBar.bottom
                topMargin: -UM.Theme.getSize("default_lining").width
                left: parent.left
                leftMargin: parent.sidePadding
                right: parent.right
                rightMargin: parent.sidePadding
            }
            z: tabBar.z - 1

            border.color: UM.Theme.getColor("lining")
            border.width: UM.Theme.getSize("default_lining").width
            width: parent.width
            height: UM.Theme.getSize("rokit_build_plate_content").height 
        } 
    }
        
    Item {
        id: buildDishSelector
        
        RokitBuildDishMenu {
            id: wellPlateMenu
            category: "Well Plate"
        }

        RokitBuildDishMenu {
            id: cultureDishMenu
            category: "Culture Dish"
        }

        RokitBuildDishMenu {
            id: cultureSlideMenu
            category: "Culture Slide"
        }

        anchors.fill: parent
        anchors.top : parent.top
        width: parent.width

        DishPreview {
            id: preview
            product_id: (buildDishType.properties.value !== undefined) ? buildDishType.properties.value : ""
        }

        OldControls.ToolButton {
            id: toolButton

            property string category: (buildDishType.properties.value !== undefined) ? buildDishType.properties.value.split(":")[0] : ""
            anchors.top: preview.bottom
            anchors.left: preview.left
            anchors.topMargin: UM.Theme.getSize("thick_margin").height * 2
            anchors.leftMargin: UM.Theme.getSize("thick_margin").width

            text: (buildDishType.properties.value !== undefined) ? buildDishType.properties.value : ""
            tooltip: text
            height: UM.Theme.getSize("rokit_build_plate_content_widget").height
            width: parent.width / 2
            style: UM.Theme.styles.print_setup_header_button
            activeFocusOnPress: true
            
            menu: {
                if (category === "Well Plate")
                    return wellPlateMenu
                else if (category === "Culture Slide")
                    return cultureSlideMenu
                else if (category === "Culture Dish")
                    return cultureDishMenu
                
                return wellPlateMenu
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
              
}
