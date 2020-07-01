# Copyright (c) 2018 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

import argparse #To run the engine in debug mode if the front-end is in debug mode.
from collections import defaultdict
import os
from PyQt5.QtCore import QObject, QTimer, pyqtSlot
import sys
from time import time
from typing import Any, cast, Dict, List, Optional, Set, TYPE_CHECKING

from UM.Backend.Backend import Backend, BackendState
from UM.Scene.SceneNode import SceneNode
from UM.Signal import Signal
from UM.Logger import Logger
from UM.Message import Message
from UM.PluginRegistry import PluginRegistry
from UM.Platform import Platform
from UM.Qt.Duration import DurationFormat
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator
from UM.Settings.Interfaces import DefinitionContainerInterface
from UM.Settings.SettingInstance import SettingInstance #For typing.
from UM.Tool import Tool #For typing.

from cura.CuraApplication import CuraApplication
from cura.Settings.ExtruderManager import ExtruderManager
from .ProcessSlicedLayersJob import ProcessSlicedLayersJob
from .StartSliceJob import StartSliceJob, StartJobResult
import Arcus

# from UM.Settings.ContainerRegistry import ContainerRegistry  # To find all the variants for this machine.
# from UM.Operations.GroupedOperation import GroupedOperation

if TYPE_CHECKING:
    from cura.Machines.Models.MultiBuildPlateModel import MultiBuildPlateModel
    from cura.Machines.MachineErrorChecker import MachineErrorChecker
    from UM.Scene.Scene import Scene
    from UM.Settings.ContainerStack import ContainerStack

from cura.Machines.Models.RokitBuildDishModel import RokitBuildDishModel

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")

class CuraEngineBackend(QObject, Backend):
    backendError = Signal()

    ##  Starts the back-end plug-in.
    #
    #   This registers all the signal listeners and prepares for communication
    #   with the back-end in general.
    #   CuraEngineBackend is exposed to qml as well.
    def __init__(self) -> None:
        super().__init__()
        # Find out where the engine is located, and how it is called.
        # This depends on how Cura is packaged and which OS we are running on.
        executable_name = "CuraEngine"
        if Platform.isWindows():
            executable_name += ".exe"
        default_engine_location = executable_name

        search_path = [
            os.path.abspath(os.path.dirname(sys.executable)),
            os.path.abspath(os.path.join(os.path.dirname(sys.executable), "bin")),
            os.path.abspath(os.path.join(os.path.dirname(sys.executable), "..")),

            os.path.join(CuraApplication.getInstallPrefix(), "bin"),
            os.path.dirname(os.path.abspath(sys.executable)),
        ]

        for path in search_path:
            engine_path = os.path.join(path, executable_name)
            if os.path.isfile(engine_path):
                default_engine_location = engine_path
                break

        if Platform.isLinux() and not default_engine_location:
            if not os.getenv("PATH"):
                raise OSError("There is something wrong with your Linux installation.")
            for pathdir in cast(str, os.getenv("PATH")).split(os.pathsep):
                execpath = os.path.join(pathdir, executable_name)
                if os.path.exists(execpath):
                    default_engine_location = execpath
                    break

        self._build_dish_model = RokitBuildDishModel()

        self._application = CuraApplication.getInstance() #type: CuraApplication
        self._multi_build_plate_model = None #type: Optional[MultiBuildPlateModel]
        self._machine_error_checker = None #type: Optional[MachineErrorChecker]

        if not default_engine_location:
            raise EnvironmentError("Could not find CuraEngine")

        Logger.log("i", "Found CuraEngine at: %s", default_engine_location)

        default_engine_location = os.path.abspath(default_engine_location)
        self._application.getPreferences().addPreference("backend/location", default_engine_location)

        # Workaround to disable layer view processing if layer view is not active.
        self._layer_view_active = False #type: bool
        self._onActiveViewChanged()

        self._stored_layer_data = []  # type: List[Arcus.PythonMessage]
        self._stored_optimized_layer_data = {}  # type: Dict[int, List[Arcus.PythonMessage]] # key is build plate number, then arrays are stored until they go to the ProcessSlicesLayersJob

        self._scene = self._application.getController().getScene() #type: Scene
        self._scene.sceneChanged.connect(self._onSceneChanged)

        # Triggers for auto-slicing. Auto-slicing is triggered as follows:
        #  - auto-slicing is started with a timer
        #  - whenever there is a value change, we start the timer
        #  - sometimes an error check can get scheduled for a value change, in that case, we ONLY want to start the
        #    auto-slicing timer when that error check is finished
        # If there is an error check, stop the auto-slicing timer, and only wait for the error check to be finished
        # to start the auto-slicing timer again.
        #
        self._global_container_stack = None #type: Optional[ContainerStack]

        # Listeners for receiving messages from the back-end.
        self._message_handlers["cura.proto.Layer"] = self._onLayerMessage
        self._message_handlers["cura.proto.LayerOptimized"] = self._onOptimizedLayerMessage
        self._message_handlers["cura.proto.Progress"] = self._onProgressMessage
        self._message_handlers["cura.proto.GCodeLayer"] = self._onGCodeLayerMessage
        self._message_handlers["cura.proto.GCodePrefix"] = self._onGCodePrefixMessage
        self._message_handlers["cura.proto.PrintTimeMaterialEstimates"] = self._onPrintTimeMaterialEstimates
        self._message_handlers["cura.proto.SlicingFinished"] = self._onSlicingFinishedMessage

        self._start_slice_job = None #type: Optional[StartSliceJob]
        self._start_slice_job_build_plate = None #type: Optional[int]
        self._slicing = False #type: bool # Are we currently slicing?
        self._restart = False #type: bool # Back-end is currently restarting?
        self._tool_active = False #type: bool # If a tool is active, some tasks do not have to do anything
        self._always_restart = True #type: bool # Always restart the engine when starting a new slice. Don't keep the process running. TODO: Fix engine statelessness.
        self._process_layers_job = None #type: Optional[ProcessSlicedLayersJob] # The currently active job to process layers, or None if it is not processing layers.
        self._build_plates_to_be_sliced = [] #type: List[int] # what needs slicing?
        self._engine_is_fresh = True #type: bool # Is the newly started engine used before or not?

        self._backend_log_max_lines = 20000 #type: int # Maximum number of lines to buffer
        self._error_message = None #type: Optional[Message] # Pop-up message that shows errors.
        self._last_num_objects = defaultdict(int) #type: Dict[int, int] # Count number of objects to see if there is something changed
        self._postponed_scene_change_sources = [] #type: List[SceneNode] # scene change is postponed (by a tool)

        self._slice_start_time = None #type: Optional[float]
        self._is_disabled = False #type: bool

        self._application.getPreferences().addPreference("general/auto_slice", False)

        self._use_timer = False #type: bool
        # When you update a setting and other settings get changed through inheritance, many propertyChanged signals are fired.
        # This timer will group them up, and only slice for the last setting changed signal.
        # TODO: Properly group propertyChanged signals by whether they are triggered by the same user interaction.
        self._change_timer = QTimer() #type: QTimer
        self._change_timer.setSingleShot(True)
        self._change_timer.setInterval(500)
        self.determineAutoSlicing()
        self._application.getPreferences().preferenceChanged.connect(self._onPreferencesChanged)

        self._application.initializationFinished.connect(self.initialize)

    def initialize(self) -> None:
        self._multi_build_plate_model = self._application.getMultiBuildPlateModel()

        self._application.getController().activeViewChanged.connect(self._onActiveViewChanged)

        if self._multi_build_plate_model:
            self._multi_build_plate_model.activeBuildPlateChanged.connect(self._onActiveViewChanged)

        self._application.getMachineManager().globalContainerChanged.connect(self._onGlobalStackChanged)
        self._onGlobalStackChanged()

        # extruder enable / disable. Actually wanted to use machine manager here, but the initialization order causes it to crash
        ExtruderManager.getInstance().extrudersChanged.connect(self._extruderChanged)

        self.backendQuit.connect(self._onBackendQuit)
        self.backendConnected.connect(self._onBackendConnected)

        # When a tool operation is in progress, don't slice. So we need to listen for tool operations.
        self._application.getController().toolOperationStarted.connect(self._onToolOperationStarted)
        self._application.getController().toolOperationStopped.connect(self._onToolOperationStopped)

        self._machine_error_checker = self._application.getMachineErrorChecker()
        self._machine_error_checker.errorCheckFinished.connect(self._onStackErrorCheckFinished)

    ##  Terminate the engine process.
    #
    #   This function should terminate the engine process.
    #   Called when closing the application.
    def close(self) -> None:
        # Terminate CuraEngine if it is still running at this point
        self._terminate()

    ##  Get the command that is used to call the engine.
    #   This is useful for debugging and used to actually start the engine.
    #   \return list of commands and args / parameters.
    def getEngineCommand(self) -> List[str]:
        command = [self._application.getPreferences().getValue("backend/location"), "connect", "127.0.0.1:{0}".format(self._port), ""]

        parser = argparse.ArgumentParser(prog = "cura", add_help = False)
        parser.add_argument("--debug", action = "store_true", default = False, help = "Turn on the debug mode by setting this option.")
        known_args = vars(parser.parse_known_args()[0])
        if known_args["debug"]:
            command.append("-vvv")

        return command

    ##  Emitted when we get a message containing print duration and material amount.
    #   This also implies the slicing has finished.
    #   \param time The amount of time the print will take.
    #   \param material_amount The amount of material the print will use.
    printDurationMessage = Signal()

    ##  Emitted when the slicing process starts.
    slicingStarted = Signal()

    ##  Emitted when the slicing process is aborted forcefully.
    slicingCancelled = Signal()

    @pyqtSlot()
    def stopSlicing(self) -> None:
        self.setState(BackendState.NotStarted)
        if self._slicing:  # We were already slicing. Stop the old job.
            self._terminate()
            self._createSocket()

        if self._process_layers_job is not None:  # We were processing layers. Stop that, the layers are going to change soon.
            Logger.log("i", "Aborting process layers job...")
            self._process_layers_job.abort()
            self._process_layers_job = None

        if self._error_message:
            self._error_message.hide()

    ##  Manually triggers a reslice
    @pyqtSlot()
    def forceSlice(self) -> None:
        self.markSliceAll()
        self.slice()

    ##  Perform a slice of the scene.
    def slice(self) -> None:
        Logger.log("i", "Starting to slice...")
        self._slice_start_time = time()
        if not self._build_plates_to_be_sliced:
            self.processingProgress.emit(1.0)
            Logger.log("w", "Slice unnecessary, nothing has changed that needs reslicing.")
            self.setState(BackendState.Done)
            return

        if self._process_layers_job:
            Logger.log("d", "Process layers job still busy, trying later.")
            return

        if not hasattr(self._scene, "gcode_dict"):
            self._scene.gcode_dict = {} #type: ignore #Because we are creating the missing attribute here.

        # see if we really have to slice
        active_build_plate = self._application.getMultiBuildPlateModel().activeBuildPlate
        build_plate_to_be_sliced = self._build_plates_to_be_sliced.pop(0)
        Logger.log("d", "Going to slice build plate [%s]!" % build_plate_to_be_sliced)
        num_objects = self._numObjectsPerBuildPlate()

        self._stored_layer_data = []


        if build_plate_to_be_sliced not in num_objects or num_objects[build_plate_to_be_sliced] == 0:
            self._scene.gcode_dict[build_plate_to_be_sliced] = [] #type: ignore #Because we created this attribute above.
            Logger.log("d", "Build plate %s has no objects to be sliced, skipping", build_plate_to_be_sliced)
            if self._build_plates_to_be_sliced:
                self.slice()
            return
        self._stored_optimized_layer_data[build_plate_to_be_sliced] = []
        if self._application.getPrintInformation() and build_plate_to_be_sliced == active_build_plate:
            self._application.getPrintInformation().setToZeroPrintInformation(build_plate_to_be_sliced)

        if self._process is None: # type: ignore
            self._createSocket()
        self.stopSlicing()
        self._engine_is_fresh = False  # Yes we're going to use the engine

        self.processingProgress.emit(0.0)
        self.backendStateChange.emit(BackendState.NotStarted)

        self._scene.gcode_dict[build_plate_to_be_sliced] = [] #type: ignore #[] indexed by build plate number
        self._slicing = True
        self.slicingStarted.emit()

        self.determineAutoSlicing()  # Switch timer on or off if appropriate

        slice_message = self._socket.createMessage("cura.proto.Slice")
        self._start_slice_job = StartSliceJob(slice_message)
        self._start_slice_job_build_plate = build_plate_to_be_sliced
        self._start_slice_job.setBuildPlate(self._start_slice_job_build_plate)
        self._start_slice_job.start()
        self._start_slice_job.finished.connect(self._onStartSliceCompleted)

    ##  Terminate the engine process.
    #   Start the engine process by calling _createSocket()
    def _terminate(self) -> None:
        self._slicing = False
        self._stored_layer_data = []
        if self._start_slice_job_build_plate in self._stored_optimized_layer_data:
            del self._stored_optimized_layer_data[self._start_slice_job_build_plate]
        if self._start_slice_job is not None:
            self._start_slice_job.cancel()

        self.slicingCancelled.emit()
        self.processingProgress.emit(0)
        Logger.log("d", "Attempting to kill the engine process")

        if self._application.getUseExternalBackend():
            return

        if self._process is not None: # type: ignore
            Logger.log("d", "Killing engine process")
            try:
                self._process.terminate() # type: ignore
                Logger.log("d", "Engine process is killed. Received return code %s", self._process.wait()) # type: ignore
                self._process = None # type: ignore

            except Exception as e:  # terminating a process that is already terminating causes an exception, silently ignore this.
                Logger.log("d", "Exception occurred while trying to kill the engine %s", str(e))

    ##  Event handler to call when the job to initiate the slicing process is
    #   completed.
    #
    #   When the start slice job is successfully completed, it will be happily
    #   slicing. This function handles any errors that may occur during the
    #   bootstrapping of a slice job.
    #
    #   \param job The start slice job that was just finished.
    def _onStartSliceCompleted(self, job: StartSliceJob) -> None:
        if self._error_message:
            self._error_message.hide()

        # Note that cancelled slice jobs can still call this method.
        if self._start_slice_job is job:
            self._start_slice_job = None

        if job.isCancelled() or job.getError() or job.getResult() == StartJobResult.Error:
            self.setState(BackendState.Error)
            self.backendError.emit(job)
            return

        if job.getResult() == StartJobResult.MaterialIncompatible:
            if self._application.platformActivity:
                self._error_message = Message(catalog.i18nc("@info:status",
                                            "Unable to slice with the current material as it is incompatible with the selected machine or configuration."), title = catalog.i18nc("@info:title", "Unable to slice"))
                self._error_message.show()
                self.setState(BackendState.Error)
                self.backendError.emit(job)
            else:
                self.setState(BackendState.NotStarted)
            return

        if job.getResult() == StartJobResult.SettingError:
            if self._application.platformActivity:
                if not self._global_container_stack:
                    Logger.log("w", "Global container stack not assigned to CuraEngineBackend!")
                    return
                extruders = ExtruderManager.getInstance().getActiveExtruderStacks()
                error_keys = [] #type: List[str]
                for extruder in extruders:
                    error_keys.extend(extruder.getErrorKeys())
                if not extruders:
                    error_keys = self._global_container_stack.getErrorKeys()
                error_labels = set()
                for key in error_keys:
                    for stack in [self._global_container_stack] + extruders: #Search all container stacks for the definition of this setting. Some are only in an extruder stack.
                        definitions = cast(DefinitionContainerInterface, stack.getBottom()).findDefinitions(key = key)
                        if definitions:
                            break #Found it! No need to continue search.
                    else: #No stack has a definition for this setting.
                        Logger.log("w", "When checking settings for errors, unable to find definition for key: {key}".format(key = key))
                        continue
                    error_labels.add(definitions[0].label)

                self._error_message = Message(catalog.i18nc("@info:status", "Unable to slice with the current settings. The following settings have errors: {0}").format(", ".join(error_labels)),
                                              title = catalog.i18nc("@info:title", "Unable to slice"))
                self._error_message.show()
                self.setState(BackendState.Error)
                self.backendError.emit(job)
            else:
                self.setState(BackendState.NotStarted)
            return

        elif job.getResult() == StartJobResult.ObjectSettingError:
            errors = {}
            for node in DepthFirstIterator(self._application.getController().getScene().getRoot()):
                stack = node.callDecoration("getStack")
                if not stack:
                    continue
                for key in stack.getErrorKeys():
                    if not self._global_container_stack:
                        Logger.log("e", "CuraEngineBackend does not have global_container_stack assigned.")
                        continue
                    definition = cast(DefinitionContainerInterface, self._global_container_stack.getBottom()).findDefinitions(key = key)
                    if not definition:
                        Logger.log("e", "When checking settings for errors, unable to find definition for key {key} in per-object stack.".format(key = key))
                        continue
                    errors[key] = definition[0].label
            self._error_message = Message(catalog.i18nc("@info:status", "Unable to slice due to some per-model settings. The following settings have errors on one or more models: {error_labels}").format(error_labels = ", ".join(errors.values())),
                                          title = catalog.i18nc("@info:title", "Unable to slice"))
            self._error_message.show()
            self.setState(BackendState.Error)
            self.backendError.emit(job)
            return

        if job.getResult() == StartJobResult.BuildPlateError:
            if self._application.platformActivity:
                self._error_message = Message(catalog.i18nc("@info:status", "Unable to slice because the prime tower or prime position(s) are invalid."),
                                              title = catalog.i18nc("@info:title", "Unable to slice"))
                self._error_message.show()
                self.setState(BackendState.Error)
                self.backendError.emit(job)
            else:
                self.setState(BackendState.NotStarted)

        if job.getResult() == StartJobResult.ObjectsWithDisabledExtruder:
            self._error_message = Message(catalog.i18nc("@info:status", "Unable to slice because there are objects associated with disabled Extruder %s.") % job.getMessage(),
                                          title = catalog.i18nc("@info:title", "Unable to slice"))
            self._error_message.show()
            self.setState(BackendState.Error)
            self.backendError.emit(job)
            return

        if job.getResult() == StartJobResult.NothingToSlice:
            if self._application.platformActivity:
                self._error_message = Message(catalog.i18nc("@info:status", "Please review settings and check if your models:"
                                                                            "\n- Fit within the build volume"
                                                                            "\n- Are assigned to an enabled extruder"
                                                                            "\n- Are not all set as modifier meshes"),
                                              title = catalog.i18nc("@info:title", "Unable to slice"))
                self._error_message.show()
                self.setState(BackendState.Error)
                self.backendError.emit(job)
            else:
                self.setState(BackendState.NotStarted)
            self._invokeSlice()
            return

        # Preparation completed, send it to the backend.
        self._socket.sendMessage(job.getSliceMessage())

        # Notify the user that it's now up to the backend to do it's job
        self.setState(BackendState.Processing)

        if self._slice_start_time:
            Logger.log("d", "Sending slice message took %s seconds", time() - self._slice_start_time )

    ##  Determine enable or disable auto slicing. Return True for enable timer and False otherwise.
    #   It disables when
    #   - preference auto slice is off
    #   - decorator isBlockSlicing is found (used in g-code reader)
    def determineAutoSlicing(self) -> bool:
        enable_timer = True
        self._is_disabled = False

        if not self._application.getPreferences().getValue("general/auto_slice"):
            enable_timer = False
        for node in DepthFirstIterator(self._scene.getRoot()):
            if node.callDecoration("isBlockSlicing"):
                enable_timer = False
                self.setState(BackendState.Disabled)
                self._is_disabled = True
            gcode_list = node.callDecoration("getGCodeList")
            if gcode_list is not None:
                self._scene.gcode_dict[node.callDecoration("getBuildPlateNumber")] = gcode_list #type: ignore #Because we generate this attribute dynamically.

        if self._use_timer == enable_timer:
            return self._use_timer
        if enable_timer:
            self.setState(BackendState.NotStarted)
            self.enableTimer()
            return True
        else:
            self.disableTimer()
            return False

    ##  Return a dict with number of objects per build plate
    def _numObjectsPerBuildPlate(self) -> Dict[int, int]:
        num_objects = defaultdict(int) #type: Dict[int, int]
        for node in DepthFirstIterator(self._scene.getRoot()):
            # Only count sliceable objects
            if node.callDecoration("isSliceable"):
                build_plate_number = node.callDecoration("getBuildPlateNumber")
                if build_plate_number is not None:
                    num_objects[build_plate_number] += 1
        return num_objects

    ##  Listener for when the scene has changed.
    #
    #   This should start a slice if the scene is now ready to slice.
    #
    #   \param source The scene node that was changed.
    def _onSceneChanged(self, source: SceneNode) -> None:
        if not source.callDecoration("isSliceable"):
            return

        # This case checks if the source node is a node that contains GCode. In this case the
        # current layer data is removed so the previous data is not rendered - CURA-4821
        if source.callDecoration("isBlockSlicing") and source.callDecoration("getLayerData"):
            self._stored_optimized_layer_data = {}

        build_plate_changed = set()
        source_build_plate_number = source.callDecoration("getBuildPlateNumber")
        if source == self._scene.getRoot():
            # we got the root node
            num_objects = self._numObjectsPerBuildPlate()
            for build_plate_number in list(self._last_num_objects.keys()) + list(num_objects.keys()):
                if build_plate_number not in self._last_num_objects or num_objects[build_plate_number] != self._last_num_objects[build_plate_number]:
                    self._last_num_objects[build_plate_number] = num_objects[build_plate_number]
                    build_plate_changed.add(build_plate_number)
        else:
            # we got a single scenenode
            if not source.callDecoration("isGroup"):
                mesh_data = source.getMeshData()
                if mesh_data is None or mesh_data.getVertices() is None:
                    return

            # There are some SceneNodes that do not have any build plate associated, then do not add to the list.
            if source_build_plate_number is not None:
                build_plate_changed.add(source_build_plate_number)

        if not build_plate_changed:
            return

        if self._tool_active:
            # do it later, each source only has to be done once
            if source not in self._postponed_scene_change_sources:
                self._postponed_scene_change_sources.append(source)
            return

        self.stopSlicing()
        for build_plate_number in build_plate_changed:
            if build_plate_number not in self._build_plates_to_be_sliced:
                self._build_plates_to_be_sliced.append(build_plate_number)
            self.printDurationMessage.emit(source_build_plate_number, {}, [])
        self.processingProgress.emit(0.0)
        self._clearLayerData(build_plate_changed)

        self._invokeSlice()

    ##  Called when an error occurs in the socket connection towards the engine.
    #
    #   \param error The exception that occurred.
    def _onSocketError(self, error: Arcus.Error) -> None:
        if self._application.isShuttingDown():
            return

        super()._onSocketError(error)
        if error.getErrorCode() == Arcus.ErrorCode.Debug:
            return

        self._terminate()
        self._createSocket()

        if error.getErrorCode() not in [Arcus.ErrorCode.BindFailedError, Arcus.ErrorCode.ConnectionResetError, Arcus.ErrorCode.Debug]:
            Logger.log("w", "A socket error caused the connection to be reset")

        # _terminate()' function sets the job status to 'cancel', after reconnecting to another Port the job status
        # needs to be updated. Otherwise backendState is "Unable To Slice"
        if error.getErrorCode() == Arcus.ErrorCode.BindFailedError and self._start_slice_job is not None:
            self._start_slice_job.setIsCancelled(False)

    # Check if there's any slicable object in the scene.
    def hasSlicableObject(self) -> bool:
        has_slicable = False
        for node in DepthFirstIterator(self._scene.getRoot()):
            if node.callDecoration("isSliceable"):
                has_slicable = True
                break
        return has_slicable

    ##  Remove old layer data (if any)
    def _clearLayerData(self, build_plate_numbers: Set = None) -> None:
        # Clear out any old gcode
        self._scene.gcode_dict = {}  # type: ignore

        for node in DepthFirstIterator(self._scene.getRoot()):
            if node.callDecoration("getLayerData"):
                if not build_plate_numbers or node.callDecoration("getBuildPlateNumber") in build_plate_numbers:
                    # We can asume that all nodes have a parent as we're looping through the scene (and filter out root)
                    cast(SceneNode, node.getParent()).removeChild(node)

    def markSliceAll(self) -> None:
        for build_plate_number in range(self._application.getMultiBuildPlateModel().maxBuildPlate + 1):
            if build_plate_number not in self._build_plates_to_be_sliced:
                self._build_plates_to_be_sliced.append(build_plate_number)

    ##  Convenient function: mark everything to slice, emit state and clear layer data
    def needsSlicing(self) -> None:
        # CURA-6604: If there's no slicable object, do not (try to) trigger slice, which will clear all the current
        # gcode. This can break Gcode file loading if it tries to remove it afterwards.
        if not self.hasSlicableObject():
            return
        self.determineAutoSlicing()
        self.stopSlicing()
        self.markSliceAll()
        self.processingProgress.emit(0.0)
        if not self._use_timer:
            # With manually having to slice, we want to clear the old invalid layer data.
            self._clearLayerData()

    ##  A setting has changed, so check if we must reslice.
    # \param instance The setting instance that has changed.
    # \param property The property of the setting instance that has changed.
    def _onSettingChanged(self, instance: SettingInstance, property: str) -> None:
        if property == "value":  # Only reslice if the value has changed.
            self.needsSlicing()
            self._onChanged()

        elif property == "validationState":
            if self._use_timer:
                self._change_timer.stop()

    def _onStackErrorCheckFinished(self) -> None:
        self.determineAutoSlicing()
        if self._is_disabled:
            return

        if not self._slicing and self._build_plates_to_be_sliced:
            self.needsSlicing()
            self._onChanged()

    ##  Called when a sliced layer data message is received from the engine.
    #
    #   \param message The protobuf message containing sliced layer data.
    def _onLayerMessage(self, message: Arcus.PythonMessage) -> None:
        self._stored_layer_data.append(message)

    ##  Called when an optimized sliced layer data message is received from the engine.
    #
    #   \param message The protobuf message containing sliced layer data.
    def _onOptimizedLayerMessage(self, message: Arcus.PythonMessage) -> None:
        if self._start_slice_job_build_plate is not None:
            if self._start_slice_job_build_plate not in self._stored_optimized_layer_data:
                self._stored_optimized_layer_data[self._start_slice_job_build_plate] = []
            self._stored_optimized_layer_data[self._start_slice_job_build_plate].append(message)

    ##  Called when a progress message is received from the engine.
    #
    #   \param message The protobuf message containing the slicing progress.
    def _onProgressMessage(self, message: Arcus.PythonMessage) -> None:
        self.processingProgress.emit(message.amount)
        self.setState(BackendState.Processing)

    def _invokeSlice(self) -> None:
        if self._use_timer:
            # if the error check is scheduled, wait for the error check finish signal to trigger auto-slice,
            # otherwise business as usual
            if self._machine_error_checker is None:
                self._change_timer.stop()
                return

            if self._machine_error_checker.needToWaitForResult:
                self._change_timer.stop()
            else:
                self._change_timer.start()

    ##  Called when the engine sends a message that slicing is finished.
    #
    #   \param message The protobuf message signalling that slicing is finished.
    def _onSlicingFinishedMessage(self, message: Arcus.PythonMessage) -> None:
        self.setState(BackendState.Done)
        self.processingProgress.emit(1.0)


        # Left 노즐 타입 (syringe, fff, hot)
        machine_nozzle_id = self._global_container_stack.extruderList[0].variant.getName()

        # 슬라이스에 참여하는 익스트루더 active_extruder
        # a = self._global_container_stack.extruderList[1].getId()
        asdf = self._application.getMachineManager()
        # asdf = self._application.getMachineManager().getInstance().getActiveExtruderStacks()
        # asdf = self._application.getMachineManager().activeMachine
        # asdh = self._application.getMachineManager().activeStack
        # akjdl = self._application.getMachineActionManager()
        # machine_nozzle_id = self._global_container_stack.extruderList[0].getMetaDataEntry("varient", "value")
        # akjdl = self._application.getMachineManager().

        # container_registry = ContainerRegistry.getInstance()
        # my_metadata = container_registry.findContainersMetadata(id = "global_variant")[0]
        # self.preferred_variant_name = my_metadata.get("preferred_variant_name", "")



        
        nozzle_type = machine_nozzle_id.split(" ") # 노즐 타입과, 노즐게이지 분리

        # 프린트 온도 설정
        print_temperature_list =[]

        for index in range(1,6):
            extruder = self._global_container_stack.extruderList[index]
            print_temperature_list.append(extruder.getProperty("material_print_temperature","value"))

        left_extruder = self._global_container_stack.extruderList[0]
        print_temperature_list.append(left_extruder.getProperty("material_print_temperature","value"))
        print_temperature_list.append(self._global_container_stack.getProperty("material_bed_temperature","value"))
        print_temperature = " ".join(map(str,print_temperature_list))

        # UV 설정 - extruder에서 읽도록 바꿔야 함
        uv_value_list = [[],[],[],[],[]]
        for index in range(1,6):
            extruder = self._global_container_stack.extruderList[index]
            uv_value_list[0].append(extruder.getProperty("uv_enable","value")) #
            uv_value_list[1].append(extruder.getProperty("uv_per_layers","value")) 
            uv_value_list[2].append(extruder.getProperty("uv_type","value")) 
            uv_value_list[3].append(extruder.getProperty("uv_time","value"))
            uv_value_list[4].append(extruder.getProperty("uv_dimming","value")) # 미구현
        
        uv_per_layers = uv_value_list[1] # UV per layers
        uv_time = uv_value_list[3] # UV time
        uv_dimming = uv_value_list[4] # UV dimming - 미구현

        # 디스펜서 설정 - dsp_enable, shot, vac, int, shot.p, vac.p
        dispenser_value_list = [[],[],[],[],[],[]]

        for index in range(1,6):
            extruder = self._global_container_stack.extruderList[index]
            dispenser_value_list[0].append(extruder.getProperty("dispensor_enable","value"))
            dispenser_value_list[1].append(extruder.getProperty("dispensor_shot","value"))
            dispenser_value_list[2].append(extruder.getProperty("dispensor_vac","value"))
            dispenser_value_list[3].append(extruder.getProperty("dispensor_int","value"))
            dispenser_value_list[4].append(extruder.getProperty("dispensor_shot_power","value"))
            dispenser_value_list[5].append(extruder.getProperty("dispensor_vac_power","value"))
        
        dispenser_value_list[0].append(left_extruder.getProperty("dispensor_enable","value"))
        dispenser_value_list[1].append(left_extruder.getProperty("dispensor_shot","value"))
        dispenser_value_list[2].append(left_extruder.getProperty("dispensor_vac","value"))
        dispenser_value_list[3].append(left_extruder.getProperty("dispensor_int","value"))
        dispenser_value_list[4].append(left_extruder.getProperty("dispensor_shot_power","value"))
        dispenser_value_list[5].append(left_extruder.getProperty("dispensor_vac_power","value"))
        
        shot_times = " ".join(map(str,dispenser_value_list[1]))
        vac_times = " ".join(map(str,dispenser_value_list[2]))
        intervals = " ".join(map(str,dispenser_value_list[3]))
        shot_pressures = " ".join(map(str,dispenser_value_list[4]))
        vac_pressures = " ".join(map(str,dispenser_value_list[5]))

        try:
            gcode_list = self._scene.gcode_dict[self._start_slice_job_build_plate] #type: ignore Because we generate this attribute dynamically.
        except KeyError:  # Can occur if the g-code has been cleared while a slice message is still arriving from the other end.
            gcode_list = []
        
        uv_type = uv_value_list[2]
        if uv_type[0] == '365': # -------------------------------수정 사항 : 슬라이스에 참여하는 익스트루더에 따라 오프셋 변경
            uv_command = ['M172','M173'] # UV type: curing ON/OFF
        elif uv_type[0] == '405': 
            uv_command = ['M174','M175'] # UV type: disinfect ON/OFF

        for index, lines in enumerate(gcode_list):            
            replaced = lines.replace("{print_time}", str(self._application.getPrintInformation().currentPrintTime.getDisplayString(DurationFormat.Format.ISO8601)))
            replaced = replaced.replace("{filament_amount}", str(self._application.getPrintInformation().materialLengths))
            replaced = replaced.replace("{filament_weight}", str(self._application.getPrintInformation().materialWeights))
            replaced = replaced.replace("{filament_cost}", str(self._application.getPrintInformation().materialCosts))
            replaced = replaced.replace("{jobname}", str(self._application.getPrintInformation().jobName))
            
            if nozzle_type[0] != "FFF":
                # set the dispenser commands
                replaced = replaced.replace(";{shot_time}","M303 " + shot_times) 
                replaced = replaced.replace(";{vac_time}","M304 " + vac_times) 
                replaced = replaced.replace(";{interval}","M305 " + intervals)
                replaced = replaced.replace(";{shot_p}","M306 " + shot_pressures)
                replaced = replaced.replace(";{vac_p}","M307 " + vac_pressures)
                replaced = replaced.replace(";{print_temp}", "M308 "+ print_temperature)
                replaced = replaced.replace("M104", ";M104")
                replaced = replaced.replace("M105", ";M105")
                replaced = replaced.replace("M140", ";M140")
                replaced = replaced.replace("M82", ";M82")
                replaced = replaced.replace("M141", ";M141")
                replaced = replaced.replace("M109 S", ";M109 S") # 임시
                replaced = replaced.replace(";FLAVOR:Marlin", ";F/W : 7.6.8.0")
                replaced = replaced.replace("G92 E0\nG92 E0", "G92 E0")

            # add the UV commends - 수정 필요
            if replaced.startswith(";LAYER:"):
                layer_no = int(replaced[len(";LAYER:"):replaced.find("\n")])
                if (layer_no % uv_per_layers[0]) == 0:
                    replaced += "G90 G0 X0.0 Y0.0\nG91 G0 X42.5 Y0.0\n"+ uv_command[0]+"; UV ON\nG4 P" + str(uv_time[0]*1000) + "\n" + uv_command[1] + "; UV OFF\nG90 G0 X0.0 Y0.0\n\n"
            gcode_list[index] = replaced

        firstZ = gcode_list[2].find("Z")
        z_Location = gcode_list[2][firstZ + 1 : gcode_list[2].find("\n",firstZ)]
        to_be_jvalue = -20.0 - float(z_Location)

        for index, lines in enumerate(gcode_list):
            # E 명령어를 J명령어로 변경
            # Change to D command from T
            # SHOT & STOP sequence
            shot_flag = True
            replaced = lines
            if index < len(gcode_list) - 1:
                layer_commands = replaced.split("\n")
                for command_index, command in enumerate(layer_commands):

                    if nozzle_type[0] != "FFF": # 실린지 일 때만 E --> J 변환
                        if command.startswith("G1"):
                            # layer_commands[command_index] = layer_commands[command_index].replace("E","J")
                            if shot_flag == True: # shot 플래그 : G1에서 G0으로 변할 때만 명령어 삽입
                                comand_number= command.split()
                                if len(comand_number) > 3: # split한 후 인자의 갯수로 판단
                                    layer_commands[command_index] = "M301 ;SHOT\n" + layer_commands[command_index]
                                    shot_flag = False
                        elif command.startswith("G0"): 
                            if command.find("Z") != -1:
                                j_location = float(command[command.find("Z") + 1:])+ to_be_jvalue
                                j_location = round(j_location,2)
                                remove_z_value = command[:command.find("Z")]
                                layer_commands[command_index] = command[:command.find("Z")]+ "\nG0 C"+ str(j_location) # 기존 z값 + 
                            if shot_flag == False:
                                layer_commands[command_index] = "M330 ;STOP\n" + layer_commands[command_index]
                                shot_flag =True
                        elif command.startswith("T"):
                            layer_commands[command_index] = layer_commands[command_index].replace("T0","D6")
                            layer_commands[command_index] = layer_commands[command_index].replace("T","D")

                    layer_commands[command_index] = layer_commands[command_index].replace("-.","-0.")

                replaced = "\n".join(layer_commands)
            gcode_list[index] = replaced

        # Well Plate's clonning part
        dishType = self._global_container_stack.getProperty("machine_build_dish_type", "value")

        if (dishType[:dishType.find(':')] == "Culture Dish"):
            selected_extruder = "\nD1\nG0 A0. F1500\n"
            axisControl = "G0 X-42.5 Y0.0\nG92 X0.0 Y0.0\nG0 B20.0\n\n"
            gcode_list[1] += selected_extruder
            gcode_list[1] += axisControl
            
        if (dishType[:dishType.find(':')] == "Well Plate"):
            # "trip": {"line_seq":96/8, "spacing":9.0, "z": 10.8, "start_point": QPoint(74,49.5)}})                
            trip = {}
            
            for index in range(self._build_dish_model.count):
                dish = self._build_dish_model.getItem(index)
                if dish['product_id'] == dishType:
                    trip = dish['trip']
                    break

            well_plate_num = dishType[dishType.find(':')+1:]

            clone_num = int(well_plate_num)-1
            line_seq = trip["line_seq"] 
            distance = str(trip["spacing"]) 
            z_height = trip["z"]
            start_point = trip["start_point"]

            # 원점 재설정 
            selected_extruder = "\nD1\nG0 A0. F1500\n"
            axisControl = "G0 X" + str(start_point.x())+" Y" + str(start_point.y())+"; start point*\nG92 X0.0 Y0.0\nG0 B20.0\n\n"
            gcode_list[1] += selected_extruder
            gcode_list[1] += axisControl

            # Clonning process
            gcode_clone = gcode_list[2:-1]
            std_str = "G1 X0.0 Y0.0"
            new_position ="X0.0 Y0.0"
            line_ctrl = 1 # forward

            gcode_body = []
            for i in range(clone_num): # Clone number
                if (i+1) % line_seq ==0:
                    dire = "X-"+ distance
                    line_ctrl = abs(line_ctrl-1) # direction control
                else:
                    if line_ctrl == 1:
                        dire = "Y-"+ distance
                    if line_ctrl == 0:
                        dire = "Y"+ distance
                # control spacing about build plate after printing one model
                gcode_spacing = ";dy_spacing\nG92 E0\n"+std_str+"\nG0 C4.0\nG91 G0 "+dire+"\nG90 G0 C10.0\nG92 "+new_position+"\n\n" 
                gcode_clone.insert(0,gcode_spacing)
                gcode_body.append(gcode_clone)
                gcode_list[-1:-1]= gcode_body[i]  # put the clones in front of the end-code
                gcode_clone.remove(gcode_spacing)
            gcode_list.insert(-1,"G92 X"+str(11) +" Y"+str(start_point.y())+"\nG0 X0 Y0 Z0 A0 F800\n") 
        #
        
        self._slicing = False
        if self._slice_start_time:
            Logger.log("d", "Slicing took %s seconds", time() - self._slice_start_time )
        Logger.log("d", "Number of models per buildplate: %s", dict(self._numObjectsPerBuildPlate()))

        # See if we need to process the sliced layers job.
        active_build_plate = self._application.getMultiBuildPlateModel().activeBuildPlate
        if (
            self._layer_view_active and
            (self._process_layers_job is None or not self._process_layers_job.isRunning()) and
            active_build_plate == self._start_slice_job_build_plate and
            active_build_plate not in self._build_plates_to_be_sliced):

            self._startProcessSlicedLayersJob(active_build_plate)
        # self._onActiveViewChanged()
        self._start_slice_job_build_plate = None

        Logger.log("d", "See if there is more to slice...")
        # Somehow this results in an Arcus Error
        # self.slice()
        # Call slice again using the timer, allowing the backend to restart
        if self._build_plates_to_be_sliced:
            self.enableTimer()  # manually enable timer to be able to invoke slice, also when in manual slice mode
            self._invokeSlice()

    ##  Called when a g-code message is received from the engine.
    #
    #   \param message The protobuf message containing g-code, encoded as UTF-8.
    def _onGCodeLayerMessage(self, message: Arcus.PythonMessage) -> None:
        try:
            self._scene.gcode_dict[self._start_slice_job_build_plate].append(message.data.decode("utf-8", "replace")) #type: ignore #Because we generate this attribute dynamically.
        except KeyError:  # Can occur if the g-code has been cleared while a slice message is still arriving from the other end.
            pass  # Throw the message away.

    ##  Called when a g-code prefix message is received from the engine.
    #
    #   \param message The protobuf message containing the g-code prefix,
    #   encoded as UTF-8.
    def _onGCodePrefixMessage(self, message: Arcus.PythonMessage) -> None:
        try:
            self._scene.gcode_dict[self._start_slice_job_build_plate].insert(0, message.data.decode("utf-8", "replace")) #type: ignore #Because we generate this attribute dynamically.
        except KeyError:  # Can occur if the g-code has been cleared while a slice message is still arriving from the other end.
            pass  # Throw the message away.

    ##  Creates a new socket connection.
    def _createSocket(self, protocol_file: str = None) -> None:
        if not protocol_file:
            plugin_path = PluginRegistry.getInstance().getPluginPath(self.getPluginId())
            if not plugin_path:
                Logger.log("e", "Could not get plugin path!", self.getPluginId())
                return
            protocol_file = os.path.abspath(os.path.join(plugin_path, "Cura.proto"))
        super()._createSocket(protocol_file)
        self._engine_is_fresh = True

    ##  Called when anything has changed to the stuff that needs to be sliced.
    #
    #   This indicates that we should probably re-slice soon.
    def _onChanged(self, *args: Any, **kwargs: Any) -> None:
        self.needsSlicing()
        if self._use_timer:
            # if the error check is scheduled, wait for the error check finish signal to trigger auto-slice,
            # otherwise business as usual
            if self._machine_error_checker is None:
                self._change_timer.stop()
                return

            if self._machine_error_checker.needToWaitForResult:
                self._change_timer.stop()
            else:
                self._change_timer.start()

    ##  Called when a print time message is received from the engine.
    #
    #   \param message The protobuf message containing the print time per feature and
    #   material amount per extruder
    def _onPrintTimeMaterialEstimates(self, message: Arcus.PythonMessage) -> None:
        material_amounts = []
        for index in range(message.repeatedMessageCount("materialEstimates")):
            material_amounts.append(message.getRepeatedMessage("materialEstimates", index).material_amount)

        times = self._parseMessagePrintTimes(message)
        self.printDurationMessage.emit(self._start_slice_job_build_plate, times, material_amounts)

    ##  Called for parsing message to retrieve estimated time per feature
    #
    #   \param message The protobuf message containing the print time per feature
    def _parseMessagePrintTimes(self, message: Arcus.PythonMessage) -> Dict[str, float]:
        result = {
            "inset_0": message.time_inset_0,
            "inset_x": message.time_inset_x,
            "skin": message.time_skin,
            "infill": message.time_infill,
            "support_infill": message.time_support_infill,
            "support_interface": message.time_support_interface,
            "support": message.time_support,
            "skirt": message.time_skirt,
            "prime_tower": message.time_prime_tower,
            "travel": message.time_travel,
            "retract": message.time_retract,
            "none": message.time_none
        }
        return result

    ##  Called when the back-end connects to the front-end.
    def _onBackendConnected(self) -> None:
        if self._restart:
            self._restart = False
            self._onChanged()

    ##  Called when the user starts using some tool.
    #
    #   When the user starts using a tool, we should pause slicing to prevent
    #   continuously slicing while the user is dragging some tool handle.
    #
    #   \param tool The tool that the user is using.
    def _onToolOperationStarted(self, tool: Tool) -> None:
        self._tool_active = True  # Do not react on scene change
        self.disableTimer()
        # Restart engine as soon as possible, we know we want to slice afterwards
        if not self._engine_is_fresh:
            self._terminate()
            self._createSocket()

    ##  Called when the user stops using some tool.
    #
    #   This indicates that we can safely start slicing again.
    #
    #   \param tool The tool that the user was using.
    def _onToolOperationStopped(self, tool: Tool) -> None:
        self._tool_active = False  # React on scene change again
        self.determineAutoSlicing()  # Switch timer on if appropriate
        # Process all the postponed scene changes
        while self._postponed_scene_change_sources:
            source = self._postponed_scene_change_sources.pop(0)
            self._onSceneChanged(source)

    def _startProcessSlicedLayersJob(self, build_plate_number: int) -> None:
        self._process_layers_job = ProcessSlicedLayersJob(self._stored_optimized_layer_data[build_plate_number])
        self._process_layers_job.setBuildPlate(build_plate_number)
        self._process_layers_job.finished.connect(self._onProcessLayersFinished)
        self._process_layers_job.start()

    ##  Called when the user changes the active view mode.
    def _onActiveViewChanged(self) -> None:
        view = self._application.getController().getActiveView()
        if view:
            active_build_plate = self._application.getMultiBuildPlateModel().activeBuildPlate
            if view.getPluginId() == "SimulationView":  # If switching to layer view, we should process the layers if that hasn't been done yet.
                self._layer_view_active = True
                # There is data and we're not slicing at the moment
                # if we are slicing, there is no need to re-calculate the data as it will be invalid in a moment.
                # TODO: what build plate I am slicing
                if (active_build_plate in self._stored_optimized_layer_data and
                    not self._slicing and
                    not self._process_layers_job and
                    active_build_plate not in self._build_plates_to_be_sliced):

                    self._startProcessSlicedLayersJob(active_build_plate)
            else:
                self._layer_view_active = False

    ##  Called when the back-end self-terminates.
    #
    #   We should reset our state and start listening for new connections.
    def _onBackendQuit(self) -> None:
        if not self._restart:
            if self._process: # type: ignore
                Logger.log("d", "Backend quit with return code %s. Resetting process and socket.", self._process.wait()) # type: ignore
                self._process = None # type: ignore

    ##  Called when the global container stack changes
    def _onGlobalStackChanged(self) -> None:
        if self._global_container_stack:
            self._global_container_stack.propertyChanged.disconnect(self._onSettingChanged)
            self._global_container_stack.containersChanged.disconnect(self._onChanged)

            for extruder in self._global_container_stack.extruderList:
                extruder.propertyChanged.disconnect(self._onSettingChanged)
                extruder.containersChanged.disconnect(self._onChanged)

        self._global_container_stack = self._application.getMachineManager().activeMachine

        if self._global_container_stack:
            self._global_container_stack.propertyChanged.connect(self._onSettingChanged)  # Note: Only starts slicing when the value changed.
            self._global_container_stack.containersChanged.connect(self._onChanged)

            for extruder in self._global_container_stack.extruderList:
                extruder.propertyChanged.connect(self._onSettingChanged)
                extruder.containersChanged.connect(self._onChanged)
            self._onChanged()

    def _onProcessLayersFinished(self, job: ProcessSlicedLayersJob) -> None:
        if job.getBuildPlate() in self._stored_optimized_layer_data:
            del self._stored_optimized_layer_data[job.getBuildPlate()]
        else:
            Logger.log("w", "The optimized layer data was already deleted for buildplate %s", job.getBuildPlate())
        self._process_layers_job = None
        Logger.log("d", "See if there is more to slice(2)...")
        self._invokeSlice()

    ##  Connect slice function to timer.
    def enableTimer(self) -> None:
        if not self._use_timer:
            self._change_timer.timeout.connect(self.slice)
            self._use_timer = True

    ##  Disconnect slice function from timer.
    #   This means that slicing will not be triggered automatically
    def disableTimer(self) -> None:
        if self._use_timer:
            self._use_timer = False
            self._change_timer.timeout.disconnect(self.slice)

    def _onPreferencesChanged(self, preference: str) -> None:
        if preference != "general/auto_slice":
            return
        auto_slice = self.determineAutoSlicing()
        if auto_slice:
            self._change_timer.start()

    ##   Tickle the backend so in case of auto slicing, it starts the timer.
    def tickle(self) -> None:
        if self._use_timer:
            self._change_timer.start()

    def _extruderChanged(self) -> None:
        if not self._multi_build_plate_model:
            Logger.log("w", "CuraEngineBackend does not have multi_build_plate_model assigned!")
            return
        for build_plate_number in range(self._multi_build_plate_model.maxBuildPlate + 1):
            if build_plate_number not in self._build_plates_to_be_sliced:
                self._build_plates_to_be_sliced.append(build_plate_number)
        self._invokeSlice()
