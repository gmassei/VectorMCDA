.. VectorMCDA documentation master file, created by
   sphinx-quickstart on Fri Jan 23 20:24:10 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to VectorMCDA's documentation!
======================================


	
Description of VectorMCDA
----------------------------

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

The page **Analysis** [figure 4] allows the user to get the outputs provided from the plugin. We can have three  types of output:

1. **cartographic:** pressing the **Load maps** button, geoUmbriaSUIT loads four  thematic maps, showing the environment (EnvIdeal), economic (EcoIdeal), social (SocIdeal) and the comprehensive sustainability performance of each **research unit**, based on the related indexes. The user can change the class numbers changing the value in **Classes map** control,  but the label will be only numeric, from the lowest to the highest value.

2. **graphic:**  the user has to select the field used for labeling the **research units** from the combo-box **Label field**. For example, if our assessment concerns the Italian regions, we have to select the field that holds the name of  the regions. The same for Provinces, municipality or other administrative or phisical units. Pressing the **Graph** button, geoUmbriaSUIT will load an html page in a web browser with four graphs. The first shows a stack – histogram whose the overall height is proportional to the sustainability value, as the sum (linear combination) of the three indexes (environmental, economic and social values) calculated using TOPSIS algorithm. The second graph is a **bubble-graph**: the  position, dimension and color of bubbles provide information about sustainability and its three dimensions. In particular, the x-axis is ordered with the environmental index, the y-axis is ordered with the economic index, while the color (from red to green) is ordered with the social index; the dimension of the bubble is proportional to the sustainability value. The first two graphs use Google chart API's and require an active internet connection. The third and the fourth graphs are quite similar to the the first two, but they are **static** and they do not require an internet active connection.

3. **alphanumeric:** geoUmbriaSUIT implements the Dominance Based Rough Set theory [5] for discovering and explaining the data outputs. In the page **Rules** there is a button named **Extract rules**, for the extraction of decisional rules on the basis of a classification given from TOPSIS algorithm. If a rule has a syntax like  **IF  A>= X THEN AT LEAST i-th**,  we can read it as: ** if criterion A has a value greater than or equal to x, then the class of membership will be at least the i-th **. On the other hand, if the extracted rule has the  syntax like  **IF  A>= X THEN AT MOST i-th**, it can be read as: **If the criterion A has a value greater than or equal to x, then the class of membership will be at most the i-th **. If the user selects a single rule, the **research units** covered  from that rule will be selected. In other words, selecting a single rule from the text box, we can see the **examples** which support that rule.


	 
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

. 