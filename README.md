# ElasticSupervisor
An Elastic Search health statistics generator.

The application polls the cluster and nodes health and stores the results in a configurable index.

Environment variables:

ELASTIC_ADDRESS: The name of the index used to store the statistics (Default=localhost:9201)
INDICE: The name of the index used to store the statistics (Default=elastic_stat)
PERIOD: The time in seconds between two polls (Default=30)

Docker version here: https://hub.docker.com/r/snuids/elasticsupervisor/

Two types of documents are generated:

## health
{
  "_index": "elastic_stat-2016.11.27",
  "_type": "health",
  "_id": "AViluLFCQ0dMYYxXxEFk",
  "_score": null,
  "_source": {
    "status": "green",
    "number_of_nodes": 4,
    "unassigned_shards": 0,
    "number_of_pending_tasks": 0,
    "number_of_in_flight_fetch": 0,
    "timed_out": false,
    "active_primary_shards": 3306,
    "task_max_waiting_in_queue_millis": 0,
    "cluster_name": "cluster-cofely",
    "relocating_shards": 0,
    "active_shards_percent_as_number": 100,
    "active_shards": 6522,
    "initializing_shards": 0,
    "@timestamp": 1480249094000,
    "number_of_data_nodes": 3,
    "delayed_unassigned_shards": 0
  },
  "fields": {
    "@timestamp": [
      1480249094000
    ]
  },
  "sort": [
    1480249094000
  ]
}

## stat (One per node)
{
  "_index": "elastic_stat-2016.11.27",
  "_type": "stat",
  "_id": "AViluLFCQ0dMYYxXxEFm",
  "_score": null,
  "_source": {
    "node": "node-C",
    "load_average": 4.22,
    "jvm_mem_heap_used_in_kbytes": 2472166,
    "cpu_percent": 36,
    "deleted": 820,
    "docs": 48317027,
    "@timestamp": 1480249094000,
    "cluster_name": "cluster-cofely",
    "store_size_in_kbytes": 13400591,
    "jvm_mem_heap_max_in_kbytes": 4225236,
    "mem_total_in_kbytes": 33691205,
    "jvm_mem_heap_used_percent": 58
  },
  "fields": {
    "@timestamp": [
      1480249094000
    ]
  },
  "sort": [
    1480249094000
  ]
}
