# Python Controller Mode CLI Framework

PYCM is designed to run various command line scripts and tools for MMS and Seeds. It simplifies argument parsing and code management

### Running in a container

PYCM is coded with Python 3.6 and uses Couchbase Python SDK and Python MySQL connector. It's recommended to use the the engine using the [python3.6.mysql.couchbase](https://hub.docker.com/r/vahankh/python3.6.mysql.couchbase/) container.
To do it simply run:
```bash
docker run --name mms --restart unless-stopped --network host -dit -w /opt/mms_engine -v /root/mms_tools/mms_engine:/opt/mms_engine -v /data/vulcan/incoming:/data/vulcan/incoming -v /var/log/adxg:/var/log/adxg vahankh/python3.6.mysql.couchbase
```
### Help

To request information about supported calls run:
```bash
docker exec -it mms ./run.py --help
```

To get help for specific call run:
```bash
docker exec -it mms ./run.py sync/seeds --help
```
### Execution script

Supply required arguments to execute a call.
```bash
docker exec -it mms ./run.py sync/seeds --seeds_chunk_size=1000
```

> NOTE: When putting docker command in cron `-it` option should be removed. It requires pseudo terminal and the command runs in interactive mode while cron doesn't attach to any TTYs
