#!/bin/bash

#SBATCH --job-name=ERA5_manifest
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:30:00
#SBATCH --output=logs/manifest_%j.out
#SBATCH --error=logs/manifest_%j.err

cd /path/to/Data_Intenstive_Physics

python generate_manifest.py
