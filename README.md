# PeakRDL SVD Importer

Import SVD files into PeakRDL.

## Installation

```sh
python -m venv .venv
source .venv/bin/activate
pip install peakrdl .
```

## Usage

### Generate HTML
```sh
peakrdl html example/STM32F429.svd -o html_dir
```

### Generate SystemRDL
```sh
peakrdl systemrdl example/STM32F429.svd -o STM32F429.rdl
```