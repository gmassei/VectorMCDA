# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name			 	 : geoMCDA - DBRA
Description          : Make a geographic multi criteria decision making on 
						vector data using dominance based rough set approach"
Date                 : 14/07/2012 
copyright            : (C) 2012 by Gianluca Massei
email                : g_massa@libero.it

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

def classFactory(iface):	# inizializza il plugin
	from VectorMCDA import vMCDA	# importiamo la classe che realizza il plugin
	return vMCDA(iface)	# creiamo una istanza del plugin
