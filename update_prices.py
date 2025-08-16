import csv
import requests
import sys
import time
import random
from lxml import etree
from datetime import datetime, timedelta
from collections import OrderedDict

# Configuration
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'
}

# API endpoints
FUND_API = 'https://fundf10.eastmoney.com/F10DataApi.aspx?type=lsjz&code='
STOCK_API = 'https://quote.eastmoney.com/'

def parse_args():
    """Parse command line arguments for start and end dates"""
    if len(sys.argv) != 3:
        print("Usage: python update_prices.py [start_date] [end_date] (format: YYYY-MM-DD)")
        sys.exit(1)
    return sys.argv[1], sys.argv[2]

def get_page_data(url, pages):
    """Get data from multiple pages"""
    page_data = []
    for page in range(1, pages+1):
        url2 = url + '&page=' + str(page)  # 拼接url

        for _ in range(10):
            try:
                resp = requests.get(url=url2, headers=headers)
                if resp.status_code == 200:  # 若网页正常响应
                    html = etree.HTML(resp.content.decode('utf-8'))  # 解析网页
                    rep_list = html.xpath("//tbody")  # 数据存在tbody下
                    break
                else:
                    time.sleep(10)
            except Exception as e:
                print(f"Error fetching page {page}: {e}")
                time.sleep(10)
                continue
                
        # 提取数据
        if len(rep_list) > 0:
            rep_list2 = rep_list[0]
            rep_list3 = rep_list2.xpath('./tr')
            if len(rep_list3) > 0:
                for m in range(len(rep_list3)):
                    rep_list4 = rep_list3[m].xpath('./td')
                    page_data_temp = []  # 生成空的list，用于存储每一天的数据
                    if len(rep_list4) > 0:
                        for n in range(len(rep_list4)):   
                            rep_list5 = rep_list4[n].text
                            if rep_list5:
                                page_data_temp.append(rep_list5.strip())
                    # Only add non-empty rows
                    if page_data_temp:
                        page_data.append(page_data_temp)
            
            # 每爬完一页，暂停一段时间，因为爬虫过于频繁会被网站识别出来        
            t = random.uniform(0.5, 1) 
            time.sleep(t)
                    
    return page_data

def get_result_data(code, start_date, end_date):
    """Get total pages and data for a fund"""
    url_prefix = 'https://fundf10.eastmoney.com/F10DataApi.aspx?type=lsjz&code='
    url1 = url_prefix + code + f'&sdate={start_date}&edate={end_date}&per=45'  # 拼接第一页的url，&per=45是每页显示的条数
    
    for _ in range(10): 
        try:
            resp = requests.get(url=url1, headers=headers)
            if resp.status_code == 200:  # 若网页正常响应
                html = etree.HTML(resp.content.decode('utf-8'))  # 解析网页
                rep_text = str(html.xpath("//body/text()")[0])
                # Extract total pages from response text
                # The response text usually contains something like "var apidata={ content:"...",records:100,pages:3,curpage:1}"
                import re
                pages_match = re.search(r'pages:(\d+)', rep_text)
                pages = int(pages_match.group(1)) if pages_match else 1
                break
            else:
                time.sleep(10)  # 如果网页没有正常响应，则停止一段时间再尝试
        except Exception as e:
            print(f"Error getting fund data for {code}: {e}")
            time.sleep(10)
            continue
            
    # Get data from all pages
    all_data = get_page_data(url1, pages)
    return all_data

def get_fund_data(code, start_date, end_date):
    """Fetch fund historical data from East Money"""
    try:
        data_list = get_result_data(code, start_date, end_date)
        data = {}
        for row in data_list:
            if len(row) >= 3:
                date = row[0].strip()
                price = row[1].strip()  # Net value
                # row[1]是单位净值 row[2]是累计净值
                data[date] = price
        return data
    except Exception as e:
        print(f"Error fetching fund data for {code}: {e}")
    return {}

def get_stock_data(code, start_date, end_date):
    """Fetch stock historical data using efinance library"""
    try:
        import efinance as ef
        
        # Format dates for efinance (YYYYMMDD)
        beg_date = start_date.replace('-', '')
        end_date = end_date.replace('-', '')
        
        # Get stock quote history
        data = ef.stock.get_quote_history(code, beg=beg_date, end=end_date)
        
        # Convert to dictionary with date as key and closing price as value
        price_data = {}
        if data is not None and not data.empty:
            for _, row in data.iterrows():
                date = str(row['日期'])  # Date is already in string format
                close_price = str(row['收盘'])  # Convert closing price to string
                price_data[date] = close_price
                
        return price_data
    except Exception as e:
        print(f"Error fetching stock data for {code} using efinance: {e}")
    return {}

def read_watchlist(filename):
    """Read existing watchlist CSV file"""
    # Try different encodings
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
    
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                reader = csv.reader(f)
                rows = list(reader)
            print(f"Successfully read file with {encoding} encoding")
            return rows
        except UnicodeDecodeError:
            continue
    
    # If all encodings fail, try with error handling
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        rows = list(reader)
    print("Read file with utf-8 encoding and error ignoring")
    return rows

def update_watchlist(rows, new_data):
    """Update watchlist with new price data"""
    if not rows:
        return rows
        
    # Get header row and existing dates
    header = rows[0]
    existing_dates = header[3:]  # Skip name, id, type columns
    
    # Create ordered dict of all dates that have data
    all_dates = OrderedDict()
    for item in new_data.values():
        for date in item.keys():
            if date not in all_dates:
                all_dates[date] = None
    
    # Add existing dates that have data
    for date in existing_dates:
        # Check if any item has data for this date
        has_data = False
        for item_data in new_data.values():
            if date in item_data and item_data[date]:
                has_data = True
                break
        if has_data and date not in all_dates:
            all_dates[date] = None
    
    # Sort dates chronologically
    sorted_dates = sorted(all_dates.keys(), key=lambda x: datetime.strptime(x, '%Y-%m-%d'))
    
    # Build new header
    new_header = header[:3] + sorted_dates
    
    # Build new rows
    new_rows = [new_header]
    for row in rows[1:]:
        name, id, type = row[:3]
        existing_prices = dict(zip(existing_dates, row[3:]))
        
        # Merge existing prices with new data
        merged_prices = []
        for date in sorted_dates:
            if date in new_data.get(id, {}):
                merged_prices.append(new_data[id][date])
            else:
                merged_prices.append(existing_prices.get(date, ''))
        
        new_row = [name, id, type] + merged_prices
        new_rows.append(new_row)
    
    return new_rows

def write_watchlist(filename, rows):
    """Write updated watchlist to CSV"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

def update_prices():
    start_date, end_date = parse_args()
    
    # Read existing watchlist
    rows = read_watchlist('watchlist.csv')
    if not rows or len(rows) < 2:
        print("No items in watchlist or invalid format")
        return
    
    # Get all items (skip header)
    items = rows[1:]
    new_data = {}
    
    # Fetch data for each item
    for item in items:
        name, id, type = item[:3]
        print(f"Fetching data for {name} ({id})...")
        
        if type == 'fund':
            data = get_fund_data(id, start_date, end_date)
        elif type == 'stock':
            data = get_stock_data(id, start_date, end_date)
        else:
            print(f"Unknown type {type} for {name}")
            continue
            
        if data:
            new_data[id] = data
            # Add random delay to avoid being blocked
            time.sleep(random.uniform(0.5, 1.5))
    
    # Update watchlist with new data
    updated_rows = update_watchlist(rows, new_data)
    
    # Write updated watchlist
    write_watchlist('watchlist.csv', updated_rows)
    print("Watchlist updated successfully")

if __name__ == '__main__':
    update_prices()
