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
        self.ctx = context
        self.simulation = ThreadSimulation()
        self.simulation.start()
        self._foggy_level = 0.0
        self._brightness_level = 1.0

        #Timer update donnees
        self.timer=QTimer()
        self.timer.timeout.connect(self.updateGUI)
        self.timer.start(500)

    # Troisième test de communication : modification directe d'un composant QML.
    def test3(self):
        # Recherche des enfants par leur attribut objectName, récupération de la valeur de leur propriété text
        foggy_level= self.win.findChild(QObject, "slider_foggy_level").property("value")
        password = self.win.findChild(QObject, "slider_brightness_level").property("value")
        #self.win.findChild(QObject, "labelCo").setProperty("text", foggy_level)
        self.simulation.set_foggy_level(foggy_level,password)
        return 0
    
    def stop_simulation(self):
        self.timer.stop()
        self.simulation.stop()
    
    def updateGUI (self):
        target_speed= self.simulation.get_target_speed()
        #print("timer finished",target_speed )
        self.win.findChild(QObject, "labelCo").setProperty("text", target_speed)