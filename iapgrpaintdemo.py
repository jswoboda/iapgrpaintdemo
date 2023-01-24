#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: IAP GR-Paint Demo
# Author: John Swoboda
# Description: Creates a pfb sythesis of images and outputs them to a pluto
# GNU Radio version: 3.10.3.0

from packaging.version import Version as StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import blocks
import pmt
from gnuradio import filter
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio
import paint



from gnuradio import qtgui

class iapgrpaintdemo(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "IAP GR-Paint Demo", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("IAP GR-Paint Demo")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "iapgrpaintdemo")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = int(2.4e6)
        self.M = M = 5
        self.pfb_taps = pfb_taps = firdes.low_pass_2(1, M*samp_rate, samp_rate/2, samp_rate/5, 80)
        self.gain = gain = 5
        self.fc = fc = int(915e6)

        ##################################################
        # Blocks
        ##################################################
        self.qtgui_sink_x_0 = qtgui.sink_c(
            1024, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            (samp_rate*M), #bw
            "", #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            True, #plotconst
            None # parent
        )
        self.qtgui_sink_x_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0.enable_rf_freq(False)

        self.top_layout.addWidget(self._qtgui_sink_x_0_win)
        self.pfb_synthesizer_ccf_0 = filter.pfb_synthesizer_ccf(
            M,
            pfb_taps,
            False)
        self.pfb_synthesizer_ccf_0.set_channel_map([])
        self.pfb_synthesizer_ccf_0.declare_sample_delay(0)
        self.paint_paint_bc_0_1_0_0 = paint.paint_bc(756, 6, paint.EQUALIZATION_OFF, paint.INTERNAL, 1)
        self.paint_paint_bc_0_1 = paint.paint_bc(320, 40, paint.EQUALIZATION_OFF, paint.INTERNAL, 1)
        self.paint_paint_bc_0_0 = paint.paint_bc(2467, 4, paint.EQUALIZATION_ON, paint.INTERNAL, 1)
        self.paint_paint_bc_0 = paint.paint_bc(2200, 4, paint.EQUALIZATION_OFF, paint.INTERNAL, 1)
        self.iio_pluto_sink_0 = iio.fmcomms2_sink_fc32('' if '' else iio.get_pluto_uri(), [True, True], 32768, False)
        self.iio_pluto_sink_0.set_len_tag_key('')
        self.iio_pluto_sink_0.set_bandwidth(20000000)
        self.iio_pluto_sink_0.set_frequency(fc)
        self.iio_pluto_sink_0.set_samplerate((samp_rate*M))
        self.iio_pluto_sink_0.set_attenuation(0, 0.)
        self.iio_pluto_sink_0.set_filter_params('Auto', '', 0, 0)
        self.blocks_throttle_0_1_0_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_throttle_0_1 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_throttle_0_0_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_throttle_0_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_null_source_0 = blocks.null_source(gr.sizeof_gr_complex*1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(gain)
        self.blocks_file_source_0_1_0_0 = blocks.file_source(gr.sizeof_char*1, 'images/hops_logo_d_icon_flip.bin', True, 0, 0)
        self.blocks_file_source_0_1_0_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_file_source_0_1 = blocks.file_source(gr.sizeof_char*1, 'images/MIT_logo_flip.bin', True, 0, 0)
        self.blocks_file_source_0_1.set_begin_tag(pmt.PMT_NIL)
        self.blocks_file_source_0_0 = blocks.file_source(gr.sizeof_char*1, 'images/mitadaptive_logo_flip.bin', True, 0, 0)
        self.blocks_file_source_0_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_char*1, 'images/MIT_HO_logo_square_flip.bin', True, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_source_0, 0), (self.paint_paint_bc_0, 0))
        self.connect((self.blocks_file_source_0_0, 0), (self.paint_paint_bc_0_0, 0))
        self.connect((self.blocks_file_source_0_1, 0), (self.paint_paint_bc_0_1, 0))
        self.connect((self.blocks_file_source_0_1_0_0, 0), (self.paint_paint_bc_0_1_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.iio_pluto_sink_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.blocks_null_source_0, 0), (self.blocks_throttle_0_0_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.pfb_synthesizer_ccf_0, 1))
        self.connect((self.blocks_throttle_0_0, 0), (self.pfb_synthesizer_ccf_0, 2))
        self.connect((self.blocks_throttle_0_0_0, 0), (self.pfb_synthesizer_ccf_0, 0))
        self.connect((self.blocks_throttle_0_1, 0), (self.pfb_synthesizer_ccf_0, 4))
        self.connect((self.blocks_throttle_0_1_0_0, 0), (self.pfb_synthesizer_ccf_0, 3))
        self.connect((self.paint_paint_bc_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.paint_paint_bc_0_0, 0), (self.blocks_throttle_0_0, 0))
        self.connect((self.paint_paint_bc_0_1, 0), (self.blocks_throttle_0_1, 0))
        self.connect((self.paint_paint_bc_0_1_0_0, 0), (self.blocks_throttle_0_1_0_0, 0))
        self.connect((self.pfb_synthesizer_ccf_0, 0), (self.blocks_multiply_const_vxx_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "iapgrpaintdemo")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_pfb_taps(firdes.low_pass_2(1, self.M*self.samp_rate, self.samp_rate/2, self.samp_rate/5, 80))
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.blocks_throttle_0_0.set_sample_rate(self.samp_rate)
        self.blocks_throttle_0_1.set_sample_rate(self.samp_rate)
        self.blocks_throttle_0_1_0_0.set_sample_rate(self.samp_rate)
        self.iio_pluto_sink_0.set_samplerate((self.samp_rate*self.M))
        self.qtgui_sink_x_0.set_frequency_range(0, (self.samp_rate*self.M))
        self.blocks_throttle_0_0_0.set_sample_rate(self.samp_rate)

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.set_pfb_taps(firdes.low_pass_2(1, self.M*self.samp_rate, self.samp_rate/2, self.samp_rate/5, 80))
        self.iio_pluto_sink_0.set_samplerate((self.samp_rate*self.M))
        self.qtgui_sink_x_0.set_frequency_range(0, (self.samp_rate*self.M))

    def get_pfb_taps(self):
        return self.pfb_taps

    def set_pfb_taps(self, pfb_taps):
        self.pfb_taps = pfb_taps
        self.pfb_synthesizer_ccf_0.set_taps(self.pfb_taps)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.blocks_multiply_const_vxx_0.set_k(self.gain)

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc
        self.iio_pluto_sink_0.set_frequency(self.fc)




def main(top_block_cls=iapgrpaintdemo, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
