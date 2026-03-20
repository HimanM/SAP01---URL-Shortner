import os
import json
import time
import psycopg2
from confluent_kafka import Consumer, KafkaError, KafkaException
from config import Config

def get_db_connection():
    return psycopg2.connect(host=Config.DB_HOST, database=Config.DB_NAME, user=Config.DB_USER, password=Config.DB_PASS)

def run_worker():
    conf = {
        'bootstrap.servers': Config.KAFKA_BROKER,
        'group.id': 'analytics_worker_group',
        'auto.offset.reset': 'earliest'
    }

    consumer = Consumer(conf)
    
    # Wait for topics to be available/created
    time.sleep(10)
    
    consumer.subscribe(['url_clicks', 'system_logs'])
    print("Worker started. Listening to 'url_clicks' and 'system_logs' topics...")
    
    try:
        conn = get_db_connection()
    except Exception as e:
        print(f"Failed to connect to DB: {e}")
        return
        
    cur = conn.cursor()

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    continue
                elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                    time.sleep(1)
                    continue
                else:
                    print(f"Kafka Error: {msg.error()}")
                    time.sleep(1)
                    continue
            
            # Process Message
            topic = msg.topic()
            val = msg.value().decode('utf-8')
            event = json.loads(val)
            
            if topic == 'url_clicks':
                short_code = event.get('short_code')
                ip_address = event.get('ip_address')
                user_agent = event.get('user_agent')
                
                try:
                    cur.execute(
                        "INSERT INTO clicks (short_code, ip_address, user_agent) VALUES (%s, %s, %s)",
                        (short_code, ip_address, user_agent)
                    )
                    conn.commit()
                    print(f"Recorded click for {short_code}")
                except Exception as e:
                    print(f"DB Error: {e}")
                    conn.rollback()
            elif topic == 'system_logs':
                level = event.get('level')
                message = event.get('message')
                source = event.get('source')
                
                try:
                    cur.execute(
                        "INSERT INTO system_logs (level, message, source) VALUES (%s, %s, %s)",
                        (level, message, source)
                    )
                    conn.commit()
                    print(f"Recorded log: {message}")
                except Exception as e:
                    print(f"DB Log Error: {e}")
                    conn.rollback()

    except KeyboardInterrupt:
        pass
    finally:
        cur.close()
        conn.close()
        consumer.close()

if __name__ == '__main__':
    # Add a retry loop to connect to DB and wait for PG to start
    connected = False
    retries = 10
    while not connected and retries > 0:
        try:
            get_db_connection().close()
            connected = True
        except Exception as e:
            print(f"Waiting for DB... {e}")
            time.sleep(5)
            retries -= 1
            
    if connected:
        run_worker()
    else:
        print("Could not connect to database after retries. Exiting.")
