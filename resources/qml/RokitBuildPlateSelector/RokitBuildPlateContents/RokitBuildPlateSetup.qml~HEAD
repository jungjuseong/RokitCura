// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4

import UM 1.2 as UM
import Cura 1.0 as Cura

//
import UM 1.3 as UM
import Cura 1.6 as Cura
import ".."

import QtQuick.Layouts 1.3

// 중요 요소
import "../../Widgets"

Item
{
    id: preparingSetup

    // 창 임시 면적 값
    height: UM.Theme.getSize("rokit_build_plate_setting_widget").height + 2 * padding
    width: UM.Theme.getSize("rokit_build_plate_setting_widget").width - 2 * UM.Theme.getSize("wide_margin").width
    
    property Action configureSettings

    property real padding: UM.Theme.getSize("thick_margin").width

    // TODO
    property real firstColumnWidth: Math.round(width / 3)

    property int choosing: 0    // 선택하는 탭

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

    Item{
        id: tabSpace

        anchors{
            top: parent.top
            left: parent.left
            leftMargin: parent.padding
            right: parent.right
            rightMargin: parent.padding
        }
        //height: UM.Theme.getSize("print_setup_big_item").height
        height: childrenRect.height   

        Label   // Title Label
        {
            id: buildPlateTitle
            anchors{
                top: parent.top
                left: parent.left
            } 

            text: catalog.i18nc("@title:label", "Build Plate Settings")
            font: UM.Theme.getFont("medium_bold")
            color: UM.Theme.getColor("text")
            renderType: Text.NativeRendering
            width: parent.width
            elide: Text.ElideRight
        }

        UM.TabRow
        {
            id: tabBar

            visible: true  

            anchors
            {
                top: buildPlateTitle.bottom
                topMargin: UM.Theme.getSize("wide_margin").width
                left: parent.left
                right: parent.right
            }

            // currentIndex: 
            // {
            //     var currentValue = machineShape.properties.value
            //     var index = 0
            //     for (var i = 0; i < model.count; i++)
            //     {
            //         if (model.get(i).value == currentValue)
            //         {
            //             index = i
            //             break
            //         }
            //     }
            //     return index
            // } 

            Repeater
            {
                id: repeater
                model: ListModel
                {
                    id : buildModel
                    ListElement{
                        name: "Culture dish"
                        value: "elliptic"
                        index: 0
                        toCenter: 'true'
                    }
                    ListElement{
                        name: "Well plate"
                        value: "elliptic"
                        index: 1
                        toCenter: 'true'
                    }
                    ListElement{
                        name: "Culture slide"
                        value: "rectangular"
                        index: 2
                        toCenter: 'false'
                    }
                }
                delegate: UM.TabRowButton
                {
                    Text{
                        text: catalog.i18nc("@label", name) // -culture slide
                        anchors.centerIn: parent
                    }

                    onClicked:
                    {
                        choosing = index;
                        
                        // var newValue = value 
                        // if (machineShape.properties.value != newValue)
                        // {
                        //     if (setValueFunction !== null)
                        //     {
                        //         setValueFunction(newValue)
                        //     }
                        //     else
                        //     {
                        //         machineShape.setPropertyValue("value", newValue)//newValue)
                        //         originAtCenter.setPropertyValue("value", toCenter)     
                        //     }
                        //     forceUpdateOnChangeFunction()
                        //     afterOnEditingFinishedFunction()
                        // }
                    }       
                    // default is center
                }
            }            
            // // binding
            // Binding
            // {
            //     target: supportExtruderCombobox
            //     property: "currentIndex"
            //     value: supportExtruderCombobox.getIndexByPosition(machineShape.properties.value)
            //     // Sometimes when the value is already changed, the model is still being built.
            //     // The when clause ensures that the current index is not updated when this happens.
            //     when: supportExtruderCombobox.model.count > 0
            // }
        }
    }

    // line
    Rectangle
    {
        id: separatorLine
        anchors{
            top: tabBar.bottom
            topMargin: UM.Theme.getSize("thick_margin")
        }
        width: parent.width
        height: UM.Theme.getSize("default_lining").width
        color: UM.Theme.getColor("lining")
    } 

    // 메인 컨텐츠
    Row{

        spacing: UM.Theme.getSize("thick_margin").height // edit
        
        anchors
        {
            left: parent.left
            right: parent.right
            top: separatorLine.bottom
            bottom : parent.bottom //edit --------
            margins: parent.padding
        }
         
        CultureDishSelector // culture Dish
        {
            id: cultureDishSelector
            visible: choosing == 0 ? true : false  //
            anchors.top : parent.top
            width: parent.width
            //width: Math.round(parent.width / 3.2)
            // TODO Create a reusable component with these properties to not define them separately for each component
            labelColumnWidth: parent.firstColumnWidth

            // Rectangle{
            //     anchors.fill:parent
            //     border.width: 2
            //     border.color: "green"
            // }
        }
        
        WellPlateSelector // well Plate
        {
            id: wellPlateSelector
            visible: choosing == 1 ? true : false   //
            anchors.top : parent.top
            width: parent.width
            //width: Math.round(parent.width / 3.2)
            // TODO Create a reusable component with these properties to not define them separately for each component
            labelColumnWidth: parent.firstColumnWidth

            // //Identifying Line
            // Rectangle{
            //     anchors.fill:parent
            //     border.width: 2
            //     border.color: "green"
            // }
        }   

        CultureSlideSelector // culture Slide
        {
            id: cultureSlideSelector
            visible: choosing == 2 ? true : false  //
            anchors.top : parent.top
            width: parent.width
            //width: Math.round(parent.width / 3.2)
            // TODO Create a reusable component with these properties to not define them separately for each component
            labelColumnWidth: parent.firstColumnWidth   

            // Rectangle{
            //     anchors.fill:parent
            //     border.width: 2
            //     border.color: "green"
            // }        
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
}
