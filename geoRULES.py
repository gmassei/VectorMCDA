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
from __future__ import absolute_import


from builtins import zip
from builtins import str
from builtins import map
from builtins import range
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QDialog, QMessageBox, QTableWidget, QTableWidgetItem, QMenu

from qgis.PyQt import QtGui
from qgis.core import *
from qgis.gui import *

from .ui_geoRULES import Ui_Dialog

import numpy as np
import webbrowser
import matplotlib
import pickle
import os
import pdb

from . import DOMLEM


class geoRULESDialog(QDialog, Ui_Dialog):
	def __init__(self, iface):
		'''costruttore'''
		QDialog.__init__(self, iface.mainWindow())	# inizializzo il QDialog
		self.setupUi(self)	# inizializzo la GUI come realizzata nel QtDesigner
		self.iface = iface	# salvo il riferimento alla interfaccia di QGis

		self.activeLayer = self.iface.activeLayer()
		
		self.SettingButtonBox.accepted.connect(self.fieldToClasses)
		self.SettingButtonBox.clicked.connect(self.reject)
		self.CritExtractBtn.clicked.connect(self.extractRules)
		self.applyRulesBtn.clicked.connect(self.parsingRules)
		self.reclassButtonBox.clicked.connect(self.reject)
		self.CritHelpBtn.clicked.connect(self.open_help) 

		msg="Use  selected features only (%s)" % (len(self.activeLayer.selectedFeatures()))
		self.checkSelected.setText(msg)
		
		self.CritMapNameLbl.setText(self.activeLayer.name())
		self.CritMapNameLbl_2.setText(self.activeLayer.name())

		#self.CritListFieldsCBox.addItems(self.getFieldNames(self.activeLayer))
		fields=self.getFieldNames(self.activeLayer) #field list
		self.DeclistFieldsCBox.addItems(self.getFieldNames(self.activeLayer))
		
		self.typeRuleCmBox.addItems(['AT_LEAST','AT_MOST'])

		CritSetLabel=["Preference","Function"]
		self.critTableWiget.setColumnCount(2)
		self.critTableWiget.setHorizontalHeaderLabels(CritSetLabel)
		self.critTableWiget.setRowCount(len(fields))
		self.critTableWiget.setVerticalHeaderLabels(fields)
		self.cobBoxFieldNameDisc.addItems(self.getFieldNames(self.activeLayer))
		
		for r in range(len(fields)):
			self.critTableWiget.setItem(r,0,QTableWidgetItem("gain"))
			self.critTableWiget.setItem(r,1,QTableWidgetItem("continuous"))

		#retrieve signal for modified cell
		self.critTableWiget.cellClicked[(int,int)].connect(self.changeValue)
		
		###############################ContextMenu########################################
		headers = self.critTableWiget.verticalHeader()
		headers.setContextMenuPolicy(Qt.CustomContextMenu)
		headers.customContextMenuRequested.connect(self.popMenu)
		#################################################################################

		

	def getFieldNames(self, layer):
		provider=layer.dataProvider()
		field_map = provider.fields()
		field_list = []
		field_type=[]
		field_min=[]
		field_max=[]
		for field in field_map:
			if field.typeName()!='String':
				field_list.append(str(field.name()))
				field_type.append(str(field.typeName()))
				provider = layer.dataProvider()
				field_min.append(provider.minimumValue( provider.fieldNameIndex(str(field.name())) ))
				field_max.append(provider.maximumValue( provider.fieldNameIndex(str(field.name())) ))
		f=list(zip(field_list,field_type,field_min,field_max))
		#self.CritTEdit.setText(str(f))
		return field_list # sorted( field_list, cmp=locale.strcoll )


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
		
		
	def addPopup(self):
		Envfields=self.getFieldNames(self.activeLayer) #field list
		criteria=[self.critTableWiget.verticalHeaderItem(f).text() for f in range(self.critTableWiget.rowCount())]
		difference=set(Envfields)-set(criteria)
		for f in difference:
			self.addField(f)
		self.DeclistFieldsCBox.clear() 
		self.DeclistFieldsCBox.addItems(Envfields)
		
	def addField(self,f=''):
		"""Add field to table in GUI"""
		if f=='':
			f=self.CritListFieldsCBox.currentText()
		self.critTableWiget.insertRow(self.critTableWiget.rowCount())
		self.critTableWiget.setVerticalHeaderItem((self.critTableWiget.rowCount()-1),QTableWidgetItem(f))
		self.critTableWiget.setItem((self.critTableWiget.rowCount()-1),0,QTableWidgetItem("gain"))
		self.critTableWiget.setItem((self.critTableWiget.rowCount()-1),1,QTableWidgetItem("continuous"))
		return 0
		
		
		
	def removePopup(self):
		selected = sorted(self.critTableWiget.selectionModel().selectedRows(),reverse=True)
		if len(selected) > 0:
			for s in selected:
				self.removeField(s.row())
			criteria=[self.critTableWiget.verticalHeaderItem(f).text() for f in range(self.critTableWiget.rowCount())]
			self.critTableWiget.setCurrentCell(-1,-1)
			self.DeclistFieldsCBox.clear() 
			self.DeclistFieldsCBox.addItems(criteria)
		else:
			QMessageBox.warning(self.iface.mainWindow(), "geoRULES",
			("column must to be selected"), QMessageBox.Ok, QMessageBox.Ok)
		return 0
		


	def removeField(self,i):
		"""Remove field in table in GUI"""
		self.critTableWiget.removeRow(i)
		return 0


	def changeValue(self):
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
		"""Retrive single field value from attributes table"""
		fields=self.activeLayer.fields()
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
		
		
	def addDecisionField(self,layer,Label):
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
			self.addDecisionField(self.activeLayer,"Classified")
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
		
		
	def retrieveCriteria(self):
		decision=str(self.DeclistFieldsCBox.currentText())
		criteria=[self.critTableWiget.verticalHeaderItem(f).text() for f in range(self.critTableWiget.rowCount())]
		preference=[str(self.critTableWiget.item(c,0).text()) for c in range(self.critTableWiget.rowCount())]
		function=[str(self.critTableWiget.item(c,1).text()) for c in range(self.critTableWiget.rowCount())]
		pos=criteria.index(decision)
		criteria+=[criteria.pop(pos)]
		preference+=[preference.pop(pos)]
		function+=[function.pop(pos)]
		return criteria,preference,function
		
		
	def writeISFfile(self):
		""""extract data from attribute table and write idf file for extract rules"""
		#self.retrieveCriteria()
		#currentDIR = str(os.path.abspath( os.path.dirname(__file__)))
		currentDIR = QgsProject.instance().readPath("./")
		out_file = open(os.path.join(currentDIR,"example.isf"),"w")
		decision=str(self.DeclistFieldsCBox.currentText())
		criteria,preference,function=self.retrieveCriteria()
		decisionList=list(set(self.extractAttributeValue(self.DeclistFieldsCBox.currentText())))
		decisionList=[int(i) for i in decisionList]
		out_file.write("**ATTRIBUTES\n") 
		for c,f in zip(criteria,function):
			if (str(c)!=decision):
				if (f=='continuous'):
					out_file.write("+ %s: (%s)\n"  % (c,f))
				else:
					values=list(set(self.extractAttributeValue(c)))
					out_file.write("+ %s: %s\n"  % (c,str(list(map(int,values)))))
			else:
				out_file.write("+ %s: %s\n"  % (c,decisionList))
		out_file.write("decision: %s" % (self.DeclistFieldsCBox.currentText()))
		out_file.write("\n\n**PREFERENCES\n")
		for c,p in zip(criteria,preference):
			out_file.write("%s: %s\n"  % (c,p))
		out_file.write("\n**EXAMPLES\n")
		provider=self.activeLayer.dataProvider()
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its names
		fiDec=fids.index(provider.fieldNameIndex(self.DeclistFieldsCBox.currentText())) #retrieve item position
		fids+=[fids.pop(fiDec)] #move the decision field at the end
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


	def extractRules(self):
		"""run DOMLEM algorithms"""
		pathSource=QgsProject.instance().readPath("./")#os.path.dirname(str(self.iface.activeLayer().source()))
		self.writeISFfile()
		DOMLEM.main(pathSource)
		#self.setModal(False)
		self.showRules()
		return 0


	def showRules(self):
		"""show rules in geoRules """
		currentDIR = QgsProject.instance().readPath("./")
		try:
			rules=open(os.path.join(currentDIR,"rules.rls"))
			R=rules.readlines()
			self.RulesListWidget.clear()
			for E in R:
				self.RulesListWidget.addItem(E)
			self.RulesListWidget.itemClicked.connect(self.selectFeatures)
			rules.close()
		except:
			QMessageBox.critical(self.iface.mainWindow(), "Error", "No rules extracted")
		return 0

	def queryByRule(self,R):
		"""perform query based on extracted rules"""
		E=R[0]
		exp="%s %s %s" % (E['label'],E['sign'],E['condition'])
		if len(R)>1:
			for F in R[1:]:
				exp=exp + " AND %s %s %s" % (F['label'],F['sign'],F['condition'])
		return exp


	def extractFeaturesByExp(self,layer,exp):
		exp = QgsExpression(exp)
		it=layer.getFeatures(QgsFeatureRequest(exp))
		listOfResults=[i.id() for i in it]
		return listOfResults

	def selectFeatures(self):
		"""select feature in attribute table based on rules"""
		layer= self.iface.activeLayer()
		currentDIR = QgsProject.instance().readPath("./")
		rulesPKL = open(os.path.join(currentDIR,"RULES.pkl"), 'rb')
		RULES=pickle.load(rulesPKL) #save RULES dict in a file for use it in geoRULES module
		rulesPKL.close()
		selectedRule=self.RulesListWidget.currentItem().text()
		selectedRule=int(selectedRule.split(":")[0])
		R=RULES[selectedRule-1]
		exp=self.queryByRule(R)
		idSel=self.extractFeaturesByExp(layer,exp)
		layer.selectByIds(idSel)
		return 0
		
		
	def parsingRules(self):
		layer=self.iface.activeLayer()
		currentDIR = QgsProject.instance().readPath("./")
		rulesPKL = open(os.path.join(currentDIR,"RULES.pkl"), 'rb')
		RULES=pickle.load(rulesPKL) #save RULES dict in a file for use it in geoRULES module
		for R in RULES:
			exp=self.queryByRule(R)
			value=R[0]['class']
			self.reclass(exp,R[0]['rule_type'],value)
		rulesPKL.close()
		self.symbolize()
		
		
		
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
		layer.selectByIds(idf)
		if(layer):
			selectedId = layer.selectedFeatureIds()
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
		for classes_name, (color, label) in list(classes.items()):
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
		#self.setModal(False)
		
		
###################################################################################################
	def about(self):
		"""
		Visualize an About window.
		"""

		QMessageBox.about(self, "About geoRules",
		"""<p>Extract rules from attrubute table using dominance based rough set approach and performs geographic 
		multi-criteria decision using DOMLEM algorithmGreco S., Matarazzo, B., Słowiński, R., Stefanowski, J.: An Algorithm for Induction of Decision Rules Consistent with the Dominance Principle. In W. Ziarko, Y. Yao (eds.): Rough Sets and Current Trends in Computing. Lecture Notes in Artificial Intelligence 2005 (2001) 304--313. Springer-Verlag).
		Documents and data 	are available in: <a href="http://maplab.alwaysdata.net/geomcda.html"> www.maplab.alwaysdata.net</a></p>
			<p>Author:  Gianluca Massei <a href="mailto:g_massa@libero.it">[g_massa at libero.it]</a></p>
		""")

	def open_help(self):
		webbrowser.open("http://maplab.alwaysdata.net/geomcda.html")
