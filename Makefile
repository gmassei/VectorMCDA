PLUGINNAME = VectorMCDA

PY_FILES = VectorMCDA.py geoWeightedSum.py geoTOPSIS.py geoFuzzy.py geoPromethee.py geoElectre.py geoRSDB.py geoXMCDA.py htmlGraph.py geoXMCDA.py fuzzify.py DOMLEM.py __init__.py

EXTRAS = metadata.txt icons/ images/ Doc/

UI_FILES = ui_geoXMCDA.py ui_geoWeightedSum.py ui_geoTOPSIS.py ui_geoRSDB.py ui_geoPromethee.py ui_geoFuzzy.py ui_geoElectre.py

RESOURCE_FILES = resources.py

default: compile

compile: $(UI_FILES) $(RESOURCE_FILES)

%.py : %.qrc
	pyrcc4 -o $@ $<

%.py : %.ui
	pyuic4 -o $@ $<

deploy: compile
	mkdir -p $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf $(PY_FILES) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf $(UI_FILES) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf $(RESOURCE_FILES) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf -r $(EXTRAS) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)

clean:
	rm $(UI_FILES) $(RESOURCE_FILES)

