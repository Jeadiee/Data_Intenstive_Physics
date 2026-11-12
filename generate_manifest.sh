#!/bin/bash

#SBATCH --job-name=ERA5_manifest
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:30:00
#SBATCH --account=phys040684
#SBATCH --output=/user/home/uo23496/Data_Intenstive_Physics/logs/manifest_%j.out
#SBATCH --error=/user/home/uo23496/Data_Intenstive_Physics/logs/manifest_%j.err

cd /user/home/uo23496/Data_Intenstive_Physics || exit 1

python generate_manifest.py
