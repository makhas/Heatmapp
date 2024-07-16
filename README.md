README

# All use cases (Start Here!)
create a python environment and install the requirements.

If you are using conda, type "conda env create -f requirements.txt [ENV_NAME]" in your appropriate terminal.

The folder drive_heatmap is scoped to store necessary files for generating heatmaps for DriverTech. You should see the following file layout (at minimum):

drive_heatmap
|--templates
    |-- *.html
|heatmapp.py
|loadStateRoute.py
|requirements.txt
|(prod.env) 

If prod.env is not available, ask a team member. If you only want to launch the webapp and view pregenerated HTMLs, this is not necessary.

# I want the app!
Once the requirements have successfully loaded, you can run "python heatmapp.py" to launch a local server and view the htmls
that are located in the templates folder. 

## I don't have any htmls!
At minimum, the templates folder will have an ``input.html`` file which is necessary for the webapp. If you don't have access to any other htmls, look at the next section for how to generate maps, or ask a friend for theirs!

# I want to make maps!
If you want to generate a map, you must additionally install folium via pip.

``pip install folium``

Once folium is installed, the script that generates heatmaps is labeled ``loadStateRoute.py``. Currently, it takes one keyword arg --state, upon which you specify a state by using it's abbreviation (Montana -> MT, New York -> NY, etc.)

To run it in terminal, apply the following command

``python loadStateRoute.py --state [STUSAB]`` where STUSAB is the State's US Abbreviation.

Currently there is no more filtering functionality available unless you go into the file query itself and modify it. The query subject to most relevant filters will be the first query in the function ``read_state_loc``.

Further filtering considerations are the density argument that is used to downsample each drive.