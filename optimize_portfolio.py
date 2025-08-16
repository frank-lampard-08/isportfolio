import csv
import numpy as np
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

def read_portfolio_data(filename):
    """Read portfolio data from CSV file"""
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    if not rows:
        return [], [], [], []
    
    # Extract data from rows (skip header)
    names = []
    ids = []
    percentages = []
    annual_returns = []
    risks = []
    
    for row in rows[1:]:  # Skip header row
        if len(row) >= 11:  # Updated to account for the two new columns
            names.append(row[0])
            ids.append(row[1])
            # Convert percentage strings to floats
            # Find column indices dynamically
            percentage_index = -1
            annual_return_index = -1
            risk_index = -1
            
            for i, col_name in enumerate(rows[0]):  # rows[0] is the header
                if col_name == 'percentage':
                    percentage_index = i
                elif col_name == 'annual_return':
                    annual_return_index = i
                elif col_name == 'risk':
                    risk_index = i
            
            # Use dynamic indices if found, otherwise fall back to original hardcoded values
            if percentage_index != -1 and annual_return_index != -1 and risk_index != -1:
                percentages.append(float(row[percentage_index].rstrip('%')) if row[percentage_index] else 0)
                annual_returns.append(float(row[annual_return_index].rstrip('%')) if row[annual_return_index] else 0)
                risks.append(float(row[risk_index].rstrip('%')) if row[risk_index] else 0)
            else:
                # Fallback to original hardcoded indices for backward compatibility
                percentages.append(float(row[6].rstrip('%')) if row[6] else 0)
                annual_returns.append(float(row[7].rstrip('%')) if row[7] else 0)
                risks.append(float(row[8].rstrip('%')) if row[8] else 0)
    
    return names, ids, percentages, annual_returns, risks

def read_correlation_data(filename):
    """Read asset correlation data from CSV file"""
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    if not rows:
        return [], np.array([])
    
    # Extract asset names from the first row (skip first empty cell)
    asset_names = rows[0][1:]
    
    # Extract correlation matrix data
    correlation_data = []
    for row in rows[1:]:  # Skip header row
        # Convert string values to floats
        corr_row = [float(val) for val in row[1:]]
        correlation_data.append(corr_row)
    
    # Convert to numpy array
    correlation_matrix = np.array(correlation_data)
    
    return asset_names, correlation_matrix

def calculate_portfolio_return(weights, returns):
    """Calculate portfolio return"""
    return np.dot(weights, returns)

def calculate_portfolio_risk(weights, risks, correlation_matrix):
    """Calculate portfolio risk (standard deviation)"""
    # Convert risks to numpy array
    risks = np.array(risks)
    
    # Calculate covariance matrix
    # Covariance[i,j] = correlation[i,j] * risk[i] * risk[j]
    covariance_matrix = np.outer(risks, risks) * correlation_matrix
    
    # Portfolio variance = weights^T * covariance_matrix * weights
    portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
    
    # Portfolio risk (standard deviation) is square root of variance
    return np.sqrt(portfolio_variance)

def sharpe_ratio(weights, returns, risks, correlation_matrix, risk_free_rate):
    """Calculate negative Sharpe ratio (negative because we want to maximize it)"""
    portfolio_return = calculate_portfolio_return(weights, returns)
    portfolio_risk = calculate_portfolio_risk(weights, risks, correlation_matrix)
    
    # Avoid division by zero
    if portfolio_risk == 0:
        return -np.inf
    
    # Calculate Sharpe ratio
    sharpe = (portfolio_return - risk_free_rate) / portfolio_risk
    
    # Return negative Sharpe ratio because we want to maximize it (minimize negative)
    return -sharpe

def optimized_sharpe_ratio(risk_free_rate=0.02, min_return=None, max_weight=1.0):
    """
    Optimize portfolio weights to maximize Sharpe ratio
    
    Parameters:
    risk_free_rate (float): Risk-free rate (default: 0.02 for 2%)
    min_return (float or None): Minimum required portfolio return (default: None)
    max_weight (float): Maximum weight for any single asset (default: 1.0 for 100%)
    
    Returns:
    list: Optimized percentage vector
    """
    # Read portfolio data
    names, ids, percentages, annual_returns, risks = read_portfolio_data('portfolio.csv')
    
    # Read correlation data
    asset_names, correlation_matrix = read_correlation_data('asset_correlationship.csv')
    
    # Check if we have data
    if not names or not asset_names:
        print("Error: No data found in portfolio or correlation files")
        return percentages
    
    # Check if asset names match between files
    if names != asset_names:
        print("Warning: Asset names don't match between portfolio.csv and asset_correlationship.csv")
        # Try to match assets by order or other means if needed
    
    # Convert to numpy arrays for easier computation
    returns = np.array(annual_returns)
    risks = np.array(risks)
    
    # Initial weights (current percentages)
    initial_weights = np.array(percentages) / 100.0  # Convert from percentages to decimals
    
    # Constraints:
    # 1. Weights must sum to 1
    # 2. Weights must be between 0 and 1 (no short selling)
    # 3. Portfolio annual return must be at least min_return (if specified)
    constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0}]
    
    # Add minimum return constraint if specified
    if min_return is not None:
        constraints.append({'type': 'ineq', 'fun': lambda x: calculate_portfolio_return(x, returns) - min_return})
    
    bounds = [(0, max_weight) for _ in range(len(initial_weights))]
    
    # Optimize: minimize negative Sharpe ratio
    result = minimize(
        sharpe_ratio,
        initial_weights,
        args=(returns, risks, correlation_matrix, risk_free_rate),
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
        tol=1e-6
    )
    
    # Check if optimization was successful
    if result.success:
        # Convert optimized weights back to percentages
        optimized_percentages = [w * 100 for w in result.x]
        
        # Calculate and print portfolio metrics for optimized weights
        opt_weights_decimal = result.x  # Already in decimal form
        opt_portfolio_return = calculate_portfolio_return(opt_weights_decimal, returns)
        opt_portfolio_risk = calculate_portfolio_risk(opt_weights_decimal, risks, correlation_matrix)
        opt_sharpe = (opt_portfolio_return - risk_free_rate * 100) / opt_portfolio_risk if opt_portfolio_risk != 0 else 0
        
        print(f"\nOptimized Portfolio Metrics:")
        print(f"Annual Return: {opt_portfolio_return:.2f}%")
        print(f"Risk (Standard Deviation): {opt_portfolio_risk:.2f}%")
        print(f"Sharpe Ratio: {opt_sharpe:.4f}")
        
        return optimized_percentages
    else:
        print(f"Optimization failed: {result.message}")
        # Return original percentages if optimization failed
        return percentages

def print_portfolio_comparison(original_percentages, optimized_percentages, asset_names):
    """Print a comparison of original and optimized portfolio weights"""
    print("\nPortfolio Weight Optimization Results:")
    print("-" * 50)
    print(f"{'Asset':<30} {'Original (%)':<12} {'Optimized (%)':<12}")
    print("-" * 50)
    
    for i, name in enumerate(asset_names):
        print(f"{name:<30} {original_percentages[i]:<12.2f} {optimized_percentages[i]:<12.2f}")
    
    print("-" * 50)

# Example usage
if __name__ == '__main__':
    # Example with default risk-free rate of 1.67%
    risk_free_rate = 0.0167
    optimized_weights = optimized_sharpe_ratio(risk_free_rate=risk_free_rate, min_return=15, max_weight=0.10)
    
    # Read asset names for display
    names, ids, percentages, annual_returns, risks = read_portfolio_data('portfolio.csv')
    
    # Print comparison
    print_portfolio_comparison(percentages, optimized_weights, names)
    
    # Calculate and print portfolio metrics for optimized weights
    asset_names, correlation_matrix = read_correlation_data('asset_correlationship.csv')
    returns = np.array(annual_returns)
    risks = np.array(risks)
    
    # Convert percentages to decimals for calculation
    original_weights = np.array(percentages) / 100.0
    opt_weights = np.array(optimized_weights) / 100.0
    
    # Calculate portfolio metrics
    original_portfolio_return = calculate_portfolio_return(original_weights, returns)
    original_portfolio_risk = calculate_portfolio_risk(original_weights, risks, correlation_matrix)
    
    opt_portfolio_return = calculate_portfolio_return(opt_weights, returns)
    opt_portfolio_risk = calculate_portfolio_risk(opt_weights, risks, correlation_matrix)
    
    # Calculate Sharpe ratios
    original_sharpe = (original_portfolio_return - risk_free_rate) / original_portfolio_risk if original_portfolio_risk != 0 else 0
    optimized_sharpe = (opt_portfolio_return - risk_free_rate) / opt_portfolio_risk if opt_portfolio_risk != 0 else 0
    
    print(f"\nOriginal Portfolio Metrics:")
    print(f"Annual Return: {original_portfolio_return:.2f}%")
    print(f"Risk (Standard Deviation): {original_portfolio_risk:.2f}%")
    print(f"Sharpe Ratio: {original_sharpe:.4f}")
    
    print(f"\nOptimized Portfolio Metrics:")
    print(f"Annual Return: {opt_portfolio_return:.2f}%")
    print(f"Risk (Standard Deviation): {opt_portfolio_risk:.2f}%")
    print(f"Sharpe Ratio: {optimized_sharpe:.4f}")
    
    print(f"\nSharpe Ratio Comparison:")
    print(f"Original Portfolio Sharpe Ratio:  {original_sharpe:.4f}")
    print(f"Optimized Portfolio Sharpe Ratio: {optimized_sharpe:.4f}")
    print(f"Improvement: {optimized_sharpe - original_sharpe:.4f}")
