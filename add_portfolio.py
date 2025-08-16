import csv
import sys
from datetime import datetime

def read_csv_file(filename):
    """Read CSV file and return rows"""
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    return rows

def write_csv_file(filename, rows):
    """Write rows to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

def get_latest_date_column(headers):
    """Find the latest date column in the header row"""
    date_columns = []
    for i in range(3, len(headers)):  # Start from index 3 (after name, id, type)
        try:
            date = datetime.strptime(headers[i], '%Y-%m-%d')
            date_columns.append((i, date))
        except ValueError:
            # Not a date column, skip
            continue
    
    # Sort date columns by date (newest first)
    date_columns.sort(key=lambda x: x[1], reverse=True)
    
    if date_columns:
        return date_columns[0][0]  # Return index of latest date column
    return None

def add_asset_to_watchlist(name, id, type, watchlist_rows):
    """Add new asset to watchlist"""
    # Find the latest date column
    header = watchlist_rows[0]
    latest_date_index = get_latest_date_column(header)
    
    # If we found a latest date column, get its value for the new asset
    new_row = [name, id, type]
    
    # Fill with empty values for all date columns
    for i in range(3, len(header)):
        new_row.append('')
    
    # If we have a latest date column, copy its value to the new row if it exists in other rows
    if latest_date_index is not None:
        # Look for a non-empty value in the latest date column from existing rows
        latest_price = ''
        for row in watchlist_rows[1:]:  # Skip header
            if len(row) > latest_date_index and row[latest_date_index]:
                latest_price = row[latest_date_index]
                break
        new_row[latest_date_index] = latest_price
    
    # Add the new row to watchlist
    watchlist_rows.append(new_row)
    return watchlist_rows

def add_asset_to_portfolio(name, id, type, portfolio_rows):
    """Add new asset to portfolio with default values"""
    # Create a new row with default values
    new_row = [
        name,           # name
        id,             # id
        type,           # type
        '',             # last_price (empty initially)
        '0',            # holdings
        '',             # holding_price (empty initially)
        '',             # holding_earnings (empty initially)
        '0',            # total_value
        '0%',           # percentage
        '0%',           # annual_return
        '0%'            # risk
    ]
    
    # Add the new row to portfolio
    portfolio_rows.append(new_row)
    return portfolio_rows

def main():
    # Check if correct number of arguments provided
    if len(sys.argv) != 4:
        print("Usage: python add_portfolio.py <name> <id> <type>")
        print("Example: python add_portfolio.py 招商成长量化选股股票C 020902 fund")
        sys.exit(1)
    
    # Get arguments
    name = sys.argv[1]
    id = sys.argv[2]
    type = sys.argv[3]
    
    try:
        # Read watchlist.csv
        watchlist_rows = read_csv_file('watchlist.csv')
        
        # Add asset to watchlist
        watchlist_rows = add_asset_to_watchlist(name, id, type, watchlist_rows)
        
        # Write updated watchlist back to file
        write_csv_file('watchlist.csv', watchlist_rows)
        print(f"Successfully added {name} to watchlist.csv")
        
        # Read portfolio.csv
        portfolio_rows = read_csv_file('portfolio.csv')
        
        # Add asset to portfolio
        portfolio_rows = add_asset_to_portfolio(name, id, type, portfolio_rows)
        
        # Write updated portfolio back to file
        write_csv_file('portfolio.csv', portfolio_rows)
        print(f"Successfully added {name} to portfolio.csv")
        
        print(f"Asset added successfully: {name} ({id}, {type})")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
