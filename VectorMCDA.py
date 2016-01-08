# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name			 	 : Vector geoMCDA
Description          : 
Date                 :  
copyright            : (C) 2010 by Gianluca Massei
email                : g_massa@libero.it

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import resources
# Import the code for the dialog
import os.path, sys
import webbrowser

class vMCDA:

	def __init__(self, iface):
		# Save the reference to the QGIS interface
		self.iface = iface
		#initialize plugin directory
		self.pluginDir = os.path.dirname(__file__)
		# initialize locale
		locale = QSettings().value("locale/userLocale")[0:2]
		localePath = os.path.join(self.pluginDir, 'i18n', 'opeNoise_{}.qm'.format(locale))

		if os.path.exists(localePath):
			self.translator = QTranslator()
			self.translator.load(localePath)

			if qVersion() > '4.3.3':
				QCoreApplication.installTranslator(self.translator)

	def initGui(self):	# aggiunge alla GUI di QGis i pulsanti per richiamare il plugin
		# creiamo l'azione che lancerà il plugin
		
		self.geoMCDAmenu = QMenu(QCoreApplication.translate("vectorMCDA", "&vectorMCDA"))
		self.geoMCDAmenu.setIcon(QIcon(":/plugins/VectorMCDA/icons/Tree.png"))
        
		self.actionWeightedSum = QAction("geoWeightedSum",self.iface.mainWindow() )
		self.actionWeightedSum.triggered.connect(self.runGeoWeightedSum )
		
		self.actionTOPSIS = QAction( "geoTOPSIS", self.iface.mainWindow() )
		self.actionTOPSIS.triggered.connect(self.runGeoTOPSIS )
		
		self.actionFuzzy = QAction( "geoFuzzy", self.iface.mainWindow() )
		self.actionFuzzy.triggered.connect(self.runGeoFuzzy )
		
		self.actionElectre = QAction( "geoConcordance", self.iface.mainWindow() )
		self.actionElectre.triggered.connect(self.runGeoElectre )
		
		self.actionPromethee = QAction( "geoPromethee", self.iface.mainWindow() )
		self.actionPromethee.triggered.connect(self.runGeoPromethee )
				
		self.actionRSDB = QAction( "geoRSDB", self.iface.mainWindow() )
		self.actionRSDB.triggered.connect(self.runGeoRSDB )
		
		self.actionRSDB = QAction( "geoRULES", self.iface.mainWindow() )
		self.actionRSDB.triggered.connect(self.runGeoRULES )
		
		self.actionXMCDA = QAction( "geoXMCDA", self.iface.mainWindow() )
		self.actionXMCDA.triggered.connect(self.runGeoXMCDA )
		
		# aggiunge il plugin alla toolbar
		self.geoMCDAmenu.addActions([self.actionWeightedSum,self.actionTOPSIS,self.actionFuzzy,\
			self.actionElectre,self.actionPromethee,self.actionRSDB,self.actionXMCDA])
		self.menu = self.iface.pluginMenu()
		self.menu.addMenu( self.geoMCDAmenu ) 
		

	def unload(self):	# rimuove dalla GUI i pulsanti aggiunti dal plugin
		#self.iface.removeToolBarIcon( self.action )
		self.iface.removePluginMenu( "&geoWeightedSum", self.actionWeightedSum )
		self.iface.removePluginMenu( "&geoTOPSIS", self.actionTOPSIS )
		self.iface.removePluginMenu( "&geoFuzzy", self.actionFuzzy )
		self.iface.removePluginMenu( "&geoConcordance", self.actionElectre )
		self.iface.removePluginMenu( "&geoPromethee", self.actionPromethee )
		self.iface.removePluginMenu( "&geoRSDB", self.actionRSDB )
		self.iface.removePluginMenu( "&geoRULES", self.actionRSDB )
		self.iface.removePluginMenu( "&geoXMCDA", self.actionXMCDA )
		 

	def runGeoWeightedSum(self):	# richiamato al click sull'azione
		from geoWeightedSum import geoWeightedSumDialog
		self.activeLayer = self.iface.activeLayer()
		if ((self.activeLayer == None) or (self.activeLayer.type() != QgsMapLayer.VectorLayer)):
			QMessageBox.warning(self.iface.mainWindow(), "VectorMCDA",
			("No active layer found\n" "Please make one or more vector layer " "active"), QMessageBox.Ok, QMessageBox.Ok)
			webbrowser.open("http://maplab.alwaysdata.net")
			return
		dlg = geoWeightedSumDialog(self.iface)
		dlg.exec_()
		
	def runGeoTOPSIS(self):	# richiamato al click sull'azione
		from geoTOPSIS import geoTOPSISDialog
		self.activeLayer = self.iface.activeLayer()
		if ((self.activeLayer == None) or (self.activeLayer.type() != QgsMapLayer.VectorLayer)):
			QMessageBox.warning(self.iface.mainWindow(), "VectorMCDA",
			("No active layer found\n" "Please make one or more vector layer " "active"), QMessageBox.Ok, QMessageBox.Ok)
			webbrowser.open("http://maplab.alwaysdata.net")
			return
		dlg = geoTOPSISDialog(self.iface)
		dlg.exec_()
	
	def runGeoFuzzy(self):	# richiamato al click sull'azione
		from geoFuzzy import geoFuzzyDialog
		self.activeLayer = self.iface.activeLayer()
		if ((self.activeLayer == None) or (self.activeLayer.type() != QgsMapLayer.VectorLayer)):
			QMessageBox.warning(self.iface.mainWindow(), "VectorMCDA",
			("No active layer found\n" "Please make one or more vector layer " "active"), QMessageBox.Ok, QMessageBox.Ok)
			webbrowser.open("http://maplab.alwaysdata.net")
			return
		dlg = geoFuzzyDialog(self.iface)
		dlg.exec_()
		
	def runGeoElectre(self):	# richiamato al click sull'azione
		from geoElectre import geoElectreDialog
		self.activeLayer = self.iface.activeLayer()
		if ((self.activeLayer == None) or (self.activeLayer.type() != QgsMapLayer.VectorLayer)):
			QMessageBox.warning(self.iface.mainWindow(), "VectorMCDA",
			("No active layer found\n" "Please make one or more vector layer " "active"), QMessageBox.Ok, QMessageBox.Ok)
			webbrowser.open("http://maplab.alwaysdata.net")
			return
		dlg = geoElectreDialog(self.iface)
		dlg.exec_()
		
	def runGeoPromethee(self):	# richiamato al click sull'azione
		from geoPromethee import geoPrometheeDialog
		self.activeLayer = self.iface.activeLayer()
		if ((self.activeLayer == None) or (self.activeLayer.type() != QgsMapLayer.VectorLayer)):
			QMessageBox.warning(self.iface.mainWindow(), "VectorMCDA",
			("No active layer found\n" "Please make one or more vector layer " "active"), QMessageBox.Ok, QMessageBox.Ok)
			webbrowser.open("http://maplab.alwaysdata.net")
			return
		dlg = geoPrometheeDialog(self.iface)
		dlg.exec_()
		
		
	def runGeoRSDB(self):	# richiamato al click sull'azione
		from geoRSDB import geoRSDBDialog
		self.activeLayer = self.iface.activeLayer()
		if ((self.activeLayer == None) or (self.activeLayer.type() != QgsMapLayer.VectorLayer)):
			QMessageBox.warning(self.iface.mainWindow(), "VectorMCDA",
			("No active layer found\n" "Please make one or more vector layer " "active"), QMessageBox.Ok, QMessageBox.Ok)
			webbrowser.open("http://maplab.alwaysdata.net")
			return
		dlg = geoRSDBDialog(self.iface)
		dlg.exec_()
		
	def runGeoRULES(self):	# richiamato al click sull'azione
		from geoRULES import geoRULESDialog
		self.activeLayer = self.iface.activeLayer()
		if ((self.activeLayer == None) or (self.activeLayer.type() != QgsMapLayer.VectorLayer)):
			QMessageBox.warning(self.iface.mainWindow(), "VectorMCDA",
			("No active layer found\n" "Please make one or more vector layer " "active"), QMessageBox.Ok, QMessageBox.Ok)
			webbrowser.open("http://maplab.alwaysdata.net")
			return
		dlg = geoRULESDialog(self.iface)
		dlg.exec_()
		
	def runGeoXMCDA(self):	# richiamato al click sull'azione
		from geoXMCDA import geoXMCDADialog
		self.activeLayer = self.iface.activeLayer()
		if ((self.activeLayer == None) or (self.activeLayer.type() != QgsMapLayer.VectorLayer)):
			QMessageBox.warning(self.iface.mainWindow(), "VectorMCDA",
			("No active layer found\n" "Please make one or more vector layer " "active"), QMessageBox.Ok, QMessageBox.Ok)
			webbrowser.open("http://maplab.alwaysdata.net")
			return
		dlg = geoXMCDADialog(self.iface)
		dlg.exec_()

