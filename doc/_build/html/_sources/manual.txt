.. VectorMCDA documentation master file, created by
   sphinx-quickstart on Fri Jan 23 20:24:10 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to VectorMCDA's documentation!
======================================


	
Description of VectorMCDA
----------------------------
**VectorMCDA** implements some multicriteria decision aid (**MCDA**) algorithms using vector data in QGIS GFOSS software. 
VectorMCDA assumes that each geographical object, described with a record in the attribute table, is a single 
alternative (**geo-alternative**). The algorithms  implemented in the plugin analyze all the attributes and elaborate 
them as criteria; then return an output creating one or more columns,  added in the attribute table.
Such an output are shown as geographic maps in QGIS canvas and in a graphical html page.
The algorithms available in the current VectorMCDA version are the follow:

**geoWeightedSum**: [1] implements the classic **weighted sum algorithm** and returns a maps shown the preference granted 
to the various geo-alternatives. The user may provide  directly the weight values, or she can calculate them with  AHP [2] approach implemented in the module.

**geoTOPSIS**: implements the **ideal point algorithms** based on TOPSIS model [3] and returns a map shown the ranking  alternatives in a colour and numerical scale and also in a graph in a html page. Even in this case, the user may provide  the weight values directly, or she can calculate them with  AHP [2] procedure implemented in the module.
 
**geoFuzzy**: implements the **fuzzy MCDA model** proposed by **Yager** [4]. It returns the fuzzy intersection and fuzzy union MCDA index. 
The **linguistic modifier** may be provided in the same way of weights, seen in the previous algorithms.

**geoConcordance**: calculates the concordance and discordance index for each geo-alternative, as a base for assessing with **Electre** [5] models family. 
The module returns two maps, one for concordance index and one for discordance index. The weighing phase is the same seen in the previous algorithms. 
 
**geoPromethee**: implements the **Promethee** [6] method in a geographic way. The outputs are the negative and the positive flux, while the net one can be calculated using a gis function. All the outputs are produced in maps and graphs in html separate page. The values are stored in the attribute table. The weighing step is the same seen in the previous algorithms.

**geoRSDB**: the module implements the **DOMLEM** algorithm for **Dominance- based Rough Set Approach(DRSA)**[7]. The output is in a set of **decisional rules** extracted from a pre-definited ranking, stored in the attributes table. The module doesn't make a classification of geo-alternatives, but  pick up the rules from the attributes table, which includes a column with ranking value. Therefore, the current implementation of the module is "discovery  knowledge oriented", instead a proper MCDA algorithm. In future development, the rules extracted will be used for 
performing a real MCDA classification.
 
**geoXMCDA**: is the first implementation of xMCDA standard (http://www.decision-deck.org/xmcda/) for granting the MCDA data interoperability. The module is not yet mature and it is not usable for proper application; anyway it is under active development and testing.  


Installation
++++++++++++
The plugin works under QGIS 2.0 environment. The first time the user need to follow the installation procedure:

1. from the menu **Plugins** choose  **Manage and Install plugin**,  the **Plugin manager** window will open;

2. if VectorMCDA is already installed, you will find it under the **installed** plugins in **Plugin manager**. Otherwise, the plugin will be listed under **Get more** and you can install it by clicking on **Install plugin**. Check to pick the option "include sperimental plugins" before.

3. after the end of installation procedure, VectorMCDA will be accessible from the menu **Plugins**;  

.. figure:: ./_images/LoadPlugin.jpg
     :align: center
     :height: 300

     Figure 1: Plugin manager in QGIS

VectorMCDA implements several MCDA algorithms, available for the users at menu shown in figure 1.

The user can download example data from the site http://maplab.alwaysdata.net/geomcda.html.

Running geoWeightedSum
+++++++++++++++++++++

The user has to load a vector geographic data in QGIS and select it by clicking with the mouse over the name. 
The attributes table of the vector file has to contain the indicators the user intends to use in the assessment and a label for identifing the geo-alternatives. 
From the menu **Plugins/VectorMCDA** we can select **geoWeightedSum** and the window shown in figure 2 will open.

In the **Criteria** page the label **Layer** shows the active layer's name, while the combo-box **field** holds the list of numerical fields in the attributes table. The **Add field** button inserts the selected field in the combo-box as a new column in the **table**, as a new criterion used in MCDA analysis. 
The columns in the table included in the card **Standard** holds all the numerical fields from the attributes table of the selected layer, used for the MCDA analysis, meaning as criteria. The first row of the table contains the weight for each criterion (column), while the second row shows the preference function as cost or gain.
The user has to decide which criterion she wants to use for the analysis. The ones she does not want to use, have to be selected on the table (clicking with the mouse on the header)  and removed through the menu activated with the right button of the mouse. 
User can add a field in the analysis using the **Add field** button on the card. 
To input the weight in the first row user can do it directly for each criterion shown on the header of the table;
otherwise it is available the AHP procedure with a pairwise comparation matrix, in the **Advance** card. In the last case, the user has to type the preferences of column criteria  respect to the rows criteria, in a range [1/9....9/1]. The weight are calculated with the 
**Calculate weight** button and the values are inserted in the weighted row in the table of **Standard** card.
In the following step the user has to define the preference function for each criterion; if a criterion is preferable in case of an increasing value, the value of the preference to be selected is **gain**, otherwise the value has to be **cost**. 

.. figure:: ./_images/geoWeightedSum.jpg
     :height: 500	
     :align: center
     
     **Figure 2.a:** geoWeightedSum algorithm in VectorMCDA plugin. Criteria Tab.

Pressing the button **Apply** the user performs the analysis, on the table will add a new field named **geoWSM** that holds the values of each alternative (each row in the table of attribute, and each relative geographic object).

With the **Analysis** the user can see the graphical and geographical outputs. The **Maps** button load the map in QGIS, with the colour 
graduated  with **geoWSM** field.  The **Graph** button open a html page with bar-graph labeled with **Label filed** in the combo-box
	 
.. figure:: ./_images/geoWeightedSum_2.jpg
     :height: 500
     :align: center

     **Figure 2.b:** geoWeightedSum algorithm in VectorMCDA plugin. Analysis Tab.

	 

Running geoTOPSIS
+++++++++++++++++++++
The geoTOPSIS module can be lunched from **Plugins/VectorMCDA/geoTOPSIS**, which open the window for perform geoTOPSIS MCDA analysis.
The general inputs are the same seen in the geoWeightedSum. The table in the **Standard** page has the same field and meaning of the previous module, 
except for the last two rows: ideal point and worst point. 
The **Ideal point** is the target and optimum value to be reached. The default value is the best in the attribute table for each single criterion, but the user may change it with a different value. The **worst point** is the opposite of the ideal point and the default value is the worse in the attributes table.
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

Comparing to the previous plugins, geoFuzzy differes or the present on the card "Standard" the label "Hedges" on the first row. Such a label identifies the linguistic modifier of the Yager model, implemented in the plugin. 

The other four fields(“first”, “second”, “third”,”fourth”) are typical of the gaussian fuzzy function and are can have a value among 0 (coloured in orange) and 1 (coloured in red). The default value is calculated a growing, linear function, which min is equal to the minimum value in the table for each criterion and max is equal to the maximum one.  
The user can change these attributes working on min and max, or modifying the value 0/1.
	 
.. figure:: ./_images/geoFuzzy_2.jpg
     :height: 500
     :align: center

     **Figure 5:** geoFuzzy algorithm in VectorMCDA plugin. Fuzzify tab.

Using the button "load maps" on the card "Analysis" two qgis maps are displayed, showing the union and intersection index.


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
This plugin does not produce a ranking of alternatives, but it is an instrument of analysis and comprehension of the choice done, thanks to the Dominance- based Rough Set Approach (DRSA).
To access to geoRULES open the menu: Plugins/VectoMCDA/geoRSDB. The output is a text contains the "decision rules". To generate such decision rules the button 
“Extract rules” (in the bottom part of the card) has to be pushed. The single rules have the following syntax: “
IF     A>= (or <=)  X   THEN   AT   LEAST   i-esima
which mean: “
if the criterion A is equal or bigger (or lower) than x, then it is at least (at most) in the i-esima class”. 
Clicking on each single rule all the units which support such rule will be underlined in yellow. At the same time, on the QGIS map all the area which 
l'area geografica ove una determinata regola risulta vera e provata.The plugin is very useful 
to understand, for instance, which criteria is more important for obtaining a certain ranking or if the Decision Maker gives a weight too big to a single criterion. 
In case of decision rules with a continuos numeric domain, it is very useful to discrete it. The process is not mandatory and it could be done using the setting card. 


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

As already write, this plugin is still ongoing and more development is required to finish it. The main objective for having this plugin is to simplify the interchange of vectorial data, according to the approach proposed by the Decision   Deck   project   (http://www.decision-
deck.org/project/index.html)

Outputs
+++++++

The page **Analysis** [figure 4] allows the user to get the outputs provided from the plugin. Although there are specific approach for each algorithms implemented,
you can have two outputs:

1. **cartographic:** pressing the **Load maps** button, the user can load the output thematic map based on the canvas showing the ranking of geo-alternatives in  choropleth map.

2. **graphic:**  the user has to select the field used for labelling the geo-alternatives from the combo-box **Label field**. Pressing the **Graph** button, 
VectorMCDA will load an html page in a web browser with a histogram  proportional with the performance of each geo-alternatives.



Bibliography
------------
[1] Triantaphyllou, E. (2000). Multi-Criteria Decision Making: A Comparative Study. Dordrecht, The Netherlands: Kluwer Academic Publishers (now Springer). p.Â 320. ISBNÂ 0-7923-6607-7. 

[2] Thomas L. Saaty, Decision Making for Leaders â€“ The Analytic Hierarchy Process for Decisions in a Complex World, RWS Publishing, Pittsburgh, 1990. 

[3] Hwang, C.L.; Yoon, K. (1981). Multiple Attribute Decision Making: Methods and Applications. New York: Springer-Verlag. 

[4] Yager, R.R., 1978, Fuzzy decision making including unequal objectives, Fuzzy Sets and
Systems, 1: 87â€“95.

[5] Roy B., (1991), â€œThe outranking approach and the foundation of ELECTRE methodsâ€, Theory an Decision, vol. 31, 49-73.

[6] J.P. Brans and P. Vincke (1985). "A preference ranking organisation method: The PROMETHEE method for MCDM". Management Science. 

[7] Greco, S., Matarazzo, B., SÅ‚owiÅ„ski, R.: Rough sets theory for multi-criteria decision analysis. European Journal of Operational Research, 129, 1 (2001) 1â€“47 


	 
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

. 
