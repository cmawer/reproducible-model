# Example of a reproducible machine learning model 

See [https://cmawer.github.io/reproducible-model](https://cmawer.github.io/reproducible-model) for the lightening talk I gave at the Women in Machine Learning and Data Science meetup on March 26, 2019 at Stitch Fix on the ingredients of a reproducible machine learning model.
 

## Repo structure 

```
├── README.md                         <- You are here
│
├── config                            <- Directory for yaml configuration files for model training, scoring, etc
│   ├── logging/                      <- Configuration of python loggers
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── archive/                      <- Place to put archive data is no longer usabled. Not synced with git. 
│   ├── external/                     <- External data sources, will be synced with git
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│
├── docs                              <- A default Sphinx project; see sphinx-doc.org for details.
│
├── figures                           <- Generated graphics and figures to be used in reporting.
│
├── models                            <- Trained model objects (TMOs), model predictions, and/or model summaries
│   ├── archive                       <- No longer current models. This directory is included in the .gitignore and is not tracked by git
│
├── notebooks
│   ├── develop                       <- Current notebooks being used in development.
│   ├── deliver                       <- Notebooks shared with others. 
│   ├── archive                       <- Develop notebooks no longer being used.
│   ├── template.ipynb                <- Template notebook for analysis with useful imports and helper functions. 
│
├── src                               <- Source data for the sybil project 
│   ├── archive/                      <- No longer current scripts.
│   ├── helpers/                      <- Helper scripts used in main src files 
│   ├── sql/                          <- SQL source code
│   ├── ingest_data.py                <- Script for ingesting data from different sources 
│   ├── generate_features.py          <- Script for cleaning and transforming data and generating features used for use in training and scoring.
│   ├── train_model.py                <- Script for training machine learning model(s)
│   ├── score_model.py                <- Script for scoring new predictions using a trained model.
│   ├── postprocess.py                <- Script for postprocessing predictions and model results
│   ├── evaluate_model.py             <- Script for evaluating model performance 
│
├── test                              <- Files necessary for running model tests (see documentation below) 
│   ├── true                          <- Directory containing sources of truth for what results produced in each test should look like 
│   ├── test                          <- Directory where artifacts and results of tests are saved to be compared to the sources of truth. Only .gitkeep in this directory should be synced to Github
│   ├── test.py                       <- Runs the tests defined in test_config.yml and then compares the produced artifacts/results with those defined as expected in the true/ directory
│   ├── test_config.yml               <- Configures the set of tests for comparing artifacts and results. Currently does not include unit testing or other traditional software testing
│
├── run.py                            <- Simplifies the execution of one or more of the src scripts 
├── requirements.txt                  <- Python package dependencies 
```
This project structure was partially influenced by the [Cookiecutter Data Science project](https://drivendata.github.io/cookiecutter-data-science/).

## Environment setup 

The `requirements.txt` file contains the packages required to run the model code. An environment can be set up in two ways. See bottom of README for exploratory data analysis environment setup. 

### With `virtualenv` and `pip`

```bash
pip install virtualenv

virtualenv reprod

source reprod/bin/activate

pip -r requirements.txt

```

## Reproducibility testing
Check that results and code behavior are what is expected  


From the repo root directory, run:
 
 ```python
 python run.py test
```
 to run tests to check that model code produces expected output. See `test/README.md` for more info. 


## Environment setup for exploratory analysis

`environment.yml` contains the specifications for an environment that will get you started for exploratory data analysis. 
It also contains the packages imported in the template Jupyer notebook, `notebooks/template.ipynb` (see more info below).  

### Create conda environment 
Create conda environment with packages in `environment.yml`: 

`conda env create -f environment.yml`

and activate:

`source activate eda3`

### Complete Jupyter extensions install
After creating and activating your conda environment, run from the commandline:

`jupyter contrib nbextension install --user`

Next, start a Jupyter notebook server by running: 

`jupyter notebook`

You can then go to the extension configurator at [http://localhost:8888/nbextensions/](http://localhost:8888/nbextensions/) and enable your desired extensions. 

#### Collapsible headings extension
I recommend enabling the `Collapsible Headings` extension so that the `Imports and setup` section on the template notebook (see section below), which is quite long, can be minimized, as well as other heading sections when desired. To maintain this collapsibility when exporting to html, run:

`jupyter nbconvert --to html_ch FILE.ipynb`

#### Table of Contents (2)
Enabling the `Table of Contents (2)` extension automatically creates a table of contents based on your notebook headings, which can be placed at the top of the notebook or at the side (which is nice for navigation in a long notebook).

To keep this table of contents when you export to html, add to the command in the prior section and run: 

`jupyter nbconvert --to html_ch FILE.ipynb --template toc2`

#### Other recommended extensions
* `Code prettify`: when enabled, you can press the little hammer icon at the top of the page and it will make "pretty" ([PEP8](https://www.python.org/dev/peps/pep-0008/) compliant) the code in the current cell. This is really nice when you're writing a long command. 
* `Execute time`: when enabled, this adds to the bottom of a code cell the time at which the cell was executed and how long it took. This is nice for traceability purposes and making sure code was run in order when looking at old code. It also helps when code takes a while to run and you leave it and come back and want to know how long it took. 
* `Ruler`: when enabled, this adds a vertical line to code cells to denote the distance of 76 characters, which is the maximum line length suggested by ([PEP8](https://www.python.org/dev/peps/pep-0008/)).

There are a lot more options so take a look through! 

### Template Jupyter Notebook 
`notebooks/template.ipynb` is a template Jupyter notebook that includes:
 * A set of regularly used package imports 
 * Code that helps reference other parts of the directory structure (e.g. `dataplus()` prepends the data directory for data import)
 * Code that sets up a SQLAlchemy connection to MySQL 
 * Headings for stating notebook objectives, guiding questions, conclusions 
 * A pretty Lineage logo at the top 
 
 