#
#    Copyright (c) Dec 2022 Chris Davies <chris@byteinsight.co.uk>
#
#    Credit to Jason Dilworth for https://github.com/jasondilworth56/iracingdataapi which I started with.
#
#    I have added potential for export to JSON and try/catch statements
#    which allow for greater reliability within wider applications.
#
"""Main entrance point for iracinginsight."""
import base64
import hashlib
import os
from http.cookiejar import LWPCookieJar
from pathlib import Path
import datetime
import requests
import json

class iRacingClient():
    """
    run iracinginsight as an unattended program
    """

    debug = False
    global_cust_id = None

    def __init__(self, _username, _password, _cust_id, _hive_root=None, _files_folder=None):
        """The init function sets up:
        :param None
        :return: None
        """
        self.authenticated = False
        self.session = requests.Session()
        self.base_url = "https://members-ng.iracing.com"

        self.username = _username
        self.encoded_password = self._encode_password(_username, _password)
        self.global_cust_id = _cust_id

        self.hive_root = _hive_root
        self.files_folder = _files_folder

    ##### PRIVATE CLASS Functions #####

    # From iracing client api
    def _encode_password(self, username, password):
        initial_hash = hashlib.sha256((password + username.lower()).encode('utf-8')).digest()
        return base64.b64encode(initial_hash).decode('utf-8')

    # From iracing client api
    def _login(self, cookie_file=None):

        self.printData("Authenticating with iRacing")
        if cookie_file:
            self.session.cookies = LWPCookieJar(cookie_file)
            if not os.path.exists(cookie_file):
                self.session.cookies.save()
            else:
                self.session.cookies.load(ignore_discard=True)
        headers = {'Content-Type': 'application/json'}
        data = {"email": self.username, "password": self.encoded_password}

        try:
            r = self.session.post('https://members-ng.iracing.com/auth', headers=headers, json=data, timeout=5.0)
        except requests.Timeout:
            raise RuntimeError("Login timed out")
        except requests.ConnectionError:
            raise RuntimeError("Connection error")
        else:
            response_data = r.json()
            if r.status_code == 200 and response_data['authcode']:
                if cookie_file:
                    self.session.cookies.save(ignore_discard=True)
                self.authenticated = True
                return "Logged in"
            else:
                raise RuntimeError("Error from iRacing: ", response_data)

    # From iracing client api
    def _build_url(self, endpoint):
        return self.base_url + endpoint

    # From iracing client api
    def _get_resource_or_link(self, url, payload=None):
        if not self.authenticated:
            self._login()
            return self._get_resource_or_link(url, payload=payload)

        r = self.session.get(url, params=payload)

        if r.status_code == 401:
            # unauthorised, likely due to a timeout, retry after a login
            self.authenticated = False

        if r.status_code != 200:
            raise RuntimeError(r.json())
        data = r.json()
        if not isinstance(data, list) and "link" in data.keys():
            return [data["link"], True]
        else:
            return [data, False]

    # From iracing client api
    def _get_resource(self, endpoint, payload=None):
        request_url = self._build_url(endpoint)
        resource_obj, is_link = self._get_resource_or_link(request_url, payload=payload)
        if not is_link:
            return resource_obj
        r = self.session.get(resource_obj)
        if r.status_code != 200:
            raise RuntimeError(r.json())
        return r.json()

    # From iracing client api
    def _get_chunks(self, chunks):
        base_url = chunks["base_download_url"]
        urls = [base_url + x for x in chunks["chunk_file_names"]]
        list_of_chunks = [self.session.get(url).json() for url in urls]
        output = [item for sublist in list_of_chunks for item in sublist]

        return output

    ##### BUILDER Functions #####

    # Tries to get a cust_id and falls back on self.cust_id.
    # Raises Runtime if none exist.
    def getCustID(self, cust_id):
        if not cust_id:
            if self.global_cust_id:
                return self.global_cust_id
            else:
                raise RuntimeError("Please supply a cust_id")
        return cust_id

    def printData(self, data):
        try:
            if self.debug:
                print(data)
        except UnicodeEncodeError as uee:
            print("printData", uee)

    def rawToJson(self, file_name, raw_data):
        export_path = os.path.join(self.hive_root, self.files_folder)
        Path(export_path).mkdir(parents=True, exist_ok=True)
        try:
            full_path = os.path.join(self.hive_root, self.files_folder, file_name)
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, ensure_ascii=False, indent=4)
        except UnicodeEncodeError as uee:
            print("rawToJson - UnicodeEncodeError", uee)
            print(full_path)
        except PermissionError as pe:
            print("rawToJson - PermissionError", pe)
            print(full_path)

    ##### API Query Functions #####

    ##### CARS #####

    #  Car Assets
    def get_cars_assets(self, export=False):
        """
        :link https://members-ng.iracing.com/data/car/assets
        :expirationSeconds 900
        :note image paths are relative to https://images-static.iracing.com/
        :param export: boolean should the file be exported to JSON
        :return: dict All data retrieved is returned.
        """
        try:
            raw_data = self._get_resource("/data/car/assets")

        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            self.rawToJson('cars_assets.json', raw_data)
        return raw_data

    # Car Get
    def get_cars(self, export=False):
        """
        :link https://members-ng.iracing.com/data/car/get
        :expirationSeconds 900
        :param export: boolean should the file be exported to JSON
        :return: dict All data retrieved is returned.
        """
        try:
            raw_data = self._get_resource("/data/car/get")

        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            self.rawToJson('cars.json', raw_data)
        return raw_data

    # CarClass
    def get_carclass(self, export=False):
        """
         :link https://members-ng.iracing.com/data/carclass/get
         :expirationSeconds 900
         :param export: boolean should the file be exported to JSON
         :return: dict All data retrieved is returned.
         """
        try:
            raw_data = self._get_resource("/data/carclass/get")

        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            export_path = os.path.join(self.hive_root, self.files_folder, 'carclass.json')
            self.rawToJson(export_path, raw_data)
        return raw_data

    ##### CONSTANTS #####

    ##### HOSTED #####

    ##### LEAGUE ACTIONS #####

    # cust_league_sessions
    def league_cust_league_sessions(self, mine=False, package_id=None, export=False):
        """
        :link https://members-ng.iracing.com/data/league/cust_league_sessions
        :expirationSeconds 900
        :param mine: (boolean) If true, return only sessions created by this user.
        :param package_id: (number) If set, return only sessions using this car or track package ID.
        :param export: boolean should the file be exported to JSON
        :return: dict All data retrieved is returned.
        """
        try:
            payload = {"mine": mine}
            if package_id:
                payload["package_id"] = package_id
            raw_data = self._get_resource("/data/league/cust_league_sessions", payload=payload)
        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            filename = "league_cust_league_sessions.json"
            self.rawToJson(filename, raw_data)

    # directory
    def get_league_directory(self, search="", tag="", restrict_to_member=False, restrict_to_recruiting=False,
                         restrict_to_friends=False, restrict_to_watched=False, minimum_roster_count=0,
                         maximum_roster_count=999, lowerbound=1, upperbound=None, sort=None, order="asc", export=False):
        """
        :link https://members-ng.iracing.com/data/league/directory
        :expirationSeconds 900
        :param search: (string) Will search against league name, description, owner, and league ID.
        :param tag: (string) One or more tags, comma-separated.
        :param restrict_to_member: (boolean) If true include only leagues for which customer is a member.
        :param restrict_to_recruiting:(boolean) If true include only leagues which are recruiting.
        :param restrict_to_friends: (boolean) If true include only leagues owned by a friend.
        :param restrict_to_watched: (boolean) If true include only leagues owned by a watched member.
        :param minimum_roster_count:(number) If set include leagues with at least this number of members.
        :param maximum_roster_count: (number) If set include leagues with no more than this number of members.
        :param lowerbound: (number) First row of results to return. Defaults to 1.
        :param upperbound:(number) Last row of results to return. Defaults to lowerbound + 39.
        :param sort: (string) One of relevance, leaguename, displayname, rostercount. displayname is owners's name. Defaults to relevance.
        :param order: (string) One of asc or desc. Defaults to asc.
        :param export: boolean should the file be exported to JSON
        :return: dict All data retrieved is returned.
        """
        try:
            params = locals()
            payload = {}
            for x in params.keys():
                if x != "self":
                    payload[x] = params[x]
            raw_data = self._get_resource("/data/league/directory", payload=payload)
        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            self.rawToJson('league_directory.json', raw_data)
        return raw_data

    # get
    def league_get(self, league_id=None, include_licenses=False, export=False):
        """
        :link https://members-ng.iracing.com/data/league/get
        :expirationSeconds 900
        :param league_id: (number)
        :param include_licenses: (boolean) For faster responses, only request when necessary.
        :param export: boolean should the file be exported to JSON
        :return: dict All data retrieved is returned.
        """
        try:
            if not league_id:
                raise RuntimeError("Please supply a league_id")
            payload = {"league_id": league_id, "include_licenses": include_licenses}
            raw_data = self._get_resource("/data/league/get", payload=payload)
        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            filename = "league_" + str(league_id) + ".json"
            self.rawToJson(filename, raw_data)
        return raw_data

    # get_points_systems
    def league_get_points_systems(self, league_id, season_id=None, export=False):
        """
        :link https://members-ng.iracing.com/data/league/get_points_systems
        :expirationSeconds 900
        :param league_id: (number)
        :param season_id: (number) If included and the season is using custom points (points_system_id:2) then the custom points option is included in the returned list. Otherwise the custom points option is not returned.
        :param export: boolean should the file be exported to JSON
        :return: dict All data retrieved is returned.
        """
        try:
            payload = {"league_id": league_id}
            raw_data = self._get_resource("/data/league/get_points_systems", payload=payload)
        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            filename = "league_points_systems_%d.json" % (league_id)
            self.rawToJson(filename, raw_data)
        return raw_data

    # membership

    # seasons
    def league_seasons(self, league_id, retired=False, export=False):
        """
        :link https://members-ng.iracing.com/data/league/seasons
        :expirationSeconds 900
        :param league_id: (number)
        :param export: boolean should the file be exported to JSON
        :return: dict All data retrieved is returned.
        """
        try:
            payload = {"league_id": league_id, "retired": retired}
            raw_data = self._get_resource("/data/league/seasons", payload=payload)
        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            filename = "league_seasons_" + str(league_id) + ".json"
            self.rawToJson(filename, raw_data)
        return raw_data

    # season_standings
    def league_season_standings(self, league_id, season_id, car_class_id=None, car_id=None, export=False):
        """
        :link https://members-ng.iracing.com/data/league/season_standings
        :expirationSeconds 900
        :param league_id: (number)
        :param season_id: (number)
        :param car_class_id: (number)
        :param car_id: (number)
        :param export: boolean should the file be exported to JSON
        :return: dict All data retrieved is returned.
        """
        try:
            payload = {"league_id": league_id, "season_id": season_id}
            if car_class_id:
                payload["car_class_id"] = car_class_id
            if car_id:
                payload["car_id"] = car_id
            raw_data = self._get_resource("/data/league/season_standings", payload=payload)
        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            filename = "league_season_standings_%d_%d.json" % (league_id, season_id)
            self.rawToJson(filename, raw_data)

        return raw_data

    # season_sessions
    def league_season_sessions(self, league_id, season_id, results_only=False, export=False):
        """
        :link https://members-ng.iracing.com/data/league/season_sessions
        :expirationSeconds 900
        :param league_id: (number)
        :param season_id: (number)
        :param results_only:
        :param export: boolean should the file be exported to JSON
        :return: dict All data retrieved is returned.
        """
        try:
            payload = {
                "league_id": league_id,
                "season_id": season_id,
                "results_only": results_only,
            }
            raw_data = self._get_resource("/data/league/season_sessions", payload=payload)
        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            filename = "league_season_sessions_%d_%d.json" %(league_id, season_id)
            self.rawToJson(filename, raw_data)
        return raw_data

    ##### LOOKUP #####

    ##### MEMBER #####

    # awards

    # chart_data
    def member_chart_data(self, cust_id=None, category_id=2, chart_type=1, export=False):
        """ Member Chart Data returns a two point dictionary that can be used to plot data.
        :param cust_id - If none returns that for the login?
        :param category_id - Road, Oval etc as a number
        :param chart_type ?
        :param export - export a json file with the name member_chart_data_category_chart.json
        :return dictionary
        """
        cust_id = self.getCustID(cust_id)

        try:

            payload = {"category_id": category_id, "chart_type": chart_type}
            if cust_id:
                payload["cust_id"] = cust_id

            raw_data = self._get_resource("/data/member/chart_data", payload=payload)

        except RuntimeError as e:
            print("Check User ID")
            return None

        if export:
            filename = 'member_chart_data_%d_cat%d_chart%d.json' % (cust_id, category_id, chart_type)
            self.rawToJson(filename, raw_data['data'])
        return raw_data

    # get
    def member_get(self, cust_id=None, include_licenses=False, export=False):
        """
        :link - https://members-ng.iracing.com/data/member/get
        :expirationSeconds - 900
        :param cust_id: number - required - note": "?cust_ids=2,3,4
        :param include_licenses: boolean
        :param export: boolean - export to json
        :return:
        """

        cust_id = self.getCustID(cust_id)

        try:
            payload = {"cust_ids": cust_id, "include_licenses": include_licenses}
            raw_data = self._get_resource("/data/member/get", payload=payload)

        except RuntimeError as e:
            print("Check User ID")
            return None

        if export:
            filename = "member_" + str(cust_id) + ".json"
            self.rawToJson(filename, raw_data)
        return raw_data

    # info
    def member_info(self, cust_id=None, export=False):
        """
        Always the authenticated member.

        @todo is custid required?

        :link https://members-ng.iracing.com/data/member/info
        :expirationSeconds	900
        :param cust_id:
        :param export: boolean should the file be exported to JSON
        :return: dict All data retrieved is returned.
        """

        cust_id = self.getCustID(cust_id)
        try:
            payload = {"cust_id": cust_id}
            raw_data = self._get_resource("/data/member/info", payload=payload)

        except RuntimeError as e:
            print("Check User ID")
            return None

        if export:
            filename = "member_info_" + str(cust_id) + ".json"
            self.rawToJson(filename, raw_data)
        return raw_data

    # participation credits
    """
    Always the authenticated member.
    
    :link	https://members-ng.iracing.com/data/member/participation_credits
    :expirationSeconds	900
    """

    # profile
    def member_profile(self, cust_id=None, export=False):
        """
        :link	https://members-ng.iracing.com/data/member/profile
        :expirationSeconds	900
        :param cust_id: (number) Defaults to the authenticated member.
        :param export: boolean should the file be exported to JSON
        :return: dict All data retrieved is returned.
        """

        cust_id = self.getCustID(cust_id)
        try:
            payload = {"cust_id": cust_id}
            raw_data = self._get_resource("/data/member/profile", payload=payload)

        except RuntimeError as e:
            print("Check User ID")
            return None

        if export:
            filename = "member_profile_" + str(cust_id) + ".json"
            self.rawToJson(filename, raw_data)
        return raw_data

    ##### RESULTS #####

    # get
    def result(self, subsession_id=None, include_licenses=False, export=False):
        """
        Get the results of a subsession, if authorized to view them. series_logo image paths are relative to https://images-static.iracing.com/img/logos/series/
        :link https://members-ng.iracing.com/data/results/get
        :param subsession_id: (number)
        :param include_licenses: (boolean)
        :param export: boolean should the file be exported to JSON
        :return: dict All data retrieved is returned.
        """

        if not subsession_id:
            raise RuntimeError("Please supply a subsession_id")

        try:
            payload = {
                "subsession_id": subsession_id,
                "include_licenses": include_licenses}

            raw_data = self._get_resource("/data/results/get", payload=payload)
            self.printData(raw_data)

        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            filename = "result_" + str(subsession_id) + ".json"
            self.rawToJson(filename, raw_data)

        return raw_data

        # dictionary of the lap data for the given sub session id.

    # event_log
    def result_event_log(self, subsession_id=None, simsession_number=0, export=False, result_file=None):
        """
        Returns a dictionary of the lap data for the given sub session id
        :link https://members-ng.iracing.com/data/results/event_log
        :param subsession_id: (number)
        :param simsession_number: (number) The main event is 0; the preceding event is -1, and so on.
        :param export: boolean should the file be exported to JSON
        :param result_file: string
        :return: dict All data retrieved is returned.
        """
        """"""

        if not subsession_id:
            raise RuntimeError("Please supply a subsession_id")

        try:
            payload = {
                "subsession_id": subsession_id,
                "simsession_number": simsession_number,
            }

            raw_data = self._get_resource("/data/results/event_log", payload=payload)

        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        if export and result_file:
            chunks = self._get_chunks(raw_data["chunk_info"])
            self.rawToJson(result_file, chunks)

        return chunks

    # lap_chart_data
    def result_lap_chart_data(self, subsession_id=None, simsession_number=0, export=False):
        """
        Returns a dictionary of the lap data for the given sub session id
        :link https://members-ng.iracing.com/data/results/lap_chart_data
        :param subsession_id: (number)
        :param simsession_number: (number) The main event is 0; the preceding event is -1, and so on.
        :param export: boolean should the file be exported to JSON
        :return: dict All data retrieved is returned.
        """

        if not subsession_id:
            raise RuntimeError("Please supply a subsession_id")

        try:
            payload = {
                "subsession_id": subsession_id,
                "simsession_number": simsession_number,
            }

            raw_data = self._get_resource("/data/results/lap_chart_data", payload=payload)
            self.printData(raw_data)

        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            filename = "result_lap_chart_data_" + str(subsession_id) + ".json"
            chunks = self._get_chunks(raw_data["chunk_info"])
            self.rawToJson(filename, chunks)

        return chunks

        # dictionary of the event/incident data for the given sub session id.

    # lap_data
    def result_lap_data(self, subsession_id=None, simsession_number=0, cust_id=None, team_id=None, export=False):
        """
        Returns a dictionary of the lap data for the given sub session id
        :link https://members-ng.iracing.com/data/results/lap_data
        :param subsession_id: (number)
        :param simsession_number: (number) The main event is 0; the preceding event is -1, and so on.
        :param cust_id: (number) Required if the subsession was a single-driver event. Optional for team events.
            If omitted for a team event then the laps driven by all the team's drivers will be included.
        :param team_id: (number) Required if the subsession was a team event.
        :param export: boolean should the file be exported to JSON
        :return: dict All data retrieved is returned.
        """

        if not subsession_id:
            raise RuntimeError("Please supply a subsession_id")

        try:
            payload = {
                "subsession_id": subsession_id,
                "simsession_number": simsession_number,
            }
            if team_id:
                payload["team_id"] = team_id
            else:
                payload["cust_id"] = self.getCustID(cust_id)

            raw_data = self._get_resource("/data/results/lap_data", payload=payload)
            chunks = self._get_chunks(raw_data["chunk_info"])

        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            filename = "result_lap_data_" + str(subsession_id) + ".json"
            self.rawToJson(filename, chunks)

        return chunks

    # search_hosted
    def result_search_hosted(self, start_range_begin=None, start_range_end=None, finish_range_begin=None,
                             finish_range_end=None, cust_id=None, host_cust_id=None, session_name=None, league_id=None,
                             league_season_id=None, car_id=None, track_id=None, category_ids=None, export=False):

        """

        Hosted and league sessions.
        Maximum time frame of 90 days. Results split into one or more files with chunks of results.
        For scraping results the most effective approach is to keep track of the maximum end_time found during a
        search then make the subsequent call using that date/time as the finish_range_begin and skip any subsessions
        that are duplicated.  Results are ordered by subsessionid which is a proxy for start time.
        Requires one of: start_range_begin, finish_range_begin.
        Requires one of: cust_id, host_cust_id, session_name.
        :link https://members-ng.iracing.com/data/results/search_hosted
        :expirationSeconds in 900
        :param start_range_begin: string - Session start times. ISO-8601 UTC time zero offset: 2022-04-01T15:45Z.
        :param start_range_end: string - ISO-8601 UTC time zero offset: 2022-04-01T15:45Z. Exclusive. May be omitted if start_range_begin is less than 90 days in the past.
        :param finish_range_begin: string - Session finish times. ISO-8601 UTC time zero offset: 2022-04-01T15:45Z\.
        :param finish_range_end: string - ISO-8601 UTC time zero offset: 2022-04-01T15:45Z. Exclusive. May be omitted if finish_range_begin is less than 90 days in the past.
        :param cust_id: number - The participant's customer ID.
        :param host_cust_id: number - The host's customer ID.
        :param session_name: string - Part or all of the session's name.
        :param league_id: number - Include only results for the league with this ID.
        :param league_season_id: number - Include only results for the league season with this ID.
        :param car_id: number - One of the cars used by the session.
        :param track_id: number - The ID of the track used by the session.
        :param category_ids: numbers - Track categories to include in the search.  Defaults to all. ?category_ids=1,2,3,4
        :param export: boolean - export to json
        :return:
        """
        try:

            # Default to 90 days ago if no date set
            if not (start_range_begin or finish_range_begin):
                tod = datetime.datetime.now()
                d = datetime.timedelta(days=30)
                start_range_begin = (tod - d).replace(second=0).replace(microsecond=0).replace(tzinfo=datetime.timezone.utc).isoformat()

            if not (cust_id or host_cust_id):
                raise RuntimeError("Please supply either cust_id or host_cust_id")

            params = locals()
            payload = {}
            for x in params.keys():
                if x != "self" and params[x]:
                    payload[x] = params[x]

            raw_data = self._get_resource("/data/results/search_hosted", payload=payload)
            chunks = self._get_chunks(raw_data["data"]["chunk_info"])

        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            filename = "result_search_hosted.json"
            self.rawToJson(filename, chunks)

        return chunks

    # search_series
    """
        Official series. Maximum time frame of 90 days. Results split into one or more files with chunks of results. 
        For scraping results the most effective approach is to keep track of the maximum end_time found during a search 
        then make the subsequent call using that date/time as the finish_range_begin and skip any subsessions that are 
        duplicated. 

        Results are ordered by subsessionid which is a proxy for start time but groups together multiple splits of a 
        series when multiple series launch sessions at the same time. 

        Requires at least one of: season_year and season_quarter, start_range_begin, finish_range_begin.
    """

    # season_results

    ##### SEASON #####

    # list
    def get_season_list(self, season_year, season_quarter, export=False):
        """
        :link https://members-ng.iracing.com/data/season/list
        :param season_year: (number)
        :param season_quarter: (number)
        :param export: boolean should the file be exported to JSON
        :return: dict All data retrieved is returned.
        """
        try:
            payload = {"season_year": season_year, "season_quarter": season_quarter}
            raw_data = self._get_resource("/data/season/list", payload=payload)

        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        except ConnectionError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            filename = "season_list_%d_%d.json" % (season_year, season_quarter)
            self.rawToJson(filename, raw_data)
        return raw_data

    # race_guide

    ##### SERIES #####

    # assets
    def get_series_assets(self, export=False):
        """
        image paths are relative to https://images-static.iracing.com/
        :link	https://members-ng.iracing.com/data/series/assets
        :expirationSeconds	900
        :param export: boolean - export to json
        :return: dictionary
        """
        try:
            raw_data = self._get_resource("/data/series/assets")

        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            self.rawToJson('series_assets.json', raw_data)
        return raw_data

    # get
    def get_series(self, export=False):
        """
        :link	https://members-ng.iracing.com/data/series/get
        :expirationSeconds	900
        :param export: boolean should the file be exported to JSON
        :return: dict All data retrieved is returned.
        """
        try:
            raw_data = self._get_resource("/data/series/get")

        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            self.rawToJson('series.json', raw_data)
        return raw_data

    # past_seasons

    # seasons
    def series_seasons(self, include_series=False, export=False):
        """
        :link	https://members-ng.iracing.com/data/series/seasons
        :expirationSeconds	900
        :param include_series:
        :param export: boolean should the file be exported to JSON
        :return: dict All data retrieved is returned.
        """
        try:
            payload = {"include_series": include_series}
            raw_data = self._get_resource("/data/series/seasons", payload=payload)

        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        except ConnectionError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            self.rawToJson('series_seasons.json', raw_data)
        return raw_data

    # stats_series

    ##### STATS #####

    # member_bests

    # member_career
    def stats_member_career(self, cust_id=None, export=False):
        """
        Returns a summary dictionary of the member stats for each year of participation
        Empty categories are excluded.

        :link	https://members-ng.iracing.com/data/stats/member_career
        :expirationSeconds	900
        :param cust_id: (number) Defaults to the authenticated member.
        :param export: boolean should the file be exported to JSON
        :return: dict All data retrieved is returned.
        """
        """ """

        cust_id = self.getCustID(cust_id)
        try:
            payload = {"cust_id": cust_id}
            raw_data = self._get_resource("/data/stats/member_career", payload=payload)

        except RuntimeError as e:
            print("Check User ID")
            return None

        if export:
            filename = "member_stats_career_" + str(cust_id) + ".json"
            self.rawToJson(filename, raw_data['stats'])
        return raw_data

    # member_division

    # recent_races
    def member_recent_races(self, cust_id=None, export=False):
        """ Returns a summary dictionary of the member stats for each year category."""

        cust_id = self.getCustID(cust_id)
        try:
            payload = {"cust_id": cust_id}
            raw_data = self._get_resource("/data/stats/member_recent_races", payload=payload)
        except RuntimeError as e:
            print("Check User ID")
            return None

        if export:
            filename = "member_recent_races_" + str(cust_id) + ".json"
            self.rawToJson(filename, raw_data['races'])
        return raw_data

    # member_summary
    def stats_member_summary(self, cust_id=None, export=False):
        """ Returns a summary dictionary of the members stats
        :param cust_id int iRacing cust_id as found in the profile.
        :returns dictionary {'this_year': {'num_official_sessions': x, 'num_league_sessions': x, 'num_official_wins': x, 'num_league_wins': x}, 'cust_id': cust_id}
        """
        cust_id = self.getCustID(cust_id)
        try:
            payload = {"cust_id": cust_id}
            raw_data = self._get_resource("/data/stats/member_summary", payload=payload)

        except RuntimeError as e:
            print("Check User ID")
            return None

        if export:
            filename = "member_stats_summary_" + str(cust_id) + ".json"
            self.rawToJson(filename, raw_data)
        return raw_data

    # member_yearly
    def stats_member_yearly(self, cust_id=None, export=False):
        """ Returns a summary dictionary of the member stats for each year category."""

        cust_id = self.getCustID(cust_id)
        try:
            payload = {"cust_id": cust_id}
            raw_data = self._get_resource("/data/stats/member_yearly", payload=payload)

        except RuntimeError as e:
            print("Check User ID")
            return None

        if export:
            filename = "member_stats_yearly_" + str(cust_id) + ".json"
            self.rawToJson(filename, raw_data['stats'])
        return raw_data

    # season_driver_standings

    # season_supersession_standings

    # season_team_standings

    # season_tt_standings

    # season_tt_results

    # season_qualify_results

    # world_records

    ##### TEAM #####

    # get

    ##### TIME ATTACK #####

    # member_season_results

    ##### TRACK #####

    # assets
    def get_track_assets(self, export=False):
        """
        image paths are relative to https://images-static.iracing.com/
        :link	https://members-ng.iracing.com/data/track/assets
        :expirationSeconds	900
        :param export: boolean - export to json
        :return: dictionary
        """
        try:
            raw_data = self._get_resource("/data/track/assets")

        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            self.rawToJson('track_assets.json', raw_data)
        return raw_data

    # get
    def get_tracks(self, export=False):
        """
        :link	https://members-ng.iracing.com/data/track/get
        :expirationSeconds	900
        :param export: boolean export to json.
        :return:
        """
        try:
            raw_data = self._get_resource("/data/track/get")
            self.get_track_assets(export)

        except RuntimeError as e:
            print("Check Resource call", str(e))
            return None

        if export:
            self.rawToJson('track_get.json', raw_data)
        return raw_data

