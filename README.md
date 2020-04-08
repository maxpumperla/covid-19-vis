# COVID-19 development Gapminder visualisation

![covid-19](covid-19-gapminder.gif)

To use this demo, first clone this repo together with its submodule and `cd` into it:

```bash_script
git clone --recursive git@github.com:maxpumperla/covid-19-vis.git
cd covid-19-vis
```

then install the requirements in a virtual environment and start a bokeh server.

```bash_script
virtualenv venv && source venv/bin/activate
pip install -r requirements.txt
bokeh serve --show main.py
```

If you want to update the underlying data, either pull the `covid-19` submodule or regenerate
data accordingly to the instructions in the `covid-19` folder.