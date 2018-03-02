from logcc.logcc import LogCC
from termcc.cc import cc


def setup_log(log_name):
    l = LogCC(name=log_name)
    l.update_color_formatter(log_name, 'DEBUG', cc(':white:'))
    l.update_color_formatter(log_name, 'INFO', cc(':green:'))
    l.update_color_formatter(log_name, 'EXCEPTION', cc(':red:'))
    l.update_color_formatter(log_name, 'WARNING', cc(':green:'))
    l.update_color_formatter(log_name, 'CRITICAL', cc(':red:'))
