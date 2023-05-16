# iRacingInsights

*** WORK IN PROGRESS ***

The system comes with no guarantees or warranties.   

## Introduction

This is a [Django](https://www.djangoproject.com/) Web Application that uses the [iRacing API](https://forums.iracing.com/discussion/15068/general-availability-of-data-api#latest) to present driver, race & league data.

Currently, the statistical analysis is limited.  Further analysis and plotting will be added in time.  The [league scoring system](https://github.com/byteinsight/iRacingInsights/wiki/League-Scoring-System) has some flexibility.  

## Installing

### Step 1 - Install Python

I've developed and run this application on Python 3.11 which you can download from [here](https://www.python.org/downloads).

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

### Step 2 - Rename Settings.py and set iRacing login details.

Inside *INSIGHT_HOME/iRacingInsights/* rename the *settings.default.py* to *settings.py*

```
Move-Item -Path iRacingInsights\settings.default.py -Destination settings.py
```

Open settings.py in your favourite text editor - we prefer [Sublime Text](https://www.sublimetext.com/3) or 
[Notepad++](https://notepad-plus-plus.org/downloads/). Now replace the placemarkers for Username and Password with your iRacing login details.

### Step 3 - Make and build Database inside the Archive Folder.

We need to create an archive folder inside INSIGHT_HOME and then get django to build its database from the model descriptions.
```
New-Item -Path archive -ItemType Directory
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

### Step 4 - Create a media folder and populate some initial data.

We need to create a media folder and populate the Update & Category tables with initial data.

```
New-Item -Path media -ItemType Directory
python manage.py loaddata updates
python manage.py loaddata categories
```

### Step 4 - Create Django Admin Super User

The Django Admin user will allow us to access the program and modify certain records.  Type the following in your Powershell and follow the prompts

```
python manage.py createsuperuser
```

### Step 5 - Logging In and setting the Admin Cust ID.

When you first run the system there is a lot of data to be pulled from the iRacing servers.   Before we can do this we need to tell the system what your iRacing Cust ID is.
Type the following into your Powershell, 

```
python manage.py runserver
```

Now visit [127.0.0.1:8000](http://127.0.0.1:8000) in a browser and using the Admin Super User details set in Step 4 login.

You should now be able to click on Users followed by YourAdminUser.  At the bottom of the screen add your six digit iRacing Customer ID and click save.

### Step 6 - First Run

Now you can click View Site at the top of the page.   This will start by loading your personal profile.   It might take a few moments.

Before clicking on any races that show you should also click on Cars, Tracks and Series to load this data.

## Running

### Temporary Running and Testing

As you have seen already the easiest way to run Django is via the command line. 

```
python manage.py runserver
```

### Using the Development Server locally.

If this is for personal local use only then you could always add the above command to a script called at start up.  


### Deployment 

If you are interested in deploying the system into a production settings then you will want to review [How to deploy Django](https://docs.djangoproject.com/en/4.2/howto/deployment/).

Currently, the system is **NOT RECOMMENDED** for deployment on any Public Networks.  

## Further Information 

The [WIKI](https://github.com/byteinsight/iRacingInsights/wiki) will be the place to find further information on how the system works, its limitations and other useful knowledge. 

