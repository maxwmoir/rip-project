#!/bin/bash

gnome-terminal --geometry 40x12+1050+00 -- bash -c "python -m daemon ./cfgs/figure1/cfg4.txt -v; exec bash" 