import sys
from PyQt5.QtCore import QObject, pyqtSlot, QVariant
from PyQt5.QtCore import QTimer
from Thread_simulation import ThreadSimulation
 
# Classe servant dans l'interaction.
class MainApp(QObject):
    def __init__(self, context, parent=None):
        super(MainApp, self).__init__(parent)
        # Recherche d'un enfant appelé myButton dont le signal clicked sera connecté à la fonction test3
        self.win = parent
        self.win.findChild(QObject, "Apply_Button").clicked.connect(self.test3)
        self.win.findChild(QObject, "Recenter_Button").clicked.connect(self.center_camera)
        self.ctx = context
        self.simulation = ThreadSimulation()
        self.simulation.start()
        self._foggy_level = 0.0
        self._brightness_level = 1.0
        self._conso = 10.0
        self._age = 0.0
        self._behavior = 0.0

        #Timer update donnees
        self.timer=QTimer()
        self.timer.timeout.connect(self.updateGUI)
        self.timer.start(500)

    # Troisième test de communication : modification directe d'un composant QML.
    def test3(self):
        # Recherche des enfants par leur attribut objectName, récupération de la valeur de leur propriété text
        foggy_level= self.win.findChild(QObject, "slider_foggy_level").property("value")
        brightness_level = self.win.findChild(QObject, "slider_brightness_level").property("value")
        conso = self.win.findChild(QObject, "slider_consomation").property("value")
        age = self.win.findChild(QObject, "slider_state_car").property("value")
        behavior = self.win.findChild(QObject, "slider_behavior_driver").property("value")

        self.simulation.set_foggy_level(foggy_level,brightness_level)
        self.simulation.set_extern_inputs(conso,age,behavior)
        return 0

    def center_camera(self):
        self.simulation.center_camera()
    
    def stop_simulation(self):
        self.timer.stop()
        self.simulation.stop()
    
    def updateGUI (self):
        target_speed= self.simulation.get_target_speed()
        output = self.simulation.get_outputs_fuzzy_systems()
        #print("timer finished",target_speed )
        self.win.findChild(QObject, "targetSpeed_level").setProperty("text", target_speed)
        self.win.findChild(QObject, "limitSpeed_level").setProperty("text", output[0])
        self.win.findChild(QObject, "foggy_level").setProperty("text", output[1])
        self.win.findChild(QObject, "brightness_level").setProperty("text", output[2])
        self.win.findChild(QObject, "conso_level").setProperty("text", output[3])
        self.win.findChild(QObject, "age_car_level").setProperty("text", output[4])
        self.win.findChild(QObject, "behavior_level").setProperty("text", output[5])
        self.win.findChild(QObject, "visibility_level").setProperty("text", float(output[7]))
        self.win.findChild(QObject, "intrinsicSpeed_level").setProperty("text", float(output[8]))
        self.win.findChild(QObject, "accessibleSpeed_level").setProperty("text", float(output[9]))
        self.win.findChild(QObject, "behavior_level2").setProperty("text", output[5])



       