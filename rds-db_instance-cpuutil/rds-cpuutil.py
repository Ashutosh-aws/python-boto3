import csv
from datetime import datetime, timedelta
import boto3

rds_list=[]
avg_datapoints=[]
vpc_list=[]
engine_list=[]

rds =  boto3.client('rds')
rds_response = rds.describe_db_instances()

for i in range(len(rds_response["DBInstances"])):
    #print(rds_response["DBInstances"][i]["Engine"])
    vpc_list.append(rds_response["DBInstances"][i]["Engine"])  ##append all vpc  to list

#print(vpc_list)

for i in range(len(rds_response["DBInstances"])):
    #print(rds_response["DBInstances"][i]["DBSubnetGroup"]["VpcId"])
    engine_list.append(rds_response["DBInstances"][i]["DBSubnetGroup"]["VpcId"])  ##append all rengine name to list

#print(engine_list)

client = boto3.client('cloudwatch')

##average function
l=[]
def avg(l):
    return sum(l)/len(l)


now = datetime.utcnow() 
past = now - timedelta(days=14)

for i in range(len(rds_response["DBInstances"])):
    #print(rds_response["DBInstances"][i]["DBInstanceIdentifier"])
    rds_list.append(rds_response["DBInstances"][i]["DBInstanceIdentifier"])  ##append all rds instances name to list


    response = client.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName='CPUUtilization',
                Dimensions=[
                {
            
                    'Name': 'DBInstanceIdentifier',
                    'Value': rds_list[i]
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

    datapoints=[]
    #print(response)

    for i in range(len(response["Datapoints"])):
        data = response['Datapoints'][i]["Average"]
        datapoints.append(data)
        #print(datapoints)
    avg_datapoints.append(avg(datapoints))

    
#print(avg_datapoints)
#print(rds_list)

#csv config
fields = ['DB-name','VPC-id','Engine' ,'Avg. CPU Utilization'] 
filename = "RDS_records.csv"
with open(filename, 'w') as csvfile: 
    writer = csv.DictWriter(csvfile, fieldnames = fields) 
    writer.writeheader() 
    for i in range(len(rds_response["DBInstances"])):
      writer.writerow({'DB-name': rds_list[i], 'VPC-id': vpc_list[i], 'Engine': engine_list[i], 'Avg. CPU Utilization': avg_datapoints[i] })


