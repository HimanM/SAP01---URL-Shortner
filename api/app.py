import os
import json
import string
import random
import psycopg2
import redis
from flask import Flask, request, jsonify, redirect
from confluent_kafka import Producer
from prometheus_client import Counter, generate_latest
from config import Config

app = Flask(__name__)

# Setup connections
def get_db_connection(replica=False):
    host = Config.DB_REPLICA_HOST if replica else Config.DB_HOST
    return psycopg2.connect(host=host, database=Config.DB_NAME, user=Config.DB_USER, password=Config.DB_PASS)

def log_system_event(level, msg):
    if producer:
        try:
            event = {"level": level, "message": msg, "source": "api"}
            producer.produce('system_logs', value=json.dumps(event).encode('utf-8'))
            producer.flush(0)
        except:
            pass

r = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0, decode_responses=True)

kafka_conf = {'bootstrap.servers': Config.KAFKA_BROKER}
try:
    producer = Producer(kafka_conf)
except Exception as e:
    print(f"Failed to connect to Kafka: {e}")
    producer = None

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.json
    original_url = data.get('url')
    if not original_url:
        return jsonify({"error": "URL is required"}), 400
    
    short_code = generate_short_code()
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO urls (short_code, original_url) VALUES (%s, %s)",
            (short_code, original_url)
        )
        conn.commit()
        log_system_event("INFO", f"DB Write (Primary): Created short_code '{short_code}'")
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()
        
    return jsonify({
        "short_url": f"{Config.BASE_URL}/api/{short_code}",
        "short_code": short_code,
        "original_url": original_url
    }), 201

@app.route('/<short_code>', methods=['GET'])
def redirect_to_url(short_code):
    # Try Redis Cache
    cached_url = r.get(short_code)
    
    if cached_url:
        target_url = cached_url
        log_system_event("INFO", f"Cache Hit: Redis returned URL for '{short_code}'")
    else:
        log_system_event("WARN", f"Cache Miss: '{short_code}' not in Redis. Falling back to DB Replica.")
        # Fallback to DB
        conn = get_db_connection(replica=True)
        cur = conn.cursor()
        cur.execute("SELECT original_url FROM urls WHERE short_code = %s", (short_code,))
        res = cur.fetchone()
        log_system_event("INFO", f"DB Read (Replica): Queried short_code '{short_code}'")
        cur.close()
        conn.close()
        
        if res:
            target_url = res[0]
            # Set cache (1 hour)
            r.setex(short_code, 3600, target_url)
        else:
            return jsonify({"error": "Not Found"}), 404
            
    # Produce Kafka Event
    if producer:
        event = {
            "short_code": short_code,
            "ip_address": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', '')
        }
        producer.produce('url_clicks', value=json.dumps(event).encode('utf-8'))
        producer.flush(0) # trigger delivery callbacks
        
    return redirect(target_url, code=302)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
