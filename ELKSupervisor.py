import time
import ConfigParser
import re
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
                ,"indice":
                {"properties":{"name":{"index":"not_analyzed","type":"string"}}}
                ,"aliases":{}}}

    address="http://"+elastic_address+"/_template/elksupervisor";

    r = requests.post(address, data=json.dumps(body))

    print "Index template saved."

print "Version v0.1f"
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
template_list=[]

def updateIndicesStats():
    global template_list

    template_list=[]

    address="http://"+elastic_address+"/_template";

    r = requests.get(address)
    templates=json.loads(r.text)

    for key in templates:
        template={};
        template['name']=templates[key]['template'];
        template['docs']=0;
        template['size']=0;
        template['@timestamp']=int(time.time())*1000

        template_list.append(template)


    address="http://"+elastic_address+"/_stats";

    r = requests.get(address)
    indices=json.loads(r.text)
    for key in indices['indices']:
        found=False

        for i in range(0,len(template_list)):
            template_pattern = template_list[i]['name'] if template_list[i]['name'] != '*' else '.*'
            searchObj = re.search( template_pattern, key, re.M|re.I)
            if(searchObj):
                found=True;
                template_list[i]['size']+=indices['indices'][key]['total']['store']['size_in_bytes'];
                template_list[i]['docs']+=indices['indices'][key]['total']['docs']['count']
                break;

        if(not found):
            template={};
            template['name']=key;
            template['docs']=indices['indices'][key]['total']['docs']['count'];
#            print indices['indices'][key]['total']['store']
            template['size']=indices['indices'][key]['total']['store']['size_in_bytes'];
            template['@timestamp']=int(time.time())*1000

            template_list.append(template)

    bulk_body=""

    print "LEN=%d" %(len(template_list))

    for i in range(0,len(template_list)):
        bulk_body += '{ "index" : { "_index" : "%s-%s", "_type" : "indice"} }\n' %(indice,datetime.now().strftime("%Y.%m.%d"))
        template_list[i]['name']=template_list[i]['name'].replace('*','');
        bulk_body += json.dumps(template_list[i])+'\n'

#    print bulk_body
    print "Bulk ready."
    es.bulk(body=bulk_body)
    print "Bulk gone."


def refreshStats():
    print "Refreshing stats."

    global indice,es,period

    health=es.cluster.health()
    stats=es.nodes.stats()

    bulk_body=""
    bulk_body += '{ "index" : { "_index" : "%s-%s", "_type" : "health"} }\n' %(indice,datetime.now().strftime("%Y.%m.%d"))
    health['@timestamp']=int(time.time())*1000
    bulk_body += json.dumps(health)+'\n'

#    print json.dumps(stats);

    for key in stats['nodes']:
        node={}
        node['cluster_name']=health['cluster_name']
        node['node']=stats['nodes'][key]['name']
        node['docs']=stats['nodes'][key]['indices']['docs']['count']
        node['deleted']=stats['nodes'][key]['indices']['docs']['deleted']
        node['store_size_in_kbytes']=stats['nodes'][key]['indices']['store']['size_in_bytes']/1000

        if('cpu_percent' in stats['nodes'][key]['os']): # Elastic version<5.0
            node['cpu_percent']=stats['nodes'][key]['os']['cpu_percent']
            node['load_average']=stats['nodes'][key]['os']['load_average']
        else:
            node['cpu_percent']=stats['nodes'][key]['os']['cpu']['percent']
            node['load_average_1m']=stats['nodes'][key]['os']['cpu']['load_average']['1m']
            node['load_average_5m']=stats['nodes'][key]['os']['cpu']['load_average']['5m']
            node['load_average_15m']=stats['nodes'][key]['os']['cpu']['load_average']['15m']

        node['mem_total_in_kbytes']=stats['nodes'][key]['os']['mem']['total_in_bytes']/1000
        node['jvm_mem_heap_used_percent']=stats['nodes'][key]['jvm']['mem']['heap_used_percent']
        node['jvm_mem_heap_max_in_kbytes']=stats['nodes'][key]['jvm']['mem']['heap_max_in_bytes']/1000
        node['jvm_mem_heap_used_in_kbytes']=stats['nodes'][key]['jvm']['mem']['heap_used_in_bytes']/1000
        node['@timestamp']=int(time.time())*1000

        bulk_body += '{ "index" : { "_index" : "%s-%s", "_type" : "stat"} }\n' %(indice,datetime.now().strftime("%Y.%m.%d"))
        bulk_body += json.dumps(node)+'\n'

    print "Bulk ready."
    es.bulk(body=bulk_body,timeout='1m')
    print "Bulk gone."

    time.sleep(float(period))

createIndexTemplate()

while True:
    updateIndicesStats()
    refreshStats()
