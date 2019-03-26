# Testing 

## Model tests

From the repo root directory, run `python run.py test` to run tests to check that model code produces expected output. 

This will execute the command in the `test_config.yml` file and check that the files produced and saved to the `test/test` directory match those that are sources of truth in the `test/true` directory.

As components of the model are developed, a sample of expected results given a sample input should be placed in `true/` and the command used to generate them and save the results to `test/` should be added to `test_config.yml`

### Configuration

The configuration file should look like the following:

```yaml
test_name:
  command: Command that should be run to generate the results/artifacts to be tested
  true_dir: Path from the repo root to where the source of truth files are held (e.g. test/true/)
  test_dir: Path from the repo root to where the files produced by the command above will be stored
  files_to_compare:
    - Names of files that will exist in both the true and test directories after the above command is written (e.g. test_output.csv)
    - The files with the same name in both directories will be compared and test will pass if they are the same
    - If files produced are JSON or other non-ordered data entities, this comparison will not work (need to add ability to compare dictionaries in future)
```

## Unit tests 

Need to add  
