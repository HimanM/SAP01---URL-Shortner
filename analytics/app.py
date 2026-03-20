import os
import psycopg2
from flask import Flask, jsonify
from psycopg2.extras import RealDictCursor
from config import Config

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(host=Config.DB_HOST, database=Config.DB_NAME, user=Config.DB_USER, password=Config.DB_PASS)

@app.route('/<short_code>', methods=['GET'])
def get_stats(short_code):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT COUNT(*) as clicks FROM clicks WHERE short_code = %s", (short_code,))
        res = cur.fetchone()
        
        cur.execute("SELECT ip_address, user_agent, created_at FROM clicks WHERE short_code = %s ORDER BY created_at DESC LIMIT 10", (short_code,))
        recent_clicks = cur.fetchall()
        
        return jsonify({
            "short_code": short_code,
            "total_clicks": res['clicks'],
            "recent_clicks": recent_clicks
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/top-links', methods=['GET'])
def get_top_links():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT short_code, COUNT(*) as clicks 
            FROM clicks 
            GROUP BY short_code 
            ORDER BY clicks DESC 
            LIMIT 10
        """)
        top_links = cur.fetchall()
        return jsonify(top_links)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/system-stats', methods=['GET'])
def get_system_stats():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT COUNT(*) as total_clicks_system FROM clicks")
        clicks_res = cur.fetchone()
        
        cur.execute("SELECT COUNT(DISTINCT short_code) as unique_links FROM clicks")
        unique_links_res = cur.fetchone()
        
        return jsonify({
            "total_clicks": clicks_res['total_clicks_system'],
            "unique_links_clicked": unique_links_res['unique_links']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
