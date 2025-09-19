# PeakRDL SVD Importer

Import SVD files into PeakRDL.

Using PeakRDL SVD from [SystemRDL/PeakRDL-svd](https://github.com/SystemRDL/PeakRDL-svd)

## Installation

```sh
python -m venv .venv
source .venv/bin/activate
pip install peakrdl .
git clone https://github.com/SystemRDL/PeakRDL-svd
pip install ./PeakRDL-svd
```

## Usage

### Generate HTML from SVD
```sh
peakrdl html example/STM32F429.svd -o html_dir
```

### Generate SystemRDL from SVD
```sh
peakrdl systemrdl example/STM32F429.svd -o STM32F429.rdl
```

### Generate SVD from SystemRDL
```sh
peakrdl svd STM32F429.rdl -o STM32F429.svd
```