# import os
# import json
# import psycopg2
#
#
# # database_access = json.load({
# #     "database": "apm_missions",
# #     "user": "postgres",
# #     "host": "docker.for.mac.localhost",
# #     "password": "123456",
# #     "port": "33121"
# # })
# #
# # fields = json.loads({
# #     "global_position_int": ["id", "lat" , "lon" , "alt" , "vx" , "vy" , "vz" , "hdg", "timestamp" , "time_boot_ms", "uuid"],
# #     "mavsim_command": ["id" , "command" , "ack" , "timestamp"],
# #     "battery_status": ["id" , "battery_remaining" , "timestamp"],
# #     "wind": ["id" , "direction" , "speed" , "speed_z" , "timestamp"],
# #     "simulation_session": ["begin", "end", "session_uuid", "timestamp"]
# # })

import os
import json
import psycopg2

#import pandas as pd


def mavsim_time(timestamp):
    """ This function converts a datetime object to a string format.
    """
    return datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")


def psycopg2_query_to_dataframe(columns, rows):
    """ This function takes a set of columns and rows and converts them
        into a pandas dataframe.
    """
    dataframe = pd.DataFrame(rows, columns=columns)
    return dataframe


def save_data(directory_path, dataframes):
    """ This function saves a dictionary of dataframes and saves each
        one to a file named after that dataframe in the directory
        provided by the `directory_path` argument.
    """
    for dataframe_name, dataframe in dataframes.items():
        file_name = dataframe_name + '.csv'
        file_path = os.path.join(directory_path, file_name)
        dataframe.to_csv(file_path)


class PostgreSQLExtractor(object):
    """ This class is used for creating a connection to a PostgreSQL
        database and collecting all the data in a set of features.
    """

    def __init__(self, database, user, host, password, port, fields):
        self.database = database
        self.user = user
        self.host = host
        self.password = password
        self.port = port
        self.fields = fields

    def establish_connection(self):
        """ This method establishes a connection to the postgres database.
        """

        con = psycopg2.connect(
            "dbname='{}' user='{}' host='{}' password='{}' port='{}'".format(
                self.database,
                self.user,
                self.host,
                self.password,
                self.port
            )
        )
        self.con = con
        self.cur = con.cursor()

    def pull_data(self):
        """ This method sends a select query to the postgres database
            and saves all the data in a dictionary of dataframes.
        """
        data = {}
        dataframes = {}
        for table in self.fields.keys():
            quoted_columns = ['"' + column + '"' for column in self.fields[table]]
            quoted_columns = ','.join(quoted_columns)
            query = 'SELECT {} FROM {}'.format(quoted_columns, table)
            data[table] = {'columns': self.fields[table]}
            print(query)
            self.cur.execute(query)
            rows = self.cur.fetchall()
            data[table]['data'] = rows
            print(data[table])
            #dataframes[table] = psycopg2_query_to_dataframe(self.fields[table], rows)

        self.data = data
        self.dataframes = dataframes


def main():
    database_access_file_path = 'ardupilot_sitl_postgres_login.json'

    database_access = {
        "database": "apm_missions",
        "user": "postgres",
        "host": "localhost",
        "password": "sterling",
        "port": "32768"
    }

    fields = {
        "global_position_int": ["id", "lat", "lon", "alt", "vx", "vy", "vz", "hdg", "timestamp", "time_boot_ms",
                                "uuid"],
        #"mavsim_command": ["id", "command", "ack", "timestamp"],
        #"battery_status": ["id", "battery_remaining", "timestamp"],
        #"wind": ["id", "direction", "speed", "speed_z", "timestamp"],
        #"simulation_session": ["begin", "end", "session_uuid", "timestamp"]
    }

    postgresql_extractor = PostgreSQLExtractor(
        database=database_access['database'],
        user=database_access['user'],
        host=database_access['host'],
        password=database_access['password'],
        port=database_access['port'],
        fields=fields,
    )

    postgresql_extractor.establish_connection()
    postgresql_extractor
    postgresql_extractor.pull_data()
    save_data('/workspace/raw_postgres_data/', postgresql_extractor.dataframes)


if __name__ == '__main__':
    main()

#48f13756bbe04bfc884acc18d30509e8