from logcc.logcc import LogCC
from termcc.cc import cc


def setup_log(log_name):
    log = LogCC(name=log_name, logfile='/tmp/netboy.log', sqlite_handler=None)
    log.update_color_formatter('name', 'DEBUG', cc(':reverse_white::black::bold:'))
    log.update_color_formatter('name', 'INFO', cc(':reverse_green::black::bold:'))
    log.update_color_formatter('name', 'WARNING', cc(':reverse_yellow::black::bold:'))
    log.update_color_formatter('name', 'ERROR', cc(':reverse_red::black::bold:'))
    log.update_color_formatter('name', 'CRITICAL', cc(':reverse_light_magenta::black::bold:'))

    log.update_color_formatter('msg', 'DEBUG', cc(':white::bold::beer:  :white:', use_aliases=True))
    log.update_color_formatter('msg', 'INFO', cc(':green::bold::running:  :green:', use_aliases=True))
    log.update_color_formatter('msg', 'WARNING', cc(':yellow::bold::yin_yang:  :yellow:', use_aliases=True))
    log.update_color_formatter('msg', 'ERROR', cc(':red::x:  :red:', use_aliases=True))
    log.update_color_formatter('msg', 'CRITICAL',
                               cc(':light_magenta::bold::smiling_imp:  :light_magenta:', use_aliases=True))
