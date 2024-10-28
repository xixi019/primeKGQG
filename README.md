## PrimeKGQA

### This is a repo for generation questions from PrimeKG
  The dataset is uploaded in the zenedo: https://zenodo.org/records/13348627

# Project Name

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)  
[![Build Status](https://img.shields.io/travis/username/repo.svg)](https://travis-ci.org/username/repo)

### Description

This code base extracts subgraphs from an endpoint, form sparqls, extract answers.
The above info would be sent to LLM for question generation.

---


## Prerequisites

- Python Version:3.8 and above
- pip install -r requirement.tex 


## How to run
- go to folder 'extract'
- run endExtract.py and statistics.py
- they would extract subgraphs based on the network motifs and output json files with related info

- go to folder generation
- rub mistral_baseline.py
- generate question from LLM

## dataset for download 
- https://zenodo.org/records/13829395
### Please cite our publication if you find this work useful

   ```console
  @incollection{yan2024bridging,
  title={Bridging the Gap: Generating a Comprehensive Biomedical Knowledge Graph Question Answering Dataset},
  author={Yan, Xi and Westphal, Patrick and Seliger, Jan and Usbeck, Ricardo},
  booktitle={ECAI 2024},
  pages={1198--1205},
  year={2024},
  publisher={IOS Press}
   }
   ```****
