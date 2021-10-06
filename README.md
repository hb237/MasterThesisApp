## Introduction ##
This repository contains the code for my master thesis Monitoring Blockchain Applications.

## Launch Instructions ##

1. Download pm4py's dependencies: https://pm4py.fit.fraunhofer.de/install-page#linux 
2. Download the Geth client: https://geth.ethereum.org/downloads/
3. Launch the Geth client with: geth --syncmode "light" --ws --ws.addr 127.0.0.1 --ws.port 8546 
4. Navigate to: Application/blockchain_monitor
5. Launch the application with: .venv/bin/python3 -m app
6. Open the application in the browser: http://localhost:5000/index

## Note ##
This project relies on the pm4py dependency. However, there might be a small bug in their code. In the file _pm4py-core/pm4py/util/constants.py_ in _line 21_ replace `PARAMETER_CONSTANT_CASEID_KEY = 'case_id_glue'` with `PARAMETER_CONSTANT_CASEID_KEY = 'pm4py:param:caseid_key'`
