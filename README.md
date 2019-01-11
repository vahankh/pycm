# Python Controller Mode CLI Framework

PYCM is designed to run various command line scripts and tools for MMS and Seeds. It simplifies argument parsing and code management

### Running in a container

PYCM is coded with Python 3.6 and uses Couchbase Python SDK and Python MySQL connector. It's recommended to use the the engine using the [python3.6.mysql.couchbase](https://hub.docker.com/r/vahankh/python3.6.mysql.couchbase/) container.
To do it simply run:
```bash
docker run --name pycl --restart unless-stopped -dit -w /opt/pycl -v ~/pycl:/opt/pycl -v /var/log/pycl:/var/log/pycl  vahankh/python3.6.mysql.couchbase
```
### Help

To request information about supported calls run:
```bash
docker exec -it mmpycls ./run.py --help
```

To get help for specific call run:
```bash
docker exec -it pycl ./run.py sync/seeds --help
```

The Help output is generated automatically using a controller's function docstring. For more details please check the provided samples.

### Execution script

Supply required arguments to execute a call.
```bash
docker exec -it pycl ./run.py controller/action --argument=1000
```
