#TODO change module name
class SQLiteHandler:

    def __init__(self, database):
        import sqlite3 as lite
        self.connection = lite.connect(database)
        self.cursor = self.connection.cursor()


    def getComponentTableCount(self):

        component_count = len(self.cursor.execute("SELECT * FROM components").fetchall())
        # return component_count
        return component_count

    def closeDatabase(self):
        self.cursor.close()
        self.connection.close()

    def getComponents(self):
        component_tuple = self.cursor.execute("SELECT * FROM components").fetchall()
        return component_tuple

    def tableExists(self, table):
        try:
            self.cursor.execute("select * from " + table + " limit 1").fetchall()
        except:
            return False
        return True
    #String, integer -> String
    def getComponentData(self, column, row):
        if column != '':
            values = self.cursor.execute("select " + column + " from components limit ?", [row+1]).fetchall()

            if (len(values) > row) :
                value = values[row][0]
                if value is not None:
                    return value

        return

    def createRefTable(self, tablename):
        self.cursor.execute("DROP TABLE  If EXISTS " + tablename)
        self.cursor.execute("""
        CREATE TABLE """ + tablename +
                            """( 
                            _id integer primary key,
                            sort_order integer,
                        code text unique,
                        description text);
                            """
                            )
        self.connection.commit()
    #String, ListOfTuples -> None
    def addRefValues(self, tablename, values):

        self.cursor.executemany("INSERT INTO " + tablename + "(sort_order,code, description) VALUES (?,?,?)" ,values)
        self.connection.commit()

    def makeDatabase(self):

        refTables = [
            'ref_component_attribute',
            'ref_component_type',
            'ref_datetime_format',
            'ref_data_format',
            'ref_power_units',
            'ref_attributes',
            'ref_time_units',
            'ref_speed_units',
            'ref_flow_units',
            'ref_voltage_units',
            'ref_current_units',
            'ref_irradiation_units',
            'ref_temperature_units',
            'ref_universal_units',
            'ref_true_false',
            'ref_env_attributes',
            'ref_frequency_units'
        ]
        for r in refTables:
            self.createRefTable(r)
        self.addRefValues('ref_current_units',[(0,'A','amps'),(1,'kA','kiloamps')])
        self.addRefValues('ref_frequency_units',[(0, 'Hz','hertz')])
        self.addRefValues('ref_temperature_units',[(0,'C','Celcius'),(1,'F','Farhenheit'),(2,'K','Kelvin')])
        self.addRefValues('ref_irradiation_units',[(0,'W/m2','Watts per square meter')])
        self.addRefValues('ref_flow_units',[(0,'m3/s', 'cubic meter per second'),(1, 'L/s', 'liters per second'),
                                            (2, 'cfm', 'cubic feet per meter'),(3,'gal/min','gallon per minute')])
        self.addRefValues('ref_voltage_units',[(0,'V','volts'),(1, 'kV','kilovolts')])
        self.addRefValues('ref_true_false',[(0,'T','True'),(1,'F','False')])
        self.addRefValues('ref_speed_units', [(0, 'm/s','meters per second'),(1,'ft/s','feet per second'),
                                              (2,'km/hr','kilometers per hour'),(3,'mi/hr','miles per hour')])
        self.addRefValues('ref_time_units',[(0,'S','Seconds'),(1,'m','Minutes')])
        self.addRefValues('ref_datetime_format',[(0,'Ordinal','Ordinal'),(1,'Excel','Excel')])

        self.addRefValues('ref_data_format',[(0,'CSV + wind', 'Load information is in a csv, wind data is in a tab delimmited text file'),
                                             (1,'AVEC CSV', 'All data is within a single CSV file')
                            ])

        self.addRefValues('ref_component_type' ,[(0,'wtg', 'windturbine'),
        (1,'gen', 'diesel generator'), (2,'inv','inverter'),(3,'tes','thermal energy storage'),(4, 'ees','energy storage')])

        self.addRefValues('ref_power_units',[(0,'W', 'watts'), (1,'kW', 'Kilowatts'),(2,'MW','Megawatts'),
                                             (3, 'var', 'vars'),(4,'kvar','kilovars'),(5,'Mvar','Megavars'),
                                             (6, 'VA','volt-ampere'),(7,'kVA','kilovolt-ampere'),(8,'MVA','megavolt-ampere')])

        self.addRefValues('ref_env_attributes', [(0,'WS', 'Windspeed'), (1,'IR', 'Solar Irradiation'),
                                                 (2,'WF','Waterflow'),(3,'Tamb','Ambient Temperature')])
        self.addRefValues('ref_attributes' ,[(0,'P', 'Real Power'), (1,'Q','Reactive Power'),(2,'S','Apparent Power'),
                                             (3,'PF','Power Factor'),(4,'V','Voltage'),(5, 'I', 'Current'),
                                             (6, 'f', 'Frequency'), (7,'TStorage','Internal Temperature Thermal Storage'),
                                             (8,'PAvail','Available Real Power'), (9,'QAvail','Available Reactive Power'),
                                             (10,'SAvail','Available Apparent Power')])

        #TODO stop deleting components

        self.cursor.execute("DROP TABLE IF EXISTS components")
        self.cursor.executescript("""CREATE TABLE components
         (_id integer primary key,
         original_field_name text,
         component_type text,
         component_name text,
         units text,
         scale numeric,
         offset numeric,
         attribute text,
         p_in_maxpa numeric,
         q_in_maxpa numeric, 
         q_out_maxpa numeric,
         is_voltage_source text,
         tags text,
         FOREIGN KEY (component_type) REFERENCES ref_component_type(code),
         FOREIGN KEY (units) REFERENCES ref_universal_units(code),
         FOREIGN KEY (attribute) REFERENCES ref_attributes(code),
         FOREIGN KEY (is_voltage_source) REFERENCES ref_true_false(code)
         );""")
        #TODO remove test components
        self.cursor.executemany("INSERT INTO components (original_field_name, component_type, component_name, scale) values (?,?,?,?)",
                                [('Hank', 'wtg','wtg1P',1),('gen1','gen','gen1P',3)])

        self.connection.commit()
    def getRefInput(self, tables):
        #table is a list of tables
        import pandas as pd
        # create list of values for a combo box
        valueStrings = []
        for t in tables:
            values = pd.read_sql_query("SELECT code, description FROM " + t + " ORDER By sort_order", self.connection)

            for v in range(len(values)):
                valueStrings.append(values.loc[v, 'code'] + ' - ' + values.loc[v, 'description'])
        return valueStrings

    def getHeaders(self,table):
        #Todo read from database
        headers = self.cursor.execute("select sql from sqlite_master where name = " + table + " and type = 'table'")

        return headers
    #String, String -> Boolean
    def hasRef(self,column):

        sql = self.cursor.execute("SELECT sql FROM sqlite_master WHERE type = 'table' and name = 'components'").fetchone()
        if column + ') references ' in sql[0].lower():
            return True
        return False
    def getRef(self,column):
        s1 = self.cursor.execute("SELECT sql FROM sqlite_master WHERE type = 'table' and name = 'components'").fetchone()
        s1 = s1[0].lower()
        s2 = column + ") references "
        table = s1[s1.find(s2) + len(s2):].replace("(code)", "")
        table = table.replace(")","")
        table = table.split(",")[0]

        table = table.strip()

        return table

    def getCodes(self,table):

        import pandas as pd
        codes = pd.read_sql_query("select code from " + table + " ORDER BY sort_order", self.connection)

        codes = (codes['code']).tolist()

        return codes