# Kafka_Tool
Lightweight web tool for real-time data streaming, built with confluent-kafka-python.

## Quick Start

### 1. Install [Docker](https://www.docker.com/)
### 2. Run run_kafka_tool.bat
       This will automatically check if Docker is installed on your computer. If it is, it will proceed with the following commands in sequence:
       (1) docker image build -t kafka-tool:test ./
       (2) docker run -p 8080:5000 kafka-tool:test
       (3) start http://localhost:8080/templates/kafkaConsumer.html
### 3. Installation and startup successful
       Access the kafka tool through http://localhost:8080/templates/index.html

## Introduction

This is a lightweight Kafka tool that provides Consumer and Publisher functionality. The tool supports both `PLAINTEXT` and `SASL_PLAINTEXT` security protocols, with `SASL_PLAINTEXT` using `GSSAPI`. When selecting `SASL_PLAINTEXT`, you need to enter the corresponding SASL principal and password to successfully connect to the bootstrap server.

After entering the bootstrap server, the connection will be established automatically. The icon next to the topic will show the connection result. If it is a green checkmark, it means the connection is successful, and `the topics section will automatically display a dropdown list of all topics` that the entered principal has permission to read. If it is a red cross, it means the connection failed, and the logs section will record the reason for the failure.

### Consumer

![Consumer](images/consumer.png)

| Buttons | Functions |
| ------- | ------- |
| Subscribe  | Start consuming the topic  |
| Unsubscribe  | Stop consuming the topic  |
| CheckTopic  | List all partitions in the topic along with their latest offsets, earliest offsets, committed offsets, and latency  |
| CheckTopicACL  | List Access Control Lists (ACLs) for the topic  |
| CheckGroup  | List all topics subscribed to by the group ID  |
| Clear  | Reset all inputs  |

### Publisher

![Publisher](images/publisher.png)

| Buttons | Functions |
| ------- | ------- |
| Publish  | Publish message to topic  |
| Clear  | Reset all inputs  |

##
