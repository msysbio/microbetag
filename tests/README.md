# Test cases for the stand-alone version


Here we provide a list of tests to:
- verify that `microbetag` was installed correctly, and
- ensure the continued functionality of its modules following a PR.


Remember, `unittest`:

  - requires the testing function to start with the `test_` prefix, e.g. `test_run_flashweave()`
  - will run your tests in alphabetical order
  - `setUpClass` is called with the class as the only argument and must be decorated as a `classmethod()`


❗ `microbetag` uses the directory containing the provided configuration (YAML) file as its base working directory.
**Thus, please make sure to place all input and output files in the same directory as the configuration file.**

For more about the tests here, their input/output files etc.,
you may have a look at the [`README` file on the `test_data` folder](../test_data/README.md).


