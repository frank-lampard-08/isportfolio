import csv
import sys
import os
from datetime import datetime

def read_portfolio(filename):
    """Read portfolio CSV file and return rows"""
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    return rows

def write_portfolio(filename, rows):
    """Write rows to portfolio CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

def update_holdings(rows, asset_id, quantity, price, operation):
    """Update holdings, holding_price and holding_earnings for an asset"""
    if not rows:
        return False
    
    # Find column indices
    header = rows[0]
    id_index = -1
    name_index = -1
    holdings_index = -1
    holding_price_index = -1
    holding_earnings_index = -1
    
    for i, col_name in enumerate(header):
        # Handle BOM in column names
        if col_name.startswith('\ufeff'):
            col_name = col_name[1:]
        if col_name == 'id':
            id_index = i
        elif col_name == 'name':
            name_index = i
        elif col_name == 'holdings':
            holdings_index = i
        elif col_name == 'holding_price':
            holding_price_index = i
        elif col_name == 'holding_earnings':
            holding_earnings_index = i
    
    # Check if required columns exist
    if (id_index == -1 or holdings_index == -1 or 
        holding_price_index == -1 or holding_earnings_index == -1 or name_index == -1):
        print(f"Error: Required columns not found in portfolio.csv")
        print(f"  id_index: {id_index}")
        print(f"  name_index: {name_index}")
        print(f"  holdings_index: {holdings_index}")
        print(f"  holding_price_index: {holding_price_index}")
        print(f"  holding_earnings_index: {holding_earnings_index}")
        return False
    
    # Find the asset row
    asset_row_index = -1
    for i in range(1, len(rows)):
        if rows[i][id_index] == asset_id:
            asset_row_index = i
            break
    
    if asset_row_index == -1:
        print(f"Error: Asset with ID {asset_id} not found in portfolio.csv")
        return False
    
    # Get current values
    row = rows[asset_row_index]
    asset_name = row[name_index]
    current_holdings = float(row[holdings_index]) if row[holdings_index] else 0
    current_holding_price = float(row[holding_price_index]) if row[holding_price_index] else 0
    
    # Convert input values
    quantity = float(quantity)
    price = float(price)
    total_price = quantity * price
    
    # Perform buy or sell operation
    if operation.lower() == 'buy':
        # Calculate new holdings
        new_holdings = current_holdings + quantity
        
        # Calculate new holding price using average cost method
        if new_holdings > 0:
            # Total cost = (current_holdings * current_holding_price) + (quantity * price)
            total_cost = (current_holdings * current_holding_price) + (quantity * price)
            new_holding_price = total_cost / new_holdings
        else:
            new_holding_price = 0
        
        # Update the row
        rows[asset_row_index][holdings_index] = str(new_holdings)
        rows[asset_row_index][holding_price_index] = f"{new_holding_price:.2f}"
        
        # Log the buy transaction
        log_transaction(operation, asset_name, asset_id, quantity, price, total_price)
        
    elif operation.lower() == 'sell':
        # Calculate new holdings
        new_holdings = current_holdings - quantity
        
        # Ensure holdings don't go negative
        if new_holdings < 0:
            print("Error: Cannot sell more than currently held")
            return False
        
        # Calculate profit/loss for this transaction
        profit_loss = (price - current_holding_price) * quantity
        
        # Update the row (holding_price remains the same for sells)
        rows[asset_row_index][holdings_index] = str(new_holdings)
        
        # If all holdings are sold, reset holding_price to 0
        if new_holdings == 0:
            rows[asset_row_index][holding_price_index] = '0'
        
        # Log the sell transaction
        log_transaction(operation, asset_name, asset_id, quantity, price, total_price, current_holding_price, profit_loss)
    
    # Recalculate holding_earnings = (last_price - holding_price) * holdings
    # We need to find the last_price column
    last_price_index = -1
    for i, col_name in enumerate(header):
        if col_name == 'last_price':
            last_price_index = i
            break
    
    if last_price_index != -1:
        last_price = float(rows[asset_row_index][last_price_index]) if rows[asset_row_index][last_price_index] else 0
        holding_price = float(rows[asset_row_index][holding_price_index]) if rows[asset_row_index][holding_price_index] else 0
        holdings = float(rows[asset_row_index][holdings_index]) if rows[asset_row_index][holdings_index] else 0
        
        holding_earnings = (last_price - holding_price) * holdings
        rows[asset_row_index][holding_earnings_index] = f"{holding_earnings:.4f}"
    else:
        # If last_price column not found, set holding_earnings to 0
        rows[asset_row_index][holding_earnings_index] = '0'
    
    return True

def log_transaction(operation, asset_name, asset_id, quantity, price, total_price, holding_price=None, profit_loss=None):
    """Log transaction to file"""
    # Create bargain_log directory if it doesn't exist
    log_dir = 'bargain_log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Log file path
    log_file = os.path.join(log_dir, 'transactions.log')
    
    # Current date and time
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Prepare log entry
    if operation.lower() == 'buy':
        log_entry = f"{timestamp} | BUY | {asset_name} | {asset_id} | {quantity} | {price} | {total_price}\n"
    else:  # sell
        log_entry = f"{timestamp} | SELL | {asset_name} | {asset_id} | {quantity} | {price} | {total_price} | {holding_price} | {profit_loss}\n"
    
    # Write to log file
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)
    
    print(f"Transaction logged: {operation} {quantity} of {asset_name} ({asset_id}) at {price}")

def main():
    # Check if correct number of arguments provided
    if len(sys.argv) != 5:
        print("Usage: python buy_or_sell.py <buy/sell> <asset_id> <quantity> <price>")
        print("Example: python buy_or_sell.py buy 000001 100 10.5")
        sys.exit(1)
    
    # Get arguments
    operation = sys.argv[1]
    asset_id = sys.argv[2]
    quantity = sys.argv[3]
    price = sys.argv[4]
    
    # Validate operation
    if operation.lower() not in ['buy', 'sell']:
        print("Error: Operation must be either 'buy' or 'sell'")
        sys.exit(1)
    
    try:
        # Read portfolio.csv
        portfolio_rows = read_portfolio('portfolio.csv')
        
        # Update holdings
        if update_holdings(portfolio_rows, asset_id, quantity, price, operation):
            # Write updated portfolio back to file
            write_portfolio('portfolio.csv', portfolio_rows)
            print(f"Successfully updated portfolio for {operation} operation on asset {asset_id}")
        else:
            sys.exit(1)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
