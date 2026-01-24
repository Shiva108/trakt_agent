import time
import subprocess
import sys

def run_step(name, command):
    print(f"⏱️  Starting {name}...")
    start = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    end = time.time()
    duration = end - start
    
    if result.returncode != 0:
        print(f"❌ {name} failed!")
        print(result.stderr)
        sys.exit(1)
        
    print(f"✅ {name} finished in {duration:.2f}s")
    return duration

def main():
    total_start = time.time()
    
    # Measure Fetch
    fetch_time = run_step("Fetch Data", "venv/bin/python cli.py fetch")
    
    # Measure Recommend
    recommend_time = run_step("Generate Recommendations", "venv/bin/python cli.py recommend")
    
    total_time = time.time() - total_start
    
    print("\n" + "="*30)
    print(f"📊 PERFORMANCE REPORT")
    print("="*30)
    print(f"Fetch Data:      {fetch_time:.2f}s")
    print(f"LLM Generation:  {recommend_time:.2f}s")
    print("-" * 30)
    print(f"TOTAL TIME:      {total_time:.2f}s")
    print("="*30)

if __name__ == "__main__":
    main()
