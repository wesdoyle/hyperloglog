use std::collections::HashSet;
use std::time::Instant;
use md5;
use regex::Regex;
use rusqlite::Connection;

struct HyperLogLog {
    precision: u8,
    registers: Vec<u8>,
}

impl HyperLogLog {
    fn new(precision: u8) -> Self {
        let num_registers = 1 << precision;
        HyperLogLog {
            precision,
            registers: vec![0; num_registers],
        }
    }

    fn hash(&self, value: &str) -> u128 {
        let hash = md5::compute(value);
        let hash_bytes: [u8; 16] = hash.into();
        u128::from_le_bytes(hash_bytes)
    }

    fn rho(&self, w: u128) -> u8 {
        (w.leading_zeros() + 1) as u8
    }

    fn add(&mut self, value: &str) {
        let hash_value = self.hash(value);
        let j = (hash_value >> (128 - self.precision)) as usize;
        let w = hash_value & ((1 << (128 - self.precision)) - 1);
        self.registers[j] = self.registers[j].max(self.rho(w));
    }

    fn count(&self) -> f64 {
        let m = self.registers.len() as f64;
        let z: f64 = 1.0 / self.registers.iter().map(|&b| 2f64.powi(-(b as i32))).sum::<f64>();
        let estimate = 0.7213 / (1.0 + 1.079 / m) * m * m * z;

        if estimate <= 2.5 * m {
            let v = self.registers.iter().filter(|&&x| x == 0).count() as f64;
            if v > 0.0 {
                m * (m / v).ln()
            } else {
                estimate
            }
        } else {
            estimate
        }
    }
}

fn process_sqlite_hll(db_path: &str, table_name: &str, column_name: &str, precision: u8) -> f64 {
    let conn = Connection::open(db_path).unwrap();
    let mut stmt = conn.prepare(&format!("SELECT {} FROM {}", column_name, table_name)).unwrap();
    let mut rows = stmt.query([]).unwrap();

    let mut hll = HyperLogLog::new(precision);
    let re = Regex::new(r"\w+").unwrap();

    while let Some(row) = rows.next().unwrap() {
        let text: String = row.get(0).unwrap();
        for word in re.find_iter(&text.to_lowercase()) {
            hll.add(word.as_str());
        }
    }

    hll.count()
}

fn process_sqlite_exact(db_path: &str, table_name: &str, column_name: &str) -> usize {
    let conn = Connection::open(db_path).unwrap();
    let mut stmt = conn.prepare(&format!("SELECT {} FROM {}", column_name, table_name)).unwrap();
    let mut rows = stmt.query([]).unwrap();

    let mut unique_words = HashSet::new();
    let re = Regex::new(r"\w+").unwrap();

    while let Some(row) = rows.next().unwrap() {
        let text: String = row.get(0).unwrap();
        for word in re.find_iter(&text.to_lowercase()) {
            unique_words.insert(word.as_str().to_string());
        }
    }

    unique_words.len()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 5 {
        eprintln!("Usage: {} <db_path> <table_name> <column_name> <precision>", args[0]);
        std::process::exit(1);
    }

    let db_path = &args[1];
    let table_name = &args[2];
    let column_name = &args[3];
    let precision: u8 = args[4].parse().unwrap();

    println!("\nRunning HyperLogLog estimation...");
    let start_time = Instant::now();
    let hll_result = process_sqlite_hll(db_path, table_name, column_name, precision);
    let hll_time = start_time.elapsed().as_secs_f64();

    println!("\nRunning Exact counting...");
    let start_time = Instant::now();
    let exact_result = process_sqlite_exact(db_path, table_name, column_name);
    let exact_time = start_time.elapsed().as_secs_f64();

    let error_percentage = (hll_result - exact_result as f64).abs() / exact_result as f64 * 100.0;

    println!("\nComparison of HyperLogLog vs Exact Counting (SQLite)");
    println!("{:-<58}", "");
    println!("{:<15} {:<10} {:<10} {:<10}", "Method", "Count", "Time (s)", "Error (%)");
    println!("{:-<58}", "");
    println!("{:<15} {:<10.0} {:<10.2} {:<10.2}", "HyperLogLog", hll_result, hll_time, error_percentage);
    println!("{:<15} {:<10} {:<10.2} {:<10}", "Exact", exact_result, exact_time, "N/A");
    println!("{:-<58}", "");
}