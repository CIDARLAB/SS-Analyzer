# SS-Analyzer

SS-Analyzer (State Space Analyzer) is a tool that allows the user to process a microfluidic design described that conforms to the ParchMint ([http://parchmint.org](http://parchmint.org)) standard to be be analyzed for Pressure and Flow Rate data. In this demonstration version of SS-Analyzer, the tool can only work with 1-1 `CONNECTION` and `MIXER` object used by 3DµF ([http://3duf.org](http://3duf.org)). Future versions of SS-Analyzer will be extended to support more component definitions and be able to complex connectivity.

## Installation

### Dependencies

In order to use SS-Analyzer, Python 3.8 or greater is required to be installed on the computer. The analyzer also uses `poetry` to manage the dependencies.

### pipenv based installation

```
# This assumes you clone the repo and have python installed on your machine

pip install pipenv          #Install pipenv 
cd <project directory>
pipenv install              #Creates sandbox runtime env and downloads all dependencies
pipenv shell                #Changes the terminal environment into the sandbox env, <ctrl + D> to exit
pip freeze                  #Ensures the runtime python interpreter finds all modules
python tool.py  <design file> -i <config>   #Runs the primary application
``` 

## Usage

### Config File Format
In order to run the tool, the user needs to pair the design created using 3DµF with a corresponding config file that is encoded in plain text. An example of the config file is as follows:

```
port_in1, IN, 1
port_in2, IN, 1
port_out, OUT, 101325
```

Where each line corresponds follows the below format :

```
<component name> <state> <flowrate (IN) / pressure(OUT)>
```

**Note**  - The current version of SS-Analyzer only annotates flow-rate for inputs and pressure for outputs. Future versions of SS-Analyzer will support additional features.

### Command Line Interface
```
usage: solve-network [-h] [-i INPUT] design
```

```
positional arguments:
  design                JSON file to Analyze
```
```
optional arguments:
  -h, --help    show this help message and exit
  -i INPUT, --input INPUT Config file
```
### Demonstration Files

The demonstration design file and config file are available with the v0.1 release ([https://github.com/CIDARLAB/SS-Analyzer/releases/](https://github.com/CIDARLAB/SS-Analyzer/releases/))

## License 

BSD 2-Clause License

Copyright (c) 2021, CIDAR LAB
All rights reserved.