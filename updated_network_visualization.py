import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')

# Set Chinese font for matplotlib
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# Load and process the data
df = pd.read_csv('integrated ABS.csv')

# Data preprocessing
df['申报日期'] = pd.to_datetime(df['申报日期'])
df['反馈/获批日期'] = pd.to_datetime(df['反馈/获批日期'].str.split('；').str[0])
df['拟发行金额(亿元)'] = pd.to_numeric(df['拟发行金额(亿元)'])

# Extract asset types from ABS names
def extract_asset_type(name):
    if '数据中心' in name:
        return '数据中心'
    elif '高速' in name:
        return '高速公路'
    elif '住房租赁' in name:
        return '住房租赁'
    elif '商业' in name:
        return '商业地产'
    elif '新能源' in name or '火电' in name:
        return '能源设施'
    elif '物流' in name:
        return '物流仓储'
    elif '产业园' in name:
        return '产业园区'
    elif '铁建' in name:
        return '基础设施'
    else:
        return '其他'

df['资产类型'] = df['ABS'].apply(extract_asset_type)

# Identify green/carbon neutral projects
def is_green_project(name):
    green_keywords = ['碳中和', '新能源', '绿色', '环保', '清洁']
    return any(keyword in name for keyword in green_keywords)

df['绿色认证'] = df['ABS'].apply(is_green_project)

# Create network visualization
fig, ax = plt.subplots(figsize=(20, 16))
ax.set_xlim(-12, 12)
ax.set_ylim(-10, 10)
ax.set_aspect('equal')

# Color schemes
colors_underwriter = {
    '中金公司': '#2E86AB',
    '国金资管': '#A23B72', 
    '人保资产': '#F18F01',
    '华泰资管': '#C73E1D',
    '中信证券': '#6A994E',
    '太平洋资产': '#577590',
    '泰康资产': '#F8961E',
    '平安证券': '#90323D'
}

colors_asset = {
    '高速公路': '#FF6B6B',
    '能源设施': '#4ECDC4', 
    '商业地产': '#45B7D1',
    '数据中心': '#96CEB4',
    '住房租赁': '#FFEAA7',
    '物流仓储': '#DDA0DD',
    '基础设施': '#98D8C8',
    '产业园区': '#F7DC6F',
    '其他': '#AED6F1'
}

# Define positions for underwriters (center circle)
underwriter_stats = df.groupby('承销商/管理人').agg({
    '拟发行金额(亿元)': 'sum',
    'ABS': 'count'
}).round(2)
underwriter_stats.columns = ['总规模', '产品数量']
underwriter_stats = underwriter_stats.sort_values('总规模', ascending=False)

# Position underwriters in center
center_radius = 3
underwriter_positions = {}
for i, (underwriter, stats) in enumerate(underwriter_stats.iterrows()):
    angle = 2 * np.pi * i / len(underwriter_stats)
    x = center_radius * np.cos(angle)
    y = center_radius * np.sin(angle)
    underwriter_positions[underwriter] = (x, y)

# Position asset types around the outside
asset_stats = df.groupby('资产类型').agg({
    '拟发行金额(亿元)': 'sum',
    'ABS': 'count'
}).round(2)
asset_stats.columns = ['总规模', '产品数量']
asset_stats = asset_stats.sort_values('总规模', ascending=False)

outer_radius = 8
asset_positions = {}
for i, (asset_type, stats) in enumerate(asset_stats.iterrows()):
    angle = 2 * np.pi * i / len(asset_stats)
    x = outer_radius * np.cos(angle)
    y = outer_radius * np.sin(angle)
    asset_positions[asset_type] = (x, y)

# Draw connections between underwriters and asset types
for _, row in df.iterrows():
    underwriter = row['承销商/管理人']
    asset_type = row['资产类型']
    scale = row['拟发行金额(亿元)']
    is_green = row['绿色认证']
    status = row['状态']
    
    if underwriter in underwriter_positions and asset_type in asset_positions:
        x1, y1 = underwriter_positions[underwriter]
        x2, y2 = asset_positions[asset_type]
        
        # Line style based on status and green certification
        if status == '已发行':
            linestyle = '-'
            alpha = 0.8
        else:
            linestyle = '--'
            alpha = 0.6
            
        if is_green:
            color = '#27AE60'
            linewidth = max(2, scale/10)
        else:
            color = '#7F8C8D'
            linewidth = max(1, scale/15)
            
        ax.plot([x1, x2], [y1, y2], color=color, linewidth=linewidth, 
                linestyle=linestyle, alpha=alpha, zorder=1)

# Draw underwriter nodes
for underwriter, (x, y) in underwriter_positions.items():
    stats = underwriter_stats.loc[underwriter]
    size = max(800, stats['总规模'] * 15)
    color = colors_underwriter.get(underwriter, '#95A5A6')
    
    # Draw circle
    circle = Circle((x, y), radius=np.sqrt(size)/50, color=color, alpha=0.8, zorder=3)
    ax.add_patch(circle)
    
    # Add text
    ax.text(x, y, f"{underwriter}\n{stats['总规模']:.1f}亿\n{stats['产品数量']}只", 
            ha='center', va='center', fontsize=10, fontweight='bold', 
            color='white', zorder=4)

# Draw asset type nodes
for asset_type, (x, y) in asset_positions.items():
    stats = asset_stats.loc[asset_type]
    size = max(600, stats['总规模'] * 12)
    color = colors_asset.get(asset_type, '#BDC3C7')
    
    # Draw circle
    circle = Circle((x, y), radius=np.sqrt(size)/60, color=color, alpha=0.7, zorder=2)
    ax.add_patch(circle)
    
    # Add text
    ax.text(x, y, f"{asset_type}\n{stats['总规模']:.1f}亿\n{stats['产品数量']}只", 
            ha='center', va='center', fontsize=9, fontweight='bold', 
            color='white', zorder=4)

# Add individual projects as small nodes
project_radius = 10
project_positions = {}
for i, (_, row) in enumerate(df.iterrows()):
    angle = 2 * np.pi * i / len(df)
    x = project_radius * np.cos(angle)
    y = project_radius * np.sin(angle)
    
    scale = row['拟发行金额(亿元)']
    status = row['状态']
    is_green = row['绿色认证']
    
    # Size based on scale
    size = max(50, scale * 8)
    
    # Color based on status
    if status == '已发行':
        color = '#2ECC71'
        alpha = 0.8
    else:
        color = '#F39C12'
        alpha = 0.6
        
    # Green border for green projects
    if is_green:
        edge_color = '#27AE60'
        edge_width = 3
    else:
        edge_color = 'white'
        edge_width = 1
    
    circle = Circle((x, y), radius=np.sqrt(size)/20, color=color, alpha=alpha, 
                   edgecolor=edge_color, linewidth=edge_width, zorder=2)
    ax.add_patch(circle)
    
    # Add project name for large projects
    if scale > 20:
        project_name = row['ABS'][:15] + '...' if len(row['ABS']) > 15 else row['ABS']
        ax.text(x, y-np.sqrt(size)/15, project_name, ha='center', va='top', 
                fontsize=7, rotation=angle*180/np.pi if abs(angle) > np.pi/2 else 0)

# Add title and legends
ax.set_title('中国持有型不动产ABS市场网络分析图\nChina Holding-Type Real Estate ABS Market Network Analysis', 
             fontsize=20, fontweight='bold', pad=30)

# Create legends
# Status legend
status_legend = [
    mpatches.Patch(color='#2ECC71', label='已发行 (Issued)'),
    mpatches.Patch(color='#F39C12', label='申报中 (Pending)')
]

# Green certification legend
green_legend = [
    mpatches.Patch(color='#27AE60', label='绿色认证 (Green Certified)'),
    mpatches.Patch(color='#7F8C8D', label='常规项目 (Regular Projects)')
]

# Add legends
legend1 = ax.legend(handles=status_legend, loc='upper left', bbox_to_anchor=(0.02, 0.98), 
                   title='项目状态 Project Status', fontsize=10)
legend2 = ax.legend(handles=green_legend, loc='upper left', bbox_to_anchor=(0.02, 0.85), 
                   title='绿色认证 Green Certification', fontsize=10)
ax.add_artist(legend1)

# Add market statistics
stats_text = f"""
市场统计 Market Statistics:
• 总规模: 324.8亿元 (Total: 324.8B RMB)
• 产品数量: 17只 (Products: 17)
• 平均规模: 19.1亿元 (Average: 19.1B RMB)
• 已发行: 10只 (Issued: 10)
• 申报中: 7只 (Pending: 7)
• 绿色认证率: 5.9% (Green Rate: 5.9%)
"""

ax.text(0.98, 0.02, stats_text, transform=ax.transAxes, fontsize=11,
        verticalalignment='bottom', horizontalalignment='right',
        bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.8))

# Add network explanation
explanation_text = """
网络结构说明 Network Structure:
• 中心圆圈: 承销商 (Center: Underwriters)
• 外围圆圈: 资产类型 (Outer: Asset Types)  
• 最外圈: 具体项目 (Outermost: Individual Projects)
• 连线粗细: 发行规模 (Line Width: Issuance Scale)
• 实线: 已发行 | 虚线: 申报中
  (Solid: Issued | Dashed: Pending)
"""

ax.text(0.02, 0.02, explanation_text, transform=ax.transAxes, fontsize=10,
        verticalalignment='bottom', horizontalalignment='left',
        bbox=dict(boxstyle="round,pad=0.5", facecolor='lightyellow', alpha=0.8))

# Remove axes
ax.set_xticks([])
ax.set_yticks([])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

plt.tight_layout()
plt.savefig('Updated_ABS_Network_Visualization.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.show()

print("=== 网络分析摘要 Network Analysis Summary ===")
print(f"承销商网络节点: {len(underwriter_stats)} (Underwriter Nodes: {len(underwriter_stats)})")
print(f"资产类型节点: {len(asset_stats)} (Asset Type Nodes: {len(asset_stats)})")
print(f"项目节点: {len(df)} (Project Nodes: {len(df)})")
print(f"网络连接数: {len(df)} (Network Connections: {len(df)})")

print("\n=== 网络中心性分析 Network Centrality Analysis ===")
print("承销商中心性排名 (Underwriter Centrality Ranking):")
for underwriter, stats in underwriter_stats.head(5).iterrows():
    centrality = stats['产品数量'] / len(df) * 100
    print(f"{underwriter}: {centrality:.1f}% ({stats['产品数量']}只产品)")

print("\n资产类型中心性排名 (Asset Type Centrality Ranking):")
for asset_type, stats in asset_stats.head(5).iterrows():
    centrality = stats['产品数量'] / len(df) * 100
    print(f"{asset_type}: {centrality:.1f}% ({stats['产品数量']}只产品)") 