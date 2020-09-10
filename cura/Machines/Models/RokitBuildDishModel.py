# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QVector3D

from UM.Logger import Logger
from UM.Qt.ListModel import ListModel
import cura.CuraApplication  # Imported like this to prevent circular dependencies.

class RokitBuildDishModel(ListModel):
    ProductIdRole = Qt.UserRole + 1
    ShapeRole = Qt.UserRole + 2
    VolumeRole = Qt.UserRole + 3
    TravelRole = Qt.UserRole + 4

    def __init__(self, parent = None):
        super().__init__(parent)

        self.addRoleName(self.ProductIdRole, "product_id")
        self.addRoleName(self.ShapeRole, "shape")
        self.addRoleName(self.VolumeRole, "volume")
        self.addRoleName(self.TravelRole, "travel")

        # cura.CuraApplication.CuraApplication.getInstance().getMachineManager().globalContainerChanged.connect(self._update)
  
        Logger.log("d", "initialize {model_class_name}.".format(model_class_name = self.__class__.__name__))

        item_list = []
        item_list.append({"product_id": "Well Plate:96", "shape": "elliptic", "volume": QVector3D(6.92, 6.92, 8.0), "travel": {"number_of_rows":96/8, "spacing":9.0, "hop_height": 30.0, "start_point": QPointF(-31.5,49.5), "number_of_walls": 96}})
        item_list.append({"product_id": "Well Plate:48", "shape": "elliptic", "volume": QVector3D(9.75, 9.75, 8.0), "travel": {"number_of_rows":48/6, "spacing":14.43, "hop_height": 30.0, "start_point": QPointF(-32.25,45.15), "number_of_walls": 48}})
        item_list.append({"product_id": "Well Plate:24", "shape": "elliptic", "volume": QVector3D(15.5, 15.5, 8.0), "travel": {"number_of_rows":24/4, "spacing":19.5, "hop_height": 30.0, "start_point": QPointF(-28.95,48.25), "number_of_walls": 24}})
        item_list.append({"product_id": "Well Plate:12", "shape": "elliptic", "volume": QVector3D(21.9, 21.9, 8.0), "travel": {"number_of_rows":12/3, "spacing":28.87, "hop_height": 30.0, "start_point": QPointF(-26.0,39.0), "number_of_walls": 12}})
        item_list.append({"product_id": "Well Plate:6", "shape": "elliptic", "volume": QVector3D(35.0, 35.0, 8.0), "travel": {"number_of_rows":6/2, "spacing":39.0, "hop_height": 30.0, "start_point": QPointF(-19.5,39.0), "number_of_walls": 6}})

        item_list.append({"product_id": "Culture Dish:11060", "shape": "elliptic", "volume": QVector3D(52.8,52.8,8.0), "travel": {"start_point": QPointF(42.5,0.0)}})
        item_list.append({"product_id": "Culture Dish:11090", "shape": "elliptic", "volume": QVector3D(80,80,8.0), "travel": {"start_point": QPointF(42.5,0.0)}})

        self.setItems(item_list)
