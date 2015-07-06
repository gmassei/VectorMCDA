.. VectorMCDA documentation master file, created by
   sphinx-quickstart on Fri Jan 23 20:24:10 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to VectorMCDA's documentation!
======================================


	
Description of VectorMCDA
----------------------------
**VectorMCDA** implements some multicriteria decision aid (**MCDA**) algorithms using vector data in QGS GFOSS software. 
VectorMCDA assumes that each geographical object, described with a records in the attribute table, is a single 
alternative (**geo-alternative**) and the algorithms  implemented in the plugin analyzes the attributes, elaborates 
these ones like criteria and return the output in one or more columns,  added in the attribute table.
The output are shows as geographic maps in QGIS canvas and in a graphical html page.
The algorithms available in the current VectorMCDA version are the follow:

**geoWeightedSum**: [1] implements the classic **weighted sum algorithm** and return a maps shows the preference granted 
to the various geo-alternatives. The user may provide  directly the weight values, or he can calculate  them with  AHP [2] approach 
implemented in the module.

**geoTOPSIS**: implements the **ideal point algorithms** base on TOPSYS model [3] and returns a maps shows the ranking  alternative 
in a colour and numerical scale and in a graph in html page. Even in this case, the user may provide directly the weight values, or  
he can calculate them with  AHP [2] approach implemented in the module
 
**geoFuzzy**: implements the **fuzzy MCDA model** proposed by **Yager** [4] and returns the fuzzy intersection and fuzzy union MCDA index. 
The **linguistic modifier** may be provided in the same way of weights, seen in the previous algorithms.

**geoConcordance**: calculates the concordance and discordance index for each geo-alternative, as a base for assessment with **Electre** [5] models family. 
The module returns two maps, one for concordance index and one for discordance index. The weighing step is the same seen in the previous algorithms. 
 
**geoPromethee**: implements the **Promethee** [6] method in a geographic way. The weighing step is the same seen in the previous algorithms, 
the outputs are the negative flux, the positive flux, the net flux, stored in the attribute table, the relative maps and graphs in html separate page.

**geoRSDB**: the module implements the **DOMLEM** algorithm for **rough set dominance based theory (RSDB)**[7]. The output is in a set of 
**decisional rules** extracted from a pre-definited ranking stored in the attribute table. The module doesn't make a classification of 
geo-alternatives, but  pick up the rules from attribute table, with a column with ranking value. The current implementation of the module 
is "discovery  knowledge oriented", instead a proper MCDA algorithm. In the next implementation, the rules extracted will be used for 
perform a real MCDA classification.
 
**geoXMCDA**: is the first implementation of xMCDA standard (http://www.decision-deck.org/xmcda/)  for grant the MCDA data interoperability. The module isn't
yet  mature and it isn't usable in production environment, anyway it is under active develop and test.  


Installation
++++++++++++
The plugin works under QGIS 2.0 environment, but the first time we use it we need to follow the installation procedure:

1. from the menu **Plugins** choose  **Manage and Install plugin**,  the **Plugin manager** window will open;

2. if VectoMCDA is already installed, we will find it under the **installed** plugins in **Plugin manager**. Otherwise, the plugin will be listed under **Get more** and we can install it by clicking on **Install plugin**;

3. after the end of installation procedure, VectoMCDA will be accessible from the menu **Plugins**;  

.. figure:: ./_images/LoadPlugin.jpg
     :align: center
     :height: 300

     Figure 1: Plugin manager in QGIS

VectorMCDA implements several MCDA algorithms and the user can access from the menu shows in figure 1.

The user can download example data from the site http://maplab.alwaysdata.net/geomcda.html.

Running geoWeightedSum
+++++++++++++++++++++

The user has to load a vector geographic data in qgis and select it clicking with the mouse over the name. 
The attribute table of that file has to contain the indicators we intend to use in the assessment and a label for 
identify the geo-alternatives. 
From the menu **Plugins/VectorMCDA** we can select **geoWeightedSum** and the window shown in figure 2 will open.

In the **Criteria** page the label **Layer** shows the active layer's name, while the combo-box **field** hold the 
list of numerical fields in the attribute table. The **Add field** button insert the selected field in the combo-box as a 
new column in the **table**, as a new criteria used in MCDA analysis. 
The columns in the table in the card **Standard** holds all the numerical fields from the attribute table of the selected layer, 
used for the MCDA analysis, meaning as criteria. The first row of the table contain the weight for each criteria (column), 
the second row shows the preference function  as cost/gain value.
The user has to decide which criteria he want to use for the analysis, the ones he doesn't want to use, have to be selected 
on the table (clicking with the mouse on the header)  and removed with the menu activated with the right button of the mouse. 
We can add a field in the analysis using the **Add field** button on the card. 
The input of the weight in the first row can be done simply digit the values for each criteria shows on the header of the table;
otherwise, and alternatively, is available the AHP approach with pairwise comparation matrix, in the **Advance** card. In the last case, the user 
has to digit the preference of column criteria  respect the rows criteria, in a range [1/9....9/1]. The weight are calculated with the 
**Calculate weight** button and the values are inserted in the weighted row in the table of **Standard** card.
In the next step the user has to define the preference function for each criteria; if a criterion is preferable if it's value increase, 
the value to be selected is **gain**, otherwise the value has to be **cost**. 

.. figure:: ./_images/geoWeightedSum.jpg
     :height: 500	
     :align: center
     
     **Figure 2.a:** geoWeightedSum algorithm in VectorMCDA plugin. Criteria Tab.

Pressing the button **Apply** the user performs the analysis, on the table will add a new field named **geoWSM** that holds the values
of each alternative (each row in the table of attribute, and each relative geographic object)

With the **Analysis**  we can shows the graphical and geographical outputs. The **Maps** button load the map in QGIS, with the colour 
graduated  with **geoWSM** field.  The **Graph** button open an html page with bar-graph labeled with **Label filed** in the combo-box
	 
.. figure:: ./_images/geoWeightedSum_2.jpg
     :height: 500
     :align: center

     **Figure 2.b:** geoWeightedSum algorithm in VectorMCDA plugin. Analysis Tab.

	 

Running geoTOPSIS
+++++++++++++++++++++
The geoTOPSIS module can be lunched from **Plugins/VectorMCDA/geoTOPSIS**. It shows the windows for perform geoTOPSIS MCDA analysis.
The general input are the same seen in the geoWeightedSum. The table in the **Standard** page has the same field and meaning of the previous module, 
except for last two rows: ideal point and worst point. 
The **Ideal point** is the target and optimum value, the default value is the best in the attribute table for each single criterion, but the user can 
change it with different value. The **worst point** is the opposite of the ideal point and the default value is the worse in the attribute table.
The **Load maps** and **Graph** buttons are described in geoWeightedSum and have the same meaning and behavior.

.. figure:: ./_images/geoTOPSIS.jpg
     :height: 500
     :align: center

     **Figure 3:** geoTOPSIS algorithm in VectorMCDA plugin. 

Running geoFuzzy
+++++++++++++++++++++

.. figure:: ./_images/geoFuzzy.jpg
     :height: 500
     :align: center

     **Figure 4:** geoFuzzy algorithm in VectorMCDA plugin. Criteria tab.
	 
.. figure:: ./_images/geoFuzzy_2.jpg
     :height: 500
     :align: center

     **Figure 5:** geoFuzzy algorithm in VectorMCDA plugin. Fuzzify tab.

Running geoConcordance
+++++++++++++++++++++

.. figure:: ./_images/geoConcordance.jpg
     :height: 500
     :align: center

     **Figure 6:** geoConcordance algorithm in VectorMCDA plugin. 

Running geoPromethee
+++++++++++++++++++++

.. figure:: ./_images/geoPromethee.jpg
     :height: 500
     :align: center

     **Figure 7:** geoPromethee algorithm in VectorMCDA plugin. 

Running geoRULES
+++++++++++++++++++++

.. figure:: ./_images/geoRULES.jpg
     :height: 500
     :align: center

     **Figure 8:** geoRULES algorithm in VectorMCDA plugin. 

Running geoXMCDA
+++++++++++++++++++++

.. figure:: ./_images/geoXMCDA.jpg
     :height: 500
     :align: center

     **Figure 9:** geoXMCDA algorithm in VectorMCDA plugin. 

Outputs
+++++++

The page **Analysis** [figure 4] allows the user to get the outputs provided from the plugin. Even if there are specific approaches for each implemented algorithm ,
we can have at least two output:
 
1. **cartographic:** pressing the **Load maps** button, you can load the output thematic maps based on the canvas showing the ranking of geo-alternatives in  choropleth map.

2. **graphic:**  the user has to select the field used for labelling the geo-alternatives from the combo-box **Label field**. Pressing the **Graph** button,  VectorMCDA will load an html page in a web browser with a histogram  proportional with the performance of each geo-alternatives.



Bibliography
------------
[1] Triantaphyllou, E. (2000). Multi-Criteria Decision Making: A Comparative Study. Dordrecht, The Netherlands: Kluwer Academic Publishers (now Springer). p. 320. ISBN 0-7923-6607-7. 

[2] Thomas L. Saaty, Decision Making for Leaders – The Analytic Hierarchy Process for Decisions in a Complex World, RWS Publishing, Pittsburgh, 1990. 

[3] Hwang, C.L.; Yoon, K. (1981). Multiple Attribute Decision Making: Methods and Applications. New York: Springer-Verlag. 

[4] Yager, R.R., 1978, Fuzzy decision making including unequal objectives, Fuzzy Sets and
Systems, 1: 87–95.

[5] Roy B., (1991), “The outranking approach and the foundation of ELECTRE methods”, Theory an Decision, vol. 31, 49-73.

[6] J.P. Brans and P. Vincke (1985). "A preference ranking organisation method: The PROMETHEE method for MCDM". Management Science. 

[7] Greco, S., Matarazzo, B., Słowiński, R.: Rough sets theory for multi-criteria decision analysis. European Journal of Operational Research, 129, 1 (2001) 1–47 


	 
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

. 