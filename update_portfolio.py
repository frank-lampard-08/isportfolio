import csv
from datetime import datetime
import os

def read_watchlist(filename):
    """Read watchlist CSV file and extract latest prices"""
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    if not rows:
        return {}
    
    # Get header row
    header = rows[0]
    
    # Find all date columns
    date_columns = []
    for i in range(3, len(header)):  # Start from index 3 (after name, id, type)
        try:
            date = datetime.strptime(header[i], '%Y-%m-%d')
            date_columns.append((i, date))
        except ValueError:
            # Not a date column, skip
            continue
    
    # Sort date columns by date (newest first)
    date_columns.sort(key=lambda x: x[1], reverse=True)
    
    if not date_columns:
        return {}
    
    # Extract latest available prices for each item
    latest_prices = {}
    for row in rows[1:]:  # Skip header row
        if len(row) <= 3:  # Skip rows without enough columns
            continue
            
        item_id = row[1]  # ID is in the second column
        
        # Find the most recent date with available data for this item
        for col_index, date in date_columns:
            if len(row) > col_index and row[col_index].strip():
                latest_prices[item_id] = row[col_index]
                break  # Found the latest available price, move to next item
    
    return latest_prices

def update_portfolio(filename, latest_prices):
    """Update portfolio CSV file with latest prices"""
    # Read existing portfolio data
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    if not rows:
        return
    
    # Find the last_price column index
    header = rows[0]
    last_price_index = -1
    for i, col_name in enumerate(header):
        if col_name == 'last_price':
            last_price_index = i
            break
    
    if last_price_index == -1:
        print("Error: 'last_price' column not found in portfolio.csv")
        return
    
    # Update last_price for each item
    for row in rows[1:]:  # Skip header row
        if len(row) > 1:  # Make sure row has ID column
            item_id = row[1]  # ID is in the second column
            if item_id in latest_prices:
                # Update last_price column
                row[last_price_index] = latest_prices[item_id]
    
    # Write updated data back to file
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    print(f"Successfully updated {filename} with latest prices")

def update_total_value(filename):
    """Update portfolio CSV file with total_value = last_price * holdings"""
    # Read existing portfolio data
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    if not rows:
        return
    
    # Find column indices
    header = rows[0]
    last_price_index = -1
    holdings_index = -1
    total_value_index = -1
    
    for i, col_name in enumerate(header):
        if col_name == 'last_price':
            last_price_index = i
        elif col_name == 'holdings':
            holdings_index = i
        elif col_name == 'total_value':
            total_value_index = i
    
    # Check if required columns exist
    if last_price_index == -1 or holdings_index == -1 or total_value_index == -1:
        print("Error: Required columns not found in portfolio.csv")
        return
    
    # Update total_value for each item
    for row in rows[1:]:  # Skip header row
        if len(row) > max(last_price_index, holdings_index, total_value_index):
            last_price = row[last_price_index]
            holdings = row[holdings_index]
            
            # Calculate total_value = last_price * holdings
            if last_price and holdings:
                try:
                    total_value = float(last_price) * float(holdings)
                    row[total_value_index] = f"{total_value:.2f}"
                except ValueError:
                    # Handle case where conversion to float fails
                    row[total_value_index] = '0'
            else:
                # If either last_price or holdings is empty, set total_value to 0
                row[total_value_index] = '0'
    
    # Write updated data back to file
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    print(f"Successfully updated {filename} with total values")

def update_holding_earnings(filename):
    """Update portfolio CSV file with holding_earnings = (last_price - holding_price) * holdings"""
    # Read existing portfolio data
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    if not rows:
        return
    
    # Find column indices
    header = rows[0]
    last_price_index = -1
    holding_price_index = -1
    holdings_index = -1
    holding_earnings_index = -1
    
    for i, col_name in enumerate(header):
        if col_name == 'last_price':
            last_price_index = i
        elif col_name == 'holding_price':
            holding_price_index = i
        elif col_name == 'holdings':
            holdings_index = i
        elif col_name == 'holding_earnings':
            holding_earnings_index = i
    
    # Check if required columns exist
    if (last_price_index == -1 or holding_price_index == -1 or 
        holdings_index == -1 or holding_earnings_index == -1):
        print("Error: Required columns not found in portfolio.csv")
        return
    
    # Update holding_earnings for each item
    for row in rows[1:]:  # Skip header row
        if len(row) > max(last_price_index, holding_price_index, holdings_index, holding_earnings_index):
            last_price = row[last_price_index]
            holding_price = row[holding_price_index]
            holdings = row[holdings_index]
            
            # Calculate holding_earnings = (last_price - holding_price) * holdings
            if last_price and holding_price and holdings:
                try:
                    last_price_val = float(last_price)
                    holding_price_val = float(holding_price)
                    holdings_val = float(holdings)
                    holding_earnings = (last_price_val - holding_price_val) * holdings_val
                    row[holding_earnings_index] = f"{holding_earnings:.2f}"
                except ValueError:
                    # Handle case where conversion to float fails
                    row[holding_earnings_index] = '0'
            else:
                # If any of the required values is empty, set holding_earnings to 0
                row[holding_earnings_index] = '0'
    
    # Write updated data back to file
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    print(f"Successfully updated {filename} with holding earnings")

def update_percentage(filename):
    """Update portfolio CSV file with percentage = (total_value / sum of all total_values) * 100%"""
    # Read existing portfolio data
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    if not rows:
        return
    
    # Find column indices
    header = rows[0]
    total_value_index = -1
    percentage_index = -1
    
    for i, col_name in enumerate(header):
        if col_name == 'total_value':
            total_value_index = i
        elif col_name == 'percentage':
            percentage_index = i
    
    # Check if required columns exist
    if total_value_index == -1 or percentage_index == -1:
        print("Error: Required columns not found in portfolio.csv")
        return
    
    # Calculate sum of all total_values
    total_sum = 0
    for row in rows[1:]:  # Skip header row
        if len(row) > total_value_index:
            total_value = row[total_value_index]
            if total_value:
                try:
                    total_sum += float(total_value)
                except ValueError:
                    # Skip invalid values
                    pass
    
    # If total_sum is zero, we can't calculate percentages
    if total_sum == 0:
        print("Warning: Total sum of all assets is zero. Cannot calculate percentages.")
        return
    
    # Update percentage for each item
    for row in rows[1:]:  # Skip header row
        if len(row) > max(total_value_index, percentage_index):
            total_value = row[total_value_index]
            
            # Calculate percentage = (total_value / total_sum) * 100
            if total_value:
                try:
                    percentage = (float(total_value) / total_sum) * 100
                    row[percentage_index] = f"{percentage:.2f}%"
                except ValueError:
                    # Handle case where conversion to float fails
                    row[percentage_index] = '0%'
            else:
                # If total_value is empty, set percentage to 0%
                row[percentage_index] = '0%'
    
    # Write updated data back to file
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    print(f"Successfully updated {filename} with percentages")

def log_total_value_sum(filename):
    """Calculate total sum of all total_value and log it with timestamp"""
    # Read existing portfolio data
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    if not rows:
        return
    
    # Find total_value column index
    header = rows[0]
    total_value_index = -1
    for i, col_name in enumerate(header):
        if col_name == 'total_value':
            total_value_index = i
            break
    
    # Check if total_value column exists
    if total_value_index == -1:
        print("Error: 'total_value' column not found in portfolio.csv")
        return
    
    # Calculate sum of all total_values
    total_sum = 0
    for row in rows[1:]:  # Skip header row
        if len(row) > total_value_index:
            total_value = row[total_value_index]
            if total_value:
                try:
                    total_sum += float(total_value)
                except ValueError:
                    # Skip invalid values
                    pass
    
    # Create total_value_log directory if it doesn't exist
    log_dir = 'total_value_log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Write to log file with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_filename = os.path.join(log_dir, 'total_value.log')
    
    with open(log_filename, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp}, {total_sum:.2f}\n")
    
    print(f"Total value sum: {total_sum:.2f}")
    print(f"Logged to {log_filename}")

def update_annual_return_and_risk(portfolio_filename, percentage_change_filename):
    """Update portfolio CSV file with annual return and risk based on percentage change data"""
    # Read portfolio data
    with open(portfolio_filename, 'r', encoding='utf-8') as f:
        portfolio_reader = csv.reader(f)
        portfolio_rows = list(portfolio_reader)
    
    if not portfolio_rows:
        return
    
    # Read percentage change data
    with open(percentage_change_filename, 'r', encoding='utf-8') as f:
        pct_change_reader = csv.reader(f)
        pct_change_rows = list(pct_change_reader)
    
    if not pct_change_rows:
        print("Error: No data found in percentage change file")
        return
    
    # Filter out empty rows from portfolio data (rows where all columns are empty)
    filtered_portfolio_rows = [row for row in portfolio_rows if any(cell.strip() for cell in row)]
    
    # Verify that the first three columns match between portfolio and percentage change files
    portfolio_header = filtered_portfolio_rows[0]
    pct_change_header = pct_change_rows[0]
    
    # Check if first three column names match
    if (portfolio_header[0] != pct_change_header[0] or 
        portfolio_header[1] != pct_change_header[1] or 
        portfolio_header[2] != pct_change_header[2]):
        print("Error: First three column names do not match between portfolio.csv and percentage_change.csv")
        return
    
    # Check if first three columns of data rows match
    # Both files should have the same number of data rows (excluding header)
    if len(filtered_portfolio_rows) != len(pct_change_rows):
        print("Error: Number of rows do not match between portfolio.csv and percentage_change.csv")
        print(f"  Portfolio rows: {len(filtered_portfolio_rows)}, Percentage change rows: {len(pct_change_rows)}")
        return
    
    for i in range(1, len(filtered_portfolio_rows)):
        if i < len(pct_change_rows):
            # Compare first three columns (name, id, type)
            if (filtered_portfolio_rows[i][0] != pct_change_rows[i][0] or 
                filtered_portfolio_rows[i][1] != pct_change_rows[i][1] or 
                filtered_portfolio_rows[i][2] != pct_change_rows[i][2]):
                print(f"Error: Data mismatch at row {i+1} in first three columns between portfolio.csv and percentage_change.csv")
                print(f"  Portfolio: {filtered_portfolio_rows[i][0]}, {filtered_portfolio_rows[i][1]}, {filtered_portfolio_rows[i][2]}")
                print(f"  Percentage Change: {pct_change_rows[i][0]}, {pct_change_rows[i][1]}, {pct_change_rows[i][2]}")
                return
    
    # Find column indices in portfolio.csv
    portfolio_header = portfolio_rows[0]
    annual_return_index = -1
    risk_index = -1
    
    for i, col_name in enumerate(portfolio_header):
        if col_name == 'annual_return':
            annual_return_index = i
        elif col_name == 'risk':
            risk_index = i
    
    # Check if required columns exist
    if annual_return_index == -1 or risk_index == -1:
        print("Error: Required columns 'annual_return' or 'risk' not found in portfolio.csv")
        return
    
    # Process each asset
    for i in range(1, len(portfolio_rows)):  # Skip header row
        if i < len(pct_change_rows):
            # Extract percentage changes for this asset (skip first 3 columns which are name, id, type)
            pct_changes = []
            for j in range(3, len(pct_change_rows[i])):
                if pct_change_rows[i][j]:  # If there's data in this cell
                    try:
                        # Remove % sign and convert to float
                        pct_change = float(pct_change_rows[i][j].rstrip('%'))
                        pct_changes.append(pct_change)
                    except ValueError:
                        # Skip invalid values
                        pass
            
            # Calculate annual return and risk if we have data
            if pct_changes:
                # Convert percentages to decimal form
                decimal_returns = [r/100 for r in pct_changes]
                
                # Calculate cumulative return using compound returns
                cumulative_return = 1.0
                for r in decimal_returns:
                    cumulative_return *= (1 + r)
                
                # Calculate annual return using compound returns (assuming 252 trading days in a year)
                # Annual Return = (1 + Cumulative Return)^(252/n) - 1
                # where n is the number of trading days with actual data (not including empty values)
                n_days = len(decimal_returns)  # Only count days with actual data
                if n_days > 0:
                    annual_return = (cumulative_return ** (252 / n_days) - 1) * 100
                else:
                    annual_return = 0
                
                # Calculate risk (standard deviation of daily returns annualized)
                if len(decimal_returns) > 1:
                    # Calculate average of decimal returns
                    avg_decimal_return = sum(decimal_returns) / len(decimal_returns)
                    
                    # Calculate variance
                    variance = sum((r - avg_decimal_return) ** 2 for r in decimal_returns) / (len(decimal_returns) - 1)
                    # Standard deviation of daily returns
                    daily_std_dev = variance ** 0.5
                    # Annualized standard deviation (risk)
                    risk = daily_std_dev * (252 ** 0.5) * 100  # Convert back to percentage
                else:
                    risk = 0
                
                # Update portfolio row with calculated values
                portfolio_rows[i][annual_return_index] = f"{annual_return:.2f}%"
                portfolio_rows[i][risk_index] = f"{risk:.2f}%"
            else:
                # No percentage change data, set to 0
                portfolio_rows[i][annual_return_index] = "0%"
                portfolio_rows[i][risk_index] = "0%"
    
    # Write updated data back to portfolio file
    with open(portfolio_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(portfolio_rows)
    
    print(f"Successfully updated {portfolio_filename} with annual returns and risks")

def update_portfolio_main():
    """Main function"""
    try:
        # Read latest prices from watchlist
        latest_prices = read_watchlist('watchlist.csv')
        print(f"Found latest prices for {len(latest_prices)} items")
        
        # Update portfolio with latest prices
        update_portfolio('portfolio.csv', latest_prices)
        
        # Update portfolio with total values
        update_total_value('portfolio.csv')
        
        # Update portfolio with percentages
        update_percentage('portfolio.csv')
        
        # Update portfolio with holding earnings
        update_holding_earnings('portfolio.csv')
        
        # Update portfolio with annual returns and risks
        update_annual_return_and_risk('portfolio.csv', 'percentage_change.csv')
        
        # Log total value sum
        log_total_value_sum('portfolio.csv')
        
        print("Process completed successfully")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    update_portfolio_main()
