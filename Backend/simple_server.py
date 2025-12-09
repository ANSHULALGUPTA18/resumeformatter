from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# Get the correct database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'templates.db')
print(f"Database path: {DB_PATH}")
print(f"Database exists: {os.path.exists(DB_PATH)}")

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all templates from local database"""
    try:
        print(f"Connecting to database: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, filename, file_type, upload_date FROM templates')
        rows = cursor.fetchall()
        
        templates = []
        for row in rows:
            templates.append({
                'id': row[0],
                'name': row[1],
                'filename': row[2],
                'file_type': row[3],
                'upload_date': row[4]
            })
        
        conn.close()
        print(f"Retrieved {len(templates)} templates from database")
        for t in templates:
            print(f"  - {t['name']} ({t['id']})")
        
        return jsonify({'success': True, 'templates': templates})
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("Starting simple template server on port 5000...")
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"ERROR: Server crashed - {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
