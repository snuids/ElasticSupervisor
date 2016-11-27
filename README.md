# ElasticSupervisor
An Elastic Search health statistics generator.

The application polls the cluster and nodes health and store the results in an configurable index.

Environment variables:

ELASTIC_ADDRESS: The name of the index used to store the statistics (Default=localhost:9201)
INDICE: The name of the index used to store the statistics (Default=elastic_stat)
PERIOD: The time in seconds between two polls (Default=30)

Docker version here: https://hub.docker.com/r/snuids/elasticsupervisor/
