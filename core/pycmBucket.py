import logging
import time
import json


from couchbase.cluster import Cluster
from couchbase.cluster import PasswordAuthenticator
import couchbase.subdocument as SD


# from couchbase.bucket import Bucket
from couchbase.n1ql import N1QLQuery, CONSISTENCY_REQUEST
from couchbase.exceptions import CouchbaseError, KeyExistsError, NotFoundError, SubdocPathExistsError
from couchbase.n1ql import N1QLError

from datetime import datetime

from core.pycm import pycm

class pycmBucket(pycm):
    _host = None
    _creds = None

    username = None
    _userpass = None

    bucket_name = None
    # _creds = None

    _cb = None

    # _timezone = "UTC"
    # _utc_offset = None

    retry_timeouts = [1,3,10,20]  # in seconds

    def __init__(self, bucket_name, host, username, password, creds=None):

        self._host = host
        self.username = username
        self._userpass = password

        # couch_bucket_url = 'couchbase://{0}/{1}'.format(host, bucket_name)

        cluster = Cluster('couchbase://{0}'.format(host))
        authenticator = PasswordAuthenticator(username, password)
        cluster.authenticate(authenticator)
        # print(bucket_name)
        self._cb = cluster.open_bucket(bucket_name)

        if self.bucket_name is None:
            self.bucket_name = bucket_name

        self._cb.n1ql_timeout = 5000*1000
        self._cb.timeout = 5000*1000
        self._cb.config_total_timeout  = 5000*1000
        # self._cb.cross_bucket = True
        self._cb.operationTimeout = 5000*1000

        if creds is not None:
            self._creds = creds

            # for cred in self._creds:
            #     self._cb.add_bucket_creds(cred['user'], cred['pass'])

        # if 'tz' in options:
        #     self._timezone = options['tz']
        #
        # if 'retry_timeouts' in options:
        #     self.retry_timeouts = options['retry_timeouts']
        #
        # if 'creds' in options:
        #     self._creds = options['creds']

        # server_timezone = pytz.timezone(self._timezone)
        # utc_offset = server_timezone.localize(datetime.now()).strftime("%z")
        # self._utc_offset = utc_offset[:3] + ":" + utc_offset[3:]

    def save_document(self, key, doc):
        retry_i = 0
        while True:
            try:
                self._cb.upsert(key, doc)
                return True

            except CouchbaseError:
                logging.debug("--- key: {0}; data: {1} ---".format(key, json.dumps(doc)))
                logging.exception("--- Failed to execute upsert. ---")

                if retry_i < len(self.retry_timeouts):
                    logging.debug(
                        "--- Waiting for {0} seconds before trying again ---".format(self.retry_timeouts[retry_i]))
                    time.sleep(self.retry_timeouts[retry_i])
                    logging.debug("--- Trying one more time (attempt #{0}) ---".format(retry_i))
                else:
                    logging.info("--- Giving up on upsert ---")
                    return False

                retry_i += 1

    def n1ql_query(self, n1ql, consistent=False):
        retry_i = 0
        if not n1ql.strip().endswith(";"):
            n1ql = n1ql + ";"

        n1qlObj = N1QLQuery(n1ql)
        n1qlObj.timeout = 3600

        if self._creds is not None:
            n1qlObj.set_option("creds", self._creds)
            # n1qlObj.set_option("creds", [{"user": "mms_events", "pass": "123456"}])
            # n1qlObj.adhoc = False
            # n1qlObj.consistency = 'not_bounded'
            # n1qlObj.cross_bucket = True

        if consistent:
            n1qlObj.consistency = CONSISTENCY_REQUEST

        n1qlObj.adhoc = True

        logging.debug("Executing: " + n1ql);

        while True:
            try:
                result = self._cb.n1ql_query(n1qlObj)

                if not n1ql.upper().lstrip(' \t\n\r').startswith("SELECT") and 'RETURNING' not in n1ql.upper():
                    result.execute()

                logging.info("--- Query executed successfully ---")
                return result

            except KeyboardInterrupt:
                raise
            # except N1QLError as e:
            #     raise
            except:
                logging.error("Failed query %s" % n1ql)
                logging.exception("--- Failed to execute query. ---")

                if retry_i < len(self.retry_timeouts):
                    logging.debug(
                        "--- Waiting for {0} seconds before trying again ---".format(self.retry_timeouts[retry_i]))
                    time.sleep(self.retry_timeouts[retry_i])
                    logging.debug("--- Trying one more time (attempt #{0}) ---".format(retry_i))
                else:
                    logging.info("--- Giving up on query ---")
                    logging.info(n1ql)
                    return False
                retry_i += 1

    def update(self, id, dict):
        """id can be string in Couchbase"""
        set_str = ", ".join(["`{0}`='{1}'".format(col, val) for col, val in dict.items()])
        sql = "UPDATE `%s` SET %s WHERE meta().id='%s'" % (self.bucket_name, set_str, id)

        self.last_query = sql
        return self.n1ql_query(sql)

    def select(self, columns="*, meta().id as meta_id", joins=None, conditions=None, orderBy=None, groupBys=None, limit=1000, consistent=False):

        if self.bucket_name is None:
            return False

        if isinstance(columns, list):
            sql = "SELECT %s FROM `%s`" % (", ".join(columns), self.bucket_name)
        else:
            sql = "SELECT %s FROM `%s`" % (columns, self.bucket_name)

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

        result = self.n1ql_query(sql, consistent)

        if not result:
            return False

        if joins is None:

            final_result = []
            for i in result:

                if self.bucket_name in i:
                    v = i[self.bucket_name]
                else:
                    v = i

                if v is None or not type(v) is dict:
                    continue

                if 'meta_id' in i and 'meta_id' not in v:
                    v['meta_id'] = i['meta_id']
                final_result.append(v)

            return final_result
            # return [i[self.bucket_name] for i in result]

        return result

    def upsert(self, key, doc, cas=0):
        return self._cb.upsert(key, doc, cas)

    def sd_get(self, key, path):
        return self._cb.lookup_in(key, SD.get(path))

    def sd_upsert(self, key, path, doc, cas=None):
        if cas is not None:
            return self._cb.mutate_in(key, SD.upsert(path, doc, True), cas=cas)
        else:
            return self._cb.mutate_in(key, SD.upsert(path, doc, True))

    def sd_insert(self, key, path, doc, cas=None):
        if cas is not None:
            return self._cb.mutate_in(key, SD.insert(path, doc), cas=cas)
        else:
            return self._cb.mutate_in(key, SD.insert(path, doc))

    def sd_array_addunique(self, key, path, val):
        try:
            return self._cb.mutate_in(key, SD.array_addunique(path, val, create_parents=True))
        except SubdocPathExistsError:
            return True

    def insert(self, key, doc):

        try:
            logging.debug("Inserting document having key: %s " % key)
            result = self._cb.insert(key, doc)
        except KeyExistsError:
            return False

        return result

    def get(self, key):
        try:
            result = self._cb.get(key)

        except (KeyExistsError, NotFoundError):
            return False

        return result

    def remove(self, key):
        return self._cb.remove(key, quiet=True)

    def remove_multi(self, keys):
        return self._cb.remove_multi(keys, quiet=True)

    def upsert_multi(self, upsert_data):
        retry_i = 0

        logging.info("Upserting documents");

        if len(upsert_data) == 0:
            logging.info("multi_upsert of zero len. Exiting")
            return

        while True:
            try:
                self._cb.upsert_multi(upsert_data)

                logging.info("--- Query executed successfully ---")
                return True

            except KeyboardInterrupt:
                raise
            except:
                logging.exception("--- Failed to execute upsert_multi. ---")

                if retry_i < len(self.retry_timeouts):
                    logging.debug(
                        "--- Waiting for {0} seconds before trying again ---".format(self.retry_timeouts[retry_i]))
                    time.sleep(self.retry_timeouts[retry_i])
                    logging.debug("--- Trying one more time (attempt #{0}) ---".format(retry_i))
                else:
                    logging.info("--- Giving up on upsert_multi ---")
                    return False
                retry_i += 1

