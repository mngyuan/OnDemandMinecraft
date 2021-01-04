from configuration import Config
from multiprocessing import Process
import time
import paramiko
import os

#Paraminko ssh information
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, Config.SSH_KEY_FILE_PATH)
key = paramiko.RSAKey.from_private_key_file(filename)
sshClient = paramiko.SSHClient()
sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#Waits for the server to reach a valid state so that commands can be executed on the server
def serverWaitOk(instanceIp, client):

    checksPassed = False
    status = 'initializing'
    instanceIds=[Config.INSTANCE_ID]

    while (not checksPassed) and (status == 'initializing'):
        statusCheckResponse = client.describe_instance_status(InstanceIds = instanceIds)
        instanceStatuses = statusCheckResponse['InstanceStatuses']
        instanceStatus = instanceStatuses[0]
        instanceStatus = instanceStatus['InstanceStatus']
        status = instanceStatus['Status']
        checksPassed = status == 'ok'
        time.sleep(5)
    
    if checksPassed:
        initServerCommands(instanceIp)
    else:
        print('An error has occurred booting the server')
    
#SSH connects to server and executes command to boot minecraft server
def initServerCommands(instanceIp):
    # Connect/ssh to an instance
    try:
        # Here 'ubuntu' is user name and 'instance_ip' is public IP of EC2
        sshClient.connect(hostname=instanceIp, username="ubuntu", pkey=key)

        # Execute a command(cmd) after connecting/ssh to an instance
        stdin, stdout, stderr = sshClient.exec_command("screen -dmS minecraft bash -c 'sudo java " + Config.MEMORY_ALLOCATION + "-jar server.jar nogui'")
        print("COMMAND EXECUTED")
        # close the client connection once the job is done
        sshClient.close()

    except:
        print('Error running server commands')

#Gets IP Address for return to webpage otherwise boots server
def manageServer(client):
    returnString = 'ERROR'

    instanceIds = [Config.INSTANCE_ID]
    response = client.describe_instances(InstanceIds = instanceIds)
    reservations = response['Reservations']
    reservation = reservations[0]

    instances = reservation['Instances']
    
    print("\nSERVER INSTANCES\n")
    print(instances)
    print("\n")
    if len(instances) > 0:
        instance = instances[0]
        state = instance['State']
        stateName = state['Name']

        if (stateName == 'stopped') or (stateName == 'shutting-down'):
            #SETUP MULTIPROCESSING HERE INSTEAD OF REDIS
            returnString = startServer(client)
        elif stateName == 'running':
            returnString = 'IP: ' + instance['PublicIpAddress']
        else:
            returnString = 'ERROR'
    return returnString

#Starts the specified AWS Instance from the configuration
def startServer(client):
    #Gets proper variables to attempt to instantiate EC2 instance and start minecraft server
    returnString = 'ERROR'
    instanceIds = [Config.INSTANCE_ID]
    response = client.start_instances(InstanceIds = instanceIds)

    stateCode = 0

    while not (stateCode == 16):
        time.sleep(3)

        print('\nAWS EC2 START RESPONSE\n')
        print(str(response))
        print('\n')

        response = client.describe_instances(InstanceIds = instanceIds)
        reservations = response['Reservations']
        reservation = reservations[0]

        instances = reservation['Instances']
        instance = instances[0]

        state = instance['State']
        stateCode = state['Code']
        
        print("\nSERVER INSTANCES\n")
        print(instances)
        print("\n")
        
    ipAddress = instance['PublicIpAddress']
    returnString = 'Server is starting, this may take a few minutes.\nIP: ' + ipAddress
    #SETUP MULTIPROCESSING HERE INSTEAD OF REDIS
    p = Process(target=serverWaitOk, args=(ipAddress, client))
    p.start()
    return returnString

