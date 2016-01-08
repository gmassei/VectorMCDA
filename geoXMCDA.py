# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name            : geoXMCDA
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

from ui_geoXMCDA import Ui_Dialog

import numpy as np
import webbrowser
import os,csv

#from xml.etree.ElementTree import Element, SubElement, Comment,parse,tostring
import xml.etree.ElementTree as ET



class geoXMCDADialog(QDialog, Ui_Dialog):
	def __init__(self, iface):
		'''costruttore'''
		QDialog.__init__(self, iface.mainWindow())	# inizializzo il QDialog
		self.setupUi(self)	# inizializzo la GUI come realizzata nel QtDesigner
		self.iface = iface	# salvo il riferimento alla interfaccia di QGis
		self.activeLayer = self.iface.activeLayer()
		# imposto l'azione da eseguire al click sui pulsanti
		QObject.connect(self.CritAddFieldBtn, SIGNAL( "clicked()" ), self.AddField)
		QObject.connect(self.CritRemoveFieldBtn, SIGNAL( "clicked()" ), self.RemoveField)
		QObject.connect(self.CritExtractBtn, SIGNAL( "clicked()" ), self.ExtractData)
		QObject.connect(self.toXMXCDAButtonBox, SIGNAL("rejected()"),self, SLOT("reject()"))
		QObject.connect(self.btnOutput, SIGNAL("clicked()"), self.outFile)
		
		self.CritMapNameLbl.setText(self.activeLayer.name())

		self.CritListFieldsCBox.addItems(self.GetFieldNames(self.activeLayer))
		self.IDListFieldsCBox.addItems(self.GetFieldNames(self.activeLayer))
		
		fields=self.GetFieldNames(self.activeLayer) #field list

		CritSetLabel=["Preference", "Weights"]
		self.CritWeighTableWidget.setColumnCount(2)
		self.CritWeighTableWidget.setHorizontalHeaderLabels(CritSetLabel)
		self.CritWeighTableWidget.setRowCount(len(fields))
		self.CritWeighTableWidget.setVerticalHeaderLabels(fields)
		
		for r in range(len(fields)):
			self.CritWeighTableWidget.setItem(r,0,QTableWidgetItem("gain"))
			#self.CritWeighTableWidget.setItem(r,1,QTableWidgetItem("continuous"))
			self.CritWeighTableWidget.setItem(r,1,QTableWidgetItem("1"))

		#retrieve signal for modified cell
		self.CritWeighTableWidget.cellClicked[(int,int)].connect(self.ChangeValue)
		

	def outFile(self):
		"Display file dialog for output XMCDA file"
		self.lineOutput.clear()
		outName = QFileDialog.getSaveFileName(self, "xMCDA output file",".", "xMCDA (*.xml)")
		self.lineOutput.clear()
		self.lineOutput.insert(outName)
		return outName

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
		else:
			self.CritWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem(str(val)))
			
#####################################################################################################


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
	
	def LoadAttributes(self,criteria):
		matrix=[self.ExtractAttributeValue(c) for c in criteria]
		matrix=[list(row) for row in zip(*matrix)]
		return matrix
		
	  
	def matrix2csv(self,matrix):
		csvMatrix = open('matrix.csv', 'wb')
		wr = csv.writer(csvMatrix, quoting=csv.QUOTE_ALL)
		wr.writerow(matrix)
	 
	def pikIDfield(self):
		IDfield=self.IDListFieldsCBox.currentText()
		IDlist=self.ExtractAttributeValue(IDfield)
		return IDlist
	 
	def matrix2xml(self,matrix,criteria,preference,weight,IDlist):
		#try:
		#print matrix
		root=ET.Element('objects')
		root.set('version', '1.0')
		comment=ET.Comment('xml data for Decision Deck interoperability [http://www.decision-deck.org/xmcda/]')
		root.append(comment)
		for row,ID in zip(matrix,IDlist):
			sample=ET.SubElement(root,'sample',{'id':str(ID)})
			for r,c,p,w in zip(row,criteria,preference,weight):
				attribute=ET.SubElement(sample,'attribute',{'name':c,'preference':p,'weight':str(w)})
				value=ET.SubElement(attribute,'value')
				value.text=str(r)
		outfile=open(self.lineOutput.text(), "w")  
		outfile.write(ET.tostring(root,encoding='utf-8',method="xml"))
		outfile.close()
		#except:
			#QMessageBox.information(None,"Exiting","I can't write %s texture file." % self.lineOutput.text())
			#return

	def ExtractData(self):
		criteria=[self.CritWeighTableWidget.verticalHeaderItem(f).text() for f in range(self.CritWeighTableWidget.rowCount())]
		preference=[str(self.CritWeighTableWidget.item(c,0).text()) for c in range(self.CritWeighTableWidget.rowCount())]
		#function=[str(self.CritWeighTableWidget.item(c,1).text()) for c in range(self.CritWeighTableWidget.rowCount())]
		weight=[str(self.CritWeighTableWidget.item(c,1).text()) for c in range(self.CritWeighTableWidget.rowCount())]
		IDlist=self.pikIDfield()
		matrix=self.LoadAttributes(criteria)
		self.matrix2xml(matrix,criteria,preference,weight,IDlist)
		#self.setModal(False)
		#self.matrix2csv(matrix)


