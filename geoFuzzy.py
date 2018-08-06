# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name            : geoFuzzy
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
from __future__ import print_function
from __future__ import absolute_import
from builtins import zip
from builtins import str
from builtins import range
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.PyQt import QtGui
import PyQt5.Qwt5 as Qwt

from qgis.core import *
from qgis.gui import *
	
import os
import webbrowser
import shutil
import csv

try:
	import matplotlib.pyplot as plt
	import numpy as np
except ImportError as e:
	QMessageBox.information(None, QCoreApplication.translate('geoFuzzy', "Plugin error"), \
	QCoreApplication.translate('geoFuzzy', "Couldn't import Python module. [Message: %s]" % e))
	
from . import htmlGraph

from .ui_geoFuzzy import Ui_Dialog

class geoFuzzyDialog(QDialog, Ui_Dialog):
	def __init__(self, iface):
		'''costruttore'''
		QDialog.__init__(self, iface.mainWindow())
		self.setupUi(self)
		self.iface = iface
		self.activeLayer = self.iface.activeLayer()
		self.Xgraph=self.Ygraph=[]
		self.fzyValuer={} #hold the valuer for fuzzify matrix
		for i in range(1,self.toolBox.count()):
			self.toolBox.setItemEnabled (i,False)
		QObject.connect(self.SetBtnQuit, SIGNAL("clicked()"),self, SLOT("reject()"))
		self.SetBtnAbout.clicked.connect(self.about)
		self.SetBtnHelp.clicked.connect(self.open_help)
		#QObject.connect(self.EnvAddFieldBtn, SIGNAL( "clicked()" ), self.AddField)
		self.EnvCalculateBtn.clicked.connect(self.AnalyticHierarchyProcess)
		self.EnvGetWeightBtn.clicked.connect(self.Elaborate)
		self.RenderBtn.clicked.connect(self.RenderLayer)
		self.GraphBtn.clicked.connect(self.BuildOutput)
		QObject.connect(self.AnlsBtnBox, SIGNAL("rejected()"),self, SLOT("reject()"))
		self.FzyFieldBtn.clicked.connect(self.getFzyGraph)
		self.FzfyListFieldsCBox.currentIndexChanged.connect(self.setqwtPlot)
		self.qwtPlot.setAutoReplot()
		self.qwtPlot.setAxisScale(0,0,1,0.1)
		self.picker = Qwt.QwtPlotPicker(Qwt.QwtPlot.xBottom,
								   Qwt.QwtPlot.yLeft,
								   #Qwt.QwtPicker.PointSelection,
								   Qwt.QwtPicker.PolygonSelection,
								   #Qwt.QwtPlotPicker.CrossRubberBand,
								   Qwt.QwtPlotPicker.PolygonRubberBand,
								   Qwt.QwtPicker.AlwaysOn,
								   self.qwtPlot.canvas())
		self.picker.setRubberBandPen(QPen(Qt.red))
		#self.picker.connect(self.picker,SIGNAL('selected(const QwtDoublePoint&)'), self.pickPoints)
		self.picker.connect(self.picker,SIGNAL('selected(const QwtPolygon&)'), self.pickPoints)
		# curves
		self.curve = Qwt.QwtPlotCurve('Fuzzify')
		self.curve.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased)
		self.curve.setPen(QPen(Qt.blue))
		self.curve.setYAxis(self.qwtPlot.yLeft)
		self.curve.attach(self.qwtPlot)
		
		sourceIn=str(self.iface.activeLayer().source())
		pathSource=os.path.dirname(sourceIn)
		outputFile="geoFuzzy.shp"
		sourceOut=os.path.join(pathSource,outputFile)

		self.EnvMapNameLbl.setText(self.activeLayer.name())
		self.EnvlistFieldsCBox.addItems(self.GetFieldNames(self.activeLayer))
		self.FzfyListFieldsCBox.addItems(self.GetFieldNames(self.activeLayer))
		self.LabelListFieldsCBox.addItems(self.GetFieldNames(self.activeLayer))
#################################################################################
		Envfields=self.GetFieldNames(self.activeLayer) #field list
		self.EnvTableWidget.setColumnCount(len(Envfields))
		self.EnvTableWidget.setHorizontalHeaderLabels(Envfields)
		self.EnvTableWidget.setRowCount(len(Envfields))
		self.EnvTableWidget.setVerticalHeaderLabels(Envfields)
		
		EnvSetLabel=["Hedges","Min", "Max", "Set"]
		self.EnvParameterWidget.setColumnCount(len(Envfields))
		self.EnvParameterWidget.setHorizontalHeaderLabels(Envfields)
		self.EnvParameterWidget.setRowCount(len(EnvSetLabel))
		self.EnvParameterWidget.setVerticalHeaderLabels(EnvSetLabel)
		for r in range(len(Envfields)):
			self.EnvTableWidget.setItem(r,r,QTableWidgetItem("1.0"))
		self.EnvTableWidget.cellChanged[(int,int)].connect(self.CompleteMatrix)
		self.updateTable()
###############################ContextMenu########################################
#		self.EnvTableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
#		self.EnvTableWidget.customContextMenuRequested.connect(self.removePopup)
		headers = self.EnvParameterWidget.horizontalHeader()
		headers.setContextMenuPolicy(Qt.CustomContextMenu)
		headers.customContextMenuRequested.connect(self.popMenu)
#################################################################################
		setting=self.csv2setting()
		try:
			self.setting2table(setting)
		except:
			pass
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
		outvLayer, __ = QFileDialog.getSaveFileName(self, "Output map",".", "ESRI Shapefile (*.shp)")
		self.OutlEdt.insert(outvLayer)
		return outvLayer
		
	def coloTable(self):
		rows=self.EnvParameterWidget.rowCount()
		cols=self.EnvParameterWidget.columnCount()
		for c in range(cols):
			self.EnvParameterWidget.item(1, c).setBackgroundColor(QtGui.QColor(255,165,0))
			self.EnvParameterWidget.item(2, c).setBackgroundColor(QtGui.QColor(255,0,0))
			self.EnvParameterWidget.item(3, c).setBackgroundColor(QtGui.QColor(216,216,216))
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
		EnvSetLabel=["Hedges","Min", "Max", "Set"]
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
			WeighTableWidget.setItem(3,r,QTableWidgetItem(str("Crisp")))
	
	def updateGUIFuzzy(self):
		provider=self.activeLayer.dataProvider() 
		self.updateFuzzyFctn(self.EnvTableWidget,self.EnvParameterWidget,provider)
		return 0


	def popMenu(self,pos):
		fields=list(range(10))
		menu = QMenu()
		removeAction = menu.addAction("Remove selected fields")
		reloadAllFields=menu.addAction("Add deleted fields")
		action = menu.exec_(self.mapToGlobal(QPoint(pos)))
		if action == removeAction:
			self.removePopup()
		elif action==reloadAllFields:
			self.addPopup()
			
	def removePopup(self):
		selected = sorted(self.EnvParameterWidget.selectionModel().selectedColumns(),reverse=True)
		if len(selected) > 0:
			for s in selected:
				self.removeField(s.column())
			self.EnvParameterWidget.setCurrentCell(-1,-1)
		else:
			QMessageBox.warning(self.iface.mainWindow(), "geoFuzzy",
			("column must to be selected"), QMessageBox.Ok, QMessageBox.Ok)
		return 0
		
		
		
	def addPopup(self):
		Envfields=self.GetFieldNames(self.activeLayer) #field list
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() for f in range(self.EnvTableWidget.columnCount())]
		difference=set(Envfields)-set(criteria)
		for f in difference:
			self.addField(f)
			
			
	def removeField(self,i):
		"""Remove field in table in GUI"""
		self.EnvTableWidget.removeColumn(i)
		self.EnvTableWidget.removeRow(i)
		self.EnvParameterWidget.removeColumn(i)
		self.FzfyListFieldsCBox.clear()
		self.FzfyListFieldsCBox.addItems([self.EnvTableWidget.verticalHeaderItem(f).text() \
			for f in range(self.EnvTableWidget.columnCount())])
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
			
			
	def addField(self,field=''):
		"""Add field to table in GUI"""
		if field=='':
			field=self.EnvlistFieldsCBox.currentText()
		self.addFieldFctn(field,self.EnvTableWidget,self.EnvParameterWidget)
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

	
	def pickPoints(self,aQPointF):
		#print 'aSlot gets:', aQPointF[0]
		Y=[self.qwtPlot.invTransform(0,p.y()) for p in aQPointF]
		X=[self.qwtPlot.invTransform(2,p.x()) for p in aQPointF]
		self.pickedTable.setColumnCount(2)
		self.pickedTable.setHorizontalHeaderLabels(['X','Y'])
		rows=list(range(len(X)))
		self.pickedTable.setRowCount(len(X))
		for x,y,r in zip(X,Y,rows):
			#self.pickedTable.setColumnWidth(r,  10);
			self.pickedTable.setItem(r,0,QTableWidgetItem(str(round(x,2))))
			self.pickedTable.setItem(r,1,QTableWidgetItem(str(round(y,2))))


		
	def plotGraph(self,valuer,field):
		X=self.ExtractAttributeValue(field)
		X=np.sort(X)
		Y=[valuer(x) for x in X]
		self.curve.setData(X,Y)
		
	def setqwtPlot(self):
		"""connected with FzfyListFieldsCBox"""
		field=self.FzfyListFieldsCBox.currentText()
		if field in self.fzyValuer:
			self.plotGraph(self.fzyValuer[field],field)
		field=self.FzfyListFieldsCBox.currentText()
		listValue=self.ExtractAttributeValue(field)
		limits=[float(min(listValue)),float(max(listValue))]
		stringa="%s - %s" % (limits[0],limits[1])
		self.rangeLineEdit.setText(stringa)
		self.qwtPlot.setAxisScale(2,limits[0],limits[1])
		self.qwtPlot.setAxisTitle(2,str(field))
		self.qwtPlot.updateAxes()


	def checkTableField(self):
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() \
			for f in range(self.EnvTableWidget.columnCount())]
		for r in range(len(criteria)):
			if str(criteria[r]) in self.fzyValuer:
				self.EnvParameterWidget.setItem(3,r,QTableWidgetItem(str("Fuzzy")))
				
	def RegressionGraph(self):
		polyFittValue=self.spinBoxFitting.value()
		rows=list(range(self.pickedTable.rowCount()))
		# fix_print_with_import
		print(rows)
		self.Xgraph=[float(self.pickedTable.item(r, 0).text()) for r in rows]
		self.Ygraph=[float(self.pickedTable.item(r, 1).text()) for r in rows]
		try:  
			import numpy as np
			#from scipy import  interpolate
			Xvalues=np.array(self.Xgraph)
			Yvalues=np.array(self.Ygraph)
			fit=np.polyfit(Xvalues, Yvalues, polyFittValue)
			valuer = np.poly1d(fit)
			return valuer
		except ImportError as e:
			QMessageBox.information(None, QCoreApplication.translate('geoFuzzy', "Plugin error"), \
			QCoreApplication.translate('geoFuzzy', "Couldn't import Python modules 'numpy' from scipy. [Message: %s]" % e))  
	
		
	def getFzyGraph(self):
		"""connected with getFzyGraph"""
		field=self.FzfyListFieldsCBox.currentText()
		valuer=self.RegressionGraph()
		self.plotGraph(valuer,field)
		self.fzyValuer[field]=valuer
		# fix_print_with_import
		print(self.fzyValuer)
		self.checkTableField()

	
	def Elaborate(self):
		matrix,criteria=self.Attributes2Matrix()
		FzyMatrix=self.FuzzifiedMatrix(matrix,criteria)
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
		except ImportError as e:
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
		return matrix, criteria
		
	
	def FuzzifiedMatrix(self,matrix,criteria):
		FzyMatrix=[]
		for i in range(len(criteria)):
			valuer=self.fzyValuer[str(criteria[i])]
			col=matrix[:,i]
			fzycol=[round(valuer(c),4) for c in col]
			FzyMatrix.append(fzycol)
		FzyMatrix=np.array(FzyMatrix, dtype = 'float32')
		#print [float(c) for c in FzyMatrix.transpose()[0]]
		return FzyMatrix.transpose()
			
	def LinguisticModification(self,matrix):
		"""+++"""
		criteria=[self.EnvParameterWidget.horizontalHeaderItem(f).text() for f in range(self.EnvParameterWidget.columnCount())]
		weight=[float(self.EnvParameterWidget.item(0, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		matrixStd=[] 
		self.EnvGetWeightBtn.setEnabled(False)
		#fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		for row in matrix:
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
		numberOfClasses=self.spinBoxClasNum.value()
		if(numberOfClasses==5):
			classes=['very low', 'low','medium','high','very high']
		else:
			classes=list(range(1,numberOfClasses+1))
		fieldName = field
		numberOfClasses=len(classes)
		layer = self.iface.activeLayer()
		fieldIndex = layer.fieldNameIndex(fieldName)
		provider = layer.dataProvider()
		minimum = provider.minimumValue( fieldIndex )
		maximum = provider.maximumValue( fieldIndex )
		RangeList = []
		Opacity = 1
		for c,i in zip(classes,list(range(len(classes)))):
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
		fields=['geoFzyAND','geoFzyOR']
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
				listValue.append(attribute)
		else:
			for feat in self.activeLayer.getFeatures():
				attribute=feat.attributes()[fid]
				listValue.append(str(attribute))
		return listValue

	def BuildOutput(self):
		"""General function for all graphical and tabula output"""
		currentDir = str(os.path.abspath( os.path.dirname(__file__)))
		if os.path.isfile(os.path.join(currentDir,"histogram.png"))==True:
			os.remove(os.path.join(currentDir,"histogram.png"))
		try:
			import matplotlib.pyplot as plt
			import numpy as np
			#self.BuildGraphPnt(currentDir)
			self.BuildGraphIstogram(currentDir)
		except ImportError as e:
			QMessageBox.information(None, QCoreApplication.translate('geoFuzzy', "Plugin error"), \
			QCoreApplication.translate('geoFuzzy', "Couldn't import Python modules 'matplotlib' and 'numpy'. [Message: %s]" % e))
		self.BuildHTML()
		webbrowser.open(os.path.join(currentDir,"barGraph.html"))
		self.setModal(False)
		return 0



	def BuildGraphIstogram(self,currentDir):
		"""Build Istogram graph using pyplot"""

		geoFuzzyAND=self.ExtractAttributeValue('geoFzyAND')
		geoFuzzyOR=self.ExtractAttributeValue('geoFzyOR')
		fig = plt.figure()
		fig.subplots_adjust(bottom=0.2)
		fig.subplots_adjust()
		ax = fig.add_subplot(111)
		ax.margins(0.05, None)
		xpos = np.arange(len(geoFuzzyOR))    # the x locations for the groups
		width = 0.35     # the width of the bars: can also be len(x) sequence
		label=self.LabelListFieldsCBox.currentText()
		labels=self.ExtractAttributeValue(label)
		p2 = plt.bar(xpos, geoFuzzyOR, width, color='r')
		p1 = plt.bar(xpos+width, geoFuzzyAND, width, color='g')
		plt.ylabel('Scores')
		plt.title('geoFuzzy')
		plt.xticks((xpos), tuple(labels),rotation=90,fontsize=6 )
		plt.legend((p1[0], p2[0]), ('Fuzzy intersection', 'Fuzzy union'))
		plt.savefig(os.path.join(currentDir,"histogram.png"))
		self.LblGraphic.setPixmap(QtGui.QPixmap(os.path.join(currentDir,"histogram.png")))
		plt.close('all')
		return 0

		p1 = plt.bar((xpos), EnvValue, width=width, color='g',align='center') # yerr=womenStd)
		p2 = plt.bar((xpos), EcoValue, width=width, color='r', bottom=EnvValue, align='center') #, yerr=menStd)
	
	def BuildHTML(self):
		geoFuzzyAND=self.ExtractAttributeValue('geoFzyAND')
		geoFuzzyOR=self.ExtractAttributeValue('geoFzyOR')
		geoFuzzyValue=[[A,B] for (A,B) in zip(geoFuzzyAND,geoFuzzyOR)]
		label=self.LabelListFieldsCBox.currentText()
		labels=self.ExtractAttributeValue(label)
		labels=[str(l) for l in labels]
		legend=['geoFzyAND','geoFzyOR']
		htmlGraph.BuilHTMLGraph(geoFuzzyValue,labels,legend)
		return 0

###################################################################################################
	def about(self):
		"""
		Visualize an About window.
		"""

		QMessageBox.about(self, "About geoFuzzy MCDA model",
		"""
			<p>Performs geographic multi-criteria decision making using Fuzzy MCDA model (Yager R. - 1977 - Multiple objective decision making using fuzzy set, International Journal of Man-Machine Studies, 12, 299-322).
			Documents and data 	are available in: <a href="http://maplab.alwaysdata.net/geomcda.html"> www.maplab.alwaysdata.net</a></p>
			<p>Author:  Gianluca Massei <a href="mailto:g_massa@libero.it">[g_massa at libero.it]</a></p>
		""")

	def open_help(self):
		webbrowser.open("http://maplab.alwaysdata.net/geomcda.html")
