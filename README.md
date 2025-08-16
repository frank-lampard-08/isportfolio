# Portfolio Updater

This Python script updates the `last_price` column in `portfolio.csv` with the latest available prices from `watchlist.csv`, calculates the `total_value` based on `last_price` and `holdings`, calculates the asset allocation percentage for each asset, and calculates annualized returns and risks based on historical percentage changes.

## How it works

The script:
1. Reads the `watchlist.csv` file to extract the latest available prices for each asset
2. Reads the `portfolio.csv` file
3. Updates the `last_price` column in `portfolio.csv` with the latest prices from `watchlist.csv`
4. Calculates the `total_value` column as `last_price` * `holdings`
5. Calculates the `percentage` column as `(total_value / sum of all total_values) * 100%`
6. Calculates the `annual_return` and `risk` columns based on historical percentage changes in `percentage_change.csv`
7. Saves the updated data back to `portfolio.csv`

## Usage

Run the script with:
```bash
python update_portfolio.py
```

## Features

- Automatically finds the latest date column in `watchlist.csv`
- Handles cases where some assets don't have prices for the latest date by using the most recent available price
- Calculates total_value as last_price * holdings
- If holdings is empty, total_value is set to 0
- Calculates percentage as (total_value / sum of all total_values) * 100%
- Calculates annual_return as average daily return * 252 trading days
- Calculates risk as annualized standard deviation of daily returns
- Validates data consistency between portfolio.csv and percentage_change.csv
- Preserves all other data in `portfolio.csv`

## Files

- `update_portfolio.py`: Main script
- `watchlist.csv`: Source of price data
- `portfolio.csv`: Target file to update
- `percentage_change.csv`: Historical percentage changes for return and risk calculations

## Requirements

- Python 3.x
- CSV files in the specified formats


# Portfolio Analysis

This Python script performs portfolio analysis including asset correlation analysis, portfolio annual return analysis, and portfolio risk analysis.

## Features

1. **Asset Correlation Analysis**: Reads data from `percentage_change.csv` and calculates correlations between assets, generating a correlation matrix stored in `asset_correlationship.csv`.

2. **Portfolio Annual Return Analysis**: Calculates the overall portfolio annual return based on individual asset weights and annual returns from `portfolio.csv`.

3. **Portfolio Risk Analysis**: Calculates the overall portfolio risk based on individual asset weights, risks, and the correlation matrix.

## Usage

Run the script with:
```bash
python portfolio_analysis.py
```

## Functions

### asset_correlation_analysis(percentage_change_file, output_file)
- Reads percentage change data from `percentage_change.csv`
- Calculates correlation coefficients between all pairs of assets
- Outputs the correlation matrix to `asset_correlationship.csv`

### portfolio_annual_return_analysis(portfolio_file)
- Reads asset weights and annual returns from `portfolio.csv`
- Calculates weighted average portfolio return
- Logs the result

### portfolio_risk_analysis(portfolio_file, correlation_file)
- Reads asset weights and individual risks from `portfolio.csv`
- Reads correlation matrix from `asset_correlationship.csv`
- Calculates portfolio risk using the formula: σ_p = √(ΣΣ w_i * w_j * σ_i * σ_j * ρ_ij)
- Logs the result

## Output Files

- `asset_correlationship.csv`: Contains the asset correlation matrix
- `log/portfolio_analysis_YYYYMMDD_HHMMSS.log`: Contains detailed logs of the analysis process and results

## Log Output

The script logs all results and process information to the console, including:
- Asset correlation matrix
- Portfolio annual return
- Portfolio risk

## Requirements

- Python 3.x
- CSV files in the specified formats
- Standard Python libraries (csv, math, logging)
