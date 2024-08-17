import sys
import sqlite3
import re
import time
from hyperloglog import HyperLogLog

def process_sqlite_hll(db_path, table_name, column_name):
    hll = HyperLogLog(precision=14)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fetch data in batches to handle large datasets
    batch_size = 1000
    offset = 0
    
    while True:
        cursor.execute(f"SELECT {column_name} FROM {table_name} LIMIT {batch_size} OFFSET {offset}")
        rows = cursor.fetchall()
        
        if not rows:
            break
        
        for row in rows:
            text = row[0]
            if text:
                words = re.findall(r'\w+', text.lower())
                for word in words:
                    hll.add(word)
        
        offset += batch_size
    
    conn.close()
    return hll.count()

def process_sqlite_exact(db_path, table_name, column_name):
    unique_words = set()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fetch data in batches to handle large datasets
    batch_size = 1000
    offset = 0
    
    while True:
        cursor.execute(f"SELECT {column_name} FROM {table_name} LIMIT {batch_size} OFFSET {offset}")
        rows = cursor.fetchall()
        
        if not rows:
            break
        
        for row in rows:
            text = row[0]
            if text:
                words = re.findall(r'\w+', text.lower())
                unique_words.update(words)
        
        offset += batch_size
    
    conn.close()
    return len(unique_words)

def main():
    if len(sys.argv) != 4:
        print("Usage: python hll_sqlite.py <db_path> <table_name> <column_name>")
        sys.exit(1)

    db_path = sys.argv[1]
    table_name = sys.argv[2]
    column_name = sys.argv[3]

    # HyperLogLog estimation
    start_time = time.time()
    hll_result = process_sqlite_hll(db_path, table_name, column_name)
    hll_time = time.time() - start_time

    # Exact counting
    start_time = time.time()
    exact_result = process_sqlite_exact(db_path, table_name, column_name)
    exact_time = time.time() - start_time

    error_percentage = abs(hll_result - exact_result) / exact_result * 100
    time_saved = exact_time - hll_time

    print("\nComparison of HyperLogLog vs Exact Counting (SQLite)")
    print("-" * 58)
    print(f"{'Method':<15}{'Count':<10}{'Time (s)':<12}{'Error (%)':<10}")
    print("-" * 58)
    print(f"{'HyperLogLog':<15}{hll_result:<10d}{hll_time:<12.4f}{error_percentage:<10.2f}")
    print(f"{'Exact':<15}{exact_result:<10d}{exact_time:<12.4f}{'N/A':<10}")
    print("-" * 58)
    print(f"Time Saved: {time_saved:.4f} seconds")

if __name__ == '__main__':
    main()