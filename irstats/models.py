from django.db import models

# Create your models here.
from django.contrib.auth.models import User

""" Extension to the built in users model which adds iRacing Cust No."""
class CustID(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    custid = models.CharField(max_length=100)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'auth_user_custids'


class Update(models.Model):
    """ Updates table so we can manage updates and not hit iracing too often"""

    type = models.CharField(max_length=16)
    interval = models.IntegerField(null=True, default=300)
    last_update = models.DateTimeField(null=True)
    next_update = models.DateTimeField(null=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'irstats_updates'
        verbose_name = 'Update'
        verbose_name_plural = 'Updates'
        ordering = ['-type']

        def __str__(self):
            return str(self.type) + " (" + str(self.id) + ")"


class Category(models.Model):
    """ Racing Categories Road, Oval etc. """

    display_name = models.CharField(max_length=100, blank=True, null=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'irstats_category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['-id']

    def __str__(self):
        return str(self.display_name) + " (" + str(self.id) + ")"


class Series(models.Model):
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    eligible = models.BooleanField()
    forum_url = models.CharField(max_length=100, blank=True, null=True)
    max_starters = models.IntegerField(null=True)
    min_starters = models.IntegerField(null=True)
    oval_caution_type = models.IntegerField(null=True)
    road_caution_type = models.IntegerField(null=True)
    series_id = models.IntegerField(null=True)
    series_name = models.CharField(max_length=100, blank=True, null=True)
    series_short_name = models.CharField(max_length=100, blank=True, null=True)
    allowed_licenses = models.CharField(max_length=255, blank=True, null=True)
    date_modified = models.DateTimeField(auto_now=True)
    show = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'irstats_series'
        verbose_name = 'Serie'
        verbose_name_plural = 'Series'
        ordering = ['-id']

    def __str__(self):
        return str(self.series_short_name) + " (" + str(self.id) + ")"


class Cars(models.Model):
    """ Tracks on the iRacing Service """

    ai_enabled = models.BooleanField()
    allow_number_colors = models.BooleanField()
    allow_number_font = models.BooleanField()
    allow_sponsor1 = models.BooleanField()
    allow_sponsor2 = models.BooleanField()
    allow_wheel_color = models.BooleanField()
    award_exempt = models.BooleanField()
    car_dirpath = models.CharField(max_length=100, blank=True, null=True)
    car_id = models.IntegerField(null=True)
    car_name = models.CharField(max_length=100, blank=True, null=True)
    car_name_abbreviated = models.CharField(max_length=100, blank=True, null=True)
    car_types = models.CharField(max_length=100, blank=True, null=True)
    car_weight = models.IntegerField(null=True)
    categories = models.CharField(max_length=100, blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    first_sale = models.DateTimeField(blank=True, null=True)
    forum_url = models.CharField(max_length=100, blank=True, null=True)
    free_with_subscription = models.BooleanField()
    has_headlights = models.BooleanField()
    has_multiple_dry_tire_types = models.BooleanField()
    hp = models.IntegerField(null=True)
    is_ps_purchasable = models.BooleanField(default=True)
    max_power_adjust_pct = models.IntegerField(null=True)
    max_weight_penalty_kg = models.IntegerField(null=True)
    min_power_adjust_pct = models.IntegerField(null=True)
    package_id = models.IntegerField(null=True)
    patterns = models.IntegerField(null=True)
    price = models.IntegerField(null=True)
    price_display = models.CharField(max_length=10, blank=True, null=True)
    retired = models.BooleanField()
    search_filters = models.CharField(max_length=100, blank=True, null=True)
    sku = models.IntegerField(null=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'irstats_cars'
        verbose_name = 'Car'
        verbose_name_plural = 'Cars'
        ordering = ['-id']

    def __str__(self):
        return str(self.car_name_abbreviated) + " (" + str(self.id) + ")"


class Tracks(models.Model):
    """ Tracks on the iRacing Service """

    ai_enabled = models.BooleanField()
    allow_pitlane_collisions = models.BooleanField()
    allow_rolling_start = models.BooleanField()
    allow_standing_start = models.BooleanField()
    award_exempt = models.BooleanField()
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    closes = models.DateField(blank=True, null=True)
    config_name = models.CharField(max_length=100, blank=True, null=True)
    corners_per_lap = models.IntegerField(null=True)
    created = models.DateTimeField(blank=True, null=True)
    first_sale = models.DateTimeField(blank=True, null=True)
    free_with_subscription = models.BooleanField()
    fully_lit = models.BooleanField()
    grid_stalls = models.IntegerField(null=True)
    has_opt_path = models.BooleanField()
    has_short_parade_lap = models.BooleanField()
    has_start_zone = models.BooleanField()
    has_svg_map = models.BooleanField()
    is_dirt = models.BooleanField()
    is_oval = models.BooleanField()
    is_ps_purchasable = models.BooleanField()
    lap_scoring = models.IntegerField(null=True)
    latitude = models.FloatField(null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.FloatField(null=True)
    max_cars = models.IntegerField(null=True)
    night_lighting = models.BooleanField()
    nominal_lap_time = models.FloatField(null=True)
    number_pitstalls = models.IntegerField(null=True)
    opens = models.DateField(blank=True, null=True)
    package_id = models.IntegerField(null=True)
    pit_road_speed_limit = models.IntegerField(null=True)
    price = models.IntegerField(null=True)
    price_display = models.CharField(max_length=10, blank=True, null=True)
    priority = models.IntegerField(null=True)
    purchasable = models.BooleanField()
    qualify_laps = models.IntegerField(null=True)
    restart_on_left = models.BooleanField()
    retired = models.BooleanField()
    search_filters = models.CharField(max_length=100, blank=True, null=True)
    site_url = models.CharField(max_length=100, blank=True, null=True)
    sku = models.IntegerField(null=True)
    solo_laps = models.IntegerField(null=True)
    start_on_left = models.BooleanField()
    supports_grip_compound = models.BooleanField()
    tech_track = models.BooleanField()
    time_zone = models.CharField(max_length=100, blank=True, null=True)
    track_config_length = models.FloatField(null=True)
    track_dirpath = models.CharField(max_length=100, blank=True, null=True)
    track_id = models.IntegerField(null=True, unique=True)
    track_name = models.CharField(max_length=100, blank=True, null=True)
    track_types = models.CharField(max_length=100, blank=True, null=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'irstats_tracks'
        verbose_name = 'Track'
        verbose_name_plural = 'Tracks'
        ordering = ['-id']

    def __str__(self):
        return str(self.track_name) + " (" + str(self.id) + ")"


class Member(models.Model):
    """ Basic Members stats """
    custid = models.IntegerField(null=True, unique=True)
    display_name = models.CharField(max_length=100, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    member_since = models.DateField(blank=True, null=True)
    club_id = models.IntegerField(null=True)
    club_name = models.CharField(max_length=100, blank=True, null=True)
    num_official_sessions = models.IntegerField(null=True)
    num_league_sessions = models.IntegerField(null=True)
    num_official_wins = models.IntegerField(null=True)
    num_league_wins = models.IntegerField(null=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'irstats_member'
        verbose_name = 'Member'
        verbose_name_plural = 'Members'
        ordering = ['-custid']

    def __str__(self):
        return str(self.display_name) + " (" + str(self.custid) + ")"


class Career(models.Model):
    """ Members Stats for Categories """
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    starts = models.IntegerField(null=True)
    wins = models.IntegerField(null=True)
    top5 = models.IntegerField(null=True)
    poles = models.IntegerField(null=True)
    avg_start_position = models.IntegerField(null=True)
    avg_finish_position = models.IntegerField(null=True)
    laps = models.IntegerField(null=True)
    laps_led = models.IntegerField(null=True)
    avg_incidents = models.FloatField(null=True)
    avg_points = models.FloatField(null=True)
    win_percentage = models.FloatField(null=True)
    top5_percentage = models.FloatField(null=True)
    laps_led_percentage = models.FloatField(null=True)
    total_club_points = models.IntegerField(null=True)
    year = models.IntegerField(null=True, default=0)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'irstats_career'
        unique_together = ('member', 'category', 'year')
        verbose_name = 'Career'
        verbose_name_plural = 'Careers'
        ordering = ['-category']

    def __str__(self):
        return str(self.member) + " (" + str(self.category) + ")"


class Races(models.Model):
    member = models.ForeignKey(Member, on_delete=models.DO_NOTHING)
    track = models.ForeignKey(Tracks, on_delete=models.DO_NOTHING)
    car = models.ForeignKey(Cars, on_delete=models.DO_NOTHING)
    series = models.ForeignKey(Series, on_delete=models.DO_NOTHING)

    license_level = models.IntegerField(null=True)
    session_start_time = models.DateTimeField(null=True)

    winner_group_id = models.IntegerField(null=True)
    winner_name = models.CharField(max_length=100, blank=True, null=True)
    winner_license_level = models.IntegerField(null=True)

    start_position = models.IntegerField(null=True)
    finish_position = models.IntegerField(null=True)
    qualifying_time = models.IntegerField(null=True)
    laps_completed = models.IntegerField(null=True)
    laps_led = models.IntegerField(null=True)
    incidents = models.IntegerField(null=True)
    club_points = models.IntegerField(null=True)
    points = models.IntegerField(null=True)
    strength_of_field = models.IntegerField(null=True)
    subsession_id = models.IntegerField(null=True)
    old_sub_level = models.IntegerField(null=True)
    new_sub_level = models.IntegerField(null=True)
    oldi_rating = models.IntegerField(null=True)
    newi_rating = models.IntegerField(null=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'irstats_races'
        verbose_name = 'Race'
        verbose_name_plural = 'Races'
        ordering = ['-session_start_time']

    def __str__(self):
        return str(self.session_start_time) + " (" + str(self.id) + ")"


class Laps(models.Model):
    race = models.ForeignKey(Races, on_delete=models.DO_NOTHING)
    member = models.ForeignKey(Member, on_delete=models.DO_NOTHING)
    group_id = models.IntegerField(null=True)
    lap_number = models.IntegerField(null=True)
    flags = models.IntegerField(null=True)
    incident = models.BooleanField()
    session_time = models.IntegerField(null=True)
    session_start_time = models.IntegerField(null=True)
    lap_time = models.IntegerField(null=True)
    team_fastest_lap = models.BooleanField()
    personal_best_lap = models.BooleanField()
    license_level = models.IntegerField(null=True)
    car_number = models.IntegerField(null=True)
    lap_events = models.CharField(max_length=255, blank=True, null=True)
    ai = models.BooleanField()
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'irstats_laps'
        verbose_name = 'Lap'
        verbose_name_plural = 'Laps'
        ordering = ['lap_number']

    def __str__(self):
        return str(self.lap_number) + " (" + str(self.id) + ")"


class Leagues(models.Model):
    league_id = models.IntegerField(null=True)
    owner_id = models.IntegerField(null=True)
    league_name = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField(null=True)
    about = models.CharField(max_length=255, blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    roster_count = models.IntegerField(null=True)
    recruiting = models.BooleanField()
    is_admin = models.BooleanField()
    is_member = models.BooleanField()
    pending_application = models.BooleanField()
    pending_invitation = models.BooleanField()
    next_update = models.DateTimeField(null=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'irstats_leagues'
        verbose_name = 'League'
        verbose_name_plural = 'Leagues'
        ordering = ['league_id']

    def __str__(self):
        return str(self.league_name) + " (" + str(self.league_id) + ")"


class LeagueSeasons(models.Model):
    league = models.ForeignKey(Leagues, on_delete=models.DO_NOTHING, null=True)
    season_id = models.IntegerField(null=True)
    points_system_id = models.IntegerField(null=True)
    season_name = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField()
    hidden = models.BooleanField()
    no_drops_on_or_after_race_num = models.IntegerField(null=True)
    points_cars = models.CharField(max_length=255, blank=True, null=True)
    driver_points_car_classes = models.CharField(max_length=255, blank=True, null=True)
    team_points_car_classes = models.CharField(max_length=255, blank=True, null=True)
    points_system_name = models.CharField(max_length=255, blank=True, null=True)
    points_system_desc = models.CharField(max_length=255, blank=True, null=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'irstats_league_seasons'
        verbose_name = 'League Season'
        verbose_name_plural = 'League Seasons'
        ordering = ['league_id', 'season_id']

    def __str__(self):
        return str(self.season_name) + " (" + str(self.season_id) + ")"


class LeagueRoster(models.Model):
    league = models.ForeignKey(Leagues, on_delete=models.DO_NOTHING, null=True)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    cust_id = models.IntegerField(null=True)
    owner = models.BooleanField()
    admin = models.BooleanField()
    league_mail_opt_out = models.BooleanField()
    league_pm_opt_out = models.BooleanField()
    league_member_since = models.DateTimeField(null=True)
    car_number = models.IntegerField(null=True)
    nick_name = models.CharField(max_length=255, blank=True, null=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    category1_license_level = models.IntegerField(null=True, default=0)
    category1_safety_rating= models.FloatField(null=True, default=0)
    category1_cpi = models.FloatField(null=True, default=0)
    category1_irating = models.IntegerField(null=True, default=0)
    category1_mpr_num_races = models.IntegerField(null=True, default=0)
    category1_tt_rating = models.IntegerField(null=True, default=0)
    category1_mpr_num_tts = models.IntegerField(null=True, default=0)
    category1_group_id = models.IntegerField(null=True, default=0)

    category2_license_level = models.IntegerField(null=True, default=0)
    category2_safety_rating= models.FloatField(null=True, default=0)
    category2_cpi = models.FloatField(null=True, default=0)
    category2_irating = models.IntegerField(null=True, default=0)
    category2_mpr_num_races = models.IntegerField(null=True, default=0)
    category2_tt_rating = models.IntegerField(null=True, default=0)
    category2_mpr_num_tts = models.IntegerField(null=True, default=0)
    category2_group_id = models.IntegerField(null=True, default=0)

    category3_license_level = models.IntegerField(null=True, default=0)
    category3_safety_rating= models.FloatField(null=True, default=0)
    category3_cpi = models.FloatField(null=True, default=0)
    category3_irating = models.IntegerField(null=True, default=0)
    category3_mpr_num_races = models.IntegerField(null=True, default=0)
    category3_tt_rating = models.FloatField(null=True, default=0)
    category3_mpr_num_tts = models.IntegerField(null=True, default=0)
    category3_group_id = models.IntegerField(null=True, default=0)

    category4_license_level = models.IntegerField(null=True, default=0)
    category4_safety_rating= models.FloatField(null=True, default=0)
    category4_cpi = models.FloatField(null=True, default=0)
    category4_irating = models.IntegerField(null=True, default=0)
    category4_mpr_num_races = models.IntegerField(null=True, default=0)
    category4_tt_rating = models.IntegerField(null=True, default=0)
    category4_mpr_num_tts = models.IntegerField(null=True, default=0)
    category4_group_id = models.IntegerField(null=True, default=0)

    class Meta:
        managed = True
        db_table = 'irstats_league_roster'
        verbose_name = 'League Roster'
        verbose_name_plural = 'League Roster'
        ordering = ['car_number']

    def __str__(self):
        return str(self.display_name) + " (" + str(self.car_number) + " | " +  str(self.nick_name) + ")"


class LeagueSessions(models.Model):
    league = models.ForeignKey(Leagues, on_delete=models.DO_NOTHING, null=True)
    season = models.ForeignKey(LeagueSeasons, on_delete=models.DO_NOTHING, null=True)
    league_season_id = models.IntegerField(null=True)
    cars = models.CharField(max_length=255, blank=True, null=True)
    consec_cautions_single_file = models.BooleanField()
    damage_model = models.IntegerField(null=True)
    do_not_count_caution_laps = models.BooleanField()
    do_not_paint_cars = models.BooleanField()
    driver_changes = models.BooleanField()
    enable_pitlane_collisions = models.BooleanField()
    entry_count = models.IntegerField(null=True)
    green_white_checkered_limit = models.IntegerField(null=True)
    has_results = models.BooleanField()
    launch_at = models.DateTimeField(null=True)
    lone_qualify = models.BooleanField()
    max_ai_drivers = models.IntegerField(null=True)
    must_use_diff_tire_types_in_race = models.BooleanField()
    no_lapper_wave_arounds = models.BooleanField()
    num_opt_laps = models.IntegerField(null=True)
    pace_car_class_id = models.IntegerField(null=True)
    pace_car_id = models.IntegerField(null=True)
    password_protected = models.BooleanField()
    practice_length = models.IntegerField(null=True)
    private_session_id = models.IntegerField(null=True)
    qualify_laps = models.IntegerField(null=True)
    qualify_length = models.IntegerField(null=True)
    race_laps = models.IntegerField(null=True)
    race_length = models.IntegerField(null=True)
    short_parade_lap = models.BooleanField()
    start_on_qual_tire = models.BooleanField()
    start_zone = models.BooleanField()
    status = models.IntegerField(null=True)
    team_entry_count = models.IntegerField(null=True)
    telemetry_force_to_disk = models.IntegerField(null=True)
    telemetry_restriction = models.IntegerField(null=True)
    time_limit = models.IntegerField(null=True)
    track_id = models.IntegerField(null=True)
    track_name = models.CharField(max_length=255, blank=True, null=True)
    track_state = models.CharField(max_length=255, blank=True, null=True)
    weather = models.CharField(max_length=255, blank=True, null=True)
    date_modified = models.DateTimeField(auto_now=True)
    subsession_id = models.IntegerField(null=True)

    class Meta:
        managed = True
        db_table = 'irstats_league_sessions'
        verbose_name = 'League Session'
        verbose_name_plural = 'League Session'
        ordering = ['launch_at']

    def __str__(self):
        return str(self.launch_at) + " (" + str(self.track_name) + ")"


class LeaguePoints(models.Model):
    league = models.ForeignKey(Leagues, on_delete=models.DO_NOTHING, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    points_system_id = models.IntegerField(null=True)
    retired = models.BooleanField()
    iracing_system = models.BooleanField()
    description = models.CharField(max_length=255, blank=True, null=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'irstats_league_points'
        verbose_name = 'League Points'
        verbose_name_plural = 'League Points'
        ordering = ['name']

    def __str__(self):
        return str(self.name) + " (" + str(self.points_system_id) + ")"


class LeagueSessionSimsession(models.Model):
    league_id = models.IntegerField(null=False)
    season_id = models.IntegerField(null=False)
    session_id = models.IntegerField(null=False)
    simsession_number = models.IntegerField(null=False)
    simsession_type = models.IntegerField(null=False)
    simsession_type_name = models.CharField(max_length=55, blank=True, null=True)
    simsession_subtype = models.IntegerField(null=False)
    simsession_name = models.CharField(max_length=55, blank=True, null=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'irstats_league_session_simsession'
        verbose_name = 'League Simsession Result'
        verbose_name_plural = 'League Simsession Results'
        ordering = ['session_id', 'simsession_number']


class LeagueSessionResults(models.Model):
    league_id = models.IntegerField(null=False)
    season_id = models.IntegerField(null=False)
    session_id = models.IntegerField(null=False)
    simsession_number = models.IntegerField(null=False)
    simsession_type = models.IntegerField(null=False)
    cust_id = models.IntegerField(null=False)
    display_name = models.CharField(max_length=255, blank=True, null=True)

    finish_position = models.IntegerField(null=True)
    finish_position_in_class = models.IntegerField(null=True)
    laps_lead = models.IntegerField(null=True)
    laps_complete = models.IntegerField(null=True)
    average_lap = models.IntegerField(null=True)
    best_lap_time = models.IntegerField(null=True)
    fast_lap = models.BooleanField(default=False)

    incidents = models.IntegerField(null=True)
    points = models.IntegerField(null=True)

    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'irstats_league_session_results'
        verbose_name = 'League Session Result'
        verbose_name_plural = 'League Session Results'
        ordering = ['session_id', 'cust_id']

    def __str__(self):
        return str(self.session_id) + " (" + str(self.cust_id) + ")"


class LeagueSeasonStandings(models.Model):
    league_id = models.IntegerField(null=True)
    season_id = models.IntegerField(null=True)
    cust_id = models.IntegerField(null=True)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    points = models.IntegerField(null=True)
    best_finish = models.IntegerField(null=True)
    average_finish = models.IntegerField(null=True)
    incidents = models.IntegerField(null=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'irstats_league_season_standings'
        verbose_name = 'League Season Standings'
        verbose_name_plural = 'League Seasons Standings'
        ordering = ['points', 'display_name']

    def __str__(self):
        return str(self.simsession_type_name) + " (" + str(self.subsession_id) + ")"