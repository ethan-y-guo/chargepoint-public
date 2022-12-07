#!/bin/bash
/usr/bin/rsync -a cs199-beg@hive21.cs.berkeley.edu:/home/aa/users/cs199-beg/tmp/chargers/ /Users/ethanguo/chargers
/Users/ethanguo/miniconda3/bin/python3 /Users/ethanguo/chargepoint/sync/chargepoint_process_latest.py
/usr/bin/scp /Users/ethanguo/chargers/latest.txt cs199-beg@hive21.cs.berkeley.edu:/home/aa/users/cs199-beg/tmp/latest.txt
