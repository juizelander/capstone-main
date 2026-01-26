import sqlite3
import os

db_path = 'db.sqlite3'
if not os.path.exists(db_path):
    print("DB file not found")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(home_program)")
        columns = cursor.fetchall()
        print("Columns in home_program:")
        for col in columns:
            print(col)
        
        # Check if program_type is present
        found = any(c[1] == 'program_type' for c in columns)
        print(f"\nprogram_type found: {found}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
