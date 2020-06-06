import QtQuick 2.10
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls 2.3 as Controls2

import UM 1.2 as UM
import Cura 1.0 as Cura

Rectangle {
    id: base

    //visible: category === "Well Plate"
    width: childrenRect.width
    height: childrenRect.height
    anchors.centerIn: parent

    property string product_id: ""

    readonly property var diameter: UM.Theme.getSize("rokit_well_plate_diameter").width
    readonly property var spacing: UM.Theme.getSize("thin_margin").height 
    readonly property var color: UM.Theme.getColor("rokit_build_plate")
    readonly property var borderColor: UM.Theme.getColor("rokit_build_plate_border")
    
    property var shapeInfo: {
        const category = product_id.split(":")[0]
        const numberOfCircles = product_id.split(":")[1]

        var shape = { rows:1, cols:1, size_factor:2.0 }

        if (category === "Well Plate") {
            switch (numberOfCircles) {
                case "96":
                    shape = { rows:8, cols:12, size_factor:1/4 }
                    break
                case "48":
                    shape = { rows:6, cols:8, size_factor:1/3 } 
                    break
                case "24":
                    shape = { rows:4, cols:6, size_factor:1/2 }
                    break
                case "12":
                    shape = { rows:3, cols:4, size_factor:2/3 }
                    break
                default:
                    shape = { rows:2, cols:3, size_factor:1 }
            }
        }
        shape.radius = (category !== "Culture Slide") ? (base.diameter * shape.size_factor) / 2 : 0

        return shape
    }

    Column {
        spacing: base.spacing * shapeInfo.size_factor
        Repeater {
            model: shapeInfo.rows
            Row {
                spacing: base.spacing * shapeInfo.size_factor                      
                Repeater {
                    model: shapeInfo.cols
                    Rectangle {
                        width: (shapeInfo.radius === 0) ? 0.66667 * base.diameter * shapeInfo.size_factor : base.diameter * shapeInfo.size_factor
                        height: base.diameter * shapeInfo.size_factor
                        radius: shapeInfo.radius
                        color: base.color
                        border.width : 1
                        border.color: base.borderColor
                    }
                }                 
            }
        }
    }
}
