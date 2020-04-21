// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4

import UM 1.3 as UM
import Cura 1.6 as Cura
import QtQuick.Layouts 1.3

import "./Contents"
import "../Widgets"

Item
{
    // 창 임시 면적 값
    height: UM.Theme.getSize("rokit_build_plate_setting_widget").height + 2 * padding
    width: UM.Theme.getSize("rokit_build_plate_setting_widget").width - 2 * UM.Theme.getSize("wide_margin").width
    
    property Action configureSettings
    property real padding: UM.Theme.getSize("thick_margin").width
    property real sidePadding: UM.Theme.getSize("thin_margin").width

    // TODO
    property real firstColumnWidth: Math.round(width / 3)

    // 1
    property string tooltipText: machineShape.properties.description

    // callback functions
    property var forceUpdateOnChangeFunction: dummy_func
    property var afterOnEditingFinishedFunction: dummy_func
    property var setValueFunction: null

    // a dummy function for default property values
    function dummy_func() {}

    // 2
    UM.I18nCatalog { id: catalog; name: "cura" }

    property int propertyStoreIndex: manager ? manager.storeContainerIndex : 1  // definition_changes
    property string machineStackId: Cura.MachineManager.activeMachine.id
    property var forceUpdateFunction: manager.forceUpdate

    property int choosing: 0    // 선택하는 탭
    property int resetPlateModel: 0    

    Item {
        id: tabSpace

        anchors{
            top: parent.top
            left: parent.left
            leftMargin: parent.sidePadding
            right: parent.right
            rightMargin: parent.sidePadding
        }
        height: childrenRect.height  
        
        Label   // Title Label
        {
            id: buildPlateTitle
            anchors{
                top: parent.top
                topMargin: UM.Theme.getSize("default_margin").height
                left: parent.left
            } 
            height: contentHeight
            text: catalog.i18nc("@header", "Build Plate Settings")// + resetPlateModel)
            font: UM.Theme.getFont("medium")
            color: UM.Theme.getColor("small_button_text")
            renderType: Text.NativeRendering
            elide: Text.ElideRight
            verticalAlignment: Text.AlignVCenter
        }

        Text{
            id: machineShapeView
            anchors{
                right: parent.right
                verticalCenter: buildPlateTitle.verticalCenter
            }
            font: UM.Theme.getFont("medium")
            text: qsTr(buildPlateType.properties.value)//+ ", "+ plateIndex)
        }

        UM.TabRow
        {
            id: tabBar
            visible: true

            anchors
            {
                top: buildPlateTitle.bottom
                topMargin: UM.Theme.getSize("default_margin").width
                left: parent.left
                right: parent.right
            }
            Repeater
            {
                id: repeater
                model: ListModel
                {
                    id : buildModel
                    ListElement{
                        name: "Culture dish"
                        value: "elliptic"
                        number: 0
                    }
                    ListElement{
                        name: "Well plate"
                        value: "elliptic"
                        number: 1
                    }
                    ListElement{
                        name: "Culture slide"
                        value: "rectangular"
                        number: 2
                    }
                }
                delegate: UM.TabRowButton
                {
                    Text{
                        text: catalog.i18nc("@label", name) // -culture slide
                        anchors.centerIn: parent
                    }
                    onClicked: // Buil Plate 타입 설정
                    {
                        choosing = number;

                    }       
                }
            }            
        }

        // 틀 
        Rectangle
        {
            id: borderLine
            anchors 
            {
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
            height: UM.Theme.getSize("rokit_build_plate_content").height // 수정 필요
        } 
    }

    // 메인 컨텐츠
    Row {

        spacing: UM.Theme.getSize("thick_margin").height // edit
        
        anchors
        {
            left: parent.left
            right: parent.right
            top: parent.top
            bottom : parent.bottom //edit --------
            margins: parent.padding
        }
         
        CultureDishSelector // culture Dish
        {
            id: cultureDishSelector
            visible: choosing === 0 
            anchors.top : parent.top
            width: parent.width
            // TODO Create a reusable component with these properties to not define them separately for each component
            labelColumnWidth: parent.firstColumnWidth
        }
        
        WellPlateSelector // well Plate
        {
            id: wellPlateSelector
            visible: choosing === 1 
            anchors.top : parent.top
            width: parent.width
            // TODO Create a reusable component with these properties to not define them separately for each component
            labelColumnWidth: parent.firstColumnWidth
        }   

        CultureSlideSelector // culture Slide
        {
            id: cultureSlideSelector
            visible: choosing === 2 
            anchors.top : parent.top
            width: parent.width
            // TODO Create a reusable component with these properties to not define them separately for each component
            labelColumnWidth: parent.firstColumnWidth        
        }            
    }
    // SupportSelector
    // InfillDensitySelector

    UM.SettingPropertyProvider
    {
        id: machineShape
        containerStack: Cura.MachineManager.activeMachine
        key: "machine_shape"
        watchedProperties: [ "value", "options", "description" ]
        storeIndex: propertyStoreIndex
        // storeIndex: 0
    }

    // "Origin at center"
    UM.SettingPropertyProvider  
    {
        id: originAtCenter
        containerStack: Cura.MachineManager.activeMachine
        key: "machine_center_is_zero"
        watchedProperties: [ "value" ]
        storeIndex: propertyStoreIndex
    }

    // "Build plate type"
    UM.SettingPropertyProvider  
    {
        id: buildPlateType
        containerStack: Cura.MachineManager.activeMachine
        key: "build_plate_type"
        watchedProperties: [ "value", "options" ]
        storeIndex: propertyStoreIndex
    }
}
