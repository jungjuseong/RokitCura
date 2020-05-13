// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4 as Controls1
import QtQuick.Controls 1.2

import UM 1.3 as UM
import Cura 1.0 as Cura

// This element contains all the elements the user needs to create a printjob from the
// model(s) that is(are) on the buildplate. Mainly the button to start/stop the slicing
// process and a progress bar to see the progress of the process.
Column {
    id: widget
    
    property string leftFirst

    spacing: UM.Theme.getSize("thin_margin").height

    UM.I18nCatalog {
        id: catalog
        name: "cura"
    }

    property real progress: UM.Backend.progress
    property int backendState: UM.Backend.state
    // As the collection of settings to send to the engine might take some time, we have an extra value to indicate
    // That the user pressed the button but it's still waiting for the backend to acknowledge that it got it.
    property bool waitingForSliceToStart: false
    onBackendStateChanged: waitingForSliceToStart = false

    function sliceOrStopSlicing() {
        if (widget.backendState == UM.Backend.NotStarted) {
            widget.waitingForSliceToStart = true
            CuraApplication.backend.forceSlice()
        }
        else {
            widget.waitingForSliceToStart = false
            CuraApplication.backend.stopSlicing()
        }
    }

    Label {
        id: autoSlicingLabel
        width: parent.width
        visible: progressBar.visible

        text: catalog.i18nc("@label:PrintjobStatus", "Slicing...")
        color: UM.Theme.getColor("text")
        font: UM.Theme.getFont("default")
        renderType: Text.NativeRendering
    }

    Cura.IconWithText {
        id: unableToSliceMessage
        width: parent.width
        visible: widget.backendState == UM.Backend.Error

        text: catalog.i18nc("@label:PrintjobStatus", "Unable to slice")
        source: UM.Theme.getIcon("warning")
        iconColor: UM.Theme.getColor("warning")
    }

    // Progress bar, only visible when the backend is in the process of slice the printjob
    UM.ProgressBar {
        id: progressBar
        width: parent.width
        height: UM.Theme.getSize("progressbar").height
        value: progress
        indeterminate: widget.backendState == UM.Backend.NotStarted
        visible: (widget.backendState == UM.Backend.Processing || (prepareButtons.autoSlice && widget.backendState == UM.Backend.NotStarted))
    }

    Item {
        id: prepareButtons
        // Get the current value from the preferences
        property bool autoSlice: UM.Preferences.getValue("general/auto_slice")
        // Disable the slice process when

        width: parent.width
        height: UM.Theme.getSize("action_button").height
        visible: !autoSlice
        Cura.PrimaryButton {
            id: sliceButton

            fixedWidthMode: true
            height: parent.height

            anchors.right: parent.right
            anchors.left: parent.left

            text: widget.waitingForSliceToStart ? catalog.i18nc("@button", "Processing"): catalog.i18nc("@button", "Slice")
            tooltip: catalog.i18nc("@label", "Start the slicing process")
            enabled: widget.backendState != UM.Backend.Error && !widget.waitingForSliceToStart
            visible: widget.backendState == UM.Backend.NotStarted || widget.backendState == UM.Backend.Error
            onClicked: sliceOrStopSlicing()
        }


        Cura.SecondaryButton {
            id: cancelButton
            fixedWidthMode: true
            height: parent.height
            anchors.left: parent.left

            anchors.right: parent.right
            text: catalog.i18nc("@button", "Cancel")
            enabled: sliceButton.enabled
            visible: !sliceButton.visible
            onClicked: sliceOrStopSlicing()
        }
    }
    CheckBox {            
        id: leftFirstCheckbox

        //anchors.top: sliceButton.top
        anchors.topMargin: UM.Theme.getSize("default_margin").height;
        //anchors.right: sliceButton.left
        anchors.leftMargin: UM.Theme.getSize("default_margin").width

        text: catalog.i18nc("@option:check","Left First");
        style: UM.Theme.styles.partially_checkbox
        tooltip: catalog.i18nc("@label", "slice in the left model first")

        enabled: widget.backendState != UM.Backend.Error && !widget.waitingForSliceToStart
        visible: widget.backendState == UM.Backend.NotStarted || widget.backendState == UM.Backend.Error

        property var checkbox_state: 0; // if the state number is 2 then the checkbox has "partially" state

        // temporary property, which is used to recalculate checkbox state and keeps reference of the
        // binging object. If the binding object changes then checkBox state will be updated.
        property var temp_checkBox_value: {
            checkbox_state = getCheckBoxState()
            // returning the slicePriority the propery will keep reference, for updating
            return widget.slicePriority
        }

        function getCheckBoxState() {
            if (widget.leftFirst == "true"){
                leftFirstCheckbox.checked = true
                return 1;
            }
            else if (widget.leftFirst == "partially"){
                leftFirstCheckbox.checked = true
                return 2;
            }
            else{
                leftFirstCheckbox.checked = false
                return 0;
            }
        }
        onClicked: {
            // If state is partially, then set Checked
            if (checkbox_state == 2){
                leftFirstCheckbox.checked = true
                UM.ActiveTool.setProperty("LeftFirst", true);
            }
            else {
                UM.ActiveTool.setProperty("LeftFirst", leftFirstCheckbox.checked);
            }

            // After clicking the widget.leftFirst is not refreshed, fot this reason manually update the state
            // Set zero because only 2 will show partially icon in checkbox
            checkbox_state = 0;
        }
    }
    // React when the user changes the preference of having the auto slice enabled
    Connections {
        target: UM.Preferences
        onPreferenceChanged: {
            if (preference !== "general/auto_slice") {
                return;
            }

            var autoSlice = UM.Preferences.getValue("general/auto_slice")
            if(prepareButtons.autoSlice != autoSlice) {
                prepareButtons.autoSlice = autoSlice
                if(autoSlice) {
                    CuraApplication.backend.forceSlice()
                }
            }
        }
    }

    // Shortcut for "slice/stop"
    Controls1.Action{
        shortcut: "Ctrl+P"
        onTriggered:
        {
            if (sliceButton.enabled)
            {
                sliceOrStopSlicing()
            }
        }
    }

    // We have to use indirect bindings, as the values can be changed from the outside, which could cause breaks
    // (for instance, a value would be set, but it would be impossible to change it).
    // Doing it indirectly does not break these.
    Binding
    {
        target: widget
        property: "leftFirst"
        value: UM.ActiveTool.properties.getValue("LeftFirst")
    }
}
