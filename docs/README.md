# Sphinx documentation 

## Accessing docs 

Open up `build/html/index.html` to access documentation. 

## Updating docs

### Changes to current files 
Any time that the current Python files or sphinx `.rst` files are changed, the `html` should be recreated by running:

```bash
make html
```

### Addition of files 

If new files are added, the autodoc files should be recreated by running 


```bash
sphinx-apidoc -f -o source/model/ ../ ../data/ ../figures ../src ../test

sphinx-apidoc -f -o source/model/test/ ../test/ 

sphinx-apidoc -f -o source/model/src/ ../src/ ../src/archive/
```

as in step 3 in the setup guide below. 

If new directories are added, the above command should be run for the new directory and the directory needs to be added to `source/index.rst` as in step 4 in the guide below. 
 
## Sphinx setup guide 
This documentation was created by doing the following from this directory: 

1. Install the necessary packages
    ```bash
    conda install sphinx
    conda install sphinx_rtd_theme
    ```
1. Run `sphinx-quickstart`

2. Edit `conf.py`

    Add the following at the top of the script: 
    
    ```python
    import sphinx_rtd_theme
    sys.path.insert(0, os.path.abspath('../..'))
    sys.path.insert(0, os.path.abspath('../'))
    sys.path.insert(0, os.path.abspath('../src'))
    ```
    
    Change `html_theme` (found around line 85) and add `html_theme_path` as follows:
    
    ```python
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
    ```

3. Run `sphinx-apidoc` to autogenerate pages with `autodoc` as follows from the command line:

    ```bash
    sphinx-apidoc -f -o source/model/ ../ ../data/ ../figures ../src ../test
    
    sphinx-apidoc -f -o source/model/test/ ../test/ 
    
    sphinx-apidoc -f -o source/model/src/ ../src/ ../src/archive/
    ```

4. Add to `source/index.rst`:

    ```markdown
    Contents
    --------
    .. toctree::
       :maxdepth: 2
    
       model/src/src
       model/test/test
       model/run
    ```

5. Make html files by running from the command line: 

    ```bash
    make html 
    ```
