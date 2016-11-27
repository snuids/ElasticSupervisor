import time
import ConfigParser
import os
import json
import requests

from datetime import datetime
from elasticsearch import Elasticsearch

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def GetVariable(vari):
    res=ConfigSectionMap('main')[vari.lower()];
    try:
        res=os.environ[vari]
    except Exception as e:
        print '%s Environment variable not set.' %(vari)
    return res

def createIndexTemplate():
    print "Create index template via a post request."
    global indice,es
    finalindice=indice+"*"

    body={"order":0,"template":finalindice,"settings":{}
    ,"mappings":{"stat":
                {"properties":{"cluster_name":{"index":"not_analyzed","type":"string"},"node":{"index":"not_analyzed","type":"string"},"@timestamp":{"format":"strict_date_optional_time||epoch_millis","type":"date"}}}
                ,"health":
                {"properties":{"cluster_name":{"index":"not_analyzed","type":"string"},"node":{"index":"not_analyzed","type":"string"},"@timestamp":{"format":"strict_date_optional_time||epoch_millis","type":"date"}}}
                ,"aliases":{}}}

    address="http://"+elastic_address+"/_template/elksupervisor";

    r = requests.post(address, data=json.dumps(body))
    print(r.status_code, r.reason)

    print "Index template saved."

print "Start %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S");

Config = ConfigParser.ConfigParser()
Config.read("./conf/elksupervisor.ini")

elastic_address=GetVariable('ELASTIC_ADDRESS')
print "ELASTIC_ADDRESS address:%s" %(elastic_address)

indice=GetVariable('INDICE')
print "INDICE for statistics:%s" %(indice)

period=GetVariable('PERIOD');
print "PERIOD for statistics:%s" %(period)

es = Elasticsearch(hosts=[elastic_address])

def RefreshStats():
    print "Refreshing stats."

    global indice,es,period

    health=es.cluster.health()
    stats=es.nodes.stats()

    bulk_body=""
    bulk_body += '{ "index" : { "_index" : "%s-%s", "_type" : "health"} }\n' %(indice,datetime.now().strftime("%Y.%m.%d"))
    health['@timestamp']=int(time.time())*1000
    bulk_body += json.dumps(health)+'\n'


    for key in stats['nodes']:
        node={}
        node['cluster_name']=health['cluster_name']
        node['node']=stats['nodes'][key]['name']
        node['docs']=stats['nodes'][key]['indices']['docs']['count']
        node['deleted']=stats['nodes'][key]['indices']['docs']['deleted']
        node['store_size_in_kbytes']=stats['nodes'][key]['indices']['store']['size_in_bytes']/1000
        node['cpu_percent']=stats['nodes'][key]['os']['cpu_percent']
        node['load_average']=stats['nodes'][key]['os']['load_average']
        node['mem_total_in_kbytes']=stats['nodes'][key]['os']['mem']['total_in_bytes']/1000
        node['jvm_mem_heap_used_percent']=stats['nodes'][key]['jvm']['mem']['heap_used_percent']
        node['jvm_mem_heap_max_in_kbytes']=stats['nodes'][key]['jvm']['mem']['heap_max_in_bytes']/1000
        node['jvm_mem_heap_used_in_kbytes']=stats['nodes'][key]['jvm']['mem']['heap_used_in_bytes']/1000
        node['@timestamp']=int(time.time())*1000

        bulk_body += '{ "index" : { "_index" : "%s-%s", "_type" : "stat"} }\n' %(indice,datetime.now().strftime("%Y.%m.%d"))
        bulk_body += json.dumps(node)+'\n'

    print "Bulk ready."
    es.bulk(body=bulk_body)
    print "Bulk gone."

    print bulk_body
    time.sleep(float(period))

createIndexTemplate()
for i in range(0,1):
    RefreshStats()
