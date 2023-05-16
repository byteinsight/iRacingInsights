# iRacingInsights

***   WORK IN PROGRESS ***

I'M STILL CHECKING AND TESTING THE REQUIREMENTS FOR INSTALL, SETUP and RUNNING OUTSIDE OF THE DEV-PC - PLEASE BEAR WITH

## Introduction

This is a [Django](https://www.djangoproject.com/) Web Application that uses the [iRacing API](https://forums.iracing.com/discussion/15068/general-availability-of-data-api#latest) to present driver, race & league data.

Currently the statistical analysis is limited but it envisaged that more will be added as time passes.   The league scoring system is currently fixed but more options will be added in time.  

## Installing

### Step 1 - Install Python

I've developed and run this application on Python 3.11 which you can dowmload from [here](https://www.python.org/downloads).

### Step 2 - Install the required packages

You can install the requirements as follows.

  - [Django](https://pypi.org/project/Django/)  ~=4.2.1   pip install Django
  - [Numpy](https://pypi.org/project/numpy/) ~=1.24.2  pip install numpy
  - [Pandas](https://pypi.org/project/pandas/)  ~=2.0.1   pip install pandas
  - [Matplotlib](https://pypi.org/project/matplotlib/) ~=3.7.1  pip install matplotlib
  - [Requests](https://pypi.org/project/requests/)  ~=2.30.0  pip install requests
  

## Set Up

### Step 1 - Move to the iRacingInsights Root Folder

From here onwards INSIGHT_HOME refers to the location of the root folder for iRacingInsights, which in my case is *C:\Users\iRacingInsights*.  Opening a Powershell terminal move into the INSIGHT_HOME folder with 

```
cd L://ocation/Of/iRacingInsights
```

### Step 2 - Rename Settings.py

Inside *INSIGHT_HOME/iRacingInsights/* rename the *settings.default.py* to *settings.py*

```
Move-Item -Path iRacingInsights\settings.default.py -Destination settings.py
```

### Step 3 - Make and build Database inside the Archive Folder.

We need to create an archive folder inside INSIGHT_HOME and then get django to build its database from the model descriptions.
```
New-Item -Path archive -ItemType Directory
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

### Step 4 - Create Django Admin Super User

Type the following in your Powershell and follow the prompts

```
python manage.py createsuperuser
```

### Step 5 - Set your iRacing Username and Password in the settings file.

Open settings.py in your favourite text editor.  We prefer [Sublime Text](https://www.sublimetext.com/3) or [Notepad++](https://notepad-plus-plus.org/downloads/).  Replace the placemarker for Username and Password with your iRacing login details.

### Step 6 - Populate the intervals table.

We need to Populate the Update & Category tables with initial data.

```
python manage.py loaddata updates
python manage.py loaddata categories
```

## Running

### Temporary Running and Testing

The easiest way to run Django is via the command line. 

```
python manage.py runserver
```

