#!/bin/sh
# AWS DSM instance create script 
start_time="$(date -u +%s)"

# Change awsRegionName to your AWS Region
awsRegionName=us-east-1 
jumpRemoteMGMTSGName=JumpHost-Remote-Mgmt-sg
jumpclusterSGName=JumpHost-2-Cluster-sg
dsmvtsSGName=DSM-VTS-Cluster-sg
jumpHostAMIName=ami-059eeca93cf09eebd
awstag=mytagvtssplit
awsAZ1=us-east-1a
awsAZ2=us-east-1b
jumphostsubnet=subnet-f3aab8ae

aws configure set default.region $awsRegionName
#find our vpc
vpcID=$(aws ec2 describe-vpcs --query 'Vpcs[*][VpcId]' --output text |  sort -r | head -1)
echo "vpcid=$vpcID"
#could have mutliple dsm ami's. find most recent one.
dsmAMI=$(aws ec2 describe-images --owners self --query 'Images[*][CreationDate , Name,ImageId]' --output text | grep dsm | sort -r | head -1 | awk '{print $3}')
echo "dsmami=$dsmAMI"
#could have mutliple vts ami's. find most recent one.
vtsAMI=$(aws ec2 describe-images --owners self --query 'Images[*][CreationDate , Name,ImageId]' --output text | grep vts | sort -r | head -1 | awk '{print $3}')
echo "vtsAMI=$vtsAMI"
#Create the jumpRemoteMGMTSG security groups
jumpRemoteMGMTSG=$(aws ec2 create-security-group --group-name $jumpRemoteMGMTSGName --description "jumpHost-Remote-Mgmt-sg" --vpc-id $vpcID --output text)
echo "jumpRemoteMGMTSG=$jumpRemoteMGMTSG"
#Create the jumpclusterSG security groups
jumpclusterSG=$(aws ec2 create-security-group --group-name $jumpclusterSGName --description "JumpHost-2-Cluster-sg" --vpc-id $vpcID --output text)
echo "jumpclusterSG=$jumpclusterSG"
#Create the DSM and VTS security groups
dsmvtsSG=$(aws ec2 create-security-group --group-name $dsmvtsSGName --description "DSM-VTS-Cluster-sg" --vpc-id $vpcID --output text)
echo "dsmvtsSG=$dsmvtsSG"

#ip=$(curl https://checkip.amazonaws.com/)
#cidr="$ip/24"
cidr="0.0.0.0/0"
echo "using cidr of $cidr"
echo "Setting jumpRemoteMGMTSG rules"
aws ec2 authorize-security-group-ingress --group-id $jumpRemoteMGMTSG --protocol tcp --port 22 --cidr $cidr
aws ec2 authorize-security-group-ingress --group-id $jumpRemoteMGMTSG --protocol tcp --port 3389 --cidr $cidr

echo "Setting jumpclusterSG rules"
aws ec2 authorize-security-group-ingress --group-id $jumpclusterSG --protocol tcp --port 22 --source-group $jumpRemoteMGMTSG 
aws ec2 authorize-security-group-ingress --group-id $jumpclusterSG --protocol tcp --port 443 --source-group $jumpRemoteMGMTSG 
#aws ec2 authorize-security-group-ingress --group-id $jumpclusterSG --protocol icmp --port 0-65535 --source-group $jumpRemoteMGMTSG 

echo "Setting DSM inbound rules"
aws ec2 authorize-security-group-ingress --group-id $dsmvtsSG --protocol tcp --port 0-65535 --source-group $dsmvtsSG 
#aws ec2 authorize-security-group-ingress --group-id $dsmvtsSG --protocol icmp --port 0-65535 --source-group $dsmvtsSG --cidr $cidr

awsSubnet1=$(aws ec2 create-subnet --vpc-id $vpcID --availability-zone $awsAZ1 --cidr-block ___insert_ip_address_range1___/20  | grep SubnetId | awk '{print $2}' | tr -d '"' | tr -d ',')
echo "awsSubnet1=$awsSubnet1"
awsSubnet2=$(aws ec2 create-subnet --vpc-id $vpcID --availability-zone $awsAZ2 --cidr-block ___insert_ip_address_range2___/20  | grep SubnetId | awk '{print $2}' | tr -d '"' | tr -d ',')
echo "awsSubnet2=$awsSubnet2"

echo "Creating DSM Instance "
#Create DSM instance.  Need the subnet so VTS and Agent can be in same network.
dsmInstanceId=$(aws ec2 run-instances --image-id $dsmAMI --count 1 --instance-type m4.large --security-group-ids $dsmvtsSG $jumpclusterSG --subnet-id $awsSubnet1 | grep InstanceId | awk '{print $2}' | tr -d '"' | tr -d ',')
if [ $? -ne 0 ]; then
   echo "Failed to Create DSM instance"
   exit 1
fi
echo "dsmInstanceId=$dsmInstanceId"

echo "Creating VTS Instance "
vtsInstanceId=$(aws ec2 run-instances --image-id $vtsAMI --count 1 --instance-type t2.xlarge --security-group-ids $dsmvtsSG $jumpclusterSG  --subnet-id $awsSubnet1  |  grep InstanceId | awk '{print $2}' | tr -d '"' | tr -d ',')
if [ $? -ne 0 ]; then
   echo "Failed to Create VTS instance"
   exit 1
fi
echo "vtsInstanceId=$vtsInstanceId"

echo "Creating VTE Ubuntu instance "
jump1InstanceId=$(aws ec2 run-instances --image-id $jumpHostAMIName --count 1 --instance-type t2.micro --key-name MyKeyPair --security-group-ids $jumpRemoteMGMTSG --subnet-id $jumphostsubnet | grep InstanceId | awk '{print $2}' | tr -d '"' | tr -d ',')
if [ $? -ne 0 ]; then
   echo "Failed to Create $jumpHostAMIName instance"
   exit 1
fi

#second DSM and VTS in different AZ
echo "Creating DSM Instance "
#Create DSM instance.  Need the subnet so VTS and Agent can be in same network.
dsmInstanceId2=$(aws ec2 run-instances --image-id $dsmAMI --count 1 --instance-type m4.large --security-group-ids $dsmvtsSG $jumpclusterSG --subnet-id $awsSubnet2 | grep InstanceId | awk '{print $2}' | tr -d '"' | tr -d ',')
if [ $? -ne 0 ]; then
   echo "Failed to Create DSM instance"
   exit 1
fi
echo "dsmInstanceId2=$dsmInstanceId2"

#dsmSubnet=$(aws ec2 describe-instances --instance-ids $dsmInstanceId --query 'Reservations[0].Instances[0].SubnetId' | tr -d '"')
echo "Creating VTS Instance "
vtsInstanceId2=$(aws ec2 run-instances --image-id $vtsAMI --count 1 --instance-type t2.xlarge --security-group-ids $dsmvtsSG $jumpclusterSG  --subnet-id  $awsSubnet2 |  grep InstanceId | awk '{print $2}' | tr -d '"' | tr -d ',')
if [ $? -ne 0 ]; then
   echo "Failed to Create VTS instance"
   exit 1
fi
echo "vtsInstanceId2=$vtsInstanceId2"

aws ec2 create-tags --resources $dsmInstanceId $vtsInstanceId $dsmInstanceId2 $vtsInstanceId2 $jump1InstanceId  --tags Key=owner,Value=$awstag
cat <<EOF
Summary of Vormetric Run
DSM instance ID: $dsmInstanceId
DSM instance ID2: $dsmInstanceId2
VTS instance ID: $vtsInstanceId
VTS instance ID2: $vtsInstanceId2
JumpHost instance ID: $jump1InstanceId
EOF

end_time="$(date -u +%s)"
elapsed="$(($end_time-$start_time))"
echo "Total of $elapsed seconds elapsed for process"
echo "Done "
exit 0
