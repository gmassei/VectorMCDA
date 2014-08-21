# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name			 	 : geoRules - DBRA
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

from ui_geoRSDB import Ui_Dialog

import numpy as np
import webbrowser
import matplotlib
import os

import DOMLEM





class geoRSDBDialog(QDialog, Ui_Dialog):
	def __init__(self, iface):
		'''costruttore'''
		QDialog.__init__(self, iface.mainWindow())	# inizializzo il QDialog
		self.setupUi(self)	# inizializzo la GUI come realizzata nel QtDesigner
		self.iface = iface	# salvo il riferimento alla interfaccia di QGis
		self.activeLayer = self.iface.activeLayer()

		if self.activeLayer == None:
			QMessageBox.warning(self.iface.mainWindow(), "geoRules",
			("No active layer found\n" "Please make one or more vector layer "\
			"active"), QMessageBox.Ok, QMessageBox.Ok)
			return
		
		QObject.connect(self.SettingButtonBox, SIGNAL("accepted()"),self.AddDiscretizedField)
		QObject.connect(self.SettingButtonBox, SIGNAL("rejected()"),self, SLOT("reject()"))
		# imposto l'azione da eseguire al click sui pulsanti
		QObject.connect(self.CritAddFieldBtn, SIGNAL( "clicked()" ), self.AddField)
		QObject.connect(self.CritRemoveFieldBtn, SIGNAL( "clicked()" ), self.RemoveField)
		QObject.connect(self.CritExtractBtn, SIGNAL( "clicked()" ), self.ExtractRules)

		QObject.connect(self.RulesBtnBox, SIGNAL("rejected()"),self, SLOT("reject()"))
		
		self.CritMapNameLbl.setText(self.activeLayer.name())

		self.CritListFieldsCBox.addItems(self.GetFieldNames(self.activeLayer))
		fields=self.GetFieldNames(self.activeLayer) #field list
		self.DeclistFieldsCBox.addItems(self.GetFieldNames(self.activeLayer))

		CritSetLabel=["Preference","Function"]
		self.CritWeighTableWidget.setColumnCount(2)
		self.CritWeighTableWidget.setHorizontalHeaderLabels(CritSetLabel)
		self.CritWeighTableWidget.setRowCount(len(fields))
		self.CritWeighTableWidget.setVerticalHeaderLabels(fields)
		self.cobBoxFieldNameDisc.addItems(self.GetFieldNames(self.activeLayer))
		
		for r in range(len(fields)):
			self.CritWeighTableWidget.setItem(r,0,QTableWidgetItem("gain"))
			self.CritWeighTableWidget.setItem(r,1,QTableWidgetItem("continuous"))

		#retrieve signal for modified cell
		self.CritWeighTableWidget.cellClicked[(int,int)].connect(self.ChangeValue)

	#def GetFieldNames(self, layer):
		#"""retrive field names from active map/layer"""
		#fields = layer.dataProvider().fields()
		#field_list = []
		#for field in fields:
			#if field.typeName()!='String':
				#field_list.append(str(field.name()))
		#return field_list

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
		self.CritTEdit.setText(str(f))
		return field_list # sorted( field_list, cmp=locale.strcoll )


	def GetFieldAttributes(self, layer):
		field_map = layer.dataProvider().fields()
		for field_name in field_map:
			# Get the field index based on the field name
			field_index = layer.fieldNameIndex(field_name)
			# Define lower and upper value
			provider = layer.dataProvider()
			minimum = provider.minimumValue( field_index ).toDouble()[ 0 ]
			maximum = provider.maximumValue( field_index ).toDouble()[ 0 ]

	def AddField(self):
		f=self.CritListFieldsCBox.currentText()
		#self.CritTEdit.setText(f)
		##############
		self.CritWeighTableWidget.insertRow(self.CritWeighTableWidget.rowCount())
		self.CritWeighTableWidget.setVerticalHeaderItem((self.CritWeighTableWidget.rowCount()-1),QTableWidgetItem(f))
		return 0


	def RemoveField(self):
		f=self.CritListFieldsCBox.currentText()
		i=self.CritWeighTableWidget.currentRow()
		if i == -1:
			QMessageBox.warning(self.iface.mainWindow(), "geoRules",
			("column or row must be selected"), QMessageBox.Ok, QMessageBox.Ok)
		else:
			self.CritWeighTableWidget.removeRow(i)
		return 0


	def ChangeValue(self):
		cell=self.CritWeighTableWidget.currentItem()
		val=cell.text()
		if val=="cost":
			self.CritWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("gain"))
		elif val=="gain":
			self.CritWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("cost"))
		elif val=="continuous":
			self.CritWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("discrete"))
		elif val=="discrete":
			self.CritWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("continuous"))
		else:
			self.CritWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem(str(val)))
	
	
	def ExtractAttributeValue(self,field):
		"""Retrive single field value from attributes table"""
		fields=self.activeLayer.pendingFields()
		provider=self.activeLayer.dataProvider()
		fid=provider.fieldNameIndex(field)
		listValue=[]
		print fid
		if fields[fid].typeName()=='Real' or fields[fid].typeName()=='Integer':
			for feat in self.activeLayer.getFeatures():
				attribute=feat.attributes()[fid]
				print attribute
				listValue.append(float(attribute))
		else:
			for feat in self.activeLayer.getFeatures():
				attribute=feat.attributes()[fid]
				listValue.append(str(attribute))
		return listValue
	
		
	def AddDecisionField(self,layer,Label):
		"""Add field on attribute table"""
		caps = layer.dataProvider().capabilities()
		if caps & QgsVectorDataProvider.AddAttributes:
			res = layer.dataProvider().addAttributes( [QgsField(Label, QVariant.Double) ] )
		return 0

	def DiscretizeDecision(self,value,listClass,numberOfClasses):
		listValue=[]
		DiscValue=-1
		for o,t in zip(range(numberOfClasses-1),range(1,numberOfClasses)) :
			if ((float(value)>=float(listClass[o])) and (float(value)<=float(listClass[t]))):
				DiscValue=o
		return DiscValue
	

	def AddDiscretizedField(self):
		"""add new field"""
		numberOfClasses=5
		provider=self.activeLayer.dataProvider()
		#provider=self.active_layer.dataProvider()
		if provider.fieldNameIndex("Classified")==-1:
			self.AddDecisionField(self.activeLayer,"Classified")
		fidClass = provider.fieldNameIndex("Classified") #obtain classify field index from its name
		listInput=self.ExtractAttributeValue(self.cobBoxFieldNameDisc.currentText())
		widthOfClass=(max(listInput)-min(listInput))/numberOfClasses
		listClass=[(min(listInput)+(widthOfClass)*i) for i in range(numberOfClasses+1)]
		#self.EnvTEdit.setText(str(listClass))
		self.activeLayer.startEditing()
		decision=[]
		for feat in self.activeLayer.getFeatures():
			DiscValue=self.DiscretizeDecision(listInput[int(feat.id())],listClass,numberOfClasses)
			self.activeLayer.changeAttributeValue(feat.id(), fidClass, float(DiscValue))
			decision.append(DiscValue)
		self.activeLayer.commitChanges()
		return list(set(decision))
		
	def WriteISFfile(self):
		currentDIR = unicode(os.path.abspath( os.path.dirname(__file__)))
		out_file = open(currentDIR+"\\example.isf","w")
		criteria=[self.CritWeighTableWidget.verticalHeaderItem(f).text() for f in range(self.CritWeighTableWidget.rowCount())]
		preference=[str(self.CritWeighTableWidget.item(c,0).text()) for c in range(self.CritWeighTableWidget.rowCount())]
		function=[str(self.CritWeighTableWidget.item(c,1).text()) for c in range(self.CritWeighTableWidget.rowCount())]
		decision=list(set(self.ExtractAttributeValue(self.DeclistFieldsCBox.currentText())))
		decision=[int(i) for i in decision]
		provider=self.activeLayer.dataProvider()
		out_file.write("**ATTRIBUTES\n") 
		for c,f in zip(criteria,function):
			if(str(c)==str(self.DeclistFieldsCBox.currentText())):
				out_file.write("+ %s: %s\n"  % (c,decision))
			else:
				out_file.write("+ %s: (%s)\n"  % (c,f))
		
		out_file.write("decision: %s" % (self.DeclistFieldsCBox.currentText()))
		out_file.write("\n\n**PREFERENCES\n")
		for c,p in zip(criteria,preference):
			out_file.write("%s: %s\n"  % (c,p))
		out_file.write("\n**EXAMPLES\n")
		#if provider.fieldNameIndex("EnvValue")==-1:
		#	self.AddDecisionField(self.active_layer,"EnvValue")
		flIdAHP = provider.fieldNameIndex("SustValue") #obtain classify field index from its name
		features=provider.featureCount() #Number of features in the layer.
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its names

		for feat in self.activeLayer.getFeatures():
			attribute = [feat.attributes()[j] for j in fids]
			for i in (attribute):
				out_file.write(" %s " % (i))
			out_file.write("\n")
		out_file.write("\n**END")
		out_file.close()
		return 0

	def SelectFeatures(self):
		self.selection_layer = self.iface.activeLayer()
		itemSelect=self.RulesListWidget.currentItem().text()
		itemSelect=str(itemSelect.split("\t")[1])
		itemSelect=itemSelect.replace('[','')
		itemSelect=itemSelect.replace(']','')
		itemSelect=map(int,itemSelect.split(','))
		itemSelect=[(cod-1) for cod in itemSelect]
		self.selection_layer.setSelectedFeatures(itemSelect)
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
		self.ShowRules()
		return 0
		



