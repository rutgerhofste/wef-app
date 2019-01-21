

# Hello world for a Dash app. 

Create virtualenv or conda environment  
`conda create --name dashtest python=3.6`  

Activate environment  
dashtest
Unix:  
`source activate dashtest`  
Windows:   
`activate dashtest`  

`pip install dash==0.35.1  # The core dash backend`  
`pip install dash-html-components==0.13.4  # HTML components`  
`pip install dash-core-components==0.42.1  # Supercharged components`  
`pip install dash-table==3.1.11  # Interactive DataTable component (new!)`  
`pip install pandas`

Hello world app:  
https://dash.plot.ly/getting-started

## Running Locally
`python app.py`


## Running in the cloud

### Heroku
[python+heroku docs](https://devcenter.heroku.com/articles/getting-started-with-python)   
[dash+heroku docs](https://dash.plot.ly/deployment)  

1. Install CLI
2. Open Terminal (as admin)
3. Heroku login
4. Add Heroku files: 
5. `heroku create`

