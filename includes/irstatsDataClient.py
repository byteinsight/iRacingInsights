from django.conf import settings

from pathlib import Path
import os
import json

from includes.scoringClient import scoringClient
from includes.iRacingClient import iRacingClient
from irstats.models import Member, Career, Category, Tracks, Cars, Series, Races, Laps, Leagues, LeagueSeasons
from irstats.models import LeagueRoster, LeagueSessions, LeaguePoints, LeagueSessionResults


class irstatsDataClient():

    irclient = None
    cust_id = None

    def __init__(self, request):

        # Get the iRacing Customer ID of the logged in user
        current_user = request.user
        self.custid = current_user.custid.custid

        # Create a irclient for the iracing api call.
        self.irclient = iRacingClient(settings.USERNAME, settings.PASSWORD, self.custid, settings.BASE_DIR, settings.FILE_FOLDER)

    def printRawData(self, title, raw_data):
        if raw_data is not None:
            print(title)
            print(str(raw_data).encode('cp1252', errors='replace').decode('cp1252'))
        else:
            print(title, "No Data Provided")

    def getJsonFile(self, file_name):
        try:
            file_path = os.path.join(settings.BASE_DIR, settings.FILE_FOLDER, file_name)
            f = open(file_path, encoding='utf-8')
            return json.load(f)
        except FileNotFoundError as e:
            print("getJsonFile", e)
        return None

    ##### GENERAL FUNCTIONS #####
    def updateCars(self, _export=False):
        """ Updates the cars database table """
        cars = self.irclient.get_cars(export=_export)
        for car in cars:
            try:
                if car.get("forum_url") is None:
                    car['forum_url'] = ""
                if car.get("price_display") is None:
                    car['price_display'] = ""
                new_car, created = Cars.objects.update_or_create(
                    car_id=car['car_id'],
                    defaults={
                        "ai_enabled": car['ai_enabled'],
                        "allow_number_colors": car['allow_number_colors'],
                        "allow_number_font": car['allow_number_font'],
                        "allow_sponsor1": car['allow_sponsor1'],
                        "allow_sponsor2": car['allow_sponsor2'],
                        "allow_wheel_color": car['allow_wheel_color'],
                        "award_exempt": car['award_exempt'],
                        "car_dirpath": car['car_dirpath'],
                        "car_id": car['car_id'],
                        "car_name": car['car_name'],
                        "car_name_abbreviated": car['car_name_abbreviated'],
                        "car_types": car['car_types'],
                        "car_weight": car['car_weight'],
                        "categories": car['categories'],
                        "created": car['created'],
                        "first_sale": car['first_sale'],
                        "forum_url": car['forum_url'],
                        "free_with_subscription": car['free_with_subscription'],
                        "has_headlights": car['has_headlights'],
                        "has_multiple_dry_tire_types": car['has_multiple_dry_tire_types'],
                        "hp": car['hp'],
                        "is_ps_purchasable": car['is_ps_purchasable'],
                        "max_power_adjust_pct": car['max_power_adjust_pct'],
                        "max_weight_penalty_kg": car['max_weight_penalty_kg'],
                        "min_power_adjust_pct": car['min_power_adjust_pct'],
                        "package_id": car['package_id'],
                        "price": car['price'],
                        "price_display": car['price_display'],
                        "retired": car['retired'],
                        "search_filters": car['search_filters'],
                        "sku": car['sku'],
                    }
                )
            except KeyError as ke:
                print("updateCars: Missing Keys", ke)

        self.irclient.get_cars_assets(_export)

    def updateMember(self, _export=False):
        """ Updates the member's basics, career stats and recent races """
        try:
            # Get basic member info
            member_info = self.irclient.member_info(export=_export)
            member_summary = self.irclient.stats_member_summary(export=_export)
            member_obj, created = Member.objects.update_or_create(
                custid=member_info['cust_id'],
                defaults={
                    'display_name' : member_info['display_name'],
                    'last_login' : member_info['last_login'],
                    'member_since' : member_info['member_since'],
                    'club_id' : member_info['club_id'],
                    'club_name' :member_info['club_name'],
                    'num_official_sessions': member_summary['this_year']['num_official_sessions'],
                    'num_league_sessions': member_summary['this_year']['num_league_sessions'],
                    'num_official_wins': member_summary['this_year']['num_official_wins'],
                    'num_league_wins': member_summary['this_year']['num_league_wins']
                }
            )

            # Get Member's Career in each category
            careers = self.irclient.stats_member_career(export=_export)
            for career in careers['stats']:
                category = Category.objects.get(id=int(career['category_id']))
                new_member_career, created = Career.objects.update_or_create(
                    member=member_obj,
                    category=category,
                    year=0,
                    defaults={
                        'starts': career['starts'],
                        'wins': career['wins'],
                        'top5': career['top5'],
                        'poles': career['poles'],
                        'avg_start_position': career['avg_start_position'],
                        'avg_finish_position': career['avg_finish_position'],
                        'laps': career['laps'],
                        'laps_led': career['laps_led'],
                        'avg_incidents': career['avg_incidents'],
                        'avg_points': career['avg_points'],
                        'win_percentage': career['win_percentage'],
                        'top5_percentage': career['top5_percentage'],
                        'laps_led_percentage': career['laps_led_percentage'],
                        'total_club_points': career['total_club_points'],
                    }
                )

                # Get Member's Career in each category
                careers = self.irclient.stats_member_yearly(export=_export)
                for career in careers['stats']:
                    category = Category.objects.get(id=int(career['category_id']))
                    new_member_career, created = Career.objects.update_or_create(
                        member=member_obj,
                        category=category,
                        year=career['year'],
                        defaults={
                            'starts': career['starts'],
                            'wins': career['wins'],
                            'top5': career['top5'],
                            'poles': career['poles'],
                            'avg_start_position': career['avg_start_position'],
                            'avg_finish_position': career['avg_finish_position'],
                            'laps': career['laps'],
                            'laps_led': career['laps_led'],
                            'avg_incidents': career['avg_incidents'],
                            'avg_points': career['avg_points'],
                            'win_percentage': career['win_percentage'],
                            'top5_percentage': career['top5_percentage'],
                            'laps_led_percentage': career['laps_led_percentage'],
                            'total_club_points': career['total_club_points'],
                        }
                    )

            # Update Recent Races
            recent_races = self.irclient.member_recent_races(export=_export)
            for race in recent_races['races']:
                member = member_obj
                track = Tracks.objects.get(track_id=int(race['track']['track_id']))
                car = Cars.objects.get(car_id=int(race['car_id']))
                series = Series.objects.get(series_id=int(race['series_id']))

                new_race, created = Races.objects.update_or_create(
                    subsession_id=race['subsession_id'],
                    defaults={
                        'member': member,
                        'track': track,
                        'car': car,
                        'series': series,
                        'license_level': race['license_level'],
                        'session_start_time': race['session_start_time'],
                        'winner_group_id': race['winner_group_id'],
                        'winner_name': race['winner_name'],
                        'winner_license_level': race['winner_license_level'],
                        'start_position': race['start_position'],
                        'finish_position': race['finish_position'],
                        'qualifying_time': race['qualifying_time'],
                        'laps': race['laps'],
                        'laps_led': race['laps_led'],
                        'incidents': race['incidents'],
                        'club_points': race['club_points'],
                        'points': race['points'],
                        'strength_of_field': race['strength_of_field'],
                        'old_sub_level': race['old_sub_level'],
                        'new_sub_level': race['new_sub_level'],
                        'oldi_rating': race['oldi_rating'],
                        'newi_rating': race['newi_rating']
                    }
                )

                #If the race has just been created then we also get the lap data.
                if created:
                    self.updateSessionResult(race['subsession_id'], True)
                    self.updateSessionEventLog(race['subsession_id'], simsession_number=0, _export=True)
                    self.updateSessionLapChartData(race['subsession_id'], True)
                    self.updateSessionLapData(race['subsession_id'], _export)

        except TypeError as e:
            print("updateMember - TypeError", e)
            return False

    def updateSeasons(self, season_year, season_quarter, _export=False):
        series = self.irclient.get_season_list(season_year, season_quarter, export=_export)

    def updateSeries(self, _export=False):

        Series.objects.all().update(show=False)
        series = self.irclient.get_series(export=_export)
        for serie in series:
            try:
                if serie.get("forum_url") is None:
                    serie['forum_url'] = ""

                category = Category.objects.get(id=serie['category_id'])
                new_serie, created = Series.objects.update_or_create(
                    series_id = serie['series_id'],
                    defaults={
                        "category": category,
                        "eligible": serie['eligible'],
                        "forum_url": serie['forum_url'],
                        "max_starters": serie['max_starters'],
                        "min_starters": serie['min_starters'],
                        "oval_caution_type": serie['oval_caution_type'],
                        "road_caution_type": serie['road_caution_type'],
                        "series_name": serie['series_name'],
                        "series_short_name": serie['series_short_name'],
                        "allowed_licenses": serie['allowed_licenses'],
                        "show": True
                    }
                )
            except KeyError as ke:
                print("updateSeries: Missing Keys", ke)

        self.irclient.get_series_assets(export=True)

    def updateTracks(self, _export=False):
        """ Updates the tracks database table """

        tracks = self.irclient.get_tracks(export=_export)
        for track in tracks:
            try:
                if track.get("config_name") is None:
                    track['config_name'] = "default"
                if track.get("price_display") is None:
                    track['price_display'] = "N/A"
                if track.get("first_sale") is None:
                    track['first_sale'] = None
                if track.get("pit_road_speed_limit") is None:
                    track['pit_road_speed_limit'] = -1
                if track.get("site_url") is None:
                    track['site_url'] = "Pending"
                category = Category.objects.get(id=track['category_id'])
                new_track, created = Tracks.objects.update_or_create(
                    track_id=track['track_id'],
                    defaults={
                        "ai_enabled": track['ai_enabled'],
                        "allow_pitlane_collisions": track['allow_pitlane_collisions'],
                        "allow_rolling_start": track['allow_rolling_start'],
                        "allow_standing_start": track['allow_standing_start'],
                        "award_exempt": track['award_exempt'],
                        "category": category,
                        "closes": track['closes'],
                        "config_name": track['config_name'],
                        "corners_per_lap": track['corners_per_lap'],
                        "created": track['created'],
                        "first_sale": track['first_sale'],
                        "free_with_subscription": track['free_with_subscription'],
                        "fully_lit": track['fully_lit'],
                        "grid_stalls": track['grid_stalls'],
                        "has_opt_path": track['has_opt_path'],
                        "has_short_parade_lap": track['has_short_parade_lap'],
                        "has_start_zone": track['has_start_zone'],
                        "has_svg_map": track['has_svg_map'],
                        "is_dirt": track['is_dirt'],
                        "is_oval": track['is_oval'],
                        "is_ps_purchasable": track['is_ps_purchasable'],
                        "lap_scoring": track['lap_scoring'],
                        "latitude": track['latitude'],
                        "location": track['location'],
                        "longitude": track['longitude'],
                        "max_cars": track['max_cars'],
                        "night_lighting": track['night_lighting'],
                        "nominal_lap_time": track['nominal_lap_time'],
                        "number_pitstalls": track['number_pitstalls'],
                        "opens": track['opens'],
                        "package_id": track['package_id'],
                        "pit_road_speed_limit": track['pit_road_speed_limit'],
                        "price": track['price'],
                        "price_display": track['price_display'],
                        "priority": track['priority'],
                        "purchasable": track['purchasable'],
                        "qualify_laps": track['qualify_laps'],
                        "restart_on_left": track['restart_on_left'],
                        "retired": track['retired'],
                        "search_filters": track['search_filters'],
                        "site_url": track['site_url'],
                        "sku": track['sku'],
                        "solo_laps": track['solo_laps'],
                        "start_on_left": track['start_on_left'],
                        "supports_grip_compound": track['supports_grip_compound'],
                        "tech_track": track['tech_track'],
                        "time_zone": track['time_zone'],
                        "track_config_length": track['track_config_length'],
                        "track_dirpath": track['track_dirpath'],
                        "track_name": track['track_name'],
                        "track_types": track['track_types'],
                    }
                )
            except KeyError as ke:
                print(ke)

        self.irclient.get_track_assets(export=True)

    ##### SESSION FUNCTIONS #####

    def updateSessionResult(self, subsession_id, _export=True):
        result_file = Path(settings.BASE_DIR, settings.FILE_FOLDER, "result_" + str(subsession_id) + ".json")
        if not result_file.is_file():
            print("UpdateSessionResult - Getting Data for ", result_file)
            raw_data = self.irclient.result(subsession_id, include_licenses=False, export=_export)
        else:
            raw_data = self.getJsonFile(result_file)
        return raw_data

    def updateSessionEventLog(self, subsession_id, simsession_number=0, _export=False):

        # Build the file path
        if simsession_number == 0:
            result_file = Path(settings.BASE_DIR, settings.FILE_FOLDER,
                               "result_event_log_" + str(subsession_id) + ".json")
        else:
            result_file = Path(settings.BASE_DIR, settings.FILE_FOLDER,
                               "result_event_log_" + str(subsession_id) + str(simsession_number) + ".json")

        if not result_file.is_file():
            print("UpdateSessionEventLog - Getting Data for ", result_file)
            raw_data = self.irclient.result_event_log(subsession_id=subsession_id, simsession_number=simsession_number, export=_export, result_file=result_file)
        else:
           raw_data = self.getJsonFile(result_file)
        return raw_data

    def updateSessionLapChartData(self, subsession_id, _export=True):
        result_file = Path(settings.BASE_DIR, settings.FILE_FOLDER, "result_lap_chart_data_" + str(subsession_id) + ".json")
        if not result_file.is_file():
            print("updateSessionLapChartData - Getting Data for ", result_file)
            raw_data = self.irclient.result_lap_chart_data(subsession_id, export=_export)

    def updateSessionLapData(self, subsession_id, _export=False):
        """ updateLapData is used by updateMember.
        If a new race is created then we will also get the lap data. """

        lap_data = self.irclient.result_lap_data(subsession_id, export=_export)
        for lap in lap_data:
            try:
                race = Races.objects.get(subsession_id=subsession_id)
                member = Member.objects.get(custid=self.custid)
                new_lap, created = Laps.objects.update_or_create(
                    race=race,
                    lap_number=lap['lap_number'],
                    member=member,
                    defaults={
                        "group_id": lap['group_id'],
                        "flags": lap['flags'],
                        "incident": lap['incident'],
                        "session_time": lap['session_time'],
                        "session_start_time": lap['session_start_time'],
                        "lap_time": lap['lap_time'],
                        "team_fastest_lap": lap['team_fastest_lap'],
                        "personal_best_lap": lap['personal_best_lap'],
                        "license_level": lap['license_level'],
                        "car_number": lap['car_number'],
                        "lap_events": lap['lap_events'],
                        "ai": lap['ai'],
                    }
                )
            except KeyError as ke:
                print("updateLaps: Missing Keys", ke)

    def updateLapDataPostInsert(self, subsession_id):
        self.updateSessionResult(subsession_id, True)
        self.updateSessionEventLog(subsession_id, True)
        self.updateSessionLapChartData(subsession_id, True)
        self.updateSessionLapData(subsession_id, False)

    ##### LEAGUE FUNCTIONS #####

    # Called by Leagues View
    def updateLeagueRegister(self, _export=False):
        raw_data = self.irclient.get_league_directory(restrict_to_member=True, export=_export)

        for league in raw_data['results_page']:
            try:
                if league.get("about") is None:
                    league['about'] = ""
                if league.get("url") is None:
                    league['url'] = ""
                new_league, created = Leagues.objects.update_or_create(
                    league_id=league['league_id'],
                    defaults={
                        "owner_id": league['owner_id'],
                        "league_name": league['league_name'],
                        "created": league['created'],
                        "about": league['about'],
                        "url": league['url'],
                        "roster_count": league['roster_count'],
                        "recruiting": league['recruiting'],
                        "is_admin": league['is_admin'],
                        "is_member": league['is_member'],
                        "pending_application": league['pending_application'],
                        "pending_invitation": league['pending_invitation'],
                    }
                )
            except KeyError as ke:
                print("updateLeagueRegister: Missing Keys", ke)

    # Called by updateLeagueData 1
    def updateLeagueRoster(self, league, _export=False):
        raw_data = self.irclient.league_get(league.league_id, include_licenses=False, export=_export)

        for driver in raw_data['roster']:
            driver_stats = self.irclient.member_profile(driver['cust_id'], export=_export)

            try:
                new_roster, created = LeagueRoster.objects.update_or_create(
                    league=league,
                    cust_id=driver['cust_id'],
                    defaults={
                        "display_name": driver['display_name'],
                        "owner": driver['owner'],
                        "admin": driver['admin'],
                        "league_mail_opt_out": driver['league_mail_opt_out'],
                        "league_pm_opt_out": driver['league_pm_opt_out'],
                        "league_member_since": driver['league_member_since'],
                        "car_number": driver['car_number'],
                        "nick_name": driver['nick_name'],
                        "category1_license_level": driver_stats['member_info']['licenses'][0]['license_level'],
                        "category1_irating": driver_stats['member_info']['licenses'][0]['irating'],
                        "category1_safety_rating": driver_stats['member_info']['licenses'][0]['safety_rating'],
                        "category1_cpi": driver_stats['member_info']['licenses'][0]['cpi'],
                        "category1_mpr_num_races": driver_stats['member_info']['licenses'][0]['mpr_num_races'],
                        "category1_tt_rating": driver_stats['member_info']['licenses'][0]['tt_rating'],
                        "category1_mpr_num_tts": driver_stats['member_info']['licenses'][0]['mpr_num_tts'],
                        "category1_group_id": driver_stats['member_info']['licenses'][0]['group_id'],
                        "category2_license_level": driver_stats['member_info']['licenses'][1]['license_level'],
                        "category2_irating": driver_stats['member_info']['licenses'][1]['irating'],
                        "category2_safety_rating": driver_stats['member_info']['licenses'][1]['safety_rating'],
                        "category2_cpi": driver_stats['member_info']['licenses'][1]['cpi'],
                        "category2_mpr_num_races": driver_stats['member_info']['licenses'][1]['mpr_num_races'],
                        "category2_tt_rating": driver_stats['member_info']['licenses'][1]['tt_rating'],
                        "category2_mpr_num_tts": driver_stats['member_info']['licenses'][1]['mpr_num_tts'],
                        "category2_group_id": driver_stats['member_info']['licenses'][1]['group_id'],
                        "category3_license_level": driver_stats['member_info']['licenses'][2]['license_level'],
                        "category3_irating": driver_stats['member_info']['licenses'][2]['irating'],
                        "category3_safety_rating": driver_stats['member_info']['licenses'][2]['safety_rating'],
                        "category3_cpi": driver_stats['member_info']['licenses'][2]['cpi'],
                        "category3_mpr_num_races": driver_stats['member_info']['licenses'][2]['mpr_num_races'],
                        "category3_tt_rating": driver_stats['member_info']['licenses'][2]['tt_rating'],
                        "category3_mpr_num_tts": driver_stats['member_info']['licenses'][2]['mpr_num_tts'],
                        "category3_group_id": driver_stats['member_info']['licenses'][2]['group_id'],
                        "category4_license_level": driver_stats['member_info']['licenses'][3]['license_level'],
                        "category4_irating": driver_stats['member_info']['licenses'][3]['irating'],
                        "category4_safety_rating": driver_stats['member_info']['licenses'][3]['safety_rating'],
                        "category4_cpi": driver_stats['member_info']['licenses'][3]['cpi'],
                        "category4_mpr_num_races": driver_stats['member_info']['licenses'][3]['mpr_num_races'],
                        "category4_tt_rating": driver_stats['member_info']['licenses'][3]['tt_rating'],
                        "category4_mpr_num_tts": driver_stats['member_info']['licenses'][3]['mpr_num_tts'],
                        "category4_group_id": driver_stats['member_info']['licenses'][3]['group_id'],
                    }
                )
            except KeyError as ke:
                print("updateLeagueData: Missing Roster Keys", ke)

    # Called by updateLeagueSeasons 1
    def updateLeagueSeasonSessions(self, league, season, _export=False):
        raw_data = self.irclient.league_season_sessions(league.league_id, season.season_id, results_only=False, export=_export)
        for session in raw_data['sessions']:
            self.createOrUpdateLeagueSession(league, season, session)

    # Called by updateLeagueSeasonSessions and updateLeagueSession
    def createOrUpdateLeagueSession(self, league, season, session, subsession_id=None):

        try:
            new_session, created = LeagueSessions.objects.update_or_create(
                league=league,
                season=season,
                league_season_id=session['league_season_id'],
                private_session_id=session['private_session_id'],
                defaults={
                    "cars": session.get('cars', ""),
                    "consec_cautions_single_file": session.get('consec_cautions_single_file', False),
                    "damage_model": session.get('damage_model', None),
                    "do_not_count_caution_laps": session.get('do_not_count_caution_laps', False),
                    "do_not_paint_cars": session.get('do_not_paint_cars', False),
                    "driver_changes": session.get('driver_changes', False),
                    "enable_pitlane_collisions": session.get('enable_pitlane_collisions', False),
                    "entry_count": session.get('entry_count', None),
                    "green_white_checkered_limit": session.get('green_white_checkered_limit', None),
                    "has_results": session.get('has_results', False),
                    "launch_at": session.get('launch_at', None),
                    "lone_qualify": session.get('lone_qualify', False),
                    "max_ai_drivers": session.get('max_ai_drivers', 0),
                    "must_use_diff_tire_types_in_race": session.get('must_use_diff_tire_types_in_race', False),
                    "no_lapper_wave_arounds": session.get('no_lapper_wave_arounds', False),
                    "num_opt_laps": session.get('num_opt_laps', None),
                    "pace_car_class_id": session.get('pace_car_class_id', None),
                    "pace_car_id": session.get('pace_car_id', None),
                    "password_protected": session.get('password_protected', False),
                    "practice_length": session.get('practice_length', None),
                    "qualify_laps": session.get('qualify_laps', None),
                    "qualify_length": session.get('qualify_length', None),
                    "race_laps": session.get('race_laps', None),
                    "race_length": session.get('race_length', None),
                    "short_parade_lap": session.get('short_parade_lap', False),
                    "start_on_qual_tire": session.get('start_on_qual_tire', False),
                    "start_zone": session.get('start_zone', False),
                    "status": session.get('status', None),
                    "team_entry_count": session.get('team_entry_count', None),
                    "telemetry_force_to_disk": session.get('telemetry_force_to_disk', None),
                    "telemetry_restriction": session.get('telemetry_restriction', None),
                    "time_limit": session.get('time_limit', None),
                    "track_id": session['track'].get('track_id', None),
                    "track_name": session['track'].get('track_name', ""),
                    "track_state": session.get('track_state', ""),
                    "weather": session.get('weather', ""),
                }
            )

        except KeyError as ke:
            print("createOrUpdateLeagueSession: Missing Session Keys", ke)

    # Called by updateLeagueSeasons 2
    def updateLeagueSeasonStandings(self, league, season, _export=True):
        raw_data = self.irclient.league_season_standings(league.league_id, season.season_id, export=_export)
        # self.printRawData("updateSeasonStandings", raw_data)

    # Called by updateLeagueData 2
    def updateLeagueSeasons(self, league, _export=False):
        raw_data = self.irclient.league_seasons(league.league_id, retired=False, export=_export)
        for season in raw_data['seasons']:
            try:
                new_season, created = LeagueSeasons.objects.update_or_create(
                    league=league,
                    season_id=season['season_id'],
                    defaults={
                        "points_system_id": season['points_system_id'],
                        "season_name": season['season_name'],
                        "active": season['active'],
                        "hidden": season['hidden'],
                        "no_drops_on_or_after_race_num": season['no_drops_on_or_after_race_num'],
                        "points_cars": season['points_cars'],
                        "driver_points_car_classes": season['driver_points_car_classes'],
                        "points_system_name": season['points_system_name'],
                        "points_system_desc": season['points_system_desc'],
                    }
                )
                self.updateLeagueSeasonSessions(league, new_season, True)
                self.updateLeagueSeasonStandings(league, new_season, _export)
            except KeyError as ke:
                print("updateLeagueData: Missing Session Keys", ke)

    # Called by updateLeagueData 3
    def updateLeaguePointSystem(self, league, _export=False):
        raw_data = self.irclient.league_get_points_systems(league.league_id, season_id=None, export=_export)
        for system in raw_data['points_systems']:

            if system['league_id'] != league.league_id:
                temp_league = None
            else:
                temp_league = league

            try:
                new_system, created = LeaguePoints.objects.update_or_create(
                    points_system_id=system['points_system_id'],
                    defaults={
                        "league": temp_league,
                        "name": system['name'],
                        "description": system['description'],
                        "retired": system['retired'],
                        "iracing_system": system['iracing_system'],
                    }
                )
            except KeyError as ke:
                print("updatePointSystem: Missing Points Keys", ke)

    # Called by league season view to update standings.
    def updateLeagueSeason(self, season):
        scoring = scoringClient()
        scoring.calculateSeasonStandings(season)

    # Called by league detail view
    def updateLeagueData(self, league, _export=False):
        self.updateLeagueRoster(league, False)
        self.updateLeagueSeasons(league, _export)
        self.updateLeaguePointSystem(league, _export)

    # Called by Session detail view
    def updateLeagueSession(self, leaguesession):

        # Get all the hosted races for the league from iRacing
        result_hosted = self.irclient.result_search_hosted(host_cust_id=leaguesession.league.owner_id, league_id=leaguesession.league.league_id, track_id=leaguesession.track_id, export=False)

        # Find the race that matches the private session ID and has a heat race as true
        session = next((item for item in result_hosted if item["private_session_id"] == leaguesession.private_session_id and item['heat_race'] == True), None)

        if session == None:
            return None

        # Update the League Session in our database
        leaguesession.subsession_id = session['subsession_id']
        leaguesession.save()

        # Update the Session Result in our database
        result_data = self.updateSessionResult(session['subsession_id'])
        #self.printRawData("Result Data", result_data)

        #Store the data processing the scores.
        scoring = scoringClient(result_data)
        results = scoring.updateScores()

        # Return the Sub Session ID
        return session['subsession_id']

    # Test Function
    def testFunction(self, _export=False):
        raw_data = self.irclient.result_search_hosted(host_cust_id=227267, league_id=9417, export=_export)
        self.printRawData("Test Function", raw_data)
