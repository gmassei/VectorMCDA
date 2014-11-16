# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name			: geoPromethee
Description		: geographical MCDA with geoPromethee model 
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
	QMessageBox.information(None, QCoreApplication.translate('geoPromethee', "Plugin error"), \
	QCoreApplication.translate('geoPromethee', "Couldn't import Python module. [Message: %s]" % e))
	

from ui_geoPromethee import Ui_Dialog

class geoPrometheeDialog(QDialog, Ui_Dialog):
	def __init__(self, iface):
		'''costruttore'''
		QDialog.__init__(self, iface.mainWindow())
		self.setupUi(self)
		self.iface = iface
		self.activeLayer = self.iface.activeLayer()
		#self.base_Layer = self.iface.activeLayer()
		for i in range(1,self.toolBox.count()):
			self.toolBox.setItemEnabled (i,False)

		QObject.connect(self.SetBtnQuit, SIGNAL("clicked()"),self, SLOT("reject()"))
		QObject.connect(self.SetBtnAbout, SIGNAL("clicked()"), self.about)
		QObject.connect(self.SetBtnHelp, SIGNAL("clicked()"),self.open_help)
		QObject.connect(self.EnvAddFieldBtn, SIGNAL( "clicked()" ), self.AddField)
		QObject.connect(self.EnvRemoveFieldBtn, SIGNAL( "clicked()" ), self.RemoveField)
		QObject.connect(self.EnvGetWeightBtn, SIGNAL( "clicked()" ), self.ElaborateAttributeTable)
		QObject.connect(self.EnvCalculateBtn, SIGNAL( "clicked()" ), self.AnalyticHierarchyProcess)
		QObject.connect(self.RenderBtn,SIGNAL("clicked()"), self.RenderLayer)
		QObject.connect(self.GraphBtn, SIGNAL("clicked()"), self.BuildOutput)
		QObject.connect(self.AnlsBtnBox, SIGNAL("rejected()"),self, SLOT("reject()"))
		
		sourceIn=str(self.iface.activeLayer().source())
		#self.baseLbl.setText(sourceIn)
		pathSource=os.path.dirname(sourceIn)
		outFile="geoPromethee.shp"
		sourceOut=os.path.join(pathSource,outFile)
		#self.OutlEdt.setText(str(sourceOut))

		self.EnvMapNameLbl.setText(self.activeLayer.name())
		self.EnvlistFieldsCBox.addItems(self.GetFieldNames(self.activeLayer))
		self.LabelListFieldsCBox.addItems(self.GetFieldNames(self.activeLayer))

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
#################################################################################
		#currentDir=unicode(os.path.abspath( os.path.dirname(__file__)))
		#self.LblLogo.setPixmap(QtGui.QPixmap(os.path.join(currentDir,"icon.png")))
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
#######################################################################################
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


	def RemoveField(self):
		"""Remove field in table in GUI"""
		f=self.EnvlistFieldsCBox.currentText()
		i=self.EnvTableWidget.currentColumn()
		j=self.EnvParameterWidget.currentColumn()
		if i == -1 and j== -1:
			QMessageBox.warning(self.iface.mainWindow(), "geoWeightedSum",
			("column or row must be selected"), QMessageBox.Ok, QMessageBox.Ok)
		elif i != -1:
			self.EnvTableWidget.removeColumn(i)
			self.EnvTableWidget.removeRow(i)
			self.EnvParameterWidget.removeColumn(i)
		elif j != -1:
			self.EnvTableWidget.removeColumn(j)
			self.EnvTableWidget.removeRow(j)
			self.EnvParameterWidget.removeColumn(j)
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
		


	def Attributes2Matrix(self):
		matrix=[]
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() for f in range(self.EnvTableWidget.columnCount())]
		weight=[float(self.EnvParameterWidget.item(0, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		preference=[str(self.EnvParameterWidget.item(1, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		fields = self.activeLayer.pendingFields()
		features= self.activeLayer.getFeatures()
		for feat in features:
			row=[feat.attributes()[self.activeLayer.fieldNameIndex(name)] for  name in criteria]
			matrix.append(row)
		matrix=np.array(matrix, dtype = 'float32')
		return matrix
	
	def setting2csv(self):
		currentDIR = (os.path.dirname(str(self.activeLayer.source())))
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() for f in range(self.EnvTableWidget.columnCount())]
		weight=[float(self.EnvParameterWidget.item(0, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		preference=[str(self.EnvParameterWidget.item(1, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		csvFile=open(os.path.join(currentDIR,'setPromethee.csv'),"wb")
		write=csv.writer(csvFile,delimiter=";",quotechar='"',quoting=csv.QUOTE_NONNUMERIC)
		write.writerow(criteria)
		write.writerow(weight)
		write.writerow(preference)
		csvFile.close()
		
	def csv2setting(self):
		currentDIR = (os.path.dirname(str(self.activeLayer.source())))
		setting=[]
		try:
			with open(os.path.join(currentDIR,'setPromethee.csv')) as csvFile:
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
					
	
	def StandardizeMatrix(self,preference,weight,matrix,minField,maxField):
		""" """
		StdMatrix=[]
		for row in matrix:
			List=[]
			for r,minF, maxF, pref  in zip(row, minField,maxField,preference):
				if pref=='gain':
					value=round(((r-minF)/(maxF-minF)),4) #gain: x-min / max - min
				else:
					value=round(((maxF-r)/(maxF-minF)),4)  #cost: max-x / max-min
				List.append(value)
			StdMatrix.append(List)
		return StdMatrix
		

	def PreferenceMatrix(self, matrix,criteria,weight):
		preference=[]
		for i in range(len(criteria)):
			col=[row[i] for row in matrix]
			for ci in col:
				for cj in col:
					if ci>cj:
						value=ci-cj
					else:
						value=value
					row.append(value)
				preference.append(row)
					

	def PreferenceMatrix(self, matrix,criteria,weight):
		preference=[]
		for row1 in matrix:
			crow=[]
			for row2 in matrix:
				value=0
				for r1,r2,w in zip(row1,row2,weight):
					if r1>r2:
						value=value+((r1-r2)*w)
					else:
						value=value
				crow.append(value)
			preference.append(crow)
		return preference

	def PoisitiveFlow(self,preference):
		positiveFlow=[sum(row) for row in preference]
		return positiveFlow
		
				
	def NegativeFlow(self,preference):
		negativeFlow=[]
		for i in range(len(preference[0])):
			col=sum([row[i] for row in preference])
			negativeFlow.append(col)
		return negativeFlow
	
		
	def ElaborateAttributeTable(self):
		"""Standardization fields values in range [0-1]"""
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() for f in range(self.EnvTableWidget.columnCount())]
		weight=[float(self.EnvParameterWidget.item(0, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		preference=[str(self.EnvParameterWidget.item(1, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		provider=self.activeLayer.dataProvider()
		if provider.fieldNameIndex("geoFlux[+]")==-1:
			self.AddDecisionField(self.activeLayer,"geoFlux[+]")
		fldPositiveFlux = provider.fieldNameIndex("geoFlux[+]") #obtain classify field index from its name
		if provider.fieldNameIndex("geoFlux[-]")==-1:
			self.AddDecisionField(self.activeLayer,"geoFlux[-]")
		fldNegativeFlux = provider.fieldNameIndex("geoFlux[-]") #obtain classify field index from its name
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		minField=[provider.minimumValue( f ) for f in fids]
		maxField=[provider.maximumValue( f ) for f in fids]

		matrix= self.Attributes2Matrix()
		
		matrix=self.StandardizeMatrix(preference,weight,matrix,minField,maxField)
		preferenceMatrix=self.PreferenceMatrix(matrix,criteria,weight)
		positiveFlow=self.PoisitiveFlow(preferenceMatrix) 
		negativeFlow=self.NegativeFlow(preferenceMatrix)  
		self.setting2csv()
		
		#feat = QgsFeature()
		self.activeLayer.startEditing()
		for posF,negF,feat in zip(positiveFlow,negativeFlow,self.activeLayer.getFeatures()):
			features=feat.attributes()
			self.activeLayer.changeAttributeValue(feat.id(),fldPositiveFlux,round(posF,4))
			self.activeLayer.changeAttributeValue(feat.id(),fldNegativeFlux,round(negF,4))
		self.activeLayer.commitChanges()
		self.EnvTEdit.append("done") 
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
		fields=['geoFlux[+]','geoFlux[-]']
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
			#self.BuildGraphPnt(currentDir)
			self.BuildGraphIstogram(currentDir)
		except ImportError, e:
			QMessageBox.information(None, QCoreApplication.translate('geoConcordance', "Plugin error"), \
			QCoreApplication.translate('geoPromethee', "Couldn't import Python modules 'matplotlib' and 'numpy'. [Message: %s]" % e))
		self.BuildHTML()
		webbrowser.open(os.path.join(currentDir,"barGraph.html"))
		self.setModal(False)
		return 0



	def BuildGraphIstogram(self,currentDir):
		"""Build Istogram graph using pyplot"""
		geoPositiveFlux=self.ExtractAttributeValue('geoFlux[+]')
		geoNegativeFlux=self.ExtractAttributeValue('geoFlux[-]')
		geoFluxNetValue=[(p-n) for p,n in zip(geoPositiveFlux,geoNegativeFlux)]
		fig = plt.figure()
		fig.subplots_adjust(bottom=0.2)
		fig.subplots_adjust()
		ax = fig.add_subplot(111)
		ax.margins(0.05, None)
		#xpos = np.arange(len(SuitValue))    # the x locations for the groups
		xpos = np.arange(len(geoFluxNetValue))    # the x locations for the groups
		width = 0.40     # the width of the bars: can also be len(x) sequence
		label=self.LabelListFieldsCBox.currentText()
		labels=self.ExtractAttributeValue(label)
		p1 = plt.bar((xpos), geoFluxNetValue, width, color='g',align='center') # yerr=womenStd)
		p2 = plt.bar((xpos+width), geoNegativeFlux, width, color='r', align='center') #, yerr=menStd)
		plt.ylabel('Scores')
		plt.title('geoPromethee')
		plt.xticks((xpos), tuple(labels),rotation=90,fontsize=6 )
		plt.legend((p1[0], p2[0]), ('geoFlux[+]', 'geoFlux[-]'))
		plt.savefig(os.path.join(currentDir,"histogram.png"))
		self.LblGraphic.setPixmap(QtGui.QPixmap(os.path.join(currentDir,"histogram.png")))
		plt.close('all')
		return 0

	
	def BuildHTML(self):
		geoPositiveFlux=self.ExtractAttributeValue('geoFlux[+]')
		geoNegativeFlux=self.ExtractAttributeValue('geoFlux[-]')
		geoFluxNetValue=[[p-n] for (p,n) in zip(geoPositiveFlux,geoNegativeFlux)]
		label=self.LabelListFieldsCBox.currentText()
		labels=self.ExtractAttributeValue(label)
		labels=[str(l) for l in labels]
		legend=['geoFluxNet']
		htmlGraph.BuilHTMLGraph(geoFluxNetValue,labels,legend)
		return 0




###################################################################################################
	def about(self):
		"""
		Visualize an About window.
		"""

		QMessageBox.about(self, "About concordance and discordance model",
		"""
			 <p>Please report any bug to <a href="mailto:g_massa@libero.it">g_massa@libero.it</a></p>
		""")

	def open_help(self):
		webbrowser.open("http://maplab.alwaysdata.net/geomcda.html")

