#!/bin/bash
/Users/ethanguo/miniconda3/bin/python3 /Users/ethanguo/chargepoint/data/chargepoint_merge_to_json.py
/Users/ethanguo/miniconda3/bin/python3 /Users/ethanguo/chargepoint/data/chargepoint_json_to_h5.py
/Users/ethanguo/miniconda3/bin/python3 /Users/ethanguo/chargepoint/data/chargepoint_create_videos.py
