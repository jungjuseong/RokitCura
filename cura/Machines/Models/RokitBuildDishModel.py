# Copyright (c) 2019 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QVector3D

from UM.Logger import Logger
from UM.Qt.ListModel import ListModel
import cura.CuraApplication  # Imported like this to prevent circular dependencies.

class RokitBuildDishModel(ListModel):
    CategoryRole = Qt.UserRole + 1
    ProductIdRole = Qt.UserRole + 2
    ShapeRole = Qt.UserRole + 3
    VolumeRole = Qt.UserRole + 4

    def __init__(self, parent = None):
        super().__init__(parent)

        self.addRoleName(self.CategoryRole, "category")
        self.addRoleName(self.ProductIdRole, "product_id")
        self.addRoleName(self.ShapeRole, "shape")
        self.addRoleName(self.VolumeRole, "volume")

        cura.CuraApplication.CuraApplication.getInstance().getMachineManager().globalContainerChanged.connect(self._update)
        self._update()

    def _update(self):
        Logger.log("d", "Updating {model_class_name}.".format(model_class_name = self.__class__.__name__))

        item_list = []     
        item_list.append({"category": "Well Plate", "product_id": "96", "shape": "elliptic", "volume": QVector3D(6.5, 6.5, 10.8)})
        item_list.append({"category": "Well Plate", "product_id": "48", "shape": "elliptic", "volume": QVector3D(9.75, 9.75, 17.50)})
        item_list.append({"category": "Well Plate", "product_id": "24", "shape": "elliptic", "volume": QVector3D(15.5, 15.5, 17.50)})
        item_list.append({"category": "Well Plate", "product_id": "12", "shape": "elliptic", "volume": QVector3D(21.9, 21.9, 17.50)})
        item_list.append({"category": "Well Plate", "product_id": "6", "shape": "elliptic", "volume": QVector3D(35.0, 35.0, 17.50)})

        item_list.append({"category": "Culture Dish", "product_id": "11035", "shape": "elliptic", "volume": QVector3D(35,35,10)})
        item_list.append({"category": "Culture Dish", "product_id": "11060", "shape": "elliptic", "volume": QVector3D(60,60,10)})
        item_list.append({"category": "Culture Dish", "product_id": "11090", "shape": "elliptic", "volume": QVector3D(90,90,15)})

        item_list.append({"category": "Culture Slide", "product_id": "11035", "shape": "rectangular", "volume": QVector3D(20,40,12)})
        item_list.append({"category": "Culture Slide", "product_id": "11060", "shape": "rectangular", "volume": QVector3D(30,60,12)})
        item_list.append({"category": "Culture Slide", "product_id": "11090", "shape": "rectangular", "volume": QVector3D(40,80,12)})

        self.setItems(item_list)