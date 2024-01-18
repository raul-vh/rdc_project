# rdc_project

First the conda environment should be created in order to have the compatible version of python and required packages. This can be done using the following command:(To be run in the same directory as the environment.yml file.)
`conda env create -f environment.yml`

This project should by run with a .env file in the directory, containing the url of the google sheet:

``` yml
GOOGLESHEETS_URL='<my_super_secret_url>'

```