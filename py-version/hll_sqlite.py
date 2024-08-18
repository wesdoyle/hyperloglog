import sys
import sqlite3
import re
import time
from memory_profiler import profile
from hyperloglog import HyperLogLog

@profile
def process_sqlite_hll(db_path, table_name, column_name, precision):
    hll = HyperLogLog(precision=precision)
    
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

@profile
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
    if len(sys.argv) != 5:
        print("Usage: python hll_sqlite.py <db_path> <table_name> <column_name> <precision>")
        sys.exit(1)

    db_path = sys.argv[1]
    table_name = sys.argv[2]
    column_name = sys.argv[3]
    precision = int(sys.argv[4])

    # HyperLogLog estimation
    hll_result = process_sqlite_hll(db_path, table_name, column_name, precision)

    # Exact counting
    exact_result = process_sqlite_exact(db_path, table_name, column_name)
    error_percentage = abs(hll_result - exact_result) / exact_result * 100

    print("\nComparison of HyperLogLog vs Exact Counting (SQLite)")
    print("-" * 58)
    print(f"{'Method':<15}{'Count':<10}{'Error (%)':<10}")
    print("-" * 58)
    print(f"{'HyperLogLog':<15}{hll_result:<10d}{error_percentage:<10.2f}")
    print(f"{'Exact':<15}{exact_result:<10d}{'N/A':<10}")
    print("-" * 58)


if __name__ == '__main__':
    main()