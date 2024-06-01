from kafka import KafkaProducer, KafkaConsumer
import json

def produce_data(topic, data):
    producer = KafkaProducer(bootstrap_servers='localhost:9092',
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    producer.send(topic, data)
    producer.flush()

def consume_data(topic):
    consumer = KafkaConsumer(topic, bootstrap_servers='localhost:9092',
                             value_deserializer=lambda m: json.loads(m.decode('utf-8')))
    for message in consumer:
        yield message.value

if __name__ == "__main__":
    data = {"example": "data"}
    produce_data('apt_detection', data)
    for message in consume_data('apt_detection'):
        print(message)
