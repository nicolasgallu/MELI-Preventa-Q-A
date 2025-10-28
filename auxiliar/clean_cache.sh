#!/bin/bash

echo "Borrando __pycache__ y archivos .pyc..."

find . -type d -name "__pycache__" -exec rm -r {} + -print
find . -type f -name "*.pyc" -delete -print
find . -type f -name "*.pyo" -delete -print

echo "Limpieza completada."
