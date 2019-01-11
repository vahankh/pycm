import mysql.connector
import logging

from core.pycmUtils import plural
from core.pycm import pycm

class pycmModel(pycm):

    _config = None
    _dbCon = None
    _cursor = None

    _tableName = None
    # _alias = None
    _primary_key = None

    lastrowid = None
    errorMessage = None

    def __init__(self, dbConfig, table=None):

        self._config = dbConfig;

        if pycmModel._dbCon is None:
            logging.info("--- Connecting to MariaDB ---")
            pycmModel._dbCon = mysql.connector.connect(**dbConfig)

        if not table is None:
            self._tableName = table
        elif self._tableName is None:
            self._tableName = plural(self.__class__.__name__.lower())

        if self._primary_key is None:
            self._primary_key = self.__class__.__name__.lower() + "_id"

    def __del__(self):
        if not pycmModel is None and not pycmModel._cursor is None:
            pycmModel._cursor.close()
            pycmModel._dbCon.close();

    def _validate_connection(fnc):
        def magic(*args, **kwargs):
            _self = args[0]
            if not pycmModel._dbCon.is_connected():
                print("MySQL Connection is dead. Reconnecting!")
                pycmModel._dbCon = mysql.connector.connect(**_self._config)

            return fnc(*args, **kwargs)

        return magic

    # if length is 0 fetch all rows
    # @_validate_connection
    def _fetch(self, length=1, commit=False):
        if pycmModel._cursor == None:
            return False

        try:

            if length == 0:
                result = pycmModel._cursor.fetchall()
            else:
                result = pycmModel._cursor.fetchmany(length)

            # to force results not to be cached
            #			if commit:
            pycmModel._dbCon.commit()

            if length == 0 or len(result) < length:
                pycmModel._cursor.close()
                pycmModel._cursor = None

            if length == 1 and result:
                result = result[0]

            return result

        except Exception as e:
            self._error(repr(e))
            return False

    @_validate_connection
    def _query(self, query, commit=False, fetchAssoc=False):
        if pycmModel._dbCon is None:
            pycmModel._dbCon = mysql.connector.connect(**self._config)

        if not pycmModel._cursor == None:
            pycmModel._cursor.close()

        pycmModel._cursor = self._dbCon.cursor(dictionary=fetchAssoc)
        pycmModel._cursor.execute(query)

        # if data is not requested close the cursor otherwise keep it for data fetching
        if not pycmModel._cursor.with_rows:
            pycmModel.lastrowid = pycmModel._cursor.lastrowid
            pycmModel._cursor.close()
            pycmModel._cursor = None

        if commit:
            pycmModel._dbCon.commit()

        return True

    def escape_string(self, str_to_escape):
        return pycmModel._dbCon.converter.escape(str_to_escape)


    def query(self, query, commit=False, fetchAssoc=True):

        normalized_query = query.lower().strip()
        if self._query(query, commit, fetchAssoc) \
                and (normalized_query.startswith("select") or normalized_query.startswith("show")):
            return self._fetch(0)

        return True

    def _error(self, message):
        self.errorMessage = message

    # def set_alias(self, short_name):
    #     self._alias = short_name

    def save(self, data):
        header = data.keys()
        values = data.values()

        if self.saveList(header, [values]):
            return pycmModel.lastrowid
        else:
            return False

    def update(self, id, dict):
        set_str = ", ".join(["`{0}`='{1}'".format(col, val) for col, val in dict.items()])
        sql = "UPDATE `%s` SET %s WHERE `%s`=%d" % (self._tableName, set_str, self._primary_key, id)

        self.last_query = sql
        self._query(sql, True)
        return True

    def saveList(self, header, data):

            headerString = "`" + '`, `'.join(header) + "`"

            values = []

            for row in data:
                if isinstance(row, dict):
                    row = row.values()

                rowValues = []
                for rowValue in row:
                    try:
                        valueType = type(rowValue)
                        if valueType is int or valueType is float or (rowValue is not None and 'NOW()' in rowValue):
                            rowValues.append(str(rowValue))
                        elif rowValue is None:
                            rowValues.append("NULL")
                        else:
                            rowValues.append("'" + rowValue + "'")
                    except:
                        print(row)
                        raise

                valueString = "(" + ', '.join(rowValues) + ")"
                values.append(valueString)

            sql = "INSERT INTO `%s` (%s) values %s" % (self._tableName, headerString, ', '.join(values));

            self.last_query = sql
            # print(sql)
            self.query(sql, True)

            return True







        #     print 'saveList exception'
        #     print self._tableName + '\n' + repr(e)
        #     self._error(self._tableName + '\n' + repr(e))
        #     return False


    def get(self, id):
        result = self.select(conditions="%s=%d" % (self._primary_key, id))
        if len(result)>0:
            return result[0]
        return result

    # simple query builder which can be improved later on
    # not all blocks of this function code are tested and serve mainly as placeholders for future development
    # columns - list of columns or comma separated column list
    # joins - can be list of sql join strings or just join string (no list) if only one join is needed
    # conditions - can be list of sql condition strings or just a condition string (no list)
    #			   conditions will be joined using AND logic
    # orderBy - list or single order by clause
    # limit - row limit, mandatory in order to control memory load
    def select(self, columns="*", joins=None, conditions=None, orderBy=None, groupBys=None, limit=1000, fetchAssoc=True):

        if self._tableName is None:
            return False

        if isinstance(columns, list):
            sql = "SELECT %s FROM `%s`" % (", ".join(columns), self._tableName)
        else:
            sql = "SELECT %s FROM `%s`" % (columns, self._tableName)

        if not joins is None:
            if isinstance(joins, list):
                sql += " " + " ".join(joins)
            else:
                sql += " " + joins

        if not conditions is None:
            sql += " WHERE "
            if isinstance(conditions, list):
                sql += " AND ".join(conditions)
            else:
                sql += conditions

        if not orderBy is None:
            sql += " ORDER BY "
            if isinstance(orderBy, list):
                sql += " ".join(orderBy)
            else:
                sql += " " + orderBy

        if not groupBys is None:
            sql += " GROUP BY "
            if isinstance(groupBys, list):
                sql += " ".join(groupBys)
            else:
                sql += " " + groupBys

        if not limit is None:
            sql += " LIMIT " + str(limit)

        self.last_query = sql

        if self._query(sql, fetchAssoc=fetchAssoc):
            return self._fetch(0)  # fetch all
        else:
            return False

    def delete(self, conditions=None, soft_delete=None):

        if self._tableName is None:
            return False

        if not soft_delete is None:
            set_str = ', '.join(key+"='"+str(value)+"'" for key, value in soft_delete.iteritems())
            sql = "UPDATE `%s` SET %s" % (self._tableName, set_str)
        else:
            sql = "DELETE FROM `%s`" % (self._tableName)

        if not conditions is None:
            sql += " WHERE "
            if isinstance(conditions, list):
                sql += " AND ".join(conditions)
            else:
                sql += conditions

        self.last_query = sql
        return self._query(sql, commit=True)



    def fetchDictionary(self, columnName, keyName):
        result = self.select(keyName + ',' + columnName)

        if result == False:
            return False

        dictionary = {}
        for row in result:
            dictionary[row[0]]

        return dictionary
