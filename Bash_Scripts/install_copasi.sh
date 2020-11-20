#!/bin/bash

# Install COPASI

COPASI_VERSION="4.29.228-Linux-64bit"
wget "https://github.com/copasi/COPASI/releases/download/Build-228/COPASI-${COPASI_VERSION}.tar.gz"
tar -xzvf COPASI-${COPASI_VERSION}.tar.gz
mv COPASI-${COPASI_VERSION} COPASI
rm COPASI-${COPASI_VERSION}.tar.gz
