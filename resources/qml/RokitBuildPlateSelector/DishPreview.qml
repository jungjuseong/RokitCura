import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 2.3 as Controls2

import UM 1.2 as UM
import Cura 1.0 as Cura

Rectangle {
    id: base

    visible: category === "Well Plate"
    width: childrenRect.width
    height: childrenRect.height
    anchors.centerIn: parent

    property var diameter: UM.Theme.getSize("rokit_well_plate_diameter").width
    property int rows: 2
    property int cols: 3
    property var size_factor: 1
    
    property var spacing: UM.Theme.getSize("thin_margin").height 
    property var color: UM.Theme.getColor("rokit_build_plate")
    property var borderColor: UM.Theme.getColor("rokit_build_plate_border")
    
    function showPreview(product_id) {
        const category = product_id.split(":")[0]
        const numberOfCircles = product_id.split(":")[1]

        console.log(product_id)

        base.rows = 1
        base.cols = 1
        base.size_factor = 2

        if (category === "Well Plate") {
            switch (numberOfCircles) {
                case "96":
                    base.rows = 8, base.cols = 12, base.size_factor = 1/4
                    break
                case "48":
                    base.rows = 6, base.cols = 8, base.size_factor = 1/3
                    break
                case "24":
                    base.rows = 4, base.cols = 6, base.size_factor = 1/2
                    break
                case "12":
                    base.rows = 3, base.cols = 4, base.size_factor = 2/3
                    break
                default:
                    base.rows = 2 , base.cols = 3, base.size_factor = 1
            }
        }
        base.radius = (category === "Culture Slide") ? 0 : (base.width * base.size_factor) / 2
    }

    Column {
        spacing: base.spacing * base.size_factor
        Repeater {
            model: base.rows
            Row {
                spacing: base.spacing * base.size_factor                      
                Repeater {
                    model: base.cols
                    Rectangle {
                        width: base.diameter * base.size_factor
                        height: base.diameter * base.size_factor
                        radius: base.radius
                        color: base.color
                        border.width : 1
                        border.color: borderColor
                    }
                }                 
            }
        }
    }
}
