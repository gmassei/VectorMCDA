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
import resources
# Import the code for the dialog
import os.path, sys

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
		self.geoMCDAmenu.setIcon(QIcon(":/plugins/VectorMCDA/icons/decision.png"))
        
		self.actionWeightedSum = QAction("geoWeightedSum",self.iface.mainWindow() )
		self.actionWeightedSum.triggered.connect(self.runGeoWeightedSum )
		
		self.actionTOPSIS = QAction( "geoTOPSIS", self.iface.mainWindow() )
		self.actionTOPSIS.triggered.connect(self.runGeoTOPSIS )
		
		self.actionFuzzy = QAction( "geoFuzzy", self.iface.mainWindow() )
		self.actionFuzzy.triggered.connect(self.runGeoFuzzy )
		
		self.actionElectre = QAction( "geoElectre", self.iface.mainWindow() )
		self.actionElectre.triggered.connect(self.runGeoElectre )
				
		self.actionRSDB = QAction( "geoRSDB", self.iface.mainWindow() )
		self.actionRSDB.triggered.connect(self.runGeoRSDB )
		
		self.actionXMCDA = QAction( "geoXMCDA", self.iface.mainWindow() )
		self.actionXMCDA.triggered.connect(self.runGeoXMCDA )
		
		# aggiunge il plugin alla toolbar
		self.geoMCDAmenu.addActions([self.actionWeightedSum,self.actionTOPSIS,\
			self.actionFuzzy,self.actionElectre,self.actionRSDB,self.actionXMCDA])
		self.menu = self.iface.pluginMenu()
		self.menu.addMenu( self.geoMCDAmenu ) 
		

	def unload(self):	# rimuove dalla GUI i pulsanti aggiunti dal plugin
		#self.iface.removeToolBarIcon( self.action )
		self.iface.removePluginMenu( "&geoWeightedSum", self.actionWeightedSum )
		self.iface.removePluginMenu( "&geoTOPSIS", self.actionTOPSIS )
		self.iface.removePluginMenu( "&geoFuzzy", self.actionFuzzy )
		self.iface.removePluginMenu( "&geoElectre", self.actionElectre )
		self.iface.removePluginMenu( "&geoRSDB", self.actionRSDB )
		self.iface.removePluginMenu( "&geoXMCDA", self.actionXMCDA )
		 

	def runGeoWeightedSum(self):	# richiamato al click sull'azione
		from geoWeightedSum import geoWeightedSumDialog
		dlg = geoWeightedSumDialog(self.iface)
		dlg.exec_()
		
	def runGeoTOPSIS(self):	# richiamato al click sull'azione
		from geoTOPSIS import geoTOPSISDialog
		dlg = geoTOPSISDialog(self.iface)
		dlg.exec_()
	
	def runGeoFuzzy(self):	# richiamato al click sull'azione
		from geoFuzzy import geoFuzzyDialog
		dlg = geoFuzzyDialog(self.iface)
		dlg.exec_()
		
	def runGeoElectre(self):	# richiamato al click sull'azione
		from geoElectre import geoElectreDialog
		dlg = geoElectreDialog(self.iface)
		dlg.exec_()
		
		
	def runGeoRSDB(self):	# richiamato al click sull'azione
		from geoRSDB import geoRSDBDialog
		dlg = geoRSDBDialog(self.iface)
		dlg.exec_()
		
	def runGeoXMCDA(self):	# richiamato al click sull'azione
		from geoXMCDA import geoXMCDADialog
		dlg = geoXMCDADialog(self.iface)
		dlg.exec_()

