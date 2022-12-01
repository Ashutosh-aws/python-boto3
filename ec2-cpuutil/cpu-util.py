from datetime import datetime, timedelta
import boto3
import csv 
import pandas as pd
ec2_ids = []


account_ids=[]
avg1=[]

ec2 = boto3.client('ec2')
ec21 = ec2.describe_instances()

##fetch account id
for i in range(len(ec21["Reservations"])):
    acId = ec21["Reservations"][0]["OwnerId"]
    #print(acId)
    account_ids.append(acId)  ##append all owner ids of instance to account_ids list


now = datetime.utcnow() 
past = now - timedelta(days=14)

##avg function
l=[]
def avg(l):
    return sum(l)/len(l)

##cloudwatch operation on cpu util metric
for reservation in ec21["Reservations"]:
    for instance in reservation["Instances"]:
        #print(instance["InstanceId"])
        ec2_ids.append(instance["InstanceId"])  ##append all ec2 instance id to ec2_ids 

        cloudwatch = boto3.client('cloudwatch')
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[
             {
        
                  'Name': 'InstanceId',
                   'Value': instance["InstanceId"]
             },
                 ],
            StartTime=past,
            EndTime=now,
            Period=1200,
            Statistics=[
                'Average',
            ],
            Unit='Percent'
            )

        
        datapoint_list=[]
        
        for i in range(len(response['Datapoints'])):
            datapoints = response['Datapoints'][i]["Average"]
            datapoint_list.append(datapoints)
        #print("Average is : ",avg(datapoint_list))
            avg1.append(avg(datapoint_list))   #append all avg cpu util of avg1 list
        



#csv config
fields = ['AccountID', 'InstanceID', 'Avg. CPU Utilization'] 
filename = "Instance_records.csv"
with open(filename, 'w') as csvfile: 
    writer = csv.DictWriter(csvfile, fieldnames = fields) 
    writer.writeheader() 
    for i in range(len(ec2_ids)):
      writer.writerow({'AccountID': account_ids[i], 'InstanceID': ec2_ids[i],'Avg. CPU Utilization': avg1[i] })


