PLUGINNAME = VectorMCDA

PY_FILES = VectorMCDA.py geoWeightedSum.py geoTOPSIS.py geoFuzzy.py geoPromethee.py geoElectre.py geoRULES.py geoXMCDA.py htmlGraph.py geoXMCDA.py fuzzify.py DOMLEM.py geoRULES.py __init__.py

EXTRAS = metadata.txt LICENCE.txt icons/ images/ Doc/

UI_FILES = ui_geoXMCDA.py ui_geoWeightedSum.py ui_geoTOPSIS.py ui_geoRULES.py ui_geoPromethee.py ui_geoFuzzy.py ui_geoElectre.py ui_geoRULES.py

RESOURCE_FILES = resources.py
#geoXMCDA.ui geoWeightedSum.ui geoTOPSIS.ui geoRSDB.ui geoPromethee.ui  geoFuzzy.ui  geoElectre.ui  geoRULES.ui
# 
#resources.py
#pyuic4 -o  ui_geoElectre.py geoElectre.ui

QGISDIR=.qgis2

default: compile

compile: $(UI_FILES) $(RESOURCE_FILES)

%.py : %.qrc
	pyrcc4 -o $@ $<

%.py : %.ui
	pyuic4 -o $@ $<
# 	

deploy: compile
	mkdir -p $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf $(PY_FILES) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf $(UI_FILES) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf $(RESOURCE_FILES) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf -r $(EXTRAS) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)

clean:
	rm $(UI_FILES) $(RESOURCE_FILES)

zip: deploy dclean
	@echo
	@echo "---------------------------"
	@echo "Creating plugin zip bundle."
	@echo "---------------------------"
	# The zip target deploys the plugin and creates a zip file with the deployed
	# content. You can then upload the zip file on http://plugins.qgis.org
	rm -f $(PLUGINNAME).zip
	cd $(HOME)/$(QGISDIR)/python/plugins; zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)

package: compile
	# Create a zip package of the plugin named $(PLUGINNAME).zip.
	# This requires use of git (your plugin development directory must be a
	# git repository).
	# To use, pass a valid commit or tag as follows:
	#   make package VERSION=Version_0.3.2
	@echo
	@echo "------------------------------------"
	@echo "Exporting plugin to zip package.	"
	@echo "------------------------------------"
	rm -f $(PLUGINNAME).zip
	git archive --prefix=$(PLUGINNAME)/ -o $(PLUGINNAME).zip $(VERSION)
	echo "Created package: $(PLUGINNAME).zip"
	
dclean:
	@echo
	@echo "-----------------------------------"
	@echo "Removing any compiled python files."
	@echo "-----------------------------------"
	rm -f $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/*.pyc
	#find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname ".git" -prune -exec rm -Rf {} \;
