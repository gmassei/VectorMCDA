import os
import operator

def BuilHTMLGraph(ListValue,labels,legend):
	header=["label"]+legend
	data=[]
	for i in range(len(labels)):
		row=[]
		row.append(labels[i])
		for j in ListValue[i]:
			row.append(j)
		data.append(row)
	currentDIR = unicode(os.path.abspath( os.path.dirname(__file__)))
	data = sorted(data, key=operator.itemgetter(-1),reverse=True)
	log=open(os.path.join(currentDIR,"log.html"),"w")
	log.write(currentDIR)
	HTMLfile=open(os.path.join(currentDIR,"barGraph.html"),"w")

	HTMLfile.write("""<!DOCTYPE html>
	<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
		<title>Sustainability box</title>
		<meta name="keywords" content="">
		<meta name="description" content="" />
		<link href="http://fonts.googleapis.com/css?family=Open+Sans:400,300,600,700|Archivo+Narrow:400,700" rel="stylesheet" type="text/css">
		<link href="default.css" rel="stylesheet" type="text/css" media="all" />
		<script type="text/javascript" src="https://www.google.com/jsapi"></script>
		<script type="text/javascript">
			google.load("visualization", "1", {packages:["corechart"]});
			google.setOnLoadCallback(drawChart);
			function drawChart() {
				var dataBar = google.visualization.arrayToDataTable([\n""")
	HTMLfile.write(str(header)+",\n")
	for r in range(len(data)):
		HTMLfile.write(str(data[r])+",\n") #last doesn't printed
	HTMLfile.write(str(data[r]))
	HTMLfile.write("\n]);\n")
	HTMLfile.write("""	var optionsBar = {
			  title: 'bars of rating',
			  legend:{position:'in'},
			};
				var chartBar = new google.visualization.ColumnChart(document.getElementById('bar_div'));
			chartBar.draw(dataBar, optionsBar);
		}
		</script>""")
		
	HTMLfile.write("""
	  </head>
	  <body>
	  <div id="logo" class="container"><h1>Graph of rating</h1>
		<br></br>
		<div id="bar_div" style="width: 1350px; height: 750px;"  border='0'></div>
		<br><hr></br>
		<a href ="http://maplab.alwaysdata.net">
			<img class="aligncenter" src="icons/Tree.png" style="width: 150px; height: 100px;"  border='0'/> 
		powered by VectorMCDA in QGIS</a>
		<hr>
	  </body>
	</html>""")
	HTMLfile.close()
	log.close()
