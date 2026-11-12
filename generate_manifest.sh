#!/bin/bash

#SBATCH --job-name=ERA5_manifest
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:30:00
#SBATCH --output=/user/home/uo23496/Data_Intenstive_Physics/logs/manifest_%j.out
#SBATCH --error=/user/home/uo23496/Data_Intenstive_Physics/logs/manifest_%j.err

set -euo pipefail

module add languages/python

cd /user/home/uo23496/Data_Intenstive_Physics

which python
python --version
python generate_manifest.py
