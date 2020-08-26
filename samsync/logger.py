#!/usr/bin/env python3

import logging

def get_logger(log_path):
    logger = logging.getLogger('samsync')
    logger.setLevel(logging.DEBUG)

    log_format = logging.Formatter(' %(asctime)s - %(levelname)s - %(message)s')
    
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.INFO)
    fh.setFormatter(log_format)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(log_format)
    logger.addHandler(ch)

    return logger
    
    