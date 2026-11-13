#!/bin/bash

#SBATCH --job-name=ERA5_download
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=02:00:00
#SBATCH --account=phys040684
#SBATCH --output=logs/era5_%A_%a.out
#SBATCH --error=logs/era5_%A_%a.err

# Download assigned chunk
python download_chunk.py $SLURM_ARRAY_TASK_ID