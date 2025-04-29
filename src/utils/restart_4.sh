#!/bin/bash

gnome-terminal --geometry 56x11+1380+00  -- bash -c "python -m daemon ./cfgs/figure1/cfg4.txt; exec bash" 