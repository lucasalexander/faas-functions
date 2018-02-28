import sys
import pika
import uuid
import datetime
import json

def get_secret(secret_name):
    try:
        with open('/run/secrets/{0}'.format(secret_name), 'r') as secret_file:
            return secret_file.read()
    except IOError:
        return None

class CrmRpcClient(object):
    def __init__(self):
        #print(get_secret('rabbitsecrets'))
        rabbitdetails = json.loads(get_secret('rabbitsecrets'))
        #RabbitMQ connection details
        self.rabbituser = rabbitdetails['rabbituser']
        self.rabbitpass = rabbitdetails['rabbitpass']
        self.rabbithost = rabbitdetails['rabbithost']
        self.rabbitport = 5672
        self.rabbitqueue = 'rpc_queue'
        rabbitcredentials = pika.PlainCredentials(self.rabbituser, self.rabbitpass)
        rabbitparameters = pika.ConnectionParameters(host=self.rabbithost,
                                    port=self.rabbitport,
                                    virtual_host='/',
                                    credentials=rabbitcredentials)
 
        self.rabbitconn = pika.BlockingConnection(rabbitparameters)
 
        self.channel = self.rabbitconn.channel()
 
        #create an anonymous exclusive callback queue
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
 
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)
 
    #callback method for when a response is received - note the check for correlation id
    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body
 
    #method to make the initial request
    def call(self, n):
        self.response = None
        #generate a new correlation id
        self.corr_id = str(uuid.uuid4())
 
        #publish the message to the rpc_queue - note the reply_to property is set to the callback queue from above
        self.channel.basic_publish(exchange='',
                                   routing_key=self.rabbitqueue,
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=n)
        while self.response is None:
            self.rabbitconn.process_data_events()
        return self.response

def handle(req):
    #instantiate an rpc client
    crm_rpc = CrmRpcClient()
 
    #read the request from the command line
    request = req
 
    #make the request and get the response
    #print(" [x] Requesting crm data("+request+")")
    #print(" [.] Start time %s" % str(datetime.datetime.now()))
    response = crm_rpc.call(request)
 
    #convert the response message body from the queue to a string 
    decoderesponse = response.decode()
 
    #print the output
    print(" [.] Received response: %s" % decoderesponse)
    #print(" [.] End time %s" % str(datetime.datetime.now()))