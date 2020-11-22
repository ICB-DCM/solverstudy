#!/bin/bash

# Create figures

cd Python_Scripts

for script in `ls plot_*`; do
  echo $script
  python $script
done
