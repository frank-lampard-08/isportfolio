import csv
from datetime import datetime

def read_watchlist(filename):
    """Read watchlist CSV file"""
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    return rows

def calculate_percentage_change(prices):
    """Calculate percentage change for each day"""
    if len(prices) < 2:
        return []
    
    changes = []
    for i in range(1, len(prices)):
        try:
            # Convert string to float for calculation
            prev_price = float(prices[i-1])
            curr_price = float(prices[i])
            
            # Calculate percentage change
            if prev_price != 0:
                change = ((curr_price - prev_price) / prev_price) * 100
                changes.append(f"{change:.4f}%")
            else:
                changes.append("")  # Cannot calculate if previous price is 0
        except (ValueError, IndexError):
            # Handle empty or invalid values
            changes.append("")
    
    return changes

def generate_percentage_change_csv(input_file, output_file):
    """Generate percentage change CSV file"""
    # Read the watchlist file
    rows = read_watchlist(input_file)
    
    if not rows:
        print("No data in watchlist file")
        return
    
    # Extract header
    header = rows[0]
    
    # Extract date columns (skip name, id, type)
    date_columns = header[3:]
    
    # Calculate percentage change columns
    # We'll have one less column since we're calculating change between consecutive days
    percentage_change_columns = []
    for i in range(1, len(date_columns)):
        percentage_change_columns.append(f"chg_{date_columns[i]}")
    
    # Create new header for output file
    new_header = header[:3] + percentage_change_columns
    
    # Process each row
    output_rows = [new_header]
    
    for row in rows[1:]:  # Skip header row
        name, id, type = row[:3]
        prices = row[3:]
        
        # Calculate percentage changes
        percentage_changes = calculate_percentage_change(prices)
        
        # Create new row with name, id, type and percentage changes
        new_row = [name, id, type] + percentage_changes
        output_rows.append(new_row)
    
    # Write to output file (overwrites if exists)
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(output_rows)
    
    print(f"Percentage change data written to {output_file}")

def percentage_change_update():
    """Main function"""
    input_file = 'watchlist.csv'
    output_file = 'percentage_change.csv'
    
    try:
        generate_percentage_change_csv(input_file, output_file)
        print("Process completed successfully")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    percentage_change_update()
