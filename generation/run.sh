#!/bin/bash
#SBATCH --gpus-per-node=1
#SBATCH --constraint=48GB
#SBATCH --job-name=val

python mistral_baseline.py
