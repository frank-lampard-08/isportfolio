import csv
import math
import logging
from datetime import datetime

# 设置日志记录
# 创建logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 创建文件处理器
import os
log_filename = f"portfolio_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_filepath = os.path.join('log', log_filename)
file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
file_handler.setLevel(logging.INFO)

# 创建格式器
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 添加处理器到logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def asset_correlation_analysis(percentage_change_file, output_file):
    """
    资产相关性分析：读取percentage_change.csv中的数据，计算各个资产之间的相关性，
    得到一个相关性矩阵并储存在asset_correlationship.csv中
    """
    try:
        # 读取percentage_change.csv数据
        with open(percentage_change_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        if not rows or len(rows) < 2:
            logger.error("percentage_change.csv文件中没有足够的数据")
            return
        
        # 提取资产名称和收益率数据
        headers = rows[0]
        assets_data = {}
        
        # 获取日期列（从第4列开始）
        date_columns = headers[3:]
        
        # 处理每个资产的数据
        for row in rows[1:]:
            asset_name = row[0]
            # 提取收益率数据并转换为数值
            returns = []
            for i in range(3, len(row)):
                if row[i]:  # 如果有数据
                    try:
                        # 移除%符号并转换为浮点数
                        returns.append(float(row[i].rstrip('%')))
                    except ValueError:
                        # 如果转换失败，跳过该数据点
                        returns.append(0.0)
                else:
                    returns.append(0.0)
            assets_data[asset_name] = returns
        
        # 获取资产名称列表
        asset_names = list(assets_data.keys())
        
        # 计算相关性矩阵
        n_assets = len(asset_names)
        correlation_matrix = [[0.0 for _ in range(n_assets)] for _ in range(n_assets)]
        
        # 计算每对资产之间的相关性
        for i in range(n_assets):
            for j in range(n_assets):
                if i == j:
                    # 同一资产的相关性为1
                    correlation_matrix[i][j] = 1.0
                else:
                    # 计算两个资产收益率之间的相关性
                    correlation = calculate_correlation(assets_data[asset_names[i]], assets_data[asset_names[j]])
                    correlation_matrix[i][j] = correlation
        
        # 将相关性矩阵写入asset_correlationship.csv
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入表头
            header_row = [''] + asset_names
            writer.writerow(header_row)
            
            # 写入相关性数据
            for i in range(n_assets):
                data_row = [asset_names[i]] + [f"{correlation_matrix[i][j]:.4f}" for j in range(n_assets)]
                writer.writerow(data_row)
        
        logger.info(f"资产相关性分析完成，结果已保存到{output_file}")
        return correlation_matrix, asset_names
        
    except Exception as e:
        logger.error(f"资产相关性分析过程中出现错误: {e}")
        return None, None

def calculate_correlation(returns1, returns2):
    """
    计算两个资产收益率序列之间的相关性
    """
    if len(returns1) != len(returns2) or len(returns1) == 0:
        return 0.0
    
    n = len(returns1)
    
    # 计算平均值
    mean1 = sum(returns1) / n
    mean2 = sum(returns2) / n
    
    # 计算协方差和标准差
    covariance = sum((returns1[i] - mean1) * (returns2[i] - mean2) for i in range(n))
    variance1 = sum((returns1[i] - mean1) ** 2 for i in range(n))
    variance2 = sum((returns2[i] - mean2) ** 2 for i in range(n))
    
    # 避免除零错误
    if variance1 == 0 or variance2 == 0:
        return 0.0
    
    # 计算相关性
    correlation = covariance / (math.sqrt(variance1) * math.sqrt(variance2))
    return correlation

def portfolio_annual_return_analysis(portfolio_file):
    """
    资产组合年化收益分析：通过读取portfolio.csv中各个资产的percentage和年化收益率计算整个资产组合的年化收益率
    """
    try:
        # 读取portfolio.csv数据
        with open(portfolio_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        if not rows or len(rows) < 2:
            logger.error("portfolio.csv文件中没有足够的数据")
            return None
        
        # 找到相关列的索引
        headers = rows[0]
        percentage_index = -1
        annual_return_index = -1
        
        for i, header in enumerate(headers):
            if header == 'percentage':
                percentage_index = i
            elif header == 'annual_return':
                annual_return_index = i
        
        if percentage_index == -1 or annual_return_index == -1:
            logger.error("无法找到percentage或annual_return列")
            return None
        
        # 计算资产组合的年化收益率
        portfolio_return = 0.0
        
        for row in rows[1:]:  # 跳过表头
            try:
                # 提取权重和年化收益率
                weight_str = row[percentage_index].rstrip('%')
                annual_return_str = row[annual_return_index].rstrip('%')
                
                weight = float(weight_str) / 100  # 转换为小数
                annual_return = float(annual_return_str) / 100  # 转换为小数
                
                # 计算加权收益
                portfolio_return += weight * annual_return
            except ValueError as e:
                logger.warning(f"处理资产{row[0]}时出现数据转换错误: {e}")
                continue
        
        # 转换为百分比形式
        portfolio_return_percentage = portfolio_return * 100
        
        logger.info(f"资产组合年化收益率分析完成: {portfolio_return_percentage:.2f}%")
        return portfolio_return_percentage
        
    except Exception as e:
        logger.error(f"资产组合年化收益分析过程中出现错误: {e}")
        return None

def portfolio_risk_analysis(portfolio_file, correlation_file):
    """
    资产组合风险分析：通过读取portfolio.csv中各个资产的percentage，risk以及相关性矩阵计算整个资产组合的风险
    """
    try:
        # 读取portfolio.csv数据
        with open(portfolio_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        if not rows or len(rows) < 2:
            logger.error("portfolio.csv文件中没有足够的数据")
            return None
        
        # 找到相关列的索引
        headers = rows[0]
        asset_names = []
        weights = []
        individual_risks = []
        
        percentage_index = -1
        risk_index = -1
        
        for i, header in enumerate(headers):
            if header == 'percentage':
                percentage_index = i
            elif header == 'risk':
                risk_index = i
        
        if percentage_index == -1 or risk_index == -1:
            logger.error("无法找到percentage或risk列")
            return None
        
        # 提取资产名称、权重和个体风险
        for row in rows[1:]:  # 跳过表头
            try:
                asset_names.append(row[0])
                weight_str = row[percentage_index].rstrip('%')
                risk_str = row[risk_index].rstrip('%')
                
                weight = float(weight_str) / 100  # 转换为小数
                risk = float(risk_str) / 100  # 转换为小数
                
                weights.append(weight)
                individual_risks.append(risk)
            except ValueError as e:
                logger.warning(f"处理资产{row[0]}时出现数据转换错误: {e}")
                return None
        
        # 读取相关性矩阵
        with open(correlation_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            correlation_rows = list(reader)
        
        if not correlation_rows or len(correlation_rows) < 2:
            logger.error("相关性矩阵文件中没有足够的数据")
            return None
        
        # 验证资产名称是否匹配
        correlation_asset_names = correlation_rows[0][1:]  # 跳过第一个空单元格
        if correlation_asset_names != asset_names:
            logger.error("portfolio.csv和相关性矩阵文件中的资产名称不匹配")
            return None
        
        # 提取相关性矩阵数据
        correlation_matrix = []
        for row in correlation_rows[1:]:  # 跳过表头
            correlation_row = []
            for i in range(1, len(row)):  # 跳过资产名称列
                try:
                    correlation_row.append(float(row[i]))
                except ValueError:
                    logger.warning(f"相关性矩阵中存在无效数据: {row[i]}")
                    correlation_row.append(0.0)
            correlation_matrix.append(correlation_row)
        
        # 计算资产组合风险
        # 公式: σ_p = √(ΣΣ w_i * w_j * σ_i * σ_j * ρ_ij)
        portfolio_variance = 0.0
        
        for i in range(len(weights)):
            for j in range(len(weights)):
                portfolio_variance += (
                    weights[i] * weights[j] * 
                    individual_risks[i] * individual_risks[j] * 
                    correlation_matrix[i][j]
                )
        
        # 计算标准差（风险）
        portfolio_risk = math.sqrt(portfolio_variance)
        
        # 转换为百分比形式
        portfolio_risk_percentage = portfolio_risk * 100
        
        logger.info(f"资产组合风险分析完成: {portfolio_risk_percentage:.2f}%")
        return portfolio_risk_percentage
        
    except Exception as e:
        logger.error(f"资产组合风险分析过程中出现错误: {e}")
        return None

def portfolio_analysis():
    """
    主函数：执行所有分析
    """
    logger.info("开始资产组合分析")
    
    # 1. 资产相关性分析
    correlation_matrix, asset_names = asset_correlation_analysis('percentage_change.csv', 'asset_correlationship.csv')
    
    # 2. 资产组合年化收益分析
    portfolio_return = portfolio_annual_return_analysis('portfolio.csv')
    
    # 3. 资产组合风险分析
    portfolio_risk = portfolio_risk_analysis('portfolio.csv', 'asset_correlationship.csv')
    
    # 输出最终结果
    logger.info("=== 资产组合分析结果 ===")
    if portfolio_return is not None:
        logger.info(f"资产组合年化收益率: {portfolio_return:.2f}%")
    if portfolio_risk is not None:
        logger.info(f"资产组合风险: {portfolio_risk:.2f}%")
    
    logger.info("资产组合分析完成")

if __name__ == '__main__':
    portfolio_analysis()
