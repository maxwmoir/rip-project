#!/bin/bash

gnome-terminal --geometry 37x11+00+00   -- bash -c "python -m daemon ./cfgs/figure1/cfg1.txt; exec bash" 
gnome-terminal --geometry 37x11+350+00  -- bash -c "python -m daemon ./cfgs/figure1/cfg2.txt; exec bash" 
gnome-terminal --geometry 37x11+700+00  -- bash -c "python -m daemon ./cfgs/figure1/cfg3.txt; exec bash" 
gnome-terminal --geometry 37x11+1050+00 -- bash -c "python -m daemon ./cfgs/figure1/cfg4.txt; exec bash" 
gnome-terminal --geometry 37x11+1400+00 -- bash -c "python -m daemon ./cfgs/figure1/cfg5.txt; exec bash" 
gnome-terminal --geometry 37x11+00+300  -- bash -c "python -m daemon ./cfgs/figure1/cfg6.txt; exec bash" 
gnome-terminal --geometry 37x11+350+300 -- bash -c "python -m daemon ./cfgs/figure1/cfg7.txt; exec bash" 



