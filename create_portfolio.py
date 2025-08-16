import csv
import sys
import os

def read_watchlist(filename):
    """Read watchlist CSV file"""
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    return rows

def create_portfolio_file(input_file, output_file):
    """Create portfolio CSV file with specified columns"""
    # Read the watchlist file
    rows = read_watchlist(input_file)
    
    if not rows:
        print("No data in watchlist file")
        return
    
    # Create new header with additional columns
    if rows:
        header = rows[0][:3] + ['last_price', 'holdings', 'holding_price', 'holding_earnings', 'total_value', 'percentage', 'annual_return', 'risk']
        portfolio_rows = [header]
        
        # Process data rows
        for row in rows[1:]:  # Skip header row
            if len(row) >= 3:
                # Keep first three columns and add empty values for new columns
                portfolio_row = row[:3] + [''] * 9  # 9 empty columns for the new fields
                portfolio_rows.append(portfolio_row)
            else:
                portfolio_rows.append(row)
    else:
        portfolio_rows = []
    
    # Write to output file (overwrites if exists)
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(portfolio_rows)
    
    print(f"Portfolio data written to {output_file}")

def update_portfolio_file(input_file, output_file):
    """Update only the first three columns of an existing portfolio file"""
    # Read the watchlist file
    watchlist_rows = read_watchlist(input_file)
    
    if not watchlist_rows:
        print("No data in watchlist file")
        return
    
    # Read the existing portfolio file
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            portfolio_reader = csv.reader(f)
            portfolio_rows = list(portfolio_reader)
    else:
        print(f"Error: {output_file} does not exist")
        return
    
    if not portfolio_rows:
        print("No data in portfolio file")
        return
    
    # Create a dictionary from watchlist data for easy lookup (using the second column as key)
    watchlist_dict = {}
    for row in watchlist_rows[1:]:  # Skip header row
        if len(row) >= 3:
            key = row[1]  # Use ID (second column) as key
            watchlist_dict[key] = row[:3]  # Store first three columns
    
    # Update the first three columns of the portfolio file
    for i in range(1, len(portfolio_rows)):  # Skip header row
        if len(portfolio_rows[i]) >= 3:
            key = portfolio_rows[i][1]  # Use ID (second column) as key
            if key in watchlist_dict:
                # Update first three columns, keep the rest unchanged
                portfolio_rows[i][:3] = watchlist_dict[key]
    
    # Write updated data back to output file
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(portfolio_rows)
    
    print(f"Portfolio data updated in {output_file}")

def create_portfolio():
    """Main function"""
    # Check if output file path is provided as command line argument
    if len(sys.argv) < 2:
        print("Usage: python create_portfolio.py <output_file_path>")
        print("Example: python create_portfolio.py portfolio.csv")
        sys.exit(1)
    
    input_file = 'watchlist.csv'
    output_file = sys.argv[1]
    
    try:
        # Check if output file already exists
        if os.path.exists(output_file):
            # If file exists, update only the first three columns
            update_portfolio_file(input_file, output_file)
        else:
            # If file doesn't exist, create a new one
            create_portfolio_file(input_file, output_file)
        print("Process completed successfully")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    create_portfolio()
