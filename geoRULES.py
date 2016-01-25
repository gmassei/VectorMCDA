# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name			 	 : geoRULES - DBRA
Description          : extract rules from attrubute table using dominance
						based rough set approach"
Date                 : 20/08/2013
copyright            : (C) 2013 by Gianluca Massei
email                : g_massa@libero.it

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

from ui_geoRULES import Ui_Dialog

import numpy as np
import webbrowser
import matplotlib
import pickle
import os

import DOMLEM


class geoRULESDialog(QDialog, Ui_Dialog):
	def __init__(self, iface):
		'''costruttore'''
		QDialog.__init__(self, iface.mainWindow())	# inizializzo il QDialog
		self.setupUi(self)	# inizializzo la GUI come realizzata nel QtDesigner
		self.iface = iface	# salvo il riferimento alla interfaccia di QGis

		self.activeLayer = self.iface.activeLayer()
		
		QObject.connect(self.SettingButtonBox, SIGNAL("accepted()"),self.fieldToClasses)
		QObject.connect(self.SettingButtonBox, SIGNAL("rejected()"),self, SLOT("reject()"))
		# imposto l'azione da eseguire al click sui pulsanti
		QObject.connect(self.CritAddFieldBtn, SIGNAL( "clicked()" ), self.AddField)
		QObject.connect(self.CritExtractBtn, SIGNAL( "clicked()" ), self.ExtractRules)
	#	QObject.connect(self.RulesBtnBox, SIGNAL("rejected()"),self, SLOT("reject()"))
		QObject.connect(self.applyRulesBtn, SIGNAL("clicked()"),self.parsingRules)
		QObject.connect(self.reclassButtonBox, SIGNAL("rejected()"),self, SLOT("reject()"))

		msg="Use  selected features only (%s)" % (len(self.activeLayer.selectedFeatures()))
		self.checkSelected.setText(msg)
		
		self.CritMapNameLbl.setText(self.activeLayer.name())
		self.CritMapNameLbl_2.setText(self.activeLayer.name())

		self.CritListFieldsCBox.addItems(self.GetFieldNames(self.activeLayer))
		fields=self.GetFieldNames(self.activeLayer) #field list
		self.DeclistFieldsCBox.addItems(self.GetFieldNames(self.activeLayer))
		
		self.typeRuleCmBox.addItems(['AT_LEAST','AT_MOST'])

		CritSetLabel=["Preference","Function"]
		self.critTableWiget.setColumnCount(2)
		self.critTableWiget.setHorizontalHeaderLabels(CritSetLabel)
		self.critTableWiget.setRowCount(len(fields))
		self.critTableWiget.setVerticalHeaderLabels(fields)
		self.cobBoxFieldNameDisc.addItems(self.GetFieldNames(self.activeLayer))
		
		for r in range(len(fields)):
			self.critTableWiget.setItem(r,0,QTableWidgetItem("gain"))
			self.critTableWiget.setItem(r,1,QTableWidgetItem("continuous"))

		#retrieve signal for modified cell
		self.critTableWiget.cellClicked[(int,int)].connect(self.ChangeValue)
		
		###############################ContextMenu########################################
		headers = self.critTableWiget.verticalHeader()
		headers.setContextMenuPolicy(Qt.CustomContextMenu)
		headers.customContextMenuRequested.connect(self.removePopup)
		#################################################################################
		self.CritListFieldsCBox.setContextMenuPolicy(Qt.CustomContextMenu)
		self.CritListFieldsCBox.customContextMenuRequested.connect(self.addPopup)
		

	def GetFieldNames(self, layer):
		field_map = layer.dataProvider().fields()
		field_list = []
		field_type=[]
		field_min=[]
		field_max=[]
		for field in field_map:
			if field.typeName()!='String':
				field_list.append(str(field.name()))
				field_type.append(str(field.typeName()))
				provider = layer.dataProvider()
				field_min.append(provider.minimumValue( layer.fieldNameIndex(str(field.name())) ))
				field_max.append(provider.maximumValue( layer.fieldNameIndex(str(field.name())) ))
		f=zip(field_list,field_type,field_min,field_max)
		#self.CritTEdit.setText(str(f))
		return field_list # sorted( field_list, cmp=locale.strcoll )


	def addPopup(self, pos):
		menu = QMenu()
		addAction = menu.addAction("Add field")
		action = menu.exec_(self.mapToGlobal(pos))
		if action == addAction:
			self.AddField()
		return 0
		
		
	def AddField(self):
		f=self.CritListFieldsCBox.currentText()
		self.critTableWiget.insertRow(self.critTableWiget.rowCount())
		self.critTableWiget.setVerticalHeaderItem((self.critTableWiget.rowCount()-1),QTableWidgetItem(f))
		return 0
		
	
		
	def removePopup(self, pos):
		i= self.critTableWiget.selectionModel().currentIndex().row()
		if i != -1:
			menu = QMenu()
			removeAction = menu.addAction("Remove field")
			action = menu.exec_(self.mapToGlobal(pos))
			if action == removeAction:
				self.RemoveField(i)
				self.critTableWiget.setCurrentCell(-1,-1)
		else:
			QMessageBox.warning(self.iface.mainWindow(), "geoRULES",
			("column or row must be selected"), QMessageBox.Ok, QMessageBox.Ok)
		return 0


	def RemoveField(self,i):
		"""Remove field in table in GUI"""
		self.critTableWiget.removeRow(i)
		return 0


	def ChangeValue(self):
		cell=self.critTableWiget.currentItem()
		val=cell.text()
		if val=="cost":
			self.critTableWiget.setItem(cell.row(),cell.column(),QTableWidgetItem("gain"))
		elif val=="gain":
			self.critTableWiget.setItem(cell.row(),cell.column(),QTableWidgetItem("cost"))
		elif val=="continuous":
			self.critTableWiget.setItem(cell.row(),cell.column(),QTableWidgetItem("discrete"))
		elif val=="discrete":
			self.critTableWiget.setItem(cell.row(),cell.column(),QTableWidgetItem("continuous"))
		else:
			self.critTableWiget.setItem(cell.row(),cell.column(),QTableWidgetItem(str(val)))
	
	
	def extractAttributeValue(self,field):
		"""Retrive single field value from attributes table"""
		fields=self.activeLayer.pendingFields()
		fid = self.activeLayer.fieldNameIndex(field)
		listValue=[]
		if self.checkSelected.isChecked():
			features=self.activeLayer.selectedFeatures()
		else:
			features=self.activeLayer.getFeatures()
		for feat in features:
			attribute=feat.attributes()[fid]
			if fields[fid].typeName()=='Real' or fields[fid].typeName()=='Integer':
				listValue.append(float(attribute))
			else:
				listValue.append(str(attribute))
		return listValue
		
		
	def AddDecisionField(self,layer,Label):
		"""Add field on attribute table"""
		caps = layer.dataProvider().capabilities()
		if caps & QgsVectorDataProvider.AddAttributes:
			res = layer.dataProvider().addAttributes( [QgsField(Label, QVariant.Double) ] )
			layer.updateFields()
		return 0


	def equalInterval(self,values, classes):
		"""Returns breaks based on dividing the range of 'values' into 
		'classes' parts ( Equal interval algorithm )."""
		_min = min(values)
		_max = max(values)
		unit = (_max - _min) / classes
		classLimits = [_min + k*unit for k in range(classes+1)]
		return classLimits


	def checkClassValue(self,value,classLimits):
		classValue=val=0
		for i,j in zip(classLimits[:-1],classLimits[1:]) :
			val=val+1
			if (float(value)>=i and float(value)<=j):
				classValue=val
		return classValue
	
	
	
	def fieldToClasses(self):
		provider=self.activeLayer.dataProvider()
		if provider.fieldNameIndex("Classified")==-1:
			self.AddDecisionField(self.activeLayer,"Classified")
		fidClass = provider.fieldNameIndex("Classified") #obtain classify field index from its name
		listValues=self.extractAttributeValue(self.cobBoxFieldNameDisc.currentText())
		classes=5 #int(self.spinClasseNum.value()) #TODO: it can use different classes, but in DOMLEM there are only 5 label_classes
		classLimits=self.equalInterval(listValues, classes)
		self.activeLayer.startEditing()
		decision=[]
		if self.checkSelected.isChecked():
			features=self.activeLayer.selectedFeatures()
		else:
			features=self.activeLayer.getFeatures()
		for feat,i in zip(features,listValues):
			classValue=self.checkClassValue(i,classLimits)
			#print feat.id(),i,classValue
			self.activeLayer.changeAttributeValue(feat.id(), fidClass, float(classValue))
			decision.append(classValue)
		self.activeLayer.commitChanges()
		return list(set(decision))
		
		
	def WriteISFfile(self):
		currentDIR = unicode(os.path.abspath( os.path.dirname(__file__)))
		out_file = open(os.path.join(currentDIR,"example.isf"),"w")
		criteria=[self.critTableWiget.verticalHeaderItem(f).text() for f in range(self.critTableWiget.rowCount())]
		preference=[str(self.critTableWiget.item(c,0).text()) for c in range(self.critTableWiget.rowCount())]
		function=[str(self.critTableWiget.item(c,1).text()) for c in range(self.critTableWiget.rowCount())]
		decision=list(set(self.extractAttributeValue(self.DeclistFieldsCBox.currentText())))
		decision=[int(i) for i in decision]
		out_file.write("**ATTRIBUTES\n") 
		for c,f in zip(criteria,function):
			if (str(c)!=str(self.DeclistFieldsCBox.currentText())):
				if (f=='continuous'):
					out_file.write("+ %s: (%s)\n"  % (c,f))
				else:
					values=list(set(self.extractAttributeValue(c)))
					out_file.write("+ %s: (%s)\n"  % (c,values))
			else:
				out_file.write("+ %s: %s\n"  % (c,decision))
		out_file.write("decision: %s" % (self.DeclistFieldsCBox.currentText()))
		out_file.write("\n\n**PREFERENCES\n")
		for c,p in zip(criteria,preference):
			out_file.write("%s: %s\n"  % (c,p))
		out_file.write("\n**EXAMPLES\n")
		provider=self.activeLayer.dataProvider()
		#features=provider.featureCount() #Number of features in the layer.
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its names
		if self.checkSelected.isChecked():
			features=self.activeLayer.selectedFeatures()
		else:
			features=self.activeLayer.getFeatures()
		
		for feat in features:
			attribute = [feat.attributes()[j] for j in fids]
			for i in (attribute):
				out_file.write(" %s " % (i))
				#self.ruleEdit.append(str(i))
			out_file.write("\n")
		out_file.write("\n**END")
		out_file.close()
		return 0


	def SelectFeatures(self):
		self.selectionLayer = self.iface.activeLayer()
		itemSelect=self.RulesListWidget.currentItem().text()
		itemSelect=str(itemSelect.split("\t")[1])
		itemSelect=itemSelect.replace('[','')
		itemSelect=itemSelect.replace(']','')
		itemSelect=map(int,itemSelect.split(','))
		itemSelect=[(cod-1) for cod in itemSelect]
		self.selectionLayer.setSelectedFeatures(itemSelect)
		#self.ruleEdit.setText(str(itemSelect))
		return 0


	def ShowRules(self):
		currentDIR = unicode(os.path.abspath( os.path.dirname(__file__)))
		rules=open(currentDIR+"\\rules.rls")
		R=rules.readlines()
		self.RulesListWidget.clear()
		for E in R:
			self.RulesListWidget.addItem(E)
		self.RulesListWidget.itemClicked.connect(self.SelectFeatures)
		return 0

		
	def ExtractRules(self):
		pathSource=os.path.dirname(str(self.iface.activeLayer().source()))
		self.WriteISFfile()
		DOMLEM.main(pathSource)
		self.setModal(False)
		self.ShowRules()
		

	def parsingRules(self):
		layer=self.iface.activeLayer()
		currentDIR = unicode(os.path.abspath( os.path.dirname(__file__)))
		rulesPKL = open(os.path.join(currentDIR,"RULES.pkl"), 'rb')
		RULES=pickle.load(rulesPKL) #save RULES dict in a file for use it in geoRULES module
		for R in RULES:
			E=R[0]
			exp="%s %s %s" % (E['label'],E['sign'],E['condition'])
			if len(R)>1:
				for F in R[:1]:
					exp=exp + " AND %s %s %s" % (F['label'],F['sign'],F['condition'])
			value=R[0]['class']
			print value
			self.reclass(exp,E['rule_type'],value)
		rulesPKL.close()
		self.symbolize()
		
	def whereExpression(self,layer, exp):
		exp = QgsExpression(exp)
		if exp.hasParserError():
			raise Exception(exp.parserErrorString())
		exp.prepare(layer.pendingFields())
		for feature in layer.getFeatures():
			value = exp.evaluate(feature)
			if exp.hasEvalError():
				raise ValueError(exp.evalErrorString())
			if bool(value):
				yield feature

		
	def reclass(self, exp, rule, value='-9999',):
		layer = self.iface.activeLayer()
		provider=layer.dataProvider()
		if provider.fieldNameIndex("AT_LEAST")==-1:
			res=layer.dataProvider().addAttributes( [QgsField("AT_LEAST", QVariant.Int) ] )
		fidAL = layer.fieldNameIndex('AT_LEAST')
		if provider.fieldNameIndex("AT_MOST")==-1:
			res=layer.dataProvider().addAttributes( [QgsField("AT_MOST", QVariant.Int) ] )
		fidAM = layer.fieldNameIndex('AT_MOST')
		
		idf=[f.id() for f in  self.whereExpression(layer, exp)]
		layer.setSelectedFeatures(idf)
		if(layer):
			selectedId = layer.selectedFeaturesIds()
			layer.startEditing()
			for i in selectedId:
				if rule=="three": #AT MOST
					layer.changeAttributeValue(int(i), fidAM, value) # 1 being the second column
				elif rule =="one": #AT LEAST
					layer.changeAttributeValue(int(i), fidAL, value) # 1 being the second column
			layer.commitChanges()
		else:
			QMessageBox.critical(self.iface.mainWindow(), "Error", "Please select a layer")
		return 0


	def symbolize(self):
		layer=self.activeLayer
		decision=list(set(self.extractAttributeValue(self.DeclistFieldsCBox.currentText())))
		decision=[int(i) for i in decision]
		numberOfClasses=5 #self.spinBoxClasNum.value()
		if(numberOfClasses==5):
			classes=['very low', 'low','medium','high','very high']
					
		classes = {
			1: ('#f59053', 'very low [1]'),
			2: ('#fede99', 'low [2]'),
			3: ('#ddefcf', 'medium [3]'),
			4: ('#91c6de', 'high [4]'),
			5: ('#2c7bb6', 'very high [5]'),
			'': ('#d7caca', 'n.c.'),
		}

		# create a category for each item in classes
		categories = []
		for classes_name, (color, label) in classes.items():
			symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
			symbol.setColor(QColor(color))
			category = QgsRendererCategoryV2(classes_name, symbol, label)
			categories.append(category)

		# create the renderer and assign it to a layer
		expression = self.typeRuleCmBox.currentText() # field name
		renderer = QgsCategorizedSymbolRendererV2(expression, categories)
		layer.setRendererV2(renderer)

	def renderLayer(self):
		""" Load thematic layers in canvas """
		fields=['AT_LEAST','AT_MOST']
		for f in fields:
			self.Symbolize(f)
		self.setModal(False)
