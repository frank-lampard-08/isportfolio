import optimize_portfolio

# Test the optimized_sharpe_ratio function
print("Testing optimized_sharpe_ratio function...")

# Call the function with a risk-free rate of 2%
optimized_weights = optimize_portfolio.optimized_sharpe_ratio(risk_free_rate=2.0)

print("Optimization completed successfully!")
print(f"Number of assets: {len(optimized_weights)}")
print("Optimized weights (%):")
for i, weight in enumerate(optimized_weights):
    print(f"  Asset {i+1}: {weight:.2f}%")
