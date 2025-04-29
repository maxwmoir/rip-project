#!/bin/bash

gnome-terminal --geometry 56x11+00+00   -- bash -c "python -m daemon ./cfgs/figure1/cfg1.txt; exec bash" 
gnome-terminal --geometry 56x11+460+00   -- bash -c "python -m daemon ./cfgs/figure1/cfg2.txt; exec bash" 
gnome-terminal --geometry 56x11+920+00   -- bash -c "python -m daemon ./cfgs/figure1/cfg3.txt; exec bash" 
gnome-terminal --geometry 56x11+1380+00  -- bash -c "python -m daemon ./cfgs/figure1/cfg4.txt; exec bash" 
gnome-terminal --geometry 56x11+230+260  -- bash -c "python -m daemon ./cfgs/figure1/cfg5.txt; exec bash" 
gnome-terminal --geometry 56x11+690+260  -- bash -c "python -m daemon ./cfgs/figure1/cfg6.txt; exec bash" 
gnome-terminal --geometry 56x11+1150+260 -- bash -c "python -m daemon ./cfgs/figure1/cfg7.txt; exec bash" 


