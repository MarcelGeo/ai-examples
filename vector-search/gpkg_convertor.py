import sqlite3

class GPKGConverter:
    """
    Converts a GeoPackage file to AI ready markdown texts.
    """
    def __init__(self, source: str):
        self.source = source

    def __convert_table(self, table_name: str):
        # Open the GeoPackage file
        with sqlite3.connect(self.source) as conn:
            # Create a cursor object
            conn.enable_load_extension(True)
            conn.load_extension('mod_spatialite')
            conn.execute("SELECT EnableGpkgMode()")
            cursor = conn.cursor()
            # get reasonable columns names
            cursor.execute("PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            geom_tables = cursor.execute("SELECT table_name, columns_name FROM gpkg_geometry_columns;").fetchall()
            select_names = []
            geom_columns = [t[1] for t in geom_tables]
            is_geom_table = table_name in [t[0] for t in geom_tables]
            for col in columns:
                if col[1] in geom_columns:
                    select_names.append(f"AsText({col[1]})")
                else:
                    select_names.append(f"{col[1]}")

            cursor.execute(f"""SELECT {", ".join(select_names)} FROM {table_name}""")
            data = cursor.fetchall()

            for row in data:
                row_dict = dict(zip([col[1] for col in columns], row))

    def __dict_to_sentence(self, dict):
        # convert dictionary to sentencte
        sentence = ""
        for key, value in dict.items():
            sentence += f"{key} {value},"
        return sentence

    def __convert_query(self, query: str):
        # Execute query and fetch data as text ready vor vectorization
        with sqlite3.connect(self.source) as conn:
            conn.enable_load_extension(True)
            conn.load_extension('mod_spatialite')
            conn.execute("SELECT EnableGpkgMode()")
            cursor = conn.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            # get columns of query
            columns = [entry[0] for entry in cursor.description]
            result = []
            for row in data:
                row_dict = dict(zip([col for col in columns], row))
                # convert dictionary to sentencte
                result.append((self.__dict_to_sentence(row_dict), row_dict))
            return result

    def convert(self, query: str) -> list[tuple[str, dict]]:
        return self.__convert_query(query)

