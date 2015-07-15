from sqlite_db import SQLITE_DB
from ConfigParser import ConfigParser

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
