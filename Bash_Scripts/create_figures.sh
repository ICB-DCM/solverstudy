#!/bin/bash

# Create figures

cd Python_Scripts

for script in `ls plot_*`; do
  python $script
done
