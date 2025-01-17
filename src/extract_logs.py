import sys
import os
from datetime import datetime
import mmap
import bisect
from typing import Optional, Tuple

class LogRetriever:
    def __init__(self, filename: str):
        """Initialize the log retriever with the log file path."""
        self.filename = filename
        self.file_size = os.path.getsize(filename)
        self.day_size_estimate = int(self.file_size / 365 * 1.1)
        
    def _binary_search_date(self, target_date: str, mm: mmap.mmap) -> Optional[int]:
        """Perform binary search to find the first occurrence of the target date."""
        left, right = 0, mm.size() - 1
        
        # Binary search for the date
        while left <= right:
            mid = (left + right) // 2
            
            mm.seek(max(0, mid - 100))  
            mm.readline()  
            
            line_start = mm.tell()
            line = mm.readline().decode('utf-8').strip()
            
            if not line:
                right = mid - 1
                continue
                
            try:
                current_date = line[:10]  
                
                if current_date == target_date:
                    while line_start > 0:
                        mm.seek(max(0, line_start - 100))
                        mm.readline() 
                        prev_line = mm.readline().decode('utf-8').strip()
                        if prev_line[:10] != target_date:
                            return line_start
                        line_start = mm.tell()
                    return line_start
                    
                elif current_date < target_date:
                    left = mid + 1
                else:
                    right = mid - 1
                    
            except (IndexError, ValueError):
                right = mid - 1
                
        return None

    def extract_logs(self, target_date: str) -> None:
        """
        Extract all logs for the given date and save to output file.
        
        Args:
            target_date: Date in YYYY-MM-DD format
        """
        try:
            datetime.strptime(target_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Incorrect date format. Please use YYYY-MM-DD")
            
        # Create output directory if it doesn't exist
        os.makedirs('output', exist_ok=True)
        output_file = f'output/output_{target_date}.txt'
        
        with open(self.filename, 'rb') as f:
            # Memory map the file for efficient reading
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            

            start_pos = self._binary_search_date(target_date, mm)
            
            if start_pos is None:
                print(f"No logs found for date {target_date}")
                return
                

            with open(output_file, 'w') as out_f:
                mm.seek(start_pos)
                
                while True:
                    line = mm.readline()
                    if not line:  
                        break
                        
                    line_str = line.decode('utf-8').strip()
                    if not line_str:  
                        continue
                        
                    current_date = line_str[:10]
                    if current_date != target_date:  
                        break
                        
                    out_f.write(line_str + '\n')
            
            mm.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_logs.py YYYY-MM-DD")
        sys.exit(1)
        
    target_date = sys.argv[1]
    log_file = "test_logs.log"
    
    try:
        retriever = LogRetriever(log_file)
        retriever.extract_logs(target_date)
        print(f"Logs for {target_date} have been saved to output/output_{target_date}.txt")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()