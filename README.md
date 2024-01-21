# rdc_project

First the conda environment should be created in order to have the compatible version of python and required packages. This can be done using the following command: (To be run in the same directory as the environment.yml file.)

```sh
conda env create -f environment.yml
```

Then the conda environment schould be activated in the terminal before working on the project:
[

```sh
conda activate rdc_project
```

[Link to official conda documentation for more info:]([Managing environments &#8212; conda 23.11.1.dev56 documentation](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html))

This project should by run with a .env file in the directory, containing the url of the google sheet:

```yml
GOOGLESHEETS_URL='<my_super_secret_url>'
```

The streamlit server can be started locally with:

```python
streamlit run app.py
```