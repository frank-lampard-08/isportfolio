import efinance as ef

# Test getting stock data
try:
    # Get stock quote data for Shenzhen Index (399001)
    data = ef.stock.get_quote_history('399300', beg='20250801', end='20250807')
    print("Stock data retrieved successfully:")
    print(data)
except Exception as e:
    print(f"Error retrieving stock data: {e}")
