from django.shortcuts import render
from django.http import Http404
from django.conf import settings
from django.db.models import Count, Min
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.contrib.auth.decorators import login_required
from django.db.models import F

import pandas as pd
import json
import os

from .models import *
from includes.irstatsDataClient import irstatsDataClient
from includes.irStatsPlotClient import irStatsPlotClient

def checkRecordUpdateInterval(type, next_update):

    try:
        # Get the update record and current time
        type_update = Update.objects.get(type=type)
        current_time = make_aware(datetime.now())

        # If no update has ever been done force it with a really old date
        if next_update is None:
            next_update = current_time - timedelta(days=1)


        print("Current Time", current_time)
        print("Date Modified", next_update)

        # See whether we have a positive time difference between now and next update.
        current_timediff = current_time - next_update
        if current_timediff.total_seconds() > type_update.interval:

            print("Updating", type, current_timediff.total_seconds())

            # Only use this is now is good time for update
            next_update = current_time + timedelta(seconds=type_update.interval)
            print("Next Update Due", next_update)
            return next_update

        else:
            print("No update required", current_timediff)
            return False

    # Something went wrong.
    except Update.DoesNotExist:
        print("No update interval available")
        return False

def checkUpdateInterval(type):
    """ Checks against the update model to see if we should check for updates
        So we are not hitting the iRacing servers too often """

    try:
        # Get the update record and our date/times
        type_update = Update.objects.get(type=type)
        current_time = make_aware(datetime.now())
        next_update = current_time +  timedelta(seconds=type_update.interval)

        if type_update.last_update is not None:
            last_update = type_update.last_update
        else:
            last_update = current_time - timedelta(days=1)

        # Get the time diff and test
        current_timediff = current_time - last_update
        if current_timediff.total_seconds() > type_update.interval:
            print("Updating", type, current_timediff.total_seconds())

            type_update.last_update = current_time
            type_update.next_update = next_update
            type_update.save()

            return True

        # Not time to update yet
        else:
            print("No update required", current_timediff)
            return False

    # Something went wrong.
    except Update.DoesNotExist:
        print("No update interval available")
        return False


@login_required(login_url='/admin/login/')
def index(request):
    """ Homepage view for the logged in users """
    try:

        # Get the iRacing Customer ID of the logged in user
        current_user = request.user
        custid = current_user.custid.custid

        # Check it we need to update the members stats based on interval.
        if checkUpdateInterval("Profile"):
            ir_stats = irstatsDataClient(request)
            ir_stats.updateMember()

        #Get the member stats & career from the database
        member_stats = Member.objects.get(custid=custid)
        member_career = Career.objects.all().filter(member=member_stats.id, year=0).order_by('-starts')
        recent_races = Races.objects.all().filter(member=member_stats.id)
        context = {'member_stats': member_stats, 'member_career': member_career, 'recent_races': recent_races}

    #If the member does not exist the call the update function.
    except Member.DoesNotExist:
        context, created = ir_stats.updateMember()
        if not created:
            raise Http404("Member does not exist")

    return render(request, 'irstats/index.html', context)


@login_required(login_url='/admin/login/')
def cars(request):
    """ Cars view """
    ir_stats = irstatsDataClient(request)

    if checkUpdateInterval("Cars"):
        ir_stats.updateCars(True)

    # Get all the cars from the database
    car_listing = Cars.objects.all()
    cars_assets = ir_stats.getJsonFile("cars_assets.json")
    context = {'car_listing': car_listing, 'cars_assets': cars_assets}
    return render(request, 'irstats/cars.html', context)


@login_required(login_url='/admin/login/')
def leagues(request):

    if checkUpdateInterval("Leagues"):
        ir_stats = irstatsDataClient(request)
        ir_stats.updateLeagueRegister()

    # Get all the cars from the database
    league_listing = Leagues.objects.all()
    context = {'league_listing': league_listing}
    return render(request, 'irstats/leagues.html', context)


@login_required(login_url='/admin/login/')
def league(request, league_id):
    """ League Detail View """

    try:

        # Get the league details from the database
        league = Leagues.objects.get(league_id=league_id)

        # Check whether its time to update.
        next_update = checkRecordUpdateInterval("Leagues", league.next_update)

        # If the next_update is not false then this means we update and save future update date.
        if next_update is not False:
            league.next_update = next_update
            league.save()

            ir_stats = irstatsDataClient(request)
            ir_stats.updateLeagueData(league, True)

        seasons = LeagueSeasons.objects.all().filter(league=league)
        context = {'league': league, 'seasons': seasons}

    #If the league does not exist the call the update function.
    except Leagues.DoesNotExist:
        raise Http404("League does not exist")

    return render(request, 'irstats/league.html', context)


@login_required(login_url='/admin/login/')
def league_roster(request, league_id):
    """ League Detail View """

    # Get the league details from the database
    try:
        league = Leagues.objects.get(league_id=league_id)
    except Leagues.DoesNotExist:
        raise Http404("League does not exist")

    try:
        roster = LeagueRoster.objects.all().filter(league=league).order_by('-category2_irating')
        roster_colnames = [field.name for field in LeagueRoster._meta.get_fields()]

        roster_df = pd.DataFrame.from_records(roster.values_list(), columns=roster_colnames)

        cols_to_norm = ['category2_safety_rating', 'category2_cpi', 'category2_irating', 'category2_mpr_num_races']
        for col in cols_to_norm:
            roster_df[col + "_norm"] = roster_df[[col]].apply(lambda x: (x - x.min()) / (x.max() - x.min()))

        cols_to_norm_names = ['category2_safety_rating_norm', 'category2_cpi_norm', 'category2_irating_norm', 'category2_mpr_num_races_norm']
        roster_df['avg_norm'] = roster_df[cols_to_norm_names].mean(axis=1)
        roster = roster_df.sort_values(by=['avg_norm'], ascending=False).to_dict(orient='records')

        plots = irStatsPlotClient(settings.BASE_DIR)
        plots.plot_distribution("iR_distribution_" + str(league_id), roster_df['category2_irating'], binwidth=500)
        #plots.plot_distribution(roster_df['category2_safety_rating'], binwidth=0.5)

    except Exception as e:

        print("General Error", e)

    context = {'league': league, 'roster': roster}

    return render(request, 'irstats/league_roster.html', context)


@login_required(login_url='/admin/login/')
def league_season(request, season_id):
    """ League Season View """

    try:

        # Get the league details from the database
        season = LeagueSeasons.objects.get(id=season_id)

        ir_stats = irstatsDataClient(request)
        ir_stats.updateLeagueSeason(season)

        standings = LeagueSeasonStandings.objects.filter(season_id=season.season_id).order_by("-points", "incidents")

        context = {'season': season, 'standings': standings}

    #If the league does not exist the call the update function.
    except LeagueSeasons.DoesNotExist:
        raise Http404("Season does not exist")

    return render(request, 'irstats/league_season.html', context)


@login_required(login_url='/admin/login/')
def league_session(request, session_id):
    """ League Detail View
    @todo Can I make this more efficient?
    """
    ir_stats = irstatsDataClient(request)

    try:

        # Get the league details from the database
        league_session = LeagueSessions.objects.get(id=session_id)

        # Only update the session if we have no subsession ID
        if not league_session.subsession_id:
            print("Getting subsession ID for ", league_session)
            subsession_id = ir_stats.updateLeagueSession(league_session)
        else:
            print("We have this subsession ID for ", league_session, str(league_session.subsession_id))
            subsession_id = league_session.subsession_id




        simsessions = LeagueSessionSimsession.objects\
            .values("simsession_number", "simsession_type", "simsession_type_name", "simsession_subtype", "simsession_name")\
            .filter(session_id=subsession_id).order_by("simsession_number")

        #Get the simsessions.
        for simsession in simsessions:

            # Order races and final scores by points
            if simsession['simsession_type'] == 6 or simsession['simsession_type'] == 99:
                simsession['results'] = LeagueSessionResults.objects.all().filter(
                    session_id=subsession_id,
                    simsession_number=simsession['simsession_number']
                ).order_by(F('points').desc(nulls_last=True), F('finish_position').asc(nulls_last=True))

                
            # Practice and Quali by Fastests
            else:
                simsession['results'] = LeagueSessionResults.objects.all().filter(
                    session_id=subsession_id,
                    simsession_number=simsession['simsession_number']
                ).order_by(F('best_lap_time').asc(nulls_last=True), F('laps_complete').desc(nulls_last=True))

            if simsession['simsession_type'] != 99:
                simsession['events'] = ir_stats.updateSessionEventLog(subsession_id, simsession['simsession_number'], True)

        context = {'subsession_id': subsession_id, 'session': league_session, 'simsessions': simsessions}

    #If the league does not exist the call the update function.
    except LeagueSessions.DoesNotExist:
        raise Http404("Session does not exist")

    return render(request, 'irstats/league_session.html', context)


@login_required(login_url='/admin/login/')
def series(request):
    ir_stats = irstatsDataClient(request)

    if checkUpdateInterval("Series"):
        ir_stats.updateSeries(True)

    # Get all the cars from the database
    series_listing = Series.objects.all().filter(show=True)
    series_assets = ir_stats.getJsonFile("series_assets.json")
    context = {'series_listing': series_listing, "series_assets": series_assets}
    return render(request, 'irstats/series.html', context)


@login_required(login_url='/admin/login/')
def serie_details(request, series_id):
    ir_stats = irstatsDataClient(request)

    # Get all the cars from the database
    series = Series.objects.get(series_id=series_id)
    series_assets = ir_stats.getJsonFile("series_assets.json")

    context = {'series': series, "series_assets": series_assets}
    return render(request, 'irstats/serie_detail.html', context)


@login_required(login_url='/admin/login/')
def race(request, subsession_id):
    """ Race Detail View """

    try:

        # Get the member stats & career from the database
        race_info = Races.objects.get(subsession_id=subsession_id)

        # TODO - Might need to limit this to the user id
        laps = Laps.objects.all().filter(race_id=race_info.id)

        ir_stats = irstatsDataClient(request)

        file_end = str(subsession_id) + ".json"
        result = ir_stats.getJsonFile("result_" + file_end)
        event_log = ir_stats.getJsonFile("result_event_log_" + file_end)

        context = {
            'race_info': race_info,
            'laps': laps,
            'session_results': result['session_results'],
            'event_log': event_log
        }

    #If the race does not exist the call the update function.
    except Races.DoesNotExist:
        raise Http404("Race does not exist")

    return render(request, 'irstats/race.html', context)


@login_required(login_url='/admin/login/')
def tracks(request):
    """ Tracks view """
    ir_stats = irstatsDataClient(request)

    # Check it we need to update tracks from iRacing based on interval.
    if checkUpdateInterval("Tracks"):
        ir_stats.updateTracks(True)

    #Get all the tracks from the database and assets from json.
    track_listing = (Tracks.objects
                     .values('sku', 'track_name')
                     .annotate(variations=Count('sku'))
                     .order_by('track_name')
                     )

    # Loop through the track variations and retrieve additional details for each variation
    for tracko in track_listing:
        # Second query to retrieve details for each track variation
        track_details = Tracks.objects.filter(sku=tracko['sku'], track_name=tracko['track_name'])\
            .values('track_id', 'location', 'created')
        tracko['details'] = list(track_details)

    track_assets = ir_stats.getJsonFile("track_assets.json")
    context = {'track_listing': track_listing, 'track_assets': track_assets}
    return render(request, 'irstats/tracks.html', context)


@login_required(login_url='/admin/login/')
def track(request, sku):
    """ Tracks view """
    ir_stats = irstatsDataClient(request)

    # Get the league details from the database
    configs = Tracks.objects.filter(sku=sku)

    track_assets = ir_stats.getJsonFile("track_assets.json")
    context = {'configs': configs, 'track_assets': track_assets}
    return render(request, 'irstats/track.html', context)


@login_required(login_url='/admin/login/')
def docs(request):
    api_doc_path = os.path.join(settings.BASE_DIR, "archive" , "api_doc.json")
    f = open(api_doc_path)
    apidoc = json.load(f)

    context = {"apidoc":apidoc}
    return render(request, 'irstats/status.html', context)