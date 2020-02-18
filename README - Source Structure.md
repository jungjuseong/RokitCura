
## Source structure


- cura_app.py: Cura앱 시작
- cura.appdata.xml
- cura.desktop.in
 
## cura 

- ApplicationMetadata.py
- AutoSave.py
- BuildVolume.py
- CameraAnimation.py
- CrashHandler.py
- CuraActions.py
- CuraApplication.py
- CuraPackageManager.py
- CuraView.py
- Layer.py
- LayerData.py
- LayerDataBuilder.py
- LayerDataDecorator.py
- LayerPolygon.py
- MachineAction.py
- MultipleObjectsJob.py
- OneAtATimeIterator.py
- PickingPass.py
- PlatformPhysics.py
- PreviewPass.py
- PrinterOutputDevice.py
- PrintJobPreviewImageProvider.py
- SingleInstance.py
- Snapshot.py
- UltimakerCloudAuthentication.py

### cura/API

- Account.py
- Backups.py

### cura/Arrange

- Arrange.py
- ArrangeObjectsAllBuildPlatesJob.py
- ArrangeObjectsJob.py
- ShapeArray.py

### cura/Backups

- Backup.py
- BackupsManager.py
 
### cura/Machines

- ContainerNode.py
- ContainerTree.py
- IntentNode.py
- MachineErrorChecker.py
- MachineNode.py
- MaterialGroup.py
- QualityChangeGroup.py
- QualityGroup.py
- QualityNode.py
- VariantNode.py
- VariantType.py

### cura/OAuth

- AuthorizationHelpers.py
- AuthorizationRequestHandler.py
- AuthorizationRequestServer.py
- AuthorizationService.py
- LocalAuthorizationServer.py
- Models.py

### cura/Operations

- PlatformPhysicsOperation.py
- SetBuildPlateNumberOperation.py
- SetParentOperation.py


### cura/PrinterOutput

- FirmwareUpdater.py
- GenericOutputController.py
- NetworkedPrinterOutputDevice.py
- NetworkMUPGImage.py
- Peripheral.py
- PrinterOutputController.py
- PrinterOutputDevice.py
- PrinterOutputModel.py
- PrintUobOutputModel.py

### cura/ReadWriters

- ProfileReader.py
- ProfileWriter.py


### cura/Scene

- BlockSlicingDecorator.py
- BuildPlateDecorator.py
- ConvexHullNode.py
- CuraSceneController.py
- CuraSceneNode.py
- GCodeListDecorator.py
- SliceableObjectDecorator.py
- ZOffsetDecorator.py

### cura/Settings

- CuraFormulaFunctions.py 
- CuraStackBuilder.py
- cura_empty_instance_containers.py 
- Exceptions.py 
- ExtruderManager.py
- ExtruderStack.py 
- GlobalStack.py 
- IntentManager.py 
- MachineManager.py 
- MachineNameValidator.py
- MaterialSettingsVisibilityHandler.py 
- PerObjectContainerStack.py 
- SetObjectExtruderOperation.py 
- SettingInheritanceManager.py 
- SettingOverrideDecorator.py
- SettingVisibilityPreset.py 
- SidebarCustomMenuItemsModel.py 
- SimpleModeSettingsManager.py 

### cura/Stages

- CuraStage.py

### cura/TaskManagement

- OnExitCallbackManager.py

### cura/UI

- AddPrinterPagesModel.py 
- CuraSplashScreen.py 
- MachineActionManager.py 
- MachineSettingsManager.py 
- ObjectsModel.py
- PrintInformation.py 
- RecommendedMode.py 
- TextManager.py 
- WelcomePagesModel.py 
- WhatsNewPagesModel.py

### cura/Utils

- Decorators.py 
- NetworkingUtil.py 
- Threading.py


## resources/

### bundled_packages

- cura.json
- uranium.json

### definitions

- 3dator.def.json
- 101Hero.def.json
- abax_pri3.def.json

### extruders

- 3dator_extruder_0.def.json
- 101Hero_extruder_0.def.json
- abax_extruder_pri3.def.json

### i18n

- de_DE/
- ko_KR
- ja_JP/

### images

 
### intent

- intent/ultimaker_s3
- intent/ultimaker_s5
- 
### materials

- scripts/check_material_profiles_new_with_lxml.py
- scripts/check_material_profiles.py
- scripts/update_version_by_one.py
- dsm_arnitel2045_175.xml.fdm_material
- dsm_novamid1070_175.xml.fdm_material

### meshes

- 3dator_platform.stl
- 101hero-platform.stl

### qml 

- ActionButton.qml
- Actions.qml
- BorderGroup.qml
- CheckBoxWithTooltip.qml
- Cura.qml
- EmptyViewMenuComponent.qml
- ExpandableComponent.qml
- ExpandableComponentHeader.qml
- ExpandablePopup.qml
- ExtruderButton.qml
- ExtruderIcon.qml
- FPSItem.qml
- IconWithText.qml
- JobSpecs.qml
- LabelBar.qml
- MachineAction.qml
- MonitorButton.qml
- ObjectItemButton.qml
- ObjectSelector.qml
- PrimaryButton.qml
- PrinterTypeLabel.qml
- PrintMonitor.qml
- PrintSetupTooltip.qml
- RadioCheckbar.qml
- RoundedRectangle.qml
- SecondaryButton.qml
- Toolbar.qml
- ToolbarButton.qml
- ToolTip.qml
- ViewOrientationButton.qml
- ViewOrientationControls.qml
- ViewsSelector.qml

### quality



### setting_visibility

- advanced.cfg
- high.inst.cfg
- normal.inst.cfg
 
### shaders 

- camera_distance.shader
- color.shader
- composite.shader
- default.shader

### texts 

### themes

- cura-dark
- cura-dark-colorblind
- cura-light
- cura-light-colorblind

### variants

- cartesio_0.4.inst.cfg
- cartesio_0.8.inst.cfg
- cartesio_0.25.inst.cfg


## plugins

- 3MFReader 
- 3MFWriter 
- AMFReader 
- ConsoleLogger
- CuraDrive 
- CuraEngineBackend 
- CuraProfileReader 
- CuraProfileWriter 
- FileHandlers 
- FileLogger
- FirmwareUpdateChecker 
- FirmwareUpdater 
- GCodeGzReader 
- GCodeGzWriter 
- GCodeProfileReader 
- GCodeReader
- GCodeWriter 
- ImageReader 
- LegacyProfileReader 
- LocalContainerProvider 
- LocalFileOutputDevice 
- MachineSettingsAction
- ModelChecker - MonitorStage 
- PerObjectSettingsTool 
- PostProcessingPlugin
- PrepareStage 
- PreviewStage
- RemovableDriveOutputDevice 
- SentryLogger 
- SimulationView 
- SliceInfoPlugin 
- SolidView 
- SupportEraser
- Toolbox 
- Tools 
- TrimeshReader 
- UFPReader - UFPWriter 
- UltimakerMachineActions
- UM3NetworkPrinting 
- UpdateChecker 
- USBPrinting 
- VersionUpgrade 
- Views 
- X3DReader
- XmlMaterialProfile 
- XRayView