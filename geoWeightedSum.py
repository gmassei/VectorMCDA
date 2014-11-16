# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name			: geoWeightedSum
Description		: geographical MCDA with Weighted Sum Model (WSM)
Date			: June 20, 2014
copyright		: Gianluca Massei  (developper) 
email			: (g_massa@libero.it)

 ***************************************************************************/

/***************************************************************************
 *																		 *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.    			   *
 *																		 *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui

from qgis.core import *
from qgis.gui import *


import os
import webbrowser
import htmlGraph
import csv

try:
	import numpy as np
	import matplotlib.pyplot as plt
except ImportError, e:
	QMessageBox.information(None, QCoreApplication.translate('geoWeightedSum', "Plugin error"), \
	QCoreApplication.translate('geoWeightedSum', "You can't get all the graphics output . [Message: %s]" % e))
	

from ui_geoWeightedSum import Ui_Dialog

class geoWeightedSumDialog(QDialog, Ui_Dialog):
	def __init__(self, iface):
		'''costruttore'''
		QDialog.__init__(self, iface.mainWindow())
		self.setupUi(self)
		self.iface = iface
		self.activeLayer = self.iface.activeLayer()
		for i in range(1,self.toolBox.count()):
			self.toolBox.setItemEnabled (i,False)

		QObject.connect(self.SetBtnQuit, SIGNAL("rejected()"),self, SLOT("reject()"))
		QObject.connect(self.SetBtnAbout, SIGNAL("clicked()"), self.about)
		QObject.connect(self.SetBtnHelp, SIGNAL("clicked()"),self.open_help)
		QObject.connect(self.EnvAddFieldBtn, SIGNAL( "clicked()" ), self.AddField)
		#QObject.connect(self.EnvRemoveFieldBtn, SIGNAL( "clicked()" ), self.RemoveField)
		QObject.connect(self.EnvGetWeightBtn, SIGNAL( "clicked()" ), self.ElaborateAttributeTable)
		QObject.connect(self.EnvCalculateBtn, SIGNAL( "clicked()" ), self.AnalyticHierarchyProcess)
		QObject.connect(self.RenderBtn,SIGNAL("clicked()"), self.RenderLayer)
		QObject.connect(self.GraphBtn, SIGNAL("clicked()"), self.BuildOutput)
		QObject.connect(self.AnlsBtnQuit, SIGNAL("rejected()"),self, SLOT("reject()"))
		
		sourceIn=str(self.iface.activeLayer().source())
		pathSource=os.path.dirname(sourceIn)
		outFile="geoWeightedSum.shp"
		sourceOut=os.path.join(pathSource,outFile)

		self.EnvMapNameLbl.setText(self.activeLayer.name())
		self.EnvlistFieldsCBox.addItems(self.GetFieldNames(self.activeLayer))
		self.LabelListFieldsCBox.addItems([str(f.name()) for f in self.activeLayer.pendingFields()])
		

#################################################################################
		Envfields=self.GetFieldNames(self.activeLayer) #field list
		self.EnvTableWidget.setColumnCount(len(Envfields))
		self.EnvTableWidget.setHorizontalHeaderLabels(Envfields)
		self.EnvTableWidget.setRowCount(len(Envfields))
		self.EnvTableWidget.setVerticalHeaderLabels(Envfields)
		EnvSetLabel=["Weigths","Preference"]
		self.EnvParameterWidget.setColumnCount(len(Envfields))
		self.EnvParameterWidget.setHorizontalHeaderLabels(Envfields)
		self.EnvParameterWidget.setRowCount(2)
		self.EnvParameterWidget.setVerticalHeaderLabels(EnvSetLabel)
		for r in range(len(Envfields)):
			self.EnvTableWidget.setItem(r,r,QTableWidgetItem("1.0"))
			self.EnvParameterWidget.setItem(0,r,QTableWidgetItem("1.0"))
			self.EnvParameterWidget.setItem(1,r,QTableWidgetItem("gain"))
		#retrieve signal for modified cell
		self.EnvTableWidget.cellChanged[(int,int)].connect(self.CompleteMatrix)
		self.EnvParameterWidget.cellClicked[(int,int)].connect(self.ChangeValue)
###############################ContextMenu########################################
#		self.EnvTableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
#		self.EnvTableWidget.customContextMenuRequested.connect(self.removePopup)
		headers = self.EnvParameterWidget.horizontalHeader()
		headers.setContextMenuPolicy(Qt.CustomContextMenu)
		headers.customContextMenuRequested.connect(self.removePopup)
#################################################################################
		for i in range(1,self.toolBox.count()):
			self.toolBox.setItemEnabled (i,True)

		setting=self.csv2setting()
		try:
			self.setting2table(setting)
		except:
			pass
		


	def GetFieldNames(self, layer):
		"""retrive field names from active map/layer"""
		fieldMap = layer.pendingFields()
		fieldList=[f.name() for f in fieldMap if f.typeName()!='String']
		return fieldList # sorted( field_list, cmp=locale.strcoll )


	def outFile(self):
		"""Display file dialog for output  file"""
		self.OutlEdt.clear()
		outvLayer = QFileDialog.getSaveFileName(self, "Output map",".", "ESRI Shapefile (*.shp)")
		if not outvLayer.isEmpty():
			self.OutlEdt.clear()
			self.OutlEdt.insert(outvLayer)
		return outvLayer


	def updateTable(self):
		"""Prepare and compile tbale in GUI"""
		pathSource=os.path.dirname(str(self.iface.activeLayer().source()))
		Envfields=[f for f in self.GetFieldNames(self.activeLayer)]
############################################################################################################################
		self.EnvTableWidget.setColumnCount(len(Envfields))
		self.EnvTableWidget.setHorizontalHeaderLabels(Envfields)
		self.EnvTableWidget.setRowCount(len(Envfields))
		self.EnvTableWidget.setVerticalHeaderLabels(Envfields)

		EnvSetLabel=["Weigths","Preference"]
		self.EnvParameterWidget.setColumnCount(len(Envfields))
		self.EnvParameterWidget.setHorizontalHeaderLabels(Envfields)
		self.EnvParameterWidget.setRowCount(2)
		self.EnvParameterWidget.setVerticalHeaderLabels(EnvSetLabel)

		for r in range(len(Envfields)):
			self.EnvParameterWidget.setItem(0,r,QTableWidgetItem("1.0"))
			self.EnvParameterWidget.setItem(1,r,QTableWidgetItem("gain"))
		return 0


	def AddField(self):
		"""Add field to table in GUI"""
		f=self.EnvlistFieldsCBox.currentText()
		self.EnvTableWidget.insertColumn(self.EnvTableWidget.columnCount())
		self.EnvTableWidget.insertRow(self.EnvTableWidget.rowCount())
		self.EnvTableWidget.setHorizontalHeaderItem((self.EnvTableWidget.columnCount()-1),QTableWidgetItem(f))
		self.EnvTableWidget.setVerticalHeaderItem((self.EnvTableWidget.rowCount()-1),QTableWidgetItem(f))
		##############
		self.EnvParameterWidget.insertColumn(self.EnvParameterWidget.columnCount())
		self.EnvParameterWidget.setHorizontalHeaderItem((self.EnvParameterWidget.columnCount()-1),QTableWidgetItem(f))
		self.EnvParameterWidget.setItem(0,(self.EnvParameterWidget.columnCount()-1),QTableWidgetItem("1.0"))
		self.EnvParameterWidget.setItem(1,(self.EnvParameterWidget.columnCount()-1),QTableWidgetItem("gain"))
		return 0


	def removePopup(self, pos):
		i= self.EnvParameterWidget.selectionModel().currentIndex().column()
		if i != -1:
			menu = QMenu()
			removeAction = menu.addAction("Remove field")
			action = menu.exec_(self.mapToGlobal(pos))
			if action == removeAction:
				self.RemoveField(i)
				self.EnvParameterWidget.setCurrentCell(-1,-1)
		else:
			QMessageBox.warning(self.iface.mainWindow(), "geoWeightedSum",
			("column or row must be selected"), QMessageBox.Ok, QMessageBox.Ok)
		return 0

	def RemoveField(self,i):
		"""Remove field in table in GUI"""
		self.EnvTableWidget.removeColumn(i)
		self.EnvTableWidget.removeRow(i)
		self.EnvParameterWidget.removeColumn(i)
		return 0


	def CompleteMatrix(self):
		"""Autocomplete matrix of  pairwise comparison"""
		try:
			cell=self.EnvTableWidget.currentItem()
			if cell.text()!=None and type(float(cell.text())==float):
				val=round(float(cell.text())**(-1),2)
				self.EnvTableWidget.setItem(cell.column(),cell.row(),QTableWidgetItem(str(val)))
			return 0
		except ValueError:
			QMessageBox.warning(self.iface.mainWindow(), "geoWeightedSum",
			("Input error\n" "Please insert numeric value "\
			"active"), QMessageBox.Ok, QMessageBox.Ok)


	def ChangeValue(self):
		"""Event for change gain/cost"""
		cell=self.EnvParameterWidget.currentItem()
		val=cell.text()
		if val=="cost":
			self.EnvParameterWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("gain"))
		elif val=="gain":
			self.EnvParameterWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("cost"))
		else:
			self.EnvParameterWidget.setItem(cell.row(),cell.column(),QTableWidgetItem(str(val)))
		return 0

	def setting2csv(self):
		currentDIR = (os.path.dirname(str(self.activeLayer.source())))
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() for f in range(self.EnvTableWidget.columnCount())]
		weight=[float(self.EnvParameterWidget.item(0, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		preference=[str(self.EnvParameterWidget.item(1, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		csvFile=open(os.path.join(currentDIR,'setWeightedSum.csv'),"wb")
		write=csv.writer(csvFile,delimiter=";",quotechar='"',quoting=csv.QUOTE_NONNUMERIC)
		write.writerow(criteria)
		write.writerow(weight)
		write.writerow(preference)
		csvFile.close()
		
	def csv2setting(self):
		currentDIR = (os.path.dirname(str(self.activeLayer.source())))
		setting=[]
		try:
			with open(os.path.join(currentDIR,'setWeightedSum.csv')) as csvFile:
				csvReader = csv.reader(csvFile, delimiter=";", quotechar='"')
				for row in csvReader:
					setting.append(row)
			return setting
		except:
			QgsMessageLog.logMessage("Problem in reading setting file","geo",QgsMessageLog.WARNING)

	def setting2table(self,setting):
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() for f in range(self.EnvTableWidget.columnCount())]
		for i in range(len(criteria)):
			for l in range(len(setting[0])):
				if criteria[i]==setting[0][l]:
					self.EnvParameterWidget.setItem(0,i,QTableWidgetItem(str(setting[1][l])))
					self.EnvParameterWidget.setItem(1,i,QTableWidgetItem(str(setting[2][l])))
					
	def calculateWeight(self,pairwise):
		"Define vector of weight based on eigenvector and eigenvalues"
		pairwise=np.array(pairwise)
		eigenvalues, eigenvector=np.linalg.eig(pairwise)
		maxindex=np.argmax(eigenvalues)
		eigenvalues=np.float32(eigenvalues)
		eigenvector=np.float32(eigenvector)
		weight=eigenvector[:, maxindex] #extract vector from eigenvector with max vaue in eigenvalues
		weight.tolist() #convert array(numpy)  to vector
		weight=[ w/sum(weight) for w in weight ]
		for i in range(len(weight)):
			self.EnvParameterWidget.setItem(0,i,QTableWidgetItem(str(round(weight[i],2))))
		return weight, eigenvalues,  eigenvector


	def Consistency(self,weight,eigenvalues):
		"Calculete Consistency index in accord with Saaty (1977)"
		try:
			RI=[0.00, 0.00, 0.00,0.52,0.90,1.12,1.24,1.32,1.41]	 #order of matrix: 0,1,2,3,4,5,6,7,8
			order=len(weight)
			CI=(np.max(eigenvalues)-order)/(order-1)
			return CI/RI[order-1]
		except:
			return 1.41

	def AnalyticHierarchyProcess(self):
		"""Calculate weight from matrix of pairwise comparison """
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() for f in range(self.EnvTableWidget.columnCount())]
		pairwise=[[float(self.EnvTableWidget.item(r, c).text()) for r in range(len(criteria))] for c in range(len(criteria))]
		weight, eigenvalues, eigenvector=self.calculateWeight(pairwise)
		consistency=self.Consistency(weight,eigenvalues)
		self.ReportLog(eigenvalues,eigenvector, weight, consistency)
		return 0

	def ReportLog(self, eigenvalues,eigenvector, weight, consistency):
		"Make a log output"
		log=" Weights: %s \n Consistency: %s" % (str([round(w,2) for w in weight]),consistency)
		self.EnvTEdit.setText(log)
		return 0


	def AddDecisionField(self,layer,Label):
		"""Add field on attribute table"""
		caps = layer.dataProvider().capabilities()
		if caps & QgsVectorDataProvider.AddAttributes:
			res = layer.dataProvider().addAttributes( [QgsField(Label, QVariant.Double) ] )
		return 0
		
	
	def ComputeWeightedSumValue(self,preference,weight,matrix,minField,maxField):
		""" """
		WeightedSumVaList=[]
		for row in matrix:
			List=[]
			for r,minF, maxF, pref, wgt  in zip(row, minField,maxField,preference,weight):
				if pref=='gain':
					value=(wgt*(r-minF)/(maxF-minF))  #cres: x-min / max - min
				else:
					value=(wgt*(maxF-r)/(maxF-minF))  #dec: max-x / max-min
				List.append(value)
			WeightedSumVaList.append(sum(List))
		#self.EnvTEdit.append(str(WeightedSumVaList))
		return WeightedSumVaList

	
	def ElaborateAttributeTable(self):
		"""Standardization fields values in range [0-1]"""
		matrix=[]
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() for f in range(self.EnvTableWidget.columnCount())]
		weight=[float(self.EnvParameterWidget.item(0, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		preference=[str(self.EnvParameterWidget.item(1, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		provider=self.activeLayer.dataProvider()
		if provider.fieldNameIndex("geoWSM")==-1:
			self.AddDecisionField(self.activeLayer,"geoWSM")
		fldValue = provider.fieldNameIndex("geoWSM") #obtain classify field index from its name
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		minField=[provider.minimumValue( f ) for f in fids]
		maxField=[provider.maximumValue( f ) for f in fids]
		fields = self.activeLayer.pendingFields()
		features= self.activeLayer.getFeatures()
		matrix=[]
		for feat in features:
			row=[feat.attributes()[self.activeLayer.fieldNameIndex(name)] for  name in criteria]
			matrix.append(row)
		matrix=np.array(matrix, dtype = 'float32')
		WeightedSumVaList=self.ComputeWeightedSumValue(preference,weight,matrix,minField,maxField)
		
		feat = QgsFeature()
		self.EnvProgressBar.setRange(1,provider.featureCount())
		progress=0
		self.activeLayer.startEditing()
		for WSM,feat in zip(WeightedSumVaList,self.activeLayer.getFeatures()):
			progress=progress+1
			features=feat.attributes()
			self.activeLayer.changeAttributeValue(feat.id(),fldValue,round(WSM,4))
			self.EnvProgressBar.setValue(progress)
		self.activeLayer.commitChanges()
		self.setting2csv()
		self.EnvTEdit.append("done")
		#self.EnvGetWeightBtn.setEnabled(False)
		return 0




	def Symbolize(self,field):
		"""Prepare legends """
		classes=['very low', 'low','medium','high','very high']
		fieldName = field
		numberOfClasses=len(classes)
		layer = self.iface.activeLayer()
		fieldIndex = layer.fieldNameIndex(fieldName)
		provider = layer.dataProvider()
		minimum = provider.minimumValue( fieldIndex )
		maximum = provider.maximumValue( fieldIndex )
		RangeList = []
		Opacity = 1
		for c,i in zip(classes,range(len(classes))):
		# Crea il simbolo ed il range...
			Min = minimum + ( maximum - minimum ) / numberOfClasses * i
			Max = minimum + ( maximum - minimum ) / numberOfClasses * ( i + 1 )
			Label = "%s [%.2f - %.2f]" % (c,Min,Max)
			Colour = QColor(255-255*i/numberOfClasses,255*i/numberOfClasses,0) #red to green
			Symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
			Symbol.setColor(Colour)
			Symbol.setAlpha(Opacity)
			Range = QgsRendererRangeV2(Min,Max,Symbol,Label)
			RangeList.append(Range)
		Renderer = QgsGraduatedSymbolRendererV2('', RangeList)
		Renderer.setMode(QgsGraduatedSymbolRendererV2.EqualInterval)
		Renderer.setClassAttribute(fieldName)
		add=QgsVectorLayer(layer.source(),field,'ogr')
		add.setRendererV2(Renderer)
		QgsMapLayerRegistry.instance().addMapLayer(add)


	def RenderLayer(self):
		""" Load thematic layers in canvas """
		fields=['geoWSM']
		for f in fields:
			self.Symbolize(f)
		self.setModal(False)

###########################################################################################


	def ExtractAttributeValue(self,field):
		"""Retrive single field value from attributes table"""
		fields=self.activeLayer.pendingFields()
		provider=self.activeLayer.dataProvider()
		fid=provider.fieldNameIndex(field)
		listValue=[]
		if fields[fid].typeName()=='Real' or fields[fid].typeName()=='Integer':
			for feat in self.activeLayer.getFeatures():
				attribute=feat.attributes()[fid]
				listValue.append(float(attribute))
		else:
			for feat in self.activeLayer.getFeatures():
				attribute=feat.attributes()[fid]
				listValue.append(str(attribute))
		return listValue




	def BuildOutput(self):
		"""General function for all graphical and tabula output"""
		currentDir = unicode(os.path.abspath( os.path.dirname(__file__)))
		if os.path.isfile(os.path.join(currentDir,"histogram.png"))==True:
			os.remove(os.path.join(currentDir,"histogram.png"))
		try:
			import matplotlib.pyplot as plt
			import numpy as np
			self.BuildGraphIstogram(currentDir)
		except ImportError, e:
			QMessageBox.information(None, QCoreApplication.translate('geoWeightedSum', "Plugin error"), \
			QCoreApplication.translate('geoWeightedSum', "Couldn't import Python modules 'matplotlib' and 'numpy'. [Message: %s]" % e))
		self.BuildHTML()
		webbrowser.open(os.path.join(currentDir,"barGraph.html"))
		self.setModal(False)
		return 0



	def BuildGraphIstogram(self,currentDir):
		"""Build Istogram graph using pyplot"""

		geoWSMValue=self.ExtractAttributeValue('geoWSM')
		fig = plt.figure()
		fig.subplots_adjust(bottom=0.2)
		fig.subplots_adjust()
		ax = fig.add_subplot(111)
		ax.margins(0.05, None)
		#xpos = np.arange(len(SuitValue))    # the x locations for the groups
		xpos = range(len(geoWSMValue))    # the x locations for the groups
		width = 0.8     # the width of the bars: can also be len(x) sequence
		label=self.LabelListFieldsCBox.currentText()
		labels=self.ExtractAttributeValue(label)
		p1 = plt.bar((xpos), geoWSMValue, width=width, color='g',align='center') # yerr=womenStd)
		plt.ylabel('Scores')
		plt.title('geoWSM')
		plt.xticks((xpos), tuple(labels),rotation=90,fontsize=6 )
		plt.savefig(os.path.join(currentDir,"histogram.png"))
		self.LblGraphic.setPixmap(QtGui.QPixmap(os.path.join(currentDir,"histogram.png")))
		plt.close('all')
		return 0

	
	def BuildHTML(self):
		geoWSMValue=self.ExtractAttributeValue('geoWSM')
		geoWSMValue=[[A] for (A) in geoWSMValue]
		label=self.LabelListFieldsCBox.currentText()
		labels=self.ExtractAttributeValue(label)
		labels=[str(l) for l in labels]
		legend=['geoWSM']
		htmlGraph.BuilHTMLGraph(geoWSMValue,labels,legend)
		return 0




###################################################################################################
	def about(self):
		"""
		Visualize an About window.
		"""

		QMessageBox.about(self, "About weighted sum model (WSM)",
		"""
			 <p>Please report any bug to <a href="mailto:g_massa@libero.it">g_massa@libero.it</a></p>
		""")

	def open_help(self):
		currentDir = unicode(os.path.abspath( os.path.dirname(__file__)))
		webbrowser.open(os.path.join(currentDir,"maplab.alwaysdata.net"))

