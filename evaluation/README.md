# 3D Commerce Evaluation Tools

## Prerequisites

You need the extracted __Test results package__ as a directory and in the correct format (the files must all start with `c-`).

The 3DC-Certification repository with all the reference images in the `models` directory.

## Python dependencies

Install Python3, either via the OS package manager or via the installer from the website [https://www.python.org/downloads/](https://www.python.org/downloads/)

Install python packages

```bash
pip3 install scikit-image argparse numpy sewar reportlab
```

You might need to install more packages than stated above. You can find the package name in the error output.


## Run the evaluation

You can get a list of all arguments for the evaluation script by running the following command from within the 
`evaluation` subdirectory.

```bash
python3 evaluation.py --help
```

Which will list the arguments of the evaluation script

```
usage: evaluation.py [-h] [--rep REP] [--name NAME] [--output OUTPUT] dir

Generate screenshots for certification

positional arguments:
  dir                   Path to the test results package (the candidate submission)

optional arguments:
  -h, --help            show this help message and exit
  --rep REP, -r REP     Path to the certification repository (defaults to "..")
  --name NAME, -n NAME  Name of the certification submission
  --output OUTPUT, -o OUTPUT
                        Output directory for results
```

Please be aware that the `--rep` option should point to the directory of the [3DC-Certification](https://github.com/KhronosGroup/3DC-Certification) repository.

### Example

An example for how to evaluate a report for a __Test results package__ at `~/Desktop/Example` would be:

```
python3 evaluation.py --output ~/Desktop/Example_Evaluation_Results --name Example ~/Desktop/Example 
```

This would then create a report PDF and JSON in `~/Desktop/Example_Evaluation_Results` and set the name of the submission in the document to `Example`.
