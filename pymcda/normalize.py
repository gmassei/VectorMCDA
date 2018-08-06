
from . import support

def increase(criterion):
	"""normalize all values in a list with linear increas/gain function"""
	miN=min(criterion)
	maX=max(criterion)
	normCritrion=[float((x-miN)/(maX-miN)) for x in criterion]
	return normCritrion
	
def decrease(criterion):
	"""normalize all values in a list with linear decreas/cost function"""
	miN=min(criterion)
	maX=max(criterion)
	normCritrion=[float((maX-x)/(maX-miN)) for x in criterion]
	return normCritrion
	
def regression(criterion,Xvalues, Yvalues, polyFittValue):
		fit=np.polyfit(Xvalues, Yvalues, polyFittValue)
		valuer = np.poly1d(fit)
		normCritrion=[valuer(x) for x in criterion]
		return normCritrion
		

		
def overAllstd(mat,preference):
	minVec=support.minColumns(mat)
	maxVec=support.maxColumns(mat)
	mat['stdMat']=[]
	for R in mat['matrix']:
		stdRow=[(float((x-miN)/(maX-miN))) if p=='gain' else (float((maX-x)/(maX-miN))) for x,p,miN,maX in zip(R,preference,minVec,maxVec)]
		mat['stdMat'].append(stdRow)
	return 0
