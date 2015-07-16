import sqlite3
import os

SQLITE_DB = 'tatts.sqlite'


def create_db_schema():
    # Connecting to the database file
    conn = sqlite3.connect(SQLITE_DB)
    c = conn.cursor()
    # Race Table
    c.execute('CREATE TABLE race (race_id TEXT PRIMARY KEY, venue_name TEXT,'
              ' weather TEXT, distance REAL, track TEXT)')

    # Race Tipsters Table
    # Consider adding flag if the tipster made a correct guess or not.
    c.execute('CREATE TABLE race_tipsters (race_id TEXT, tipster_id INTEGER,'
              ' tipster_name TEXT, tipster_tips TEXT, tf_candidate INTEGRE, won_tf INTEGER,'
              ' PRIMARY KEY (race_id, tipster_id))')

    # Race Runners Table
    c.execute('CREATE TABLE race_runners (race_id TEXT, runner_no INTEGER, runner_name TEXT,'
              ' box_no INTEGER, scratched INTEGER, trainer TEXT, win_price REAL,'
              ' place_price REAL, PRIMARY KEY (race_id, runner_no))')

    # Race Results Table
    c.execute('CREATE TABLE race_results (race_id TEXT, place_no INTEGER, runner_no INTEGER,'
              ' pool_type TEXT, divid_end REAL,'
              ' PRIMARY KEY (race_id, place_no, runner_no, pool_type))')

    # Race Pools Table
    c.execute('CREATE TABLE race_pools (race_id TEXT, pool_type TEXT,'
              ' pool_total REAL, PRIMARY KEY (race_id, pool_type))')

    # Pool Details Table
    c.execute('CREATE TABLE pool_details (race_id TEXT, pool_type TEXT, div_amount REAL,'
              ' runners_place_list TEXT, PRIMARY KEY (race_id, pool_type,'
              ' runners_place_list))')

    # Committing changes and closing the connection to the database file
    conn.commit()
    conn.close()

if __name__ == "__main__":
    if not os.path.isfile(SQLITE_DB):
        create_db_schema()
        print "DB file created."
    else:
        print "DB already exist, delete it if you want to re-create it."
