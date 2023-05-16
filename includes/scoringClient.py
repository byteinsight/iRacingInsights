"""
This is a scoring class.

simsession_type 3 = open practice
simsession_type 5 = open qualifying
simsession_type 6 = race

Note about Podium positions.   System counts from 0 so 0=1st, 1=2nd and 2=3rd.

"""
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Sum

import pandas as pd
import os
import json
import math

from irstats.models import LeagueSeasonStandings, LeagueSessionResults, LeagueSessionSimsession

class scoringClient():

    results = None

    # FIA Standard Points
    # 1st:25 point, 2nd:18 points, 3rd:15 points, 4th:12 points, 5th:10 points
    # 6th:8 points, 7th:6 points, 8th:4 points, 9th:2 points, 10th:1 point
    fia_race = {0: 25, 1: 18, 2: 15, 3: 12, 4: 10, 5: 8, 6: 6, 7: 4, 8: 2, 9: 1}

    # Bonus Point - Fastest Lap
    fast_lap_bonus = 1
    outside_podium = True

    # Clean Race Bonus
    booti_point = 3

    # Qualifying
    # 1st:3 point, 2nd:2 points, 3rd:1 point,
    bonus_quali = {0: 3, 1: 2, 2: 1}

    finalSessionID = 99

    def __init__(self, _results=None):
        self.results = _results
        self.hive_root = settings.BASE_DIR
        self.files_folder = settings.FILE_FOLDER

    def printRawData(self, title, raw_data=None):
        if raw_data is not None:
            print(str(title).encode('cp1252', errors='replace').decode('cp1252'))
            print(str(raw_data).encode('cp1252', errors='replace').decode('cp1252'))
        else:
            print(str(title).encode('cp1252', errors='replace').decode('cp1252'))

    def rawToJson(self):

        filename = self.filename.replace(".json", "_complete.json")
        export_path = os.path.join(self.hive_root, self.files_folder, filename)

        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=4)
        except UnicodeEncodeError as uee:
            print("rawToJson - UnicodeEncodeError", uee)
        except PermissionError as pe:
            print("rawToJson - PermissionError", pe)

    def updateScores(self):

        league_id = self.results['league_id']
        season_id = self.results['league_season_id']
        session_id = self.results['subsession_id']

        for simsession in self.results['session_results']:
            simsession_number = simsession.get('simsession_number', None)

            # Create a simsession entry
            new_simsession, created = LeagueSessionSimsession.objects.update_or_create(
                league_id=league_id,
                season_id=season_id,
                session_id=session_id,
                simsession_number=simsession_number,
                defaults={
                    "simsession_type": simsession.get('simsession_type', None),
                    "simsession_type_name": simsession.get('simsession_type_name', None),
                    "simsession_subtype": simsession.get('simsession_subtype', None),
                    "simsession_name": simsession.get('simsession_name', None),
            })


            if simsession['simsession_type'] == 5:
                self.scoreQualifying(simsession)

            elif simsession['simsession_type'] == 6:
                self.scoreRace(simsession)
                self.setFastLap(session_id, simsession_number)
            else:
                self.scorePractice(simsession)


        # Calculate the overall session results
        self.createFinalSimSessionEntry(league_id, season_id, session_id)
        results = LeagueSessionResults.objects.all().filter(session_id=session_id)
        finals = self.calculateFinalScores(results)
        self.saveFinalSessionToDatabase(league_id, season_id, session_id, finals)
        self.setFastLap(session_id, self.finalSessionID)

    def createFinalSimSessionEntry(self, league_id, season_id, session_id):
        new_simsession, created = LeagueSessionSimsession.objects.update_or_create(
            league_id=league_id,
            season_id=season_id,
            session_id=session_id,
            simsession_number=99,
            defaults={
                "simsession_type": self.finalSessionID,
                "simsession_type_name": "final",
                "simsession_subtype": 0,
                "simsession_name": "OVERALL",
            })

    def calculateFinalScores(self, results):
        finals = {}

        for result in results:

            #Skip any final entries that we have already created.
            if result.simsession_type == self.finalSessionID:
                continue

            # Get the finals dictionary object for the driver
            driver = finals.get(result.cust_id, {})

            # Get running totals if they are present or initialise.
            driver['display_name'] = driver.get('display_name', result.display_name)
            points = driver.get('points', 0)
            incidents = driver.get('incidents', 0)
            average_lap = driver.get('average_lap', 0)
            average_lap_count = driver.get('average_lap_count', 0)
            average_position = driver.get('average_position', 0)
            average_position_count = driver.get('average_position_count', 0)
            best_lap_time = driver.get('best_lap_time', None)

            # Accumalate points and incidents
            driver['points'] = points + result.points if result.points else points
            driver['incidents'] = incidents + result.incidents

            # Accumulate the average if a time was set.
            # This is across all simsessions.
            new_average_lap = result.average_lap
            if new_average_lap > 0:
                driver['average_lap'] = average_lap + new_average_lap
                driver['average_lap_count'] = average_lap_count + 1

            # Update Best Lap Time from races.
            if result.simsession_type == 6:
                new_best_lap_time = result.best_lap_time
                if new_best_lap_time and (best_lap_time is None or new_best_lap_time < best_lap_time):
                    driver['best_lap_time'] = new_best_lap_time

            # For races we store the average finishing position
            if result.simsession_type == 6:
                finish_position = result.finish_position
                if finish_position >= 0 and result.laps_complete > 0:
                    driver['average_position'] = average_position + (finish_position + 1)
                    driver['average_position_count'] = average_position_count + 1

            # Update or add the row to the finals dictionary
            finals[result.cust_id] = driver
            #self.printRawData(result.cust_id, driver)

        return finals

    def scorePractice(self, simsession):
        for result in simsession['results']:
            best_lap_time = result['best_lap_time'] if result['best_lap_time'] > 0 else None
            entry = {
                "league_id": self.results['league_id'],
                "season_id": self.results['league_season_id'],
                "session_id": self.results['subsession_id'],
                "simsession_number": simsession['simsession_number'],
                "simsession_type": simsession['simsession_type'],
                "cust_id": result['cust_id'],
                "display_name": result['display_name'],
                "finish_position": result['finish_position'],
                "finish_position_in_class": result['finish_position_in_class'],
                "laps_lead": result['laps_lead'],
                "laps_complete": result['laps_complete'],
                "average_lap": result['average_lap'],
                "best_lap_time": best_lap_time,
                "incidents": result['incidents'],
            }
            #self.printRawData("scorePractice", entry)
            self.saveSessionToDatabase(entry)

    def scoreQualifying(self, simsession):
        for result in simsession['results']:
            best_lap_time = result['best_lap_time'] if result['best_lap_time'] > 0 else None
            entry = {
                "league_id": self.results['league_id'],
                "season_id": self.results['league_season_id'],
                "session_id": self.results['subsession_id'],
                "simsession_number": simsession['simsession_number'],
                "simsession_type": simsession['simsession_type'],
                "cust_id": result['cust_id'],
                "display_name": result['display_name'],
                "finish_position": result['finish_position'],
                "finish_position_in_class": result['finish_position_in_class'],
                "laps_lead": result['laps_lead'],
                "laps_complete": result['laps_complete'],
                "average_lap": result['average_lap'],
                "best_lap_time": best_lap_time,
                "incidents": result['incidents'],
                "points": self.bonus_quali.get(result['finish_position'], 0)
            }
            #self.printRawData("scoreQualifying", entry)
            self.saveSessionToDatabase(entry)

    def scoreRace(self, simsession):

        for idx, result in enumerate(simsession['results']):
            best_lap_time = result['best_lap_time'] if result['best_lap_time'] > 0 else None
            entry = {
                "league_id": self.results['league_id'],
                "season_id": self.results['league_season_id'],
                "session_id": self.results['subsession_id'],
                "simsession_number": simsession['simsession_number'],
                "simsession_type": simsession['simsession_type'],
                "cust_id": result['cust_id'],
                "display_name": result['display_name'],
                "finish_position": result['finish_position'],
                "finish_position_in_class": result['finish_position_in_class'],
                "laps_lead": result['laps_lead'],
                "laps_complete": result['laps_complete'],
                "average_lap": result['average_lap'],
                "best_lap_time": best_lap_time,
                "incidents": result['incidents'],
                "points": self.fia_race.get(result['finish_position'], 0) # Add the points positions
            }

            # Add the clean race bonus
            if result['average_lap'] > 0 and result['incidents'] == 0:
                entry['points'] = entry['points'] + self.booti_point

            #Save the data
            self.saveSessionToDatabase(entry)

    def setFastLap(self, session_id, simsession_number):
        #print("Set Fast Lap", session_id, simsession_number)

        # Get all the entries in order where a time was set and they are outside the top 3.
        entries = LeagueSessionResults.objects.all()\
            .filter(session_id=session_id, simsession_number=simsession_number, finish_position__gte=3)\
            .exclude(best_lap_time=0).exclude(best_lap_time=None).exclude(finish_position=3)\
            .order_by('best_lap_time')
        #self.printRawData("Fast Lap", entries)

        # Save that record with the bonus and fast_lap flag set.
        fastest = entries[0]
        fastest.fast_lap = True
        fastest.points = fastest.points + self.fast_lap_bonus
        fastest.save()

    def saveFinalSessionToDatabase(self, league_id, season_id, session_id, finals):
        for key, final in finals.items():
            average_finish_position = self.getAverage(final.get('average_position', 0), final.get('average_position_count'))
            final_average_lap = self.getAverage(final.get('average_lap', 0), final.get('average_lap_count'))

            entry = {
                "league_id": league_id,
                "season_id": season_id,
                "session_id": session_id,
                "simsession_number": self.finalSessionID,
                "simsession_type": self.finalSessionID,
                "cust_id": key,
                "display_name": final['display_name'],
                "finish_position": average_finish_position,
                "finish_position_in_class": None,
                "laps_lead": None,
                "laps_complete": None,
                "average_lap": final_average_lap,
                "best_lap_time": final.get('best_lap_time', None),
                "incidents": final.get('incidents', None),
                "points": final.get('points', None),
            }
            self.saveSessionToDatabase(entry)

    def saveSessionToDatabase(self, entry):
        try:
            driver, created = LeagueSessionResults.objects.update_or_create(
                league_id=entry.get('league_id', None),
                season_id=entry.get('season_id', None),
                session_id=entry.get('session_id', None),
                simsession_number=entry.get('simsession_number', None),
                cust_id=entry.get('cust_id', None),
                defaults={
                    "simsession_type": entry.get('simsession_type', None),
                    "display_name": entry.get('display_name', None),
                    "finish_position": entry.get('finish_position', None),
                    "finish_position_in_class": entry.get('finish_position_in_class', None),
                    "laps_lead": entry.get('laps_lead', None),
                    "laps_complete": entry.get('laps_complete', None),
                    "average_lap": entry.get('average_lap', None),
                    "best_lap_time": entry.get('best_lap_time', None),
                    "incidents": entry.get('incidents', None),
                    "points": entry.get('points', None),
                }
            )
        except IntegrityError as e:
            self.printRawData("saveSessionToDatabase | IntegrityError", e, entry)

    def getAverage(self, total, count):
        if count and count != 0:
            return int(total / count)
        else:
            return None

    def validateValues(self, value):
        if math.isnan(value):
            return None
        return value

    def calculateSeasonStandings(self, season):
        participating_drivers = LeagueSessionResults.objects.filter(season_id=season.season_id, simsession_number=99).order_by("cust_id")
        col_names = ["cust_id", "display_name", "points", "finish_position", "incidents"]
        standings = {}
        for driver in participating_drivers:
            if standings.get(driver.cust_id) is None:

                best_results = LeagueSessionResults.objects.filter(season_id=season.season_id, simsession_number=99, cust_id=driver.cust_id).values(*col_names).order_by("-points")[:8]
                df = pd.DataFrame.from_records(best_results, columns=col_names)
                standings[driver.cust_id] = {
                    'display_name': driver.display_name,
                    'points': df['points'].sum(),
                    'finish_position': df['finish_position'].min(),
                    'average_position': df['finish_position'].mean(),
                    'incidents': df['incidents'].sum(),
                }
        self.printRawData("Complete Standings", standings)
        self.saveSeasonStandingsToDatabase(season.league_id, season.season_id, standings)

    def saveSeasonStandingsToDatabase(self, league_id, season_id, standings):
        for key, result in standings.items():
            try:
                new_result, created = LeagueSeasonStandings.objects.update_or_create(
                    league_id=league_id,
                    season_id=season_id,
                    cust_id=key,
                    defaults={
                        "display_name": result['display_name'],
                        "points": result['points'],
                        "incidents": result['incidents'],
                        "best_finish": result['finish_position'],
                        "average_finish": result['average_position'],
                    }
                )
            except KeyError as ke:
                print("updateLeagueData: Missing Session Keys", ke)