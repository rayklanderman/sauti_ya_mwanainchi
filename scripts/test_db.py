import os
import sys

# Add PostgreSQL binary path to system PATH
postgres_path = r"C:\Program Files\PostgreSQL\17\bin"
if postgres_path not in os.environ["PATH"]:
    os.environ["PATH"] = postgres_path + os.pathsep + os.environ["PATH"]

import psycopg2
from psycopg2 import OperationalError

def test_connection():
    try:
        # Connect to default database first
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="coding2066",
            host="localhost",
            port="5432"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if our database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='sauti_ya_mwananchi'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Creating database 'sauti_ya_mwananchi'...")
            cursor.execute("CREATE DATABASE sauti_ya_mwananchi")
            print("Database created successfully!")
        else:
            print("Database 'sauti_ya_mwananchi' already exists!")
            
        cursor.close()
        conn.close()
        
        # Test connection to our database
        conn = psycopg2.connect(
            dbname="sauti_ya_mwananchi",
            user="postgres",
            password="coding2066",
            host="localhost",
            port="5432"
        )
        print("Successfully connected to sauti_ya_mwananchi database!")
        conn.close()
        
    except OperationalError as e:
        print(f"Error: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Check if PostgreSQL service is running")
        print("2. Verify password is correct")
        print("3. Ensure PostgreSQL is running on port 5432")
        print("4. Check if firewall is blocking connections")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing PostgreSQL connection...")
    test_connection()
