#!/usr/bin/env python
#coding:utf-8

import boto.ec2
import re
import json
import time

# 读取变量

## boto2
conn = boto.ec2.connect_to_region("ap-northeast-1",aws_access_key_id='test',aws_secret_access_key='test',debug=2)
def create_instance(info=[]):
    # 创建seuciryt!!!!!!!!!!!!!!!!!!!!!
    instance_vpcid = "!!!"
    security_name = "security-%s"%info[0]
    security_ports = info[7].split("__")
    web = conn.create_security_group(security_name, security_name, vpc_id = instance_vpcid)
    for security_port in security_ports:
        web.authorize('tcp', security_port, security_port, '0.0.0.0/0')
    web.authorize('-1',-1,-1,'172.31.0.0/16')
    # 创建instance
    instance_name = info[0]
    instance_type = info[1]
    instance_disksize = info[2]
    instance_imageid = info[4]
    #instance_keyname = info[5]
    instance_keyname = "tokyo_tmp" #!!!!!!!!!!!!!!!!!!!!!
    instance_count = int(info[6])
    instance_placements = [ info[3]+'a', info[3] + 'c'] #!!!!!!!!!!!!!!!!
    #instance_placements = [ 'subnet-c2a33ea7', 'subnet-d242948b'] #!!!!!!!!!!!!!!!!!!
    if info[8] == "public":
        # 公有子网，每个可用区一个
        instance_subnetids = [ 'subnet-38cf4e', 'subnet-b05ee8' ] #!!!!!!!!!!!!!!!!!!
    elif info[8] == "private":
        # 私有子网，每个可用区一个
        instance_subnetids = [ 'subnet-ef8b99', 'subnet-d70c88'] #!!!!!!!!!!!!!!!!

    ## 准备磁盘
    dev_sda1 = boto.ec2.blockdevicemapping.EBSBlockDeviceType()
    dev_sda1.size = instance_disksize  # size in Gigabytes
    dev_sda1.volume_type = "gp2"
    bdm = boto.ec2.blockdevicemapping.BlockDeviceMapping()
    bdm['/dev/sda1'] = dev_sda1
    # 绑定security到instance
    for count in range(instance_count):
        instance_placement = instance_placements[count%2]
        instance_subnetid = instance_subnetids[count%2]
        print "instance subnetid: %s"%instance_subnetid
	print "security Name : %s"%security_name
        #reservation = conn.run_instances(image_id=instance_imageid, key_name=instance_keyname,instance_type=instance_type, placement = instance_placement, subnet_id = instance_subnetid, security_groups = [security_name], block_device_map = bdm )
        reservation = conn.run_instances(image_id=instance_imageid, key_name=instance_keyname,instance_type=instance_type, placement = instance_placement, subnet_id = instance_subnetid, security_group_ids = [web.id], block_device_map = bdm )
        # 添加tag为主机名
        instance = reservation.instances[0]
        status = instance.update()
        while status == 'pending':
            time.sleep(10)
            status = instance.update()
        if status == 'running':
            instance.add_tag("Name", instance_name)
        else:
            print('Instance status: ' + status)
            return None

def main():
    with open("./instances.csv") as f:
        for line in f:
            #print line
            info = []
            info = line.replace("\r","").replace("\n","").split(",")
            print info
            if len(info) == 9:
                create_instance(info)
            else:
                print "该行不满足执行条件！"
                continue

main()
#create_security()
