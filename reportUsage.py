#!/usr/bin/env python
# Prints EC2 instances in txt, html and raw formats in report.txt, report.html and report.yaml correspondingly.
import sys,skew, yaml, prettytable
from pprint import pprint

# for TomTom we must use eu-west-1
if len(sys.argv) > 1 :
    region = sys.argv[1]
else :
    region = '*'

reportHTML = open("report.html", "w")
reportTXT = open("report.txt", "w")
reportRAW = open("report.yaml", "w")

debug = 0

def getAccountName (client) :
    return client._config['accounts'][client.account_id]['profile'] + " (" + client.account_id + ")"

accs = {}

arn = skew.scan('arn:aws:ec2:' + region + ':*:instance/*')
for resource in arn:
    if debug : pprint (vars(resource._client))
    accid = getAccountName(resource._client)
    volumes = [] 
    instanceData = { 
      'State': resource.data['State']['Name'],
      'LaunchTime': resource.data['LaunchTime'].isoformat(' '),
      'Name': resource.tags['Name'],
      'Lifecycle': resource.data['InstanceLifecycle'] if 'InstanceLifecycle' in resource.data else "ondemand",
      'Type': resource.data['InstanceType'],
      'ImageId' : resource.data['ImageId']
    }
    if 'PrivateIpAddress' in resource.data :
        instanceData['PrivateIpAddress'] = resource.data['PrivateIpAddress']

    if 'BlockDeviceMappings' in resource.data :
        for device in resource.data['BlockDeviceMappings'] :
            volumes.append({ 'VolumeId': device['Ebs']['VolumeId'], 
                             "DeviceName": device['DeviceName'],
                             "AttachTime": device['Ebs']['AttachTime'].isoformat(' '),
                             "DeleteOnTermination": device['Ebs']['DeleteOnTermination']
                           })

    if volumes :
        instanceData['Volumes'] = volumes;

    if 'PublicIpAddress' in resource.data :
        instanceData['PublicIpAddress'] = resource.data['PublicIpAddress']

    if 'Placement' in resource.data :
        instanceData['AZ'] = resource.data['Placement']['AvailabilityZone']

    accs.setdefault(accid, {})[resource.id] = instanceData
    if debug : print resource.data

#print yaml.dump(accs,default_flow_style=False)

for accName, accResources in accs.iteritems() :
    table = prettytable.PrettyTable(["Name", "State", "Type", "AMI", "AZ", "Private IP", "Public IP", "Launch Time"])
    table.align["Name"] = "l"
    table.align["Type"] = "l"
    for instanceId, instanceData in accResources.iteritems() :
        privIP = ""
        if 'PrivateIpAddress' in instanceData : 
            privIP = instanceData['PrivateIpAddress']
        publicIP = ""
        if 'PublicIpAddress' in instanceData : 
            publicIP = instanceData['PublicIpAddress']
        az = ""
        if 'AZ' in instanceData : 
            az = instanceData['AZ']
        table.add_row([ instanceData['Name'], instanceData['State'], 
                instanceData['Type'] + "/" + instanceData['Lifecycle'], instanceData['ImageId'],
                az, privIP, publicIP, instanceData['LaunchTime']])
    reportTXT.write(accName + "\n" + table.get_string() + "\n\n")
    table.border = True
    reportHTML.write("<div>" + accName + ":" + table.get_html_string(attributes={"name":"AWS resources", "border": "1"}) + "</div><br/>")

if debug: print yaml.dump(accs)

reportRAW.write(yaml.dump(accs))



