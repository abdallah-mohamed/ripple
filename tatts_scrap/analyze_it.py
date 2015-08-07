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
                                                "tf_pool_size_gt": "N/A", "number_of_runners": "N/A"},
           "winning_box": {"venue": "N/A", "start_date": "N/A", "end_date": "N/A",
                           "distance_minimum": "N/A", "distance_maximum": "N/A",
                           "win_pool_size_gt": "N/A", "number_of_runners": "N/A",
                           "trainer": "N/A"},
           "winning_ranking": {"venue": "N/A", "start_date": "N/A", "end_date": "N/A",
                           "distance_minimum": "N/A", "distance_maximum": "N/A",
                           "win_pool_size_gt": "N/A", "number_of_runners": "N/A",
                           "trainer": "N/A", "price_categories": "1.5-2-3-4-5-10-20-30-40-50"},
           }


def validate_user_input(user_input):
    """
    Validates user input
    """
    try:
        user_input = int(user_input)
        if user_input >= 0 and user_input < 4:
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

    print 'FILTERS["tipsters_performance"] = ', FILTERS["tipsters_performance"]
    filters_exist = any([0 if filter_item == "N/A" else 1
                         for filter_item in FILTERS["tipsters_performance"]])
    print "filters exist = ", filters_exist
    try:
        conn = sqlite3.connect(SQLITE_DB)
        c = conn.cursor()

        c.execute('Drop view if Exists tipsters_performance')

        sql_stmt_part1 = 'CREATE VIEW tipsters_performance AS select rt.tipster_name, '
        sql_stmt_part1 += ' count(rt.race_id) as number_of_events, '

        sql_stmt_part1 += ' (select count(rt2.won_tf) from race_tipsters rt2'
        sql_stmt_part1 += " inner join race r on rt2.race_id = r.race_id"

        sql_stmt_part1 += ' where rt2.won_tf = 1 and '
        sql_stmt_part1 += ' rt2.tipster_name = rt.tipster_name'

        sql_stmt_part2 = ' ) as num_of_wins,'
        sql_stmt_part2 += ' (select COALESCE(sum(b.div_amount), 0) from race_tipsters rt2'
        sql_stmt_part2 += ' inner join pool_details b on '
        sql_stmt_part2 += ' rt2.race_id = b.race_id'
        sql_stmt_part2 += " inner join race r on rt2.race_id = r.race_id"
        sql_stmt_part2 += ' where rt2.won_tf = 1 and'
        sql_stmt_part2 += ' rt2.tipster_name = rt.tipster_name and b.pool_type = "TF"'

        sql_stmt_part3 = ' ) as sum_winning_payout'
        sql_stmt_part3 += ' from race_tipsters rt'
        sql_stmt_part3 += " inner join race r on r.race_id = rt.race_id"
        sql_stmt_part3 += " Where 1"

        if filters_exist:
            print "consolidating filters"
            if FILTERS["tipsters_performance"]["tipster_name"] != "N/A":
                added_sql = ' and rt.tipster_name = "%s"' % FILTERS["tipsters_performance"]["tipster_name"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql
                sql_stmt_part3 += added_sql

            if FILTERS["tipsters_performance"]["venue"] != "N/A":
                added_sql = ' and r.venue_name = "%s"' % FILTERS["tipsters_performance"]["venue"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql
                sql_stmt_part3 += added_sql

            if FILTERS["tipsters_performance"]["start_date"] != "N/A":
                added_sql = ' and r.date >= "%s"' % FILTERS["tipsters_performance"]["start_date"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql
                sql_stmt_part3 += added_sql

            if FILTERS["tipsters_performance"]["end_date"] != "N/A":
                added_sql = ' and r.date <= "%s"' % FILTERS["tipsters_performance"]["end_date"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql
                sql_stmt_part3 += added_sql

            if FILTERS["tipsters_performance"]["distance_minimum"] != "N/A":
                added_sql = ' and r.distance >= "%s"' % FILTERS["tipsters_performance"]["distance_minimum"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql
                sql_stmt_part3 += added_sql

            if FILTERS["tipsters_performance"]["distance_maximum"] != "N/A":
                added_sql = ' and r.distance <= "%s"' % FILTERS["tipsters_performance"]["distance_maximum"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql
                sql_stmt_part3 += added_sql

            if FILTERS["tipsters_performance"]["number_of_runners"] != "N/A":
                added_sql = ' and r.no_runners = "%s"' % FILTERS["tipsters_performance"]["number_of_runners"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql
                sql_stmt_part3 += added_sql

            if FILTERS["tipsters_performance"]["tf_pool_size_gt"] != "N/A":
                added_sql = ' and r.tf_pool_size >= "%s"' % FILTERS["tipsters_performance"]["tf_pool_size_gt"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql
                sql_stmt_part3 += added_sql


        sql_stmt_part3 += ' Group by rt.tipster_name'
        sql_stmt = sql_stmt_part1 + sql_stmt_part2 + sql_stmt_part3
        print "Executing sql: %s" % sql_stmt
        c.execute(sql_stmt)

        c.execute('Drop view if Exists tipsters_performance_details')

        sql_stmt = 'CREATE VIEW tipsters_performance_details AS select *, '
        sql_stmt += 'COALESCE((number_of_events*1.0/num_of_wins), 0) as avg_num_races_between_wins, '
        sql_stmt += 'COALESCE((sum_winning_payout/num_of_wins), 0) as avg_win_payout '
        sql_stmt += 'from tipsters_performance'
        print "Executing sql: %s" % sql_stmt
        c.execute(sql_stmt)

        c.execute('select *,'
                  ' COALESCE( '
                  ' (((avg_win_payout - 24)/avg_num_races_between_wins) - 24 * (1 - (1/avg_num_races_between_wins)))'
                  ' , 0) as expected_value'
                  ' from tipsters_performance_details')

        rows = c.fetchall()
        for row in rows:
            print row

        keys = ""
        values = ""
        for key, value in sorted(FILTERS["tipsters_performance"].iteritems()):
            print "tp (%s, %s)" %(key, value)
            keys += key + ","
            values += value + ","

        keys = keys[:-1] + "\n"
        values = values[:-1] + "\n"
        header = keys + values

        header += 'tipster_name,number_of_events,num_of_wins,sum_winning_payout,avg_num_races_between_wins,'
        header += 'avg_win_payout,expected_value\n'

        write_to_csv_file("tipsters_performance.csv", header, rows)

    finally:
        conn.commit()
        conn.close()


def write_to_csv_file(file_path, header, data):
    with open(file_path, 'w') as csv_file:
        csv_file.write(header)
        for line in data:
            csv_file.write(','.join([str(item) for item in line]))
            csv_file.write('\n')


def winning_ranking():
    global FILTERS
    print "winning ranking method"
    parse_config_update_filters(file_path=TATTS_ANALYSIS_CFG, section_name="winning_ranking")

    for key, value in FILTERS.iteritems():
        print "%s = %s" % (key, value)

    print 'FILTERS["winning_ranking"] = ', FILTERS["winning_ranking"]
    filters_exist = any([0 if filter_item == "N/A" else 1
                         for filter_item in FILTERS["winning_ranking"]])
    print "filters exist = ", filters_exist
    try:
        conn = sqlite3.connect(SQLITE_DB)
        c = conn.cursor()

        price_categories = [1.5, 2, 3, 4, 5, 10, 20, 30, 40, 50]
        if filters_exist:
            print "consolidating filters"
            if (FILTERS["winning_ranking"]
                ["price_categories"] != "N/A") and len(FILTERS["winning_ranking"]
                                        ["price_categories"].split(',')) == 10:
                print " * overriding price categories *"
                price_categories = [float(item) for item in
                                    FILTERS["winning_ranking"]
                                    ["price_categories"].split(',')]

        c.execute('Drop view if Exists runners_ranking')
        sql_stmt = 'CREATE VIEW runners_ranking AS select race_id, runner_no,'
        sql_stmt += ' scratched, win_price, trainer,'
        sql_stmt += '  (select count (*) + 1 from race_runners rr'
        sql_stmt += ' where rr.win_price < r.win_price '
        sql_stmt += ' and rr.race_id = r.race_id ) as rank_no, '
        sql_stmt += ' (Select '
        sql_stmt += ' CASE WHEN win_price < %s THEN "< %s" ' % (price_categories[0], price_categories[0])
        sql_stmt += ' WHEN (win_price >= %s) and (win_price < %s) THEN "%s to < %s" ' % (price_categories[0], price_categories[1],
                            price_categories[0], price_categories[1])
        sql_stmt += ' WHEN (win_price >= %s) and (win_price < %s) THEN "%s to < %s" ' % (price_categories[1], price_categories[2],
                            price_categories[1], price_categories[2])
        sql_stmt += ' WHEN (win_price >= %s) and (win_price < %s) THEN "%s to < %s" ' % (price_categories[2], price_categories[3],
                            price_categories[2], price_categories[3])
        sql_stmt += ' WHEN (win_price >= %s) and (win_price < %s) THEN "%s to < %s" ' % (price_categories[3], price_categories[4],
                            price_categories[3], price_categories[4])
        sql_stmt += ' WHEN (win_price >= %s) and (win_price < %s) THEN "%s to < %s" ' % (price_categories[4], price_categories[5],
                            price_categories[4], price_categories[5])
        sql_stmt += ' WHEN (win_price >= %s) and (win_price < %s) THEN "%s to < %s" ' % (price_categories[5], price_categories[6],
                            price_categories[5], price_categories[6])
        sql_stmt += ' WHEN (win_price >= %s) and (win_price < %s) THEN "%s to < %s" ' % (price_categories[6], price_categories[7],
                            price_categories[6], price_categories[7])
        sql_stmt += ' WHEN (win_price >= %s) and (win_price < %s) THEN "%s to < %s" ' % (price_categories[7], price_categories[8],
                            price_categories[7], price_categories[8])
        sql_stmt += ' WHEN (win_price >= %s) and (win_price < %s) THEN "%s to < %s" ' % (price_categories[8], price_categories[9],
                            price_categories[8], price_categories[9])
        sql_stmt += ' WHEN win_price >= %s THEN ">= %s" ' % (price_categories[9], price_categories[9])
        sql_stmt += ' End '
        sql_stmt += ' from race_runners rr '
        sql_stmt += ' where rr.runner_no = r.runner_no and '
        sql_stmt += ' rr.race_id = r.race_id) as price_category '
        sql_stmt += ' from race_runners r '

        print "Executing sql: %s" % sql_stmt
        c.execute(sql_stmt)

        c.execute('Drop view if Exists winning_ranking')

        sql_stmt_part1 = 'CREATE VIEW winning_ranking AS select rr.rank_no, rr.price_category,'

        sql_stmt_part1 += ' (select count(rr2.race_id) from runners_ranking rr2'
        sql_stmt_part1 += ' inner join race r on r.race_id = rr2.race_id'
        sql_stmt_part1 += ' inner join race_pools rp on rr2.race_id = rp.race_id'
        sql_stmt_part1 += ' where rr2.scratched = 0 and rr2.rank_no = rr.rank_no and'
        sql_stmt_part1 += ' rr2.price_category = rr.price_category and'
        sql_stmt_part1 += ' rp.pool_type = "WW" and rr2.rank_no < 9'

        sql_stmt_part2 = ' group by rr2.rank_no, price_category) as no_races,'
        sql_stmt_part2 += ' count(r.race_id) as no_wins,'
        sql_stmt_part2 += ' sum(rs.divid_end) as win_pool_size'
        sql_stmt_part2 += ' from runners_ranking rr'
        sql_stmt_part2 += ' inner join race_results rs on rr.race_id = rs.race_id and'
        sql_stmt_part2 += ' rr.runner_no = rs.runner_no'
        sql_stmt_part2 += ' inner join race r on rr.race_id = r.race_id'
        sql_stmt_part2 += ' inner join race_pools rp on rr.race_id = rp.race_id'
        sql_stmt_part2 += ' where  rs.place_no = 1 and rs.pool_type = "WW" and'
        sql_stmt_part2 += ' rr.scratched = 0 and rp.pool_type = "WW"'
        sql_stmt_part2 += ' and rr.rank_no < 9'

        if filters_exist:
            print "consolidating filters"
            if FILTERS["winning_ranking"]["venue"] != "N/A":
                added_sql = ' and r.venue_name = "%s"' % FILTERS["winning_ranking"]["venue"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql

            if FILTERS["winning_ranking"]["start_date"] != "N/A":
                added_sql = ' and r.date >= "%s"' % FILTERS["winning_ranking"]["start_date"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql

            if FILTERS["winning_ranking"]["end_date"] != "N/A":
                added_sql = ' and r.date <= "%s"' % FILTERS["winning_ranking"]["end_date"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql

            if FILTERS["winning_ranking"]["distance_minimum"] != "N/A":
                added_sql = ' and r.distance >= "%s"' % FILTERS["winning_ranking"]["distance_minimum"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql

            if FILTERS["winning_ranking"]["distance_maximum"] != "N/A":
                added_sql = ' and r.distance <= "%s"' % FILTERS["winning_ranking"]["distance_maximum"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql

            if FILTERS["winning_ranking"]["number_of_runners"] != "N/A":
                added_sql = ' and r.no_runners = "%s"' % FILTERS["winning_ranking"]["number_of_runners"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql

            if FILTERS["winning_ranking"]["win_pool_size_gt"] != "N/A":
                added_sql = ' and rp.pool_total >= %s' % FILTERS["winning_ranking"]["win_pool_size_gt"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql

            if FILTERS["winning_ranking"]["trainer"] != "N/A":
                added_sql = ' and rr2.trainer = "%s"' % FILTERS["winning_ranking"]["trainer"]
                sql_stmt_part1 += added_sql
                added_sql = ' and rr.trainer = "%s"' % FILTERS["winning_ranking"]["trainer"]
                sql_stmt_part2 += added_sql

        sql_stmt_part2 += ' group by rank_no, price_category'
        sql_stmt = sql_stmt_part1 + sql_stmt_part2
        print "Executing sql: %s" % sql_stmt
        c.execute(sql_stmt)

        c.execute('Drop view if Exists winning_ranking_details')

        sql_stmt = 'CREATE VIEW winning_ranking_details AS select *, '
        sql_stmt += ' (no_races*1.0/no_wins) as avg_num_races_between_wins,'
        sql_stmt += ' (win_pool_size*1.0/no_wins) avg_win_payout'
        sql_stmt += ' from winning_ranking'
        sql_stmt += ' Where 1'

        print "Executing sql: %s" % sql_stmt
        c.execute(sql_stmt)

        c.execute('select *,'
                  ' COALESCE( '
                  ' (((avg_win_payout - 1)/avg_num_races_between_wins) - 1 * (1 - (1/avg_num_races_between_wins)))'
                  ' , 0) as expected_value'
                  ' from winning_ranking_details order by rank_no')

        rows = c.fetchall()
        for row in rows:
            print row

        keys = ""
        values = ""
        for key, value in sorted(FILTERS["winning_ranking"].iteritems()):
            keys += key + ","
            if key == "price_categories":
                values += "-".join(str(item) for item in price_categories) + ","
            else:
                values += value + ","

        keys = keys[:-1] + "\n"
        values = values[:-1] + "\n"
        header = keys + values

        header += 'rank_no,price_category,no_races,no_wins,total_payout,avg_num_races_between_wins,'
        header += 'avg_win_payout,expected_value\n'

        write_to_csv_file("winning_ranking.csv", header, rows)

    finally:
        conn.commit()
        conn.close()


def winning_box():
    global FILTERS
    print "winning box method"
    parse_config_update_filters(file_path=TATTS_ANALYSIS_CFG, section_name="winning_box")

    for key, value in FILTERS.iteritems():
        print "%s = %s" % (key, value)

    print 'FILTERS["winning_box"] = ', FILTERS["winning_box"]
    filters_exist = any([0 if filter_item == "N/A" else 1
                         for filter_item in FILTERS["winning_box"]])
    print "filters exist = ", filters_exist
    try:
        conn = sqlite3.connect(SQLITE_DB)
        c = conn.cursor()

        c.execute('Drop view if Exists winning_box')

        sql_stmt_part1 = 'CREATE VIEW winning_box AS select rr.box_no,'
        sql_stmt_part1 += ' (select count(rr2.race_id) from race_runners rr2'
        sql_stmt_part1 += ' inner join race r on r.race_id = rr2.race_id'
        sql_stmt_part1 += ' inner join race_pools rp on rr2.race_id = rp.race_id'
        sql_stmt_part1 += ' where rr2.scratched = 0 and rr2.box_no = rr.box_no and'
        sql_stmt_part1 += ' rp.pool_type = "WW"'

        sql_stmt_part2 = ' group by rr2.box_no) as no_races,'
        sql_stmt_part2 += ' count(r.race_id) as no_wins,'
        sql_stmt_part2 += ' sum(rs.divid_end) as win_pool_size'
        sql_stmt_part2 += ' from race_runners rr'
        sql_stmt_part2 += ' inner join race_results rs on rr.race_id = rs.race_id and'
        sql_stmt_part2 += ' rr.runner_no = rs.runner_no'
        sql_stmt_part2 += ' inner join race r on rr.race_id = r.race_id'
        sql_stmt_part2 += ' inner join race_pools rp on rr.race_id = rp.race_id'
        sql_stmt_part2 += ' where  rs.place_no = 1 and rs.pool_type = "WW" and'
        sql_stmt_part2 += ' rr.scratched = 0 and rp.pool_type = "WW"'

        if filters_exist:
            print "consolidating filters"
            if FILTERS["winning_box"]["venue"] != "N/A":
                added_sql = ' and r.venue_name = "%s"' % FILTERS["winning_box"]["venue"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql

            if FILTERS["winning_box"]["start_date"] != "N/A":
                added_sql = ' and r.date >= "%s"' % FILTERS["winning_box"]["start_date"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql

            if FILTERS["winning_box"]["end_date"] != "N/A":
                added_sql = ' and r.date <= "%s"' % FILTERS["winning_box"]["end_date"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql

            if FILTERS["winning_box"]["distance_minimum"] != "N/A":
                added_sql = ' and r.distance >= "%s"' % FILTERS["winning_box"]["distance_minimum"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql

            if FILTERS["winning_box"]["distance_maximum"] != "N/A":
                added_sql = ' and r.distance <= "%s"' % FILTERS["winning_box"]["distance_maximum"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql

            if FILTERS["winning_box"]["number_of_runners"] != "N/A":
                added_sql = ' and r.no_runners = "%s"' % FILTERS["winning_box"]["number_of_runners"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql

            if FILTERS["winning_box"]["win_pool_size_gt"] != "N/A":
                added_sql = ' and rp.pool_total >= %s' % FILTERS["winning_box"]["win_pool_size_gt"]
                sql_stmt_part1 += added_sql
                sql_stmt_part2 += added_sql

            if FILTERS["winning_box"]["trainer"] != "N/A":
                added_sql = ' and rr2.trainer = "%s"' % FILTERS["winning_box"]["trainer"]
                sql_stmt_part1 += added_sql
                added_sql = ' and rr.trainer = "%s"' % FILTERS["winning_box"]["trainer"]
                sql_stmt_part2 += added_sql

        sql_stmt_part2 += ' group by  rr.box_no'
        sql_stmt = sql_stmt_part1 + sql_stmt_part2
        print "Executing sql: %s" % sql_stmt
        c.execute(sql_stmt)

        c.execute('Drop view if Exists winning_box_details')

        sql_stmt = 'CREATE VIEW winning_box_details AS select *, '
        sql_stmt += ' (no_races*1.0/no_wins) as avg_num_races_between_wins,'
        sql_stmt += ' (win_pool_size*1.0/no_wins) avg_win_payout'
        sql_stmt += ' from winning_box'
        sql_stmt += ' Where 1'

        print "Executing sql: %s" % sql_stmt
        c.execute(sql_stmt)

        c.execute('select *,'
                  ' COALESCE( '
                  ' (((avg_win_payout - 1)/avg_num_races_between_wins) - 1 * (1 - (1/avg_num_races_between_wins)))'
                  ' , 0) as expected_value'
                  ' from winning_box_details')

        rows = c.fetchall()
        for row in rows:
            print row

        keys = ""
        values = ""
        for key, value in sorted(FILTERS["winning_box"].iteritems()):
            keys += key + ","
            values += value + ","

        keys = keys[:-1] + "\n"
        values = values[:-1] + "\n"
        header = keys + values

        header += 'box_no,no_races,no_wins,total_payout,avg_num_races_between_wins,'
        header += 'avg_win_payout,expected_value\n'

        write_to_csv_file("winning_box.csv", header, rows)

    finally:
        conn.commit()
        conn.close()


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
                if option in FILTERS[section].keys():
                    FILTERS[section][option] = config.get(section, option)


def analyze_it():
    """
    Main analysis method.
    """
    print "Please select the type of analysis you would like to do:"
    print "1. Tipsters performance"
    print "2. Winning box"
    print "3. Winning ranking"
    user_input = raw_input("Enter 0 for exit: ")
    while not validate_user_input(user_input):
        user_input = raw_input("The value you enetered is not correct, "
                            "valid inputs are (0, 1, 2, 3): ")

    if user_input == "0":
        return
    elif user_input == "1":
        tipsters_performance()
    elif user_input == "2":
        winning_box()
    elif user_input == "3":
        winning_ranking()

if __name__ == "__main__":
    analyze_it()
