import sqlite3

def patch():
    conn = sqlite3.connect(r'd:\Redhope\redhope.db')
    try:
        conn.execute('ALTER TABLE users ADD COLUMN latitude REAL')
        print("Added latitude")
    except Exception as e:
        print(f"latitude error: {e}")
        
    try:
        conn.execute('ALTER TABLE users ADD COLUMN longitude REAL')
        print("Added longitude")
    except Exception as e:
        print(f"longitude error: {e}")
        
    conn.commit()
    conn.close()

if __name__ == '__main__':
    patch()
