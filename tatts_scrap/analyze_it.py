from sqlite_db import SQLITE_DB
from ConfigParser import ConfigParser
import sqlite3

TATTS_ANALYSIS_CFG = "tatts_analysis.cfg"
global FILTERS

FILTERS = {"tipsters_performance": {"box_number": "N/A", "tipster_name": "N/A",
                                               "tipster_id": "N/A", "venue": "N/A",
                                               "start_date": "N/A", "end_date": "N/A",
                                                "distance_minimum": "N/A",
                                                "distance_maximum": "N/A",
                                                "tf_pool_size": "N/A", "number_of_runners": "N/A"}}


def validate_user_input(user_input):
    """
    Validates user input
    """
    try:
        user_input = int(user_input)
        if user_input >= 0 and user_input < 3:
            return True
        else:
            return False
    except:
        return False


def tipsters_performance():
    global FILTERS
    print "tipster performance method"
    parse_config_update_filters(file_path=TATTS_ANALYSIS_CFG, section_name="tipsters_performance")

    for key, value in FILTERS.iteritems():
        print "%s = %s" % (key, value)

    try:
        conn = sqlite3.connect(SQLITE_DB)
        c = conn.cursor()

        c.execute('Drop view if Exists tipsters_performance')

        sql_stmt = 'CREATE VIEW tipsters_performance AS select rt.tipster_name, '
        sql_stmt += ' count(rt.race_id) as number_of_events, '
        sql_stmt += '(select count(won_tf) from race_tipsters where won_tf = 1 and '
        sql_stmt += 'tipster_name = rt.tipster_name ) as num_of_wins, '
        sql_stmt += '(select sum(b.div_amount) from race_tipsters a inner join pool_details b on '
        sql_stmt += 'a.race_id = b.race_id where a.won_tf = 1 and'
        sql_stmt += ' a.tipster_name = rt.tipster_name and b.pool_type = "TF")'
        sql_stmt += ' as sum_winning_payout '
        sql_stmt += 'from race_tipsters rt Group by rt.tipster_name'
        print "Executing sql: %s" % sql_stmt
        c.execute(sql_stmt)

        c.execute('Drop view if Exists tipsters_performance_details')

        sql_stmt = 'CREATE VIEW tipsters_performance_details AS select *, '
        sql_stmt += '(num_of_wins*1.0/number_of_events) as avg_num_wins, '
        sql_stmt += '(sum_winning_payout/num_of_wins) as avg_win_payout '
        sql_stmt += 'from tipsters_performance'
        print "Executing sql: %s" % sql_stmt
        c.execute(sql_stmt)

        c.execute('select *, '
                  '((avg_win_payout/avg_num_wins) - 24) as expected_value '
                  'from tipsters_performance_details')

        rows = c.fetchall()
        for row in rows:
            print row

        write_to_csv_file("tipsters_performance.csv", rows)

    finally:
        conn.commit()
        conn.close()


def write_to_csv_file(file_path, data):
    with open(file_path, 'w') as csv_file:
        for line in data:
            csv_file.write(','.join([str(item) for item in line]))
            csv_file.write('\n')


def winning_box():
    print "winning box method"


def parse_config_update_filters(file_path, section_name):
    """
    This method will read the config file and return key value pair.
    """
    global FILTERS
    config = ConfigParser()
    config.read(file_path)
    for section in config.sections():
        print "section = ", section
        if section in FILTERS.keys():
            for option in config.options(section):
                print "option = ", option
                print "option value = ", config.get(section, option)
                FILTERS[section] = config.get(section, option)


def analyze_it():
    """
    Main analysis method.
    """
    print "Please select the type of analysis you would like to do:"
    print "1. Tipsters performance"
    print "2. Winning box"
    user_input = raw_input("Enter 0 for exit: ")
    while not validate_user_input(user_input):
        user_input = raw_input("The value you enetered is not correct, "
                            "valid inputs are (0, 1, 2): ")

    if user_input == "0":
        return
    elif user_input == "1":
        tipsters_performance()
    elif user_input == "2":
        winning_box()

if __name__ == "__main__":
    analyze_it()
