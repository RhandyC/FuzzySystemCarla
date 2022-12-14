import sys
import logging
import threading
import time

from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtWidgets import QPushButton,QRadioButton

from agents.navigation.basic_agent import BasicAgent
#from Thread_simulation import ThreadSimulation
from MainApp import MainApp

try:
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    # Création d'un objet QQmlContext pour communiquer avec le code QML
    ctx = engine.rootContext()

    engine.quit.connect(app.quit)
    engine.load('main.qml')
    win = engine.rootObjects()[0]
    

    py_mainapp = MainApp(ctx, win)
    ctx.setContextProperty("py_MainApp", py_mainapp)

    win.show()
    #simulation = ThreadSimulation()
    #simulation.start()
    sys.exit(app.exec())
    
finally:
    py_mainapp.stop_simulation()
    #simulation.stop()
    print("App finished")

