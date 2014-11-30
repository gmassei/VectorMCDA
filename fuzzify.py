#!/usr/bin/env python

import sys
from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt
from ui_fuzzify import Ui_Dialog

		def aSlot(aQPointF):
			print 'aSlot gets:', aQPointF

		# aSlot()

		def make():
			demo = Qwt.QwtPlot()
			picker = Qwt.QwtPlotPicker(Qwt.QwtPlot.xBottom,
									   Qwt.QwtPlot.yLeft,
									   Qwt.QwtPicker.PointSelection,
									   Qwt.QwtPlotPicker.CrossRubberBand,
									   Qwt.QwtPicker.AlwaysOn,
									   demo.canvas())
			picker.connect(
				picker, Qt.SIGNAL('selected(const QwtDoublePoint&)'), aSlot)
			return demo

		# make()

		def main(args):
			app = Qt.QApplication(args)
			demo = make()
			demo.show()
			sys.exit(app.exec_())

		# main()

		if __name__ == '__main__':
			main(sys.argv)

