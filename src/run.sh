#!/bin/bash

gnome-terminal --geometry 40x12+00+00   -- bash -c "python -m daemon ./cfgs/figure1/cfg1.txt; exec bash" 
gnome-terminal --geometry 40x12+350+00  -- bash -c "python -m daemon ./cfgs/figure1/cfg2.txt; exec bash" 
gnome-terminal --geometry 40x12+700+00  -- bash -c "python -m daemon ./cfgs/figure1/cfg3.txt; exec bash" 
gnome-terminal --geometry 40x12+1050+00 -- bash -c "python -m daemon ./cfgs/figure1/cfg4.txt; exec bash" 
gnome-terminal --geometry 40x12+1400+00 -- bash -c "python -m daemon ./cfgs/figure1/cfg5.txt; exec bash" 
gnome-terminal --geometry 40x12+00+300  -- bash -c "python -m daemon ./cfgs/figure1/cfg6.txt; exec bash" 
gnome-terminal --geometry 40x12+350+300 -- bash -c "python -m daemon ./cfgs/figure1/cfg7.txt; exec bash" 



