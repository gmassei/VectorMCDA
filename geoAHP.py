# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name			: geoWeightedSum
Description		: geographical MCDA for sustainability assessment
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
try:
	import numpy as np
	import matplotlib.pyplot as plt
	import matplotlib.cm as cm
except ImportError, e:
	QMessageBox.information(None, QCoreApplication.translate('geoWeightedSum', "Plugin error"), \
	QCoreApplication.translate('geoWeightedSum', "Couldn't import Python module. [Message: %s]" % e))
	

from ui_geoWeightedSum import Ui_Dialog

class geoWeightedSumDialog(QDialog, Ui_Dialog):
	def __init__(self, iface):
		'''costruttore'''
		QDialog.__init__(self, iface.mainWindow())
		self.setupUi(self)
		self.iface = iface
		self.activeLayer = self.iface.activeLayer()
		self.base_Layer = self.iface.activeLayer()
		for i in range(1,self.toolBox.count()):
			self.toolBox.setItemEnabled (i,False)

		QObject.connect(self.RetriveFileTBtn, SIGNAL( "clicked()" ), self.outFile)
		QObject.connect(self.SetBtnBox, SIGNAL("accepted()"), self.Standardization)
		QObject.connect(self.SetBtnBox, SIGNAL("rejected()"),self, SLOT("reject()"))
		QObject.connect(self.SetBtnAbout, SIGNAL("clicked()"), self.about)
		QObject.connect(self.SetBtnHelp, SIGNAL("clicked()"),self.open_help)

		QObject.connect(self.EnvAddFieldBtn, SIGNAL( "clicked()" ), self.AddField)
		QObject.connect(self.EnvRemoveFieldBtn, SIGNAL( "clicked()" ), self.RemoveField)
		QObject.connect(self.EnvCalculateBtn, SIGNAL( "clicked()" ), self.AnalyticHierarchyProcess)
		QObject.connect(self.EnvGetWeightBtn, SIGNAL( "clicked()" ), self.ComputeWeightedSumlValue)

		QObject.connect(self.RenderBtn,SIGNAL("clicked()"), self.RenderLayer)
		QObject.connect(self.GraphBtn, SIGNAL("clicked()"), self.BuildOutput)

		QObject.connect(self.AnlsBtnBox, SIGNAL("rejected()"),self, SLOT("reject()"))
		
		sourceIn=str(self.iface.activeLayer().source())
		#self.baseLbl.setText(sourceIn)
		pathSource=os.path.dirname(sourceIn)
		outFile="geoWeightedSum.shp"
		sourceOut=os.path.join(pathSource,outFile)
		self.OutlEdt.setText(str(sourceOut))

		self.EnvMapNameLbl.setText(self.activeLayer.name())
		self.EnvlistFieldsCBox.addItems(self.GetFieldNames(self.activeLayer))

#################################################################################
		Envfields=self.GetFieldNames(self.activeLayer) #field list
		self.EnvTableWidget.setColumnCount(len(Envfields))
		self.EnvTableWidget.setHorizontalHeaderLabels(Envfields)
		self.EnvTableWidget.setRowCount(len(Envfields))
		self.EnvTableWidget.setVerticalHeaderLabels(Envfields)
		EnvSetLabel=["Weigths","Preference"]
		self.EnvWeighTableWidget.setColumnCount(len(Envfields))
		self.EnvWeighTableWidget.setHorizontalHeaderLabels(Envfields)
		self.EnvWeighTableWidget.setRowCount(2)
		self.EnvWeighTableWidget.setVerticalHeaderLabels(EnvSetLabel)
		for r in range(len(Envfields)):
			self.EnvTableWidget.setItem(r,r,QTableWidgetItem("1.0"))
			self.EnvWeighTableWidget.setItem(0,r,QTableWidgetItem("1.0"))
			self.EnvWeighTableWidget.setItem(1,r,QTableWidgetItem("gain"))
		#retrieve signal for modified cell
		self.EnvTableWidget.cellChanged[(int,int)].connect(self.CompleteMatrix)
		self.EnvWeighTableWidget.cellClicked[(int,int)].connect(self.ChangeValue)
#################################################################################

		currentDir=unicode(os.path.abspath( os.path.dirname(__file__)))
		self.LblLogo.setPixmap(QtGui.QPixmap(os.path.join(currentDir,"icon.png")))
		
		for i in range(1,self.toolBox.count()):
			self.toolBox.setItemEnabled (i,True)


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


	def settingStart(self):
		""" Prepare file for processing """
		outputFilename=self.OutlEdt.text()
		for i in range(1,self.toolBox.count()):
			self.toolBox.setItemEnabled (i,True)
		layer = self.iface.activeLayer()
		crs=layer.crs().authid()
		provider = layer.dataProvider()
		fields = provider.fields()
		writer = QgsVectorFileWriter(outputFilename, "CP1250", fields, provider.geometryType(), layer.crs(), "ESRI Shapefile")
		inFeat = QgsFeature()
		outFeat = QgsFeature()
		inGeom = QgsGeometry()
		provider.select(provider.attributeIndexes() )
		self.LoadProgressBar.setRange(1,layer.featureCount())
		progress=0
		#self.EnvTEdit.clear()
		while provider.nextFeature(inFeat):
			progress=progress+1
			inGeom = inFeat.geometry()
			outFeat.setGeometry(inFeat.geometry() )
			outFeat.setAttributeMap(inFeat.attributeMap() )
			writer.addFeature( outFeat )
			self.LoadProgressBar.setValue(progress)
		del writer
		newlayer = QgsVectorLayer(outputFilename, "geosustainability", "ogr")
		QgsMapLayerRegistry.instance().addMapLayer(newlayer)
		self.activeLayer =newlayer
		self.activeLayer=QgsVectorLayer(self.OutlEdt.text(), self.activeLayer.name(), "ogr") ##TODO verify
		self.toolBox.setEnabled(True)
		self.updateTable()
		self.LabelListFieldsCBox.addItems(provider.fieldNameMap().keys())
		return 0



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
		self.EnvWeighTableWidget.setColumnCount(len(Envfields))
		self.EnvWeighTableWidget.setHorizontalHeaderLabels(Envfields)
		self.EnvWeighTableWidget.setRowCount(2)
		self.EnvWeighTableWidget.setVerticalHeaderLabels(EnvSetLabel)

		for r in range(len(Envfields)):
			self.EnvWeighTableWidget.setItem(0,r,QTableWidgetItem("1.0"))
			self.EnvWeighTableWidget.setItem(1,r,QTableWidgetItem("gain"))
		return 0


	def AddField(self):
		"""Add field to table in GUI"""
		f=self.EnvlistFieldsCBox.currentText()
		self.EnvTableWidget.insertColumn(self.EnvTableWidget.columnCount())
		self.EnvTableWidget.insertRow(self.EnvTableWidget.rowCount())
		self.EnvTableWidget.setHorizontalHeaderItem((self.EnvTableWidget.columnCount()-1),QTableWidgetItem(f))
		self.EnvTableWidget.setVerticalHeaderItem((self.EnvTableWidget.rowCount()-1),QTableWidgetItem(f))
		##############
		self.EnvWeighTableWidget.insertColumn(self.EnvWeighTableWidget.columnCount())
		self.EnvWeighTableWidget.setHorizontalHeaderItem((self.EnvWeighTableWidget.columnCount()-1),QTableWidgetItem(f))
		self.EnvWeighTableWidget.setItem(0,(self.EnvWeighTableWidget.columnCount()-1),QTableWidgetItem("1.0"))
		self.EnvWeighTableWidget.setItem(1,(self.EnvWeighTableWidget.columnCount()-1),QTableWidgetItem("gain"))

		return 0


	def RemoveField(self):
		"""Remove field in table in GUI"""
		f=self.EnvlistFieldsCBox.currentText()
		i=self.EnvTableWidget.currentColumn()
		j=self.EnvWeighTableWidget.currentColumn()
		if i == -1 and j== -1:
			QMessageBox.warning(self.iface.mainWindow(), "geoWeightedSum",
			("column or row must be selected"), QMessageBox.Ok, QMessageBox.Ok)
		elif i != -1:
			self.EnvTableWidget.removeColumn(i)
			self.EnvTableWidget.removeRow(i)
			self.EnvWeighTableWidget.removeColumn(i)
		elif j != -1:
			self.EnvTableWidget.removeColumn(j)
			self.EnvTableWidget.removeRow(j)
			self.EnvWeighTableWidget.removeColumn(j)
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
		cell=self.EnvWeighTableWidget.currentItem()
		val=cell.text()
		if val=="cost":
			self.EnvWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("gain"))
		elif val=="gain":
			self.EnvWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("cost"))
		else:
			self.EnvWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem(str(val)))
		return 0

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
			self.EnvWeighTableWidget.setItem(0,i,QTableWidgetItem(str(round(weight[i],2))))
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
		

	def Standardization(self):
		"""Standardization fields values in range [0-1]"""
		matrix=[]
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() for f in range(self.EnvTableWidget.columnCount())]
		preference=[str(self.EnvWeighTableWidget.item(1, c).text()) for c in range(self.EnvWeighTableWidget.columnCount())]
		#provider=self.activeLayer.dataProvider()
		#allAttrs = provider.attributeIndexes()
		#fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		#features= self.activeLayer.getFeatures()
		for field in criteria:
			matrix.append(self.ExtractAttributeValue(field))
		matrix=np.array(matrix)
		#self.EnvTEdit.append(str(len(matrix[4])))
		minField=[np.nanmin(matrix[i]) for i in range(len(matrix)) ]
		maxField=[np.nanmax(matrix[i]) for i in range(len(matrix)) ]
		self.EnvTEdit.append(str(minField))
		#minField=dict(zip(fids,[provider.minimumValue( f ).toDouble()[ 0 ] for f in fids]))
		#maxField=dict(zip(fids,[provider.maximumValue( f ).toDouble()[ 0 ] for f in fids]))
		#feat = QgsFeature()
		#provider.select(fids)
		#self.activeLayer.startEditing()
		#for i,f in zip(preference,fids):
			#while provider.nextFeature( feat ):
				#if i=='gain':
					#attrs=feat.attributeMap()
					#value=(float(attrs[f].toString())-float(minField[f]))/(float(maxField[f])-float(minField[f]))   #cres: x-min / max - min
					#self.activeLayer.changeAttributeValue(feat.id(),f,QVariant(value))
				#else:
					#attrs=feat.attributeMap()
					#value=(float(maxField[f])-float(attrs[f].toString()))/(float(maxField[f])-float(minField[f])) #dec: max-x / max-min
					#self.activeLayer.changeAttributeValue(feat.id(),f,QVariant(value))
		#self.activeLayer.commitChanges()
		return 0


	def ComputeWeightedSumlValue(self):
		""" Calculate Environmental and Socio-Economicos Value"""
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() for f in range(self.EnvTableWidget.columnCount())]
		weight=[float(self.EnvWeighTableWidget.item(0, c).text()) for c in range(self.EnvWeighTableWidget.columnCount())]
		self.Standardization()
		provider=self.activeLayer.dataProvider()
		if provider.fieldNameIndex("geoWSM")==-1:
			self.AddDecisionField(self.activeLayer,"geoWSM")
		fldValue = provider.fieldNameIndex("geoWSM") #obtain classify field index from its name
		self.EnvTEdit.append("done") #   setText
		
		features=provider.featureCount() #Number of features in the layer.
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		feat = QgsFeature()
		provider.select(fids)
		self.activeLayer.startEditing()
		self.EnvProgressBar.setRange(1,features)
		progress=0
		while provider.nextFeature(feat):
			progress=progress+1
			attributeMap = feat.attributeMap()
			value=0
			for i,j in zip(attributeMap,weight):
				value =(value+float(attributeMap[i].toString())*j)
			self.activeLayer.changeAttributeValue(feat.id(), fldValue, round(float(value),4))
			self.EnvProgressBar.setValue(progress)
		self.activeLayer.commitChanges()
		#self.ComputeOverlValue()
		self.EnvProgressBar.setValue(1)
		return 0

	def ComputeOverlValue(self):
		"""Sum Environmental and Socio-economics value for calculate  Sustainable value"""
		provider=self.activeLayer.dataProvider()
		if provider.fieldNameIndex("geoWSM")==-1:
			self.AddDecisionField(self.activeLayer,"geoWSM")
		fldValue = provider.fieldNameIndex("geoWSM") #obtain classify field index from its name
		features=provider.featureCount() #Number of features in the layer.
		fids=[provider.fieldNameIndex(geoWeightedSum)]  #obtain array fields index from its name
		feat = QgsFeature()
		provider.select(fids)
		self.activeLayer.startEditing()
		while provider.nextFeature(feat):
			attributeMap = feat.attributeMap()
			value=sum([float(att.toString()) for att in attributeMap.values()])
			self.activeLayer.changeAttributeValue(feat.id(), fldValue, float(value))
		self.activeLayer.commitChanges()
		return 0



	def Symbolize(self,field):
		"""Prepare legends for environmental, socio economics and sustainable values"""
		classes=['very low', 'low','medium','high','very high']
		fieldName = field
		numberOfClasses=len(classes)
		layer = self.iface.activeLayer()
		fieldIndex = layer.fieldNameIndex(fieldName)
		provider = layer.dataProvider()
		minimum = provider.minimumValue( fieldIndex ).toDouble()[ 0 ]
		maximum = provider.maximumValue( fieldIndex ).toDouble()[ 0 ]
		RangeList = []
		Opacity = 1
		for c,i in zip(classes,range(len(classes))):
		# Crea il simbolo ed il range...
			Min = minimum + ( maximum - minimum ) / numberOfClasses * i
			Max = minimum + ( maximum - minimum ) / numberOfClasses * ( i + 1 )
			Label = "%s [%.2f - %.2f]" % (c,Min,Max)
			field=='geoWSM'
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
		layer = self.iface.activeLayer()
		QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
		#layer = QgsVectorLayer(self.OutlEdt.text(), "geosustainability", "ogr")
		layer = QgsVectorLayer(self.OutlEdt.text(), (os.path.basename(str(self.OutlEdt.text()))), "ogr")
		QgsMapLayerRegistry.instance().addMapLayer(layer)
		fields=['geoWSM']
		for f in fields:
			self.Symbolize(f)

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
		self.BuildGraphIstogram(currentDir)
		webbrowser.open(os.path.join(currentDir,"index.html"))
		return 0



	def BuildGraphIstogram(self,currentDir):
		"""Build Istogram graph using pyplot"""
		geoWeightedSumValue=self.ExtractAttributeValue('geoWSM')
		fig = plt.figure()
		#fig.subplots_adjust(bottom=0.2)
		ax = fig.add_subplot(111)
		N = len(geoWeightedSumValue)
		ind = np.arange(N)    # the x locations for the groups
		width = 0.70     # the width of the bars: can also be len(x) sequence
		label=self.LabelListFieldsCBox.currentText()
		labels=self.ExtractAttributeValue(label)
		p1 = plt.bar((ind+width), geoWeightedSumValue, width, color='g',align='center') # yerr=womenStd)
		plt.ylabel('Scores')
		plt.title('Sustainability')
		plt.xticks((ind+width), tuple(labels),rotation=90,fontsize=5 )
		#plt.yticks(np.arange(0,max(SuitValue),0.10),fontsize=5)
		plt.legend((p1[0]), ('geoWeightedSum'))

		plt.savefig(os.path.join(currentDir,"histogram.png"))
		plt.close('all')
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
		webbrowser.open(os.path.join(currentDir,"data.html"))

