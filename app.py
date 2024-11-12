from flask import Flask, Response, request, render_template, jsonify
from confluent_kafka import Consumer, Producer, TopicPartition, ConsumerGroupState, ConsumerGroupTopicPartitions
from confluent_kafka.admin import AdminClient, AclBindingFilter, ResourceType, ResourcePatternType, AclOperation, AclPermissionType
import json
import socket

app = Flask(__name__)

is_stop = False

@app.route('/templates/')
def main():
    return render_template('index.html')

@app.route('/templates/index.html')
def index():
    return render_template('index.html')

@app.route('/templates/kafkaConsumer.html')
def kafkaConsumer():
    return render_template('kafkaConsumer.html')

@app.route('/templates/kafkaPublisher.html')
def kafkaPublisher():
    return render_template('kafkaPublisher.html')

@app.route('/kafka/consume/')
def kafka_consume():
    security_protocol = request.args.get('security_protocol')
    bootstrap_servers = request.args.get('bootstrap_servers')
    principal = request.args.get('principal')
    password = request.args.get('password')
    group_id = request.args.get('group_id')
    offset = request.args.get('offset')
    topic = request.args.get('topic')

    try:
        consumer_config = createConsumerConfig(security_protocol, bootstrap_servers, principal, password, group_id, offset)
        consumer = Consumer(consumer_config)
        consumer.subscribe([topic])

        def events():
            global is_stop
            is_stop = False
            while True:
                msg = consumer.poll(1.0)

                if is_stop:
                    consumer.close()
                    yield f"data: Stop to subscribe to {topic}\n\n"
                    return '', 200
                if msg is None:
                    continue
                if msg.error():
                    print("Consumer error: {}".format(msg.error()))
                    continue
                print('Received message: {}'.format(msg.value().decode('utf-8')))
                yield f"data: {msg.value().decode('utf-8')}\n\n"

        return Response(events(), content_type='text/event-stream')

    except Exception as e:
        print(e)

@app.route('/kafka/stopConsume/')
def stop_consume():
    global is_stop
    is_stop = True

    return '', 200

@app.route('/kafka/checkTopic/')
def kafka_checkTopic():
    security_protocol = request.args.get('security_protocol')
    bootstrap_servers = request.args.get('bootstrap_servers')
    principal = request.args.get('principal')
    password = request.args.get('password')
    group_id = request.args.get('group_id')
    offset = request.args.get('offset')
    topic = request.args.get('topic')

    try:
        topic_info = ''
        consumer_config = createConsumerConfig(security_protocol, bootstrap_servers, principal, password, group_id, offset)
        consumer = Consumer(consumer_config)
        topic_list = consumer.list_topics(topic=topic)
        partitions = [TopicPartition(topic, partition) for partition in list(topic_list.topics[topic].partitions.keys())]

        for partition in partitions:
            low_offset, high_offset = consumer.get_watermark_offsets(partition)
            commit_offset = consumer.committed([partition])[0].offset
            if commit_offset > 0:
                lag = "%d" % (high_offset - commit_offset)
            else:
                lag = 0
            topic_info += f'\nTopic = "{topic}" | Partition = {partition.partition} | Lowest offset: {low_offset} | Latest offset: {high_offset} | Committed offset : {commit_offset} | Lag : {lag}'


    except Exception as e:
        topic_info = f'{e}'
    return topic_info

##ongoing
@app.route('/kafka/checkTopicACL/')
def kafka_checkTopicACL():
    security_protocol = request.args.get('security_protocol')
    bootstrap_servers = request.args.get('bootstrap_servers')
    principal = request.args.get('principal')
    password = request.args.get('password')
    group_id = request.args.get('group_id')
    offset = request.args.get('offset')
    topic = request.args.get('topic')

    try:
        acl_info = ''
        consumer_config = createProducerConfig(security_protocol, bootstrap_servers, principal, password)
        consumer = AdminClient(consumer_config)

        acl_binding_filter = AclBindingFilter(
            restype=ResourceType.ANY,
            name=None,
            resource_pattern_type=ResourcePatternType.ANY,
            principal=None,
            host=None,
            operation=AclOperation.ANY,
            permission_type=AclPermissionType.ANY
        )
        acl_info += f'\nacl_binding_filter: {acl_binding_filter}'
        acl_list = consumer.describe_acls(acl_binding_filter, request_timeout=10).result()
        acl_info += f'\nacl_list: {acl_list}'

        for acl_binding in acl_list:
            print(acl_binding)
            acl_info += f'\n{acl_binding}'


    except Exception as e:
        acl_info = f'{e}'
    return acl_info

@app.route('/kafka/checkGroup/')
def kafka_checkGroup():
    security_protocol = request.args.get('security_protocol')
    bootstrap_servers = request.args.get('bootstrap_servers')
    principal = request.args.get('principal')
    password = request.args.get('password')
    group_id = request.args.get('group_id')
    offset = request.args.get('offset')
    topic = request.args.get('topic')

    try:
        group_info = f'\nGroup: {group_id}'
        consumer_config = createProducerConfig(security_protocol, bootstrap_servers, principal, password)
        consumer = AdminClient(consumer_config)
        
        topic_list = consumer.list_topics(topic=topic)
        partitions = [TopicPartition(topic, partition) for partition in list(topic_list.topics[topic].partitions.keys())]
        groups = [ConsumerGroupTopicPartitions(group_id, partitions)]
        futureMap = consumer.list_consumer_group_offsets(groups)
        for group_id, future in futureMap.items():
            response_offset_info = future.result()
            for topic_partition in response_offset_info.topic_partitions:
                group_info += f'\nTopic: {topic_partition.topic} | Partition: {topic_partition.partition} | Offset: {topic_partition.offset}'

    except Exception as e:
        group_info = f'{e}'
    return group_info

@app.route('/kafka/list/')
def kafka_list():
    security_protocol = request.args.get('security_protocol')
    bootstrap_servers = request.args.get('bootstrap_servers')
    principal = request.args.get('principal')
    password = request.args.get('password')
    group_id = request.args.get('group_id')
    offset = request.args.get('offset')

    try:
        topic_list_str = ''
        consumer_config = createConsumerConfig(security_protocol, bootstrap_servers, principal, password, group_id, offset)
        consumer = Consumer(consumer_config)
        topic_list = consumer.list_topics().topics
        for topic in topic_list:
            topic_list_str += str(topic) + ', '

        return topic_list_str

    except Exception as e:
        return f"Fail to list kafka topics: {e}", 400

def createConsumerConfig(security_protocol, bootstrap_servers, principal, password, group_id, offset):
    try:
        consumer_config = {}

        if security_protocol == "PLAINTEXT":
            consumer_config = {
                'bootstrap.servers': bootstrap_servers,
                'group.id': group_id,
                'auto.offset.reset': offset,
                'security.protocol': 'PLAINTEXT',
                'log_level': 4
            }

        if security_protocol == "SASL_PLAINTEXT":

            consumer_config = {
                'bootstrap.servers': bootstrap_servers,
                'group.id': group_id,
                'auto.offset.reset': offset,
                'security.protocol': 'SASL_PLAINTEXT',
                'sasl.mechanism': 'GSSAPI',
                'sasl.kerberos.service.name': 'kafka',
                'sasl.kerberos.kinit.cmd': f'echo -n {password} | kinit -V {principal}',
                'log_level': 4
            }

        return consumer_config

    except Exception as e:
        print(e)
        return None

@app.route('/kafka/publish/', methods=['POST'])
def kafka_publish():
    data = request.get_json()
    security_protocol = data['security_protocol']
    bootstrap_servers = data['bootstrap_servers']
    principal = data['principal']
    password = data['password']
    topic = data['topic']
    message = data['message']

    try:
        producer_config = createProducerConfig(security_protocol, bootstrap_servers, principal, password)
        producer = Producer(producer_config)
        producer.produce(topic, key='', value=message, callback=acked)
        producer.poll(1)
        producer.flush()

    except Exception as e:
        print(e)
        return f'{e}'
    return f'{message} sent to {topic} successfully'

def acked(err, message):
    if err is not None:
        print(err)
    else:
        print(f'Successfully sent {str(message)}')

def createProducerConfig(security_protocol, bootstrap_servers, principal, password):
    try:
        producer_config = {}

        if security_protocol == "PLAINTEXT":
            producer_config = {
                'bootstrap.servers': bootstrap_servers,
                'security.protocol': 'PLAINTEXT',
                'client.id': socket.gethostname()
            }

        if security_protocol == "SASL_PLAINTEXT":

            producer_config = {
                'bootstrap.servers': bootstrap_servers,
                'security.protocol': 'SASL_PLAINTEXT',
                'sasl.mechanism': 'GSSAPI',
                'sasl.kerberos.service.name': 'kafka',
                'sasl.kerberos.kinit.cmd': f'echo -n {password} | kinit -V {principal}',
                'client.id': socket.gethostname(),
                'log_level': 4
            }

        return producer_config

    except Exception as e:
        print(e)
        return None

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)