# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name            : geoTOPSIS
Description        : geographical MCDA 
Date            : June 27, 2014
copyright		: Gianluca Massei  (developper) 
email			: (g_massa@libero.it)

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui

from qgis.core import *
from qgis.gui import *
	
import os
import webbrowser
import shutil
import csv

try:
	import numpy as np
except ImportError, e:
	QMessageBox.information(None, QCoreApplication.translate('geoFuzzy', "Plugin error"), \
	QCoreApplication.translate('geoFuzzy', "Couldn't import Python module. [Message: %s]" % e))
	

import htmlGraph

from ui_geoFuzzy import Ui_Dialog

class geoFuzzyDialog(QDialog, Ui_Dialog):
	def __init__(self, iface):
		'''costruttore'''
		QDialog.__init__(self, iface.mainWindow())
		self.setupUi(self)
		self.iface = iface
		self.activeLayer = self.iface.activeLayer()
		for i in range(1,self.toolBox.count()):
			self.toolBox.setItemEnabled (i,False)
		#QObject.connect(self.SetBtnBox, SIGNAL("rejected()"),self, SLOT("reject()"))
		QObject.connect(self.SetBtnAbout, SIGNAL("clicked()"), self.about)
		QObject.connect(self.SetBtnHelp, SIGNAL("clicked()"),self.open_help)

		QObject.connect(self.EnvAddFieldBtn, SIGNAL( "clicked()" ), self.AddField)
		QObject.connect(self.EnvRemoveFieldBtn, SIGNAL( "clicked()" ), self.RemoveField)
		QObject.connect(self.EnvCalculateBtn, SIGNAL( "clicked()" ), self.AnalyticHierarchyProcess)
		QObject.connect(self.EnvGetWeightBtn, SIGNAL( "clicked()" ), self.Elaborate)

		QObject.connect(self.RenderBtn,SIGNAL("clicked()"), self.RenderLayer)
		QObject.connect(self.GraphBtn, SIGNAL("clicked()"), self.BuildOutput)

		QObject.connect(self.AnlsBtnBox, SIGNAL("rejected()"),self, SLOT("reject()"))
		#QObject.connect(self.CritExtractBtn, SIGNAL( "clicked()" ), self.ExtractRules)
		#QObject.connect(self.SaveRulesBtn, SIGNAL( "clicked()" ), self.SaveRules)
		
		
		sourceIn=str(self.iface.activeLayer().source())
		pathSource=os.path.dirname(sourceIn)
		outputFile="geoFuzzy.shp"
		sourceOut=os.path.join(pathSource,outputFile)
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
		EnvSetLabel=["Hedges","First", "Second", "Third","Fourth"]

		self.EnvParameterWidget.setColumnCount(len(Envfields))
		self.EnvParameterWidget.setHorizontalHeaderLabels(Envfields)
		self.EnvParameterWidget.setRowCount(len(EnvSetLabel))
		self.EnvParameterWidget.setVerticalHeaderLabels(EnvSetLabel)
		for r in range(len(Envfields)):
			self.EnvTableWidget.setItem(r,r,QTableWidgetItem("1.0"))
		self.EnvTableWidget.cellChanged[(int,int)].connect(self.CompleteMatrix)
		self.updateTable()
		try:
			self.EnvParameterWidget.cellClicked[(int,int)].connect(self.ChangeValue)
		except:
			pass
		setting=self.csv2setting()
		try:
			self.setting2table(setting)
		except:
			pass
#################################################################################
		header = self.EnvParameterWidget.horizontalHeader()
		header.sectionClicked.connect(self.ReverseValues)
#################################################################################
		for i in range(1,self.toolBox.count()):
			self.toolBox.setItemEnabled (i,True)


	def GetFieldNames(self, layer):
		"""retrive field names from active map/layer"""
		fields = layer.dataProvider().fields()
		field_list = []
		for field in fields:
			if field.typeName()!='String':
				field_list.append(str(field.name()))
		return field_list


	def outFile(self):
		"""Display file dialog for output  file"""
		self.OutlEdt.clear()
		outvLayer = QFileDialog.getSaveFileName(self, "Output map",".", "ESRI Shapefile (*.shp)")
		self.OutlEdt.insert(outvLayer)
		return outvLayer
		
	def coloTable(self):
		rows=self.EnvParameterWidget.rowCount()
		cols=self.EnvParameterWidget.columnCount()
		for r in range(rows):
			if r==1:
				for c in range(cols):
					self.EnvParameterWidget.item(r, c).setBackgroundColor(QtGui.QColor(255,165,0))
			elif r>1:
				for c in range(cols):
					self.EnvParameterWidget.item(r, c).setBackgroundColor(QtGui.QColor(255,0,0))
		return 0
		
	def updateTable(self):
		"""Prepare and compile table in GUI"""
		fields=self.GetFieldNames(self.activeLayer)
		#fields = [field.name() for field in self.activeLayer.pendingFields() ]
		pathSource=os.path.dirname(str(self.activeLayer.source()))
		self.EnvTableWidget.setColumnCount(len(fields))
		self.EnvTableWidget.setHorizontalHeaderLabels(fields)
		self.EnvTableWidget.setRowCount(len(fields))
		self.EnvTableWidget.setVerticalHeaderLabels(fields)
		EnvSetLabel=["Hedges","First", "Second", "Third","Fourth"]
		self.EnvParameterWidget.setColumnCount(len(fields))
		self.EnvParameterWidget.setHorizontalHeaderLabels(fields)
		self.EnvParameterWidget.setRowCount(len(EnvSetLabel))
		self.EnvParameterWidget.setVerticalHeaderLabels(EnvSetLabel)
		for r in range(len(fields)):
			self.EnvParameterWidget.setItem(0,r,QTableWidgetItem("1.0"))
		self.updateGUIFuzzy()
		self.coloTable()
		return 0


	def updateFuzzyFctn(self,TableWidget,WeighTableWidget,provider):
		"""base function for updateGUIIdealPoint()"""
		criteria=[TableWidget.verticalHeaderItem(f).text() for f in range(TableWidget.columnCount())]
		#preference=[str(WeighTableWidget.item(2, c).text()) for c in range(WeighTableWidget.columnCount())]
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		minField=[provider.minimumValue( f ) for f in fids]
		maxField=[provider.maximumValue( f ) for f in fids]
		for r in range(len(criteria)):
			WeighTableWidget.setItem(0,r,QTableWidgetItem(str(1.0)))
			WeighTableWidget.setItem(1,r,QTableWidgetItem(str(minField[r])))#
			WeighTableWidget.setItem(2,r,QTableWidgetItem(str(maxField[r])))#
			WeighTableWidget.setItem(3,r,QTableWidgetItem(str(maxField[r])))
			WeighTableWidget.setItem(4,r,QTableWidgetItem(str(maxField[r])))
	
	def updateGUIFuzzy(self):
		provider=self.activeLayer.dataProvider() #provider=self.active_layer.dataProvider() 
		##Environmental
		self.updateFuzzyFctn(self.EnvTableWidget,self.EnvParameterWidget,provider)
		return 0

	def addFieldFctn(self,listFields,TableWidget,WeighTableWidget):
		"""base function for AddField()"""
		TableWidget.insertColumn(TableWidget.columnCount())
		TableWidget.insertRow(TableWidget.rowCount())
		TableWidget.setHorizontalHeaderItem((TableWidget.columnCount()-1),QTableWidgetItem(listFields))
		TableWidget.setVerticalHeaderItem((TableWidget.rowCount()-1),QTableWidgetItem(listFields))
		##############
		WeighTableWidget.insertColumn(WeighTableWidget.columnCount())
		WeighTableWidget.setHorizontalHeaderItem((WeighTableWidget.columnCount()-1),QTableWidgetItem(listFields))
		self.updateGUIFuzzy()
		return 0
			
	def AddField(self):
		"""Add field to table in GUI"""
		listFields=self.EnvlistFieldsCBox.currentText()
		self.addFieldFctn(listFields,self.EnvTableWidget,self.EnvParameterWidget)
		return 0

	def removeFieldFctn(self,TableWidget,WeighTableWidget):
		"""base function for RemoveField()"""
		i=TableWidget.currentColumn()
		j=WeighTableWidget.currentColumn()
		if i == -1 and j== -1:
			QMessageBox.warning(self.iface.mainWindow(), "geoFuzzy",
			("column or row must be selected"), QMessageBox.Ok, QMessageBox.Ok)
		elif i != -1:
			TableWidget.removeColumn(i)
			TableWidget.removeRow(i)
			WeighTableWidget.removeColumn(i)
		elif j != -1:
			TableWidget.removeColumn(j)
			TableWidget.removeRow(j)
			WeighTableWidget.removeColumn(j)

	def RemoveField(self):
		"""Remove field in table in GUI"""
		self.EnvTableWidget.currentColumn()
		self.removeFieldFctn(self.EnvTableWidget,self.EnvParameterWidget)
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
			QMessageBox.warning(self.iface.mainWindow(), "geoFuzzy",
			("Input error\n" "Please insert numeric value "\
			"active"), QMessageBox.Ok, QMessageBox.Ok)


	def ChangeValue(self):
		"""Event for change values"""
		cell=self.EnvParameterWidget.currentItem()
		r=cell.row()
		c=cell.column()
		if r>0:
			if (self.EnvParameterWidget.item(r, c).backgroundColor().getRgb())== \
				(QtGui.QColor(255,165,0).getRgb()):
				self.EnvParameterWidget.item(r, c).setBackgroundColor(QtGui.QColor(255,0,0))
			else:
				self.EnvParameterWidget.item(r, c).setBackgroundColor(QtGui.QColor(255,165,0))
	
	def ReverseValues(self):
		cell=self.EnvParameterWidget.currentItem()
		c=cell.column()
		first=self.EnvParameterWidget.item(1,cell.column()).text()
		second=self.EnvParameterWidget.item(2,cell.column()).text()
		third=self.EnvParameterWidget.item(3,cell.column()).text()
		fourth=self.EnvParameterWidget.item(4,cell.column()).text()
		print first,second,third,fourth
		self.EnvParameterWidget.setItem(1,cell.column(),QTableWidgetItem(fourth))
		self.EnvParameterWidget.setItem(2,cell.column(),QTableWidgetItem(third))
		self.EnvParameterWidget.setItem(3,cell.column(),QTableWidgetItem(second))
		self.EnvParameterWidget.setItem(4,cell.column(),QTableWidgetItem(first))
		self.coloTable()
	
	
	def Elaborate(self):
		matrix=self.Attributes2Matrix()
		FzyMatrix=self.FuzzifiedMatrix(matrix)
		FzyMatrix=self.LinguisticModification(FzyMatrix)
		fzyIntersection=self.IntersectionMatrix(FzyMatrix)
		fzyUnion=self.UnionMatrix(FzyMatrix)
		self.OveralValue(fzyIntersection, fzyUnion)
		self.setModal(True)
		return 0
#############################################################################################################

	def calculateWeight(self,pairwise):
		"Define vector of weight based on eigenvector and eigenvalues"
		try:
			import numpy as np
			pairwise=np.array(pairwise)
			eigenvalues, eigenvector=np.linalg.eig(pairwise)
			maxindex=np.argmax(eigenvalues)
			eigenvalues=np.float32(eigenvalues)
			eigenvector=np.float32(eigenvector)
			weight=eigenvector[:, maxindex] #extract vector from eigenvector with max vaue in eigenvalues
			weight.tolist() #convert array(numpy)  to vector
			weight=[ w/sum(weight) for w in weight ]
			for i in range(len(weight)):
				self.EnvParameterWidget.setItem(1,i,QTableWidgetItem(str(round(weight[i],2))))
			return weight, eigenvalues, eigenvector
		except ImportError, e:
			QMessageBox.information(None, QCoreApplication.translate('geoFuzzy', "Plugin error"), \
			QCoreApplication.translate('geoFuzzy', "Couldn't import Python module 'numpy'.  You can install 'numpy' \
			with the following command: sudo easy_install numpy'.<br> or you can use 32bit version of QGS. [Message: %s]" % e))
			return

	def Consistency(self,weight,eigenvalues):
		"Calculete Consistency index in accord with Saaty (1977)"
		try:
			RI=[0.00, 0.00, 0.00,0.52,0.90,1.12,1.24,1.32,1.41]     #order of matrix: 0,1,2,3,4,5,6,7,8
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
			res = layer.dataProvider().addAttributes( [QgsField(Label, QVariant.Double,"",24,4,"")] )
		return 0


###########################################################################################

	def setting2csv(self):
		currentDIR = (os.path.dirname(str(self.activeLayer.source())))
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() for f in range(self.EnvTableWidget.columnCount())]
		weight=[float(self.EnvParameterWidget.item(0, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		#preference=[str(self.EnvParameterWidget.item(1, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		csvFile=open(os.path.join(currentDIR,'setFuzzy.csv'),"wb")
		write=csv.writer(csvFile,delimiter=";",quotechar='"',quoting=csv.QUOTE_NONNUMERIC)
		write.writerow(criteria)
		write.writerow(weight)
		#write.writerow(preference)
		csvFile.close()
		
	def csv2setting(self):
		currentDIR = (os.path.dirname(str(self.activeLayer.source())))
		setting=[]
		try:
			with open(os.path.join(currentDIR,'setFuzzy.csv')) as csvFile:
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
					#self.EnvParameterWidget.setItem(1,i,QTableWidgetItem(str(setting[2][l])))
					
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
		
	def RetriveXvalues(self):
		criteria=[self.EnvParameterWidget.horizontalHeaderItem(f).text() for f in range(self.EnvParameterWidget.columnCount())]
		firsth=[float(self.EnvParameterWidget.item(1, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		second=[float(self.EnvParameterWidget.item(2, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		third=[float(self.EnvParameterWidget.item(3, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		fourth=[float(self.EnvParameterWidget.item(4, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		return firsth,second,third,fourth
		
	def binaryYvalue(self,values):
		yValue=[]
		for co in values:
			if co == QtGui.QColor(255,165,0).getRgb():
				yValue.append(0)
			else:
				yValue.append(1)
		return yValue
	
	def RetriveYvalues(self):
		criteria=[self.EnvParameterWidget.horizontalHeaderItem(f).text() \
			for f in range(self.EnvParameterWidget.columnCount())]
		firsth=[self.EnvParameterWidget.item(1, c).backgroundColor().getRgb() \
			for c in range(self.EnvParameterWidget.columnCount())]
		second=[self.EnvParameterWidget.item(2, c).backgroundColor().getRgb() \
			for c in range(self.EnvParameterWidget.columnCount())]
		third=[self.EnvParameterWidget.item(3, c).backgroundColor().getRgb() \
			for c in range(self.EnvParameterWidget.columnCount())]
		fourth=[self.EnvParameterWidget.item(4, c).backgroundColor().getRgb() \
			for c in range(self.EnvParameterWidget.columnCount())]
		firsth=self.binaryYvalue(firsth)
		second=self.binaryYvalue(second)
		third=self.binaryYvalue(third)
		fourth=self.binaryYvalue(fourth)
		print firsth,second,third,fourth
		return firsth,second,third,fourth
	
	def Regression(self,Xvalues,Yvalue):
		"""y = slope*x+intercept 
		scipy.stats.linregress(x,y)"""
		try:  
			import numpy as np
			Xvalues=np.array(Xvalues)
			Yvalues=np.array(Yvalue)
			regFunct=np.polyfit(Xvalues, Yvalues, 3)
			valuer = np.poly1d(regFunct)
			print Xvalues
			print Yvalues
			return valuer
		except ImportError, e:
			QMessageBox.information(None, QCoreApplication.translate('geoFuzzy', "Plugin error"), \
			QCoreApplication.translate('geoFuzzy', "Couldn't import Python modules 'stast' from scipy. [Message: %s]" % e))  
	
	
	def FuzzifiedMatrix(self,matrix):
		""" """
		FzyMatrix=[]
		xfirsth,xsecond,xthird,xfourth=self.RetriveXvalues()
		yfirsth,ysecond,ythird,yfourth=self.RetriveYvalues()
		for i in range(len(xfirsth)):
			Xvalue=[xfirsth[i],xsecond[i],xthird[i],xfourth[i]]
			Yvalue=[yfirsth[i],ysecond[i],ythird[i],yfourth[i]]
			col=matrix[:,i]
			valuer=self.Regression(Xvalue,Yvalue)
			fzycol=[round(valuer(c),4) for c in col]
			FzyMatrix.append(fzycol)
		FzyMatrix=np.array(FzyMatrix, dtype = 'float32')
		#print [float(c) for c in FzyMatrix.transpose()[0]]
		return FzyMatrix.transpose()
			
	
	def LinguisticModification(self,matrix):
		"""+++"""
		criteria=[self.EnvParameterWidget.horizontalHeaderItem(f).text() for f in range(self.EnvParameterWidget.columnCount())]
		weight=[float(self.EnvParameterWidget.item(0, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		weight=[round(w/sum(weight),4) for w in weight ]
		matrixStd=[]
		for c,w in zip(range(len(criteria)),weight):
			self.EnvParameterWidget.setItem(0,c,QTableWidgetItem(str(w))) 
		self.EnvGetWeightBtn.setEnabled(False)
		provider=self.activeLayer.dataProvider()
		feat = QgsFeature()
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		for row in matrix:
			#print [float(f) for f in row]
			#print str(weight)
			rowMod=[(float(f)**w) for f,w in zip(row,weight)]
			matrixStd.append(rowMod)
		return matrixStd
	
	def IntersectionMatrix(self,matrix):
		intersection=[min(row) for row in matrix]
		return intersection
		
	def UnionMatrix(self,matrix):
		union=[max(row) for row in matrix]
		return union
			
	def OveralValue(self, fzyIntersection, fzyUnion):
		""" Calculate Environmental and Socio-Economicos distance from ideal point"""
		criteria=[self.EnvParameterWidget.horizontalHeaderItem(f).text() for f in range(self.EnvParameterWidget.columnCount())]
		provider=self.activeLayer.dataProvider()
		if provider.fieldNameIndex("geoFzyAND")==-1:
			self.AddDecisionField(self.activeLayer,"geoFzyAND")
		if provider.fieldNameIndex("geoFzyOR")==-1:
			self.AddDecisionField(self.activeLayer,"geoFzyOR")
		fldValueAND = provider.fieldNameIndex("geoFzyAND") #obtain classify field index from its name
		fldValueOR = provider.fieldNameIndex("geoFzyOR") #obtain classify field index from its name
		features=provider.featureCount() #Number of features in the layer.
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		##################################################################
		self.activeLayer.startEditing()
		self.EnvProgressBar.setRange(1,features)
		progress=0
		for feat,fzyValueAND,fzyValueOR in zip(self.activeLayer.getFeatures(),\
				fzyIntersection,fzyUnion):
			progress=progress+1
			self.activeLayer.changeAttributeValue(feat.id(), fldValueAND, round(float(fzyValueAND),4))
			self.activeLayer.changeAttributeValue(feat.id(), fldValueOR, round(float(fzyValueOR),4))
			self.EnvProgressBar.setValue(progress)
		self.activeLayer.commitChanges()
		self.EnvProgressBar.setValue(1)
		##################################################################
		self.EnvTEdit.append("done") #   setText
		self.setting2csv()
		return 0

###########################################################################################

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
			field=='geoFuzzy'
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
		layer = self.activeLayer
		layer = QgsVectorLayer(layer.source(), 'geoFuzzy', 'ogr')
		QgsMapLayerRegistry.instance().addMapLayer(layer)
		fields=['geoFuzzy']
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
			self.BuildGraphPnt(currentDir)
			self.BuildGraphIstogram(currentDir)
		except ImportError, e:
			QMessageBox.information(None, QCoreApplication.translate('geoFuzzy', "Plugin error"), \
			QCoreApplication.translate('geoFuzzy', "Couldn't import Python modules 'matplotlib' and 'numpy'. [Message: %s]" % e))
		self.BuildHTML()
		webbrowser.open(os.path.join(currentDir,"barGraph.html"))
		self.setModal(False)
		return 0



	def BuildGraphIstogram(self,currentDir):
		"""Build Istogram graph using pyplot"""

		geoFuzzyValue=self.ExtractAttributeValue('geoFuzzy')
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
		p1 = plt.bar((xpos), geoFuzzyValue, width=width, color='g',align='center') # yerr=womenStd)
		plt.ylabel('Scores')
		plt.title('geoFuzzy')
		plt.xticks((xpos), tuple(labels),rotation=90,fontsize=6 )
		plt.legend((p1[0]), ('geoFuzzy'))
		plt.savefig(os.path.join(currentDir,"histogram.png"))
		self.LblGraphic.setPixmap(QtGui.QPixmap(os.path.join(currentDir,"histogram.png")))
		plt.close('all')
		return 0

	
	def BuildHTML(self):
		geoFuzzyValue=self.ExtractAttributeValue('geoFuzzy')
		#SuitValue=[x+y+z for (x,y,z) in zip(EnvValue,EcoValue,SocValue)]
		label=self.LabelListFieldsCBox.currentText()
		labels=self.ExtractAttributeValue(label)
		labels=[str(l) for l in labels]
		htmlGraph.BuilHTMLGraph(geoFuzzyValue,labels,"geoFuzzy")
		return 0




###################################################################################################
	def about(self):
		"""
		Visualize an About window.
		"""

		QMessageBox.about(self, "About Fuzzy MCDA model",
		"""
			 <p>Please report any bug to <a href="mailto:g_massa@libero.it">g_massa@libero.it</a></p>
		""")

	def open_help(self):
		currentDir = unicode(os.path.abspath( os.path.dirname(__file__)))
		webbrowser.open(os.path.join(currentDir,"maplab.alwaysdata.net"))
