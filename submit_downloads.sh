#!/bin/bash

#SBATCH --job-name=ERA5_download
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=02:00:00
#SBATCH --account=phys040684
#SBATCH --output=logs/era5_%A_%a.out
#SBATCH --error=logs/era5_%A_%a.err

set -euo pipefail

module add languages/python
cd /user/home/uo23496/Data_Intenstive_Physics

# Download assigned chunk
python download_chunk.py $SLURM_ARRAY_TASK_ID