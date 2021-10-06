This repository contains the code for my master thesis Monitoring Blockchain Applications.

This project relies on the pm4py dependency. However, theere might be a small bug in their code. In the file pm4py-core/pm4py/util/constants.py in line 21 replace PARAMETER_CONSTANT_CASEID_KEY = 'case_id_glue' with PARAMETER_CONSTANT_CASEID_KEY = 'pm4py:param:caseid_key'
