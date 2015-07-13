import requests
from datetime import datetime, timedelta
import sqlite3
from xml.dom.minidom import parseString
import time


def get_racing_info_by_day(day):
    """
    Collect the racing info for specific day
    """
    year, month, day = datetime.strftime(day, "%Y %m %d").split()
    if int(month) < 10:
        month = month[1:]
    if int(day) < 10:
        day = day[1:]
    # https://tatts.com/pagedata/racing/2015/7/8/RaceDay.xml
    url = "https://tatts.com/pagedata/racing/" + "/".join([year, month, day, "RaceDay.xml"])
    r = requests.get(url)
    # Strip out the BOM from the returned utf-8 encoded xml
    # BOM is simply the first three bytes in the beginning of the file.
    raceday_dom = parseString(r.text[3:])
    meetings = raceday_dom.getElementsByTagName("Meeting")
    greyhounds_meetings = []
    for meeting in meetings:
        if meeting.getAttribute('MeetingType') == 'G':
            greyhounds_meetings.append(meeting)

    for greyhound_meeting in greyhounds_meetings:
        meeting_code = greyhound_meeting.getAttribute("MeetingCode")
        venue_name = greyhound_meeting.getAttribute("VenueName")
        races = greyhound_meeting.getElementsByTagName("Race")
        # <Race CloseTime="2015-07-10T15:42:44.683" Distance="431" RaceDisplayStatus="PAYING"
        # RaceName="MAIDEN" RaceNo="1" RaceTime="2015-07-10T15:42:00" SubFav="0" TrackChanged="N"
        # TrackCond="1" TrackDesc="Good" TrackRating="0" TrackRatingChanged="N" WeatherChanged="N"
        # WeatherCond="1" WeatherDesc="Fine">
        for race in races:
            if race.getAttribute("RaceDisplayStatus") != "PAYING":
                print "skipping race as its status is not PAYING"
                continue
            race_no = race.getAttribute("RaceNo")
            weather = race.getAttribute("WeatherDesc")
            distance = race.getAttribute("Distance")
            track = race.getAttribute("TrackDesc")
            # https://tatts.com/pagedata/racing/2015/7/10/BG1.xml
            race_url = "https://tatts.com/pagedata/racing/" + "/".join([year, month, day,
                                                                        meeting_code +
                                                                        race_no +
                                                                        ".xml"])
            race_data = requests.get(race_url)
            race_dom = parseString(race_data.text[3:])

            print "************* Begin Race info ****************"
            print "Race No \t Venue Name \t Meeting Code \t Weather \t Distance \t Track"
            print "%s \t \t %s \t %s \t \t %s \t %s \t \t %s" % (race_no, venue_name, meeting_code,
                                                              weather, distance, track)

            tipsters = race_dom.getElementsByTagName("TipsterTip")
            print "-----Tipsters-----"
            for tipster in tipsters:
                tipster_id = tipster.getAttribute("TipsterId")
                tipster_tips = tipster.getAttribute("Tips")
                tipster_name = tipster.getElementsByTagName("Tipster"
                                                            )[0].getAttribute("TipsterName")
                print "Tipster Id \t Tipster Tips \t Tipster Name"
                print "%s \t \t %s \t %s" % (tipster_id, tipster_tips, tipster_name)

            runners = race_dom.getElementsByTagName("Runner")
            for runner in runners:
                runner_no = runner.getAttribute("RunnerNo")
                runner_name = runner.getAttribute("RunnerName")
                box_no = runner.getAttribute("Box")
                scratched = runner.getAttribute("Scratched")
                trainer = runner.getAttribute("Rider")
                win_price = runner.getElementsByTagName("WinOdds")[0].getAttribute("Odds")
                place_price = runner.getElementsByTagName("PlaceOdds")[0].getAttribute("Odds")
                print "Runner No \t Box No \t Runner Name \t Scratched \t Trainer  \t \t "
                "Win \t Place"
                print "%s \t \t %s \t \t %s \t %s \t \t %s \t \t %s \t \t %s" % (runner_no, box_no,
                                                                        runner_name, scratched,
                                                                        trainer, win_price,
                                                                        place_price)

            result_places = race_dom.getElementsByTagName("ResultPlace")
            for result_place in result_places:
                place_no = result_place.getAttribute("PlaceNo")
                results = result_place.getElementsByTagName("Result")
                print "----------RESULTS---------"
                for result in results:
                    runner_no = result.getAttribute("RunnerNo")
                    pool_type = result.getAttribute("PoolType")
                    pool_results = result.getElementsByTagName("PoolResult")
                    if pool_results[0].hasAttribute("Dividend"):
                        divid_end = pool_results[0].getAttribute("Dividend")
                    else:
                        divid_end = 0

                    if divid_end != 0:
                        print "Place No \t \t Runner No \t Pool Type \t Dividend"
                        print "%s \t \t \t %s \t \t \t %s \t \t %s" % (place_no, runner_no,
                                                           pool_type, divid_end)

            pools = race_dom.getElementsByTagName("Pool")
            print "---POOLS---"
            for pool in pools:
                pool_type = pool.getAttribute("PoolType")
                pool_total = pool.getAttribute("PoolTotal")
                print "Pool Type \t \t Pool total"
                print "%s \t \t \t \t %s $" % (pool_type, pool_total)
                divid_ends = pool.getElementsByTagName("Dividend")
                for divid_end in divid_ends:
                    div_amount = divid_end.getAttribute("DivAmount")
                    print "\t Div amount = %s" % div_amount
                    div_results = divid_end.getElementsByTagName("DivResult")
                    for div_result in div_results:
                        leg_no = div_result.getAttribute("LegNo")
                        div_result_runner_no = div_result.getAttribute("RunnerNo")
                        print "\t \t Leg No \t Runner No"
                        print "\t \t %s \t \t %s" % (leg_no, div_result_runner_no)
            time.sleep(1)
            print "************* End Race info ****************"


def scrap_tatts_by_date(from_date, to_date):
    """
    Scrap tatts website for greyhound races for specific date ranges
    """
    while from_date <= to_date:
        print "########## Scraping greyhounds racing info. for day %s ##########" % from_date
        get_racing_info_by_day(from_date)
        from_date = from_date + timedelta(hours=24)


def scrap_tatts():
    """
    Main method that contains the high level logic for scraping the tatts website.
    """
    last_date = raw_input("Please enter date until which you want to scrap data from "
                          "tatts website (YYYY/MM/DD): ")
    last_date = datetime.strptime(last_date, '%Y/%m/%d')
    # always scrap already finished races so scrap data latest by yesterday
    yesterday = datetime.now() - timedelta(hours=24)
    scrap_tatts_by_date(last_date, yesterday)

if __name__ == "__main__":
    scrap_tatts()
