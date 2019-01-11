from core.pycmBucket import pycmBucket

from couchbase.exceptions import CouchbaseError, KeyExistsError, NotFoundError

class Sample(pycmBucket):

    bucket_name = "sample"
