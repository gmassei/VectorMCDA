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
	QMessageBox.information(None, QCoreApplication.translate('geoWeightedSum', "Plugin error"), \
	QCoreApplication.translate('geoWeightedSum', "Couldn't import Python module. [Message: %s]" % e))
	


#import DOMLEM
import htmlGraph

from ui_geoTOPSIS import Ui_Dialog

class geoTOPSISDialog(QDialog, Ui_Dialog):
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
		outputFile="geoTOPSIS.shp"
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
		EnvSetLabel=["Label","Weigths","Preference","Ideal point", "Worst point "]
		self.EnvParameterWidget.setColumnCount(len(Envfields))
		self.EnvParameterWidget.setHorizontalHeaderLabels(Envfields)
		self.EnvParameterWidget.setRowCount(5)
		self.EnvParameterWidget.setVerticalHeaderLabels(EnvSetLabel)
		for r in range(len(Envfields)):
			self.EnvTableWidget.setItem(r,r,QTableWidgetItem("1.0"))
			#self.EnvParameterWidget.setItem(1,r,QTableWidgetItem("1.0"))
			#self.EnvParameterWidget.setItem(2,r,QTableWidgetItem("gain"))
		#retrieve signal for modified cell
		self.EnvTableWidget.cellChanged[(int,int)].connect(self.CompleteMatrix)
		self.updateTable()
		try:
			self.EnvParameterWidget.cellClicked[(int,int)].connect(self.ChangeValue)
		except:
			pass
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
		
		
	def updateTable(self):
		"""Prepare and compile table in GUI"""
		fields=self.GetFieldNames(self.activeLayer)
		#fields = [field.name() for field in self.activeLayer.pendingFields() ]
		pathSource=os.path.dirname(str(self.activeLayer.source()))
		self.EnvTableWidget.setColumnCount(len(fields))
		self.EnvTableWidget.setHorizontalHeaderLabels(fields)
		self.EnvTableWidget.setRowCount(len(fields))
		self.EnvTableWidget.setVerticalHeaderLabels(fields)
		EnvSetLabel=["Label","Weigths","Preference","Ideal point", "Worst point "]
		self.EnvParameterWidget.setColumnCount(len(fields))
		self.EnvParameterWidget.setHorizontalHeaderLabels(fields)
		self.EnvParameterWidget.setRowCount(5)
		self.EnvParameterWidget.setVerticalHeaderLabels(EnvSetLabel)
		for r in range(len(fields)):
			self.EnvParameterWidget.setItem(0,r,QTableWidgetItem("*"))
			self.EnvParameterWidget.setItem(1,r,QTableWidgetItem("1.0"))
			self.EnvParameterWidget.setItem(2,r,QTableWidgetItem("gain"))
		self.updateGUIIdealPoint()
		return 0


	def updateGUIIdealPointFctn(self,TableWidget,WeighTableWidget,provider):
		"""base function for updateGUIIdealPoint()"""
		criteria=[TableWidget.verticalHeaderItem(f).text() for f in range(TableWidget.columnCount())]
		preference=[str(WeighTableWidget.item(2, c).text()) for c in range(WeighTableWidget.columnCount())]
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		minField=[provider.minimumValue( f ) for f in fids]
		maxField=[provider.maximumValue( f ) for f in fids]
		for r in range(len(preference)):
			if preference[r]=='gain':
				WeighTableWidget.setItem(3,r,QTableWidgetItem(str(maxField[r])))#ideal point
				WeighTableWidget.setItem(4,r,QTableWidgetItem(str(minField[r])))#worst point
			elif preference[r]=='cost':
				WeighTableWidget.setItem(3,r,QTableWidgetItem(str(minField[r])))
				WeighTableWidget.setItem(4,r,QTableWidgetItem(str(maxField[r])))
			else:
				WeighTableWidget.setItem(3,r,QTableWidgetItem("0"))
				WeighTableWidget.setItem(4,r,QTableWidgetItem("0"))
	
	def updateGUIIdealPoint(self):
		provider=self.activeLayer.dataProvider() #provider=self.active_layer.dataProvider() 
		##Environmental
		self.updateGUIIdealPointFctn(self.EnvTableWidget,self.EnvParameterWidget,provider)
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
		WeighTableWidget.setItem(1,(WeighTableWidget.columnCount()-1),QTableWidgetItem("1.0"))
		WeighTableWidget.setItem(2,(WeighTableWidget.columnCount()-1),QTableWidgetItem("gain"))
		WeighTableWidget.setItem(3,(WeighTableWidget.columnCount()-1),QTableWidgetItem("0.0"))
		WeighTableWidget.setItem(4,(WeighTableWidget.columnCount()-1),QTableWidgetItem("0.0"))
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
			QMessageBox.warning(self.iface.mainWindow(), "geoTOPSYS",
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
			QMessageBox.warning(self.iface.mainWindow(), "geoTOPSYS",
			("Input error\n" "Please insert numeric value "\
			"active"), QMessageBox.Ok, QMessageBox.Ok)


	def ChangeValue(self):
		"""Event for change gain/cost"""
		cell=self.EnvParameterWidget.currentItem()
		r=cell.row()
		c=cell.column()
		first=self.EnvParameterWidget.item(3, c).text()
		second=self.EnvParameterWidget.item(4, c).text()
		if cell.row()==2:
			val=cell.text()
			if val=="cost":
				self.EnvParameterWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("gain"))
			elif val=="gain":
				self.EnvParameterWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("cost"))
			else:
				self.EnvParameterWidget.setItem(cell.row(),cell.column(),QTableWidgetItem(str(val)))
			self.EnvParameterWidget.setItem(3,c, QTableWidgetItem(second))
			self.EnvParameterWidget.setItem(4,c, QTableWidgetItem(first))
		
			
	def Elaborate(self):
		matrix=self.StandardizationIdealPoint()
		self.RelativeCloseness(matrix)
		#self.OveralValue()
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
			QMessageBox.information(None, QCoreApplication.translate('geoTOPSYS', "Plugin error"), \
			QCoreApplication.translate('geoTOPSYS', "Couldn't import Python module 'numpy'.  You can install 'numpy' \
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
	def ExtractFieldSumSquare(self,field):
		"""Retrive single field value from attributes table"""
		provider=self.activeLayer.dataProvider()
		fid=provider.fieldNameIndex(field)
		listValue=[]
		for feat in self.activeLayer.getFeatures():
			attribute=feat.attributes()[fid]
			listValue.append(attribute)
		listValue=[pow(l,2) for l in listValue]
		return (sum(listValue)**(0.5))
	
	def StandardizationIdealPoint(self):
		"""Perform STEP 1 and STEP 2 of TOPSIS algorithm"""
		criteria=[self.EnvParameterWidget.horizontalHeaderItem(f).text() for f in range(self.EnvParameterWidget.columnCount())]
		weight=[float(self.EnvParameterWidget.item(1, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		weight=[ round(w/sum(weight),4) for w in weight ]
		for c,w in zip(range(len(criteria)),weight):
			self.EnvParameterWidget.setItem(1,c,QTableWidgetItem(str(w))) 
		self.EnvGetWeightBtn.setEnabled(False)
		provider=self.activeLayer.dataProvider()
		feat = QgsFeature()
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		#self.EnvTEdit.append(str(dict(zip(fids,[(field) for field in criteria]))))
		sumSquareColumn=[self.ExtractFieldSumSquare(field) for field in criteria]
		matrix=[]
		for feat in self.activeLayer.getFeatures():
			row=[feat.attributes()[self.activeLayer.fieldNameIndex(name)] for  name in criteria]
			matrix.append(row)
		matrix=np.array(matrix, dtype = 'float32')
		matrixStd=[]
		for row in matrix:
			rowStd=[]
			for f,w,sSq in zip(row,weight,sumSquareColumn): #N.B. verifica corretto allineamento con i pesi
				value=(float(f)/float(sSq))*w   # TOPSIS algorithm: STEP 1 and STEP 2
				rowStd.append(value)
			matrixStd.append(rowStd)
		return matrixStd
		
			
	def RelativeCloseness(self, matrix):
		""" Calculate Environmental and Socio-Economicos distance from ideal point"""
		criteria=[self.EnvParameterWidget.horizontalHeaderItem(f).text() for f in range(self.EnvParameterWidget.columnCount())]
		weight=[float(self.EnvParameterWidget.item(1, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		idealPoint=[float(self.EnvParameterWidget.item(3, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		sumSquareColumnList=[self.ExtractFieldSumSquare(field) for field in criteria]
		idealPoint=[float(self.EnvParameterWidget.item(3, c).text())/sumSquareColumnList[c]*weight[c] \
			for c in range(self.EnvParameterWidget.columnCount())]
		worstPoint=[float(self.EnvParameterWidget.item(4, c).text())/sumSquareColumnList[c]*weight[c] \
			for c in range(self.EnvParameterWidget.columnCount())]
		provider=self.activeLayer.dataProvider()
		if provider.fieldNameIndex("geoTOPSYS")==-1:
			self.AddDecisionField(self.activeLayer,"geoTOPSYS")
		fldValue = provider.fieldNameIndex("geoTOPSYS") #obtain classify field index from its name
		self.EnvTEdit.append("done") #   setText
		#self.EnvTEdit.append(str(idealPoint)+"#"+str(worstPoint))
		features=provider.featureCount() #Number of features in the layer.
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name

		##################################################################
		self.activeLayer.startEditing()
		self.EnvProgressBar.setRange(1,features)
		progress=0
		relativeClosenessList=[]
		for row in matrix:
			IP=WP=0
			for f,idp,wrp in zip(row,idealPoint,worstPoint):
				IP =IP+(float(f-idp)**2)   # TOPSIS algorithm: STEP 4
				WP =WP+(float(f-wrp)**2)
			relativeClosenessList.append((WP**(0.5))/((WP**(0.5))+(IP**(0.5))))
		for feat,relativeCloseness in zip(self.activeLayer.getFeatures(),relativeClosenessList):
			progress=progress+1
			self.activeLayer.changeAttributeValue(feat.id(), fldValue, round(float(relativeCloseness),4))
			self.EnvProgressBar.setValue(progress)
		self.activeLayer.commitChanges()
		self.EnvProgressBar.setValue(1)
		##################################################################
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
		fields=['geoTOPSYS']
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
			QMessageBox.information(None, QCoreApplication.translate('geoUmbriaSUIT', "Plugin error"), \
			QCoreApplication.translate('geoTOPSIS', "Couldn't import Python modules 'matplotlib' and 'numpy'. [Message: %s]" % e))
		self.BuildHTML()
		webbrowser.open(os.path.join(currentDir,"barGraph.html"))
		self.setModal(False)
		return 0



	def BuildGraphIstogram(self,currentDir):
		"""Build Istogram graph using pyplot"""

		geoWSMValue=self.ExtractAttributeValue('geoTOPSIS')
		
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
		#p2 = plt.bar((xpos), EcoValue, width=width, color='r', bottom=EnvValue, align='center') #, yerr=menStd)
		#bot=[e+c for e,c in zip(EnvValue,EcoValue)]
		#p3 = plt.bar((xpos), SocValue, width=width, color='c', bottom=bot, align='center') #, yerr=menStd)
		#n, bins, patches = plt.hist( [EnvValue,EcoValue,SocValue], histtype='bar', stacked=True)
		plt.ylabel('Scores')
		plt.title('geoTOPSIS')
		plt.xticks((xpos), tuple(labels),rotation=90,fontsize=6 )
		plt.legend((p1[0]), ('geoTOPSIS'))
		plt.savefig(os.path.join(currentDir,"histogram.png"))
		self.LblGraphic.setPixmap(QtGui.QPixmap(os.path.join(currentDir,"histogram.png")))
		plt.close('all')
		return 0

	
	def BuildHTML(self):
		geoWSMValue=self.ExtractAttributeValue('geoTOPSIS')
		#SuitValue=[x+y+z for (x,y,z) in zip(EnvValue,EcoValue,SocValue)]
		label=self.LabelListFieldsCBox.currentText()
		labels=self.ExtractAttributeValue(label)
		labels=[str(l) for l in labels]
		htmlGraph.BuilHTMLGraph(geoWSMValue,labels,"geoTOPSIS")
		return 0




###################################################################################################
	def about(self):
		"""
		Visualize an About window.
		"""

		QMessageBox.about(self, "About TOPSIS model",
		"""
			 <p>Please report any bug to <a href="mailto:g_massa@libero.it">g_massa@libero.it</a></p>
		""")

	def open_help(self):
		currentDir = unicode(os.path.abspath( os.path.dirname(__file__)))
		webbrowser.open(os.path.join(currentDir,"maplab.alwaysdata.net"))
