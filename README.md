# 投资组合管理系统

这是一个完整的投资组合管理系统，可以帮助您跟踪、分析和优化您的投资组合。

## 功能特性

1. **自动获取价格数据** - 从网络自动获取基金和股票的历史价格
2. **投资组合跟踪** - 实时更新投资组合的价值和收益
3. **资产分析** - 分析资产间的相关性、年化收益和风险
4. **投资组合优化** - 使用现代投资组合理论优化资产配置
5. **交易记录** - 记录买入和卖出操作
6. **日志记录** - 详细记录所有操作和分析结果

## 文件结构

```
portfolio_from_csv/
├── watchlist.csv           # 资产观察列表（输入）
├── portfolio.csv           # 投资组合数据（核心文件）
├── percentage_change.csv   # 价格变化百分比数据
├── asset_correlationship.csv  # 资产相关性矩阵
├── create_portfolio.py     # 创建/初始化投资组合
├── update_prices.py        # 更新价格数据
├── calculate_percentage_change.py  # 计算价格变化
├── update_portfolio.py     # 更新投资组合数据
├── portfolio_analysis.py   # 投资组合分析
├── optimize_portfolio.py   # 投资组合优化
├── buy_or_sell.py          # 买入/卖出操作
├── main.py                 # 主程序
└── README.md
```

## 快速开始

### 1. 准备工作

确保已安装Python 3.x和必要的依赖包：
```bash
pip install requests lxml numpy scipy efinance
```

### 2. 设置观察列表

编辑 `watchlist.csv` 文件，添加您要跟踪的基金和股票：
```csv
name,id,type
招商双债增强债券(LOF)C,161716,fund
深证成指,399001,stock
```

### 3. 创建投资组合

运行以下命令创建初始投资组合文件：
```bash
python create_portfolio.py portfolio.csv
```

### 4. 获取价格数据

获取指定日期范围内的历史价格数据：
```bash
python update_prices.py 2023-01-01 2023-12-31
```

### 5. 计算价格变化

生成价格变化百分比数据：
```bash
python calculate_percentage_change.py
```

### 6. 更新投资组合

更新投资组合中的价格、价值和风险等数据：
```bash
python update_portfolio.py
```

### 7. 分析投资组合

进行资产相关性分析、年化收益分析和风险分析：
```bash
python portfolio_analysis.py
```

### 8. 优化投资组合

优化资产配置以最大化夏普比率：
```bash
python optimize_portfolio.py
```

### 9. 运行完整流程

按顺序执行所有步骤，可以直接运行main.py代替5-7的操作：
```bash
python main.py
```

## 详细使用说明

### 买入/卖出操作

使用以下命令记录买入或卖出操作：
```bash
# 买入：python buy_or_sell.py buy 资产ID 数量 价格
python buy_or_sell.py buy 161716 1000 1.5

# 卖出：python buy_or_sell.py sell 资产ID 数量 价格
python buy_or_sell.py sell 161716 500 1.6
```

### 查看日志

所有操作和分析结果都会记录在以下日志文件中：
- `log/` 目录：包含投资组合分析日志
- `bargain_log/` 目录：包含交易日志
- `total_value_log/` 目录：包含总资产价值日志

## 数据文件说明

### watchlist.csv
资产观察列表，包含资产名称、ID和类型。

### portfolio.csv
投资组合核心文件，包含以下列：
- name: 资产名称
- id: 资产ID
- type: 资产类型
- last_price: 最新价格
- holdings: 持有数量
- holding_price: 持仓成本价
- holding_earnings: 持仓收益
- total_value: 总价值
- percentage: 资产配置比例
- annual_return: 年化收益率
- risk: 风险

### percentage_change.csv
每日价格变化百分比数据。

### asset_correlationship.csv
资产相关性矩阵。

## 常见问题

### 如何添加新资产？
1. 在 `watchlist.csv` 中添加新资产信息或运行 `python add_portfolio.py` 添加新资产`
2. 运行 `python update_prices.py` 获取价格数据
3. 运行 `python create_portfolio.py portfolio.csv` 更新投资组合

### 如何更新价格数据？
运行 `python update_prices.py` 命令，并指定开始和结束日期。

### 如何查看分析结果？
运行 `python portfolio_analysis.py`，结果会显示在控制台并保存到 `log/` 目录的日志文件中。

## 贡献

欢迎提交问题和拉取请求来改进这个项目。

## 许可证

本项目采用Apache 2.0 许可证。
