import crhelper
import boto3
import os
s3_client = boto3.client('s3')
s3 = boto3.resource('s3')
dynamodb = boto3.client('dynamodb')
s3_bucket_name = os.environ['s3BucketName']
api_endpoint_url = os.environ['apiEndpointURL']
# initialise logger
logger = crhelper.log_config({"RequestId": "CONTAINER_INIT"})
logger.info('Logging configured')
# set global to track init failures
init_failed = False

try:
    # Place initialization code here
    logger.info("Container initialization completed")
except Exception as e:
    logger.error(e, exc_info=True)
    init_failed = e


def create(event, context):
    """
    Place your code to handle Create events here.
    
    To return a failure to CloudFormation simply raise an exception, the exception message will be sent to CloudFormation Events.
    """
    logger.info("Loading sample Data to DynamoDb")
    dynamodb = boto3.client('dynamodb')
    courses_items= [['Python','Python','','Lima-Lucas','3','Programming'],['Java','Java','','Noah-Jack','3','Programming'],['Nodejs','Nodejs','','Michael-Oliver','2','Programming'],['Go','Go','','Martin-Simon','4','Programming'],['C','C','','Joseph-Mason','6','Programming']]
    authors_items= [['Lima-Lucas','Lima','Lucas'],['Noah-Jack','Noah','Jack'],['Oliver-Ben','Oliver','Ben'],['Michael-Oliver','Michael','Oliver'],['Joseph-Mason','Joseph','Mason'],['Martin-Simon','Martin','Simon']]
    for item in authors_items:
        dynamodb.put_item(TableName='authors', Item={'id':{'S':item[0]},'firstName':{'S':item[1]},'lastName':{'S':item[2]}})
    for item in courses_items:
        dynamodb.put_item(TableName='courses', Item={'id':{'S':item[0]},'title':{'S':item[1]},'watchHref':{'S':item[2]},'authorId':{'S':item[3]},'length':{'S':item[4]},'category':{'S':item[5]}})
    logger.info("loading sample Data to DynamoDb has been completed")
    logger.info("loading static website files to s3")
    src_bucket_name = 'attya-public-files-shared-2021'
    src_prefix = ''
    dest_bucket_name = s3_bucket_name
    src_bucket = s3.Bucket(src_bucket_name)
    dest_bucket = s3.Bucket(dest_bucket_name)
    for obj in src_bucket.objects.filter(Prefix=src_prefix):
        old_source = { 'Bucket': src_bucket_name,
                       'Key': obj.key}
        # replace the prefix
        new_obj = dest_bucket.Object(obj.key)
        new_obj.copy(old_source)

    #modify js file with the correct api endpoint
    s3_client.download_file(s3_bucket_name, 'static/js/main.5feaed36.js', '/tmp/main.5feaed36.js')
    #read input file
    fin = open("/tmp/main.5feaed36.js", "rt")
    #read file contents to string
    data = fin.read()
    #replace all occurrences of the required string
    data = data.replace('THIS-IS-TO-BE-REPLACED-WITH-API-ENDPOINT', api_endpoint_url)
    #close the input file
    fin.close()
    #open the input file in write mode
    fin = open("/tmp/main.5feaed36.js", "wt")
    #overrite the input file with the resulting data
    fin.write(data)
    #close the file
    fin.close()
    s3_client.upload_file('/tmp/main.5feaed36.js', s3_bucket_name, 'static/js/main.5feaed36.js')

    physical_resource_id = 'myResourceId'
    response_data = {}
    return physical_resource_id, response_data
'''
def update(event, context):
    """
    Place your code to handle Update events here
    
    To return a failure to CloudFormation simply raise an exception, the exception message will be sent to CloudFormation Events.
    """
    physical_resource_id = event['PhysicalResourceId']
    response_data = {}
    return physical_resource_id, response_data

'''
def delete(event, context):
    """
    Place your code to handle Delete events here
    
    To return a failure to CloudFormation simply raise an exception, the exception message will be sent to CloudFormation Events.
    """
    bucket = s3.Bucket(s3_bucket_name)
    bucket.objects.all().delete()
    return


def handler(event, context):
    """
    Main handler function, passes off it's work to crhelper's cfn_handler
    """
    # update the logger with event info
    global logger
    logger = crhelper.log_config(event)
    return crhelper.cfn_handler(event, context, create, create, delete, logger,
                                init_failed)