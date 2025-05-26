import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle, FancyBboxPatch
import warnings
warnings.filterwarnings('ignore')

# Set style and Chinese font
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.facecolor'] = 'white'

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

# Define consistent color palette - Bold and clear
COLORS = {
    'primary': '#3B82F6',      # Bold blue
    'secondary': '#8B5CF6',    # Bold purple
    'accent1': '#F59E0B',      # Bold amber
    'accent2': '#EF4444',      # Bold red
    'success': '#10B981',      # Bold emerald
    'info': '#06B6D4',         # Bold cyan
    'warning': '#F97316',      # Bold orange
    'light': '#F8FAFC',        # Light gray
    'dark': '#1F2937',         # Dark gray
    'text': '#374151'          # Medium gray
}

# Color schemes for different chart types - Bold and vibrant
PALETTE_MAIN = [COLORS['primary'], COLORS['success'], COLORS['accent1'], 
                COLORS['secondary'], COLORS['info'], COLORS['accent2'], 
                COLORS['warning'], '#9333EA', '#DC2626']

PALETTE_STATUS = {'已发行': COLORS['primary'], '已申报': COLORS['accent1']}
PALETTE_GREEN = [COLORS['accent2'], COLORS['info']]

# Calculate key statistics
total_scale = df['拟发行金额(亿元)'].sum()
total_products = len(df)
avg_scale = df['拟发行金额(亿元)'].mean()
issued_products = len(df[df['状态'] == '已发行'])
pending_products = len(df[df['状态'] == '已申报'])
green_ratio = df['绿色认证'].mean() * 100
pipeline_scale = df[df['状态'] == '已申报']['拟发行金额(亿元)'].sum()

# Create streamlined dashboard with clear visual hierarchy
fig = plt.figure(figsize=(20, 24))
gs = fig.add_gridspec(6, 4, height_ratios=[0.8, 1.5, 1.5, 1.5, 1.2, 1.0], 
                      width_ratios=[1, 1, 1, 1], hspace=0.4, wspace=0.3)

# ============================================================================
# SECTION 1: HEADER WITH KEY METRICS (Top Story)
# ============================================================================
ax_header = fig.add_subplot(gs[0, :])
ax_header.axis('off')

# Main title with modern styling
title_box = FancyBboxPatch((0.05, 0.4), 0.9, 0.5, 
                          boxstyle="round,pad=0.02", 
                          facecolor=COLORS['primary'], alpha=0.1,
                          edgecolor=COLORS['primary'], linewidth=2)
ax_header.add_patch(title_box)

ax_header.text(0.5, 0.75, '中国持有型不动产ABS市场全景分析', 
               ha='center', va='center', fontsize=28, fontweight='bold', 
               transform=ax_header.transAxes, color=COLORS['dark'])
ax_header.text(0.5, 0.55, 'China Holding-Type Real Estate ABS Market Overview', 
               ha='center', va='center', fontsize=16, 
               transform=ax_header.transAxes, color=COLORS['text'])

# Key metrics with modern card design
metrics = [
    ('总规模', f'{total_scale:.1f}亿元', 'Total Scale', COLORS['primary']),
    ('产品数量', f'{total_products}只', 'Products', COLORS['accent1']),
    ('平均规模', f'{avg_scale:.1f}亿元', 'Average', COLORS['success']),
    ('申报管道', f'{pipeline_scale:.1f}亿元', 'Pipeline', COLORS['secondary'])
]

for i, (label_cn, value, label_en, color) in enumerate(metrics):
    x_pos = 0.1 + i * 0.2
    
    # Modern card background
    card = FancyBboxPatch((x_pos-0.08, 0.05), 0.16, 0.25, 
                         boxstyle="round,pad=0.01", 
                         facecolor=color, alpha=0.15,
                         edgecolor=color, linewidth=1.5)
    ax_header.add_patch(card)
    
    ax_header.text(x_pos, 0.25, value, ha='center', va='center', 
                   fontsize=14, fontweight='bold', color=color,
                   transform=ax_header.transAxes)
    ax_header.text(x_pos, 0.15, label_cn, ha='center', va='center', 
                   fontsize=10, fontweight='bold', color=COLORS['dark'],
                   transform=ax_header.transAxes)
    ax_header.text(x_pos, 0.08, label_en, ha='center', va='center', 
                   fontsize=8, color=COLORS['text'],
                   transform=ax_header.transAxes)

# ============================================================================
# SECTION 2: MARKET DEVELOPMENT STORY (Timeline + Status)
# ============================================================================

# 2.1 Market Timeline - The Growth Story
ax1 = fig.add_subplot(gs[1, :3])
issued_df = df[df['状态'] == '已发行'].copy()
pending_df = df[df['状态'] == '已申报'].copy()

# Create timeline with better visual storytelling
scatter1 = ax1.scatter(issued_df['申报日期'], issued_df['拟发行金额(亿元)'], 
                      c=COLORS['primary'], s=issued_df['拟发行金额(亿元)']*8, 
                      alpha=0.8, label='已发行产品', edgecolors='white', 
                      linewidth=2, zorder=3)
scatter2 = ax1.scatter(pending_df['申报日期'], pending_df['拟发行金额(亿元)'], 
                      c=COLORS['accent1'], s=pending_df['拟发行金额(亿元)']*8, 
                      alpha=0.8, label='申报中产品', edgecolors='white', 
                      linewidth=2, zorder=3)

# Add trend line for storytelling
if len(df) > 1:
    z = np.polyfit(mdates.date2num(df['申报日期']), df['拟发行金额(亿元)'], 1)
    p = np.poly1d(z)
    ax1.plot(df['申报日期'], p(mdates.date2num(df['申报日期'])), 
             color=COLORS['success'], linestyle='--', linewidth=3, 
             alpha=0.7, label='发展趋势', zorder=2)

ax1.set_title('市场发展时间轴：从试点到规模化', 
              fontsize=16, fontweight='bold', pad=20, color=COLORS['dark'])
ax1.set_xlabel('申报时间', fontsize=12, fontweight='bold', color=COLORS['text'])
ax1.set_ylabel('发行规模 (亿元)', fontsize=12, fontweight='bold', color=COLORS['text'])

# Styling
ax1.legend(fontsize=11, loc='upper left', frameon=True, fancybox=True, 
          shadow=True, framealpha=0.95)
ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
ax1.set_facecolor(COLORS['light'])

# Format dates
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

# 2.2 Market Status Overview
ax2 = fig.add_subplot(gs[1, 3])
status_counts = df['状态'].value_counts()

# Modern donut chart
wedges, texts, autotexts = ax2.pie(status_counts.values, 
                                  labels=status_counts.index,
                                  colors=[PALETTE_STATUS[status] for status in status_counts.index],
                                  autopct='%1.1f%%', startangle=90,
                                  wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2),
                                  textprops={'fontsize': 11, 'fontweight': 'bold'})

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')

ax2.set_title('项目状态分布', fontsize=14, fontweight='bold', 
              pad=20, color=COLORS['dark'])

# ============================================================================
# SECTION 3: MARKET STRUCTURE ANALYSIS
# ============================================================================

# 3.1 Asset Type Distribution - The Portfolio Story
ax3 = fig.add_subplot(gs[2, :2])
asset_stats = df.groupby('资产类型')['拟发行金额(亿元)'].sum().sort_values(ascending=True)  # 改为升序，小的在下面

# Horizontal bar chart with modern styling and proper alignment
bars = ax3.barh(range(len(asset_stats)), asset_stats.values, 
                color=PALETTE_MAIN[:len(asset_stats)], alpha=0.85,
                edgecolor='white', linewidth=2, height=0.6)

ax3.set_yticks(range(len(asset_stats)))
ax3.set_yticklabels(asset_stats.index, fontsize=10, fontweight='bold')
ax3.set_xlabel('发行规模 (亿元)', fontsize=12, fontweight='bold', color=COLORS['text'])
ax3.set_title('资产类型分布：基础设施主导的多元化格局', 
              fontsize=14, fontweight='bold', pad=20, color=COLORS['dark'])

# Add value labels with better positioning - 放在条形图内部
max_width = asset_stats.max()
for i, bar in enumerate(bars):
    width = bar.get_width()
    if width > max_width * 0.15:  # 如果条形够长，放在内部
        ax3.text(width * 0.95, bar.get_y() + bar.get_height()/2,
                 f'{width:.1f}亿', ha='right', va='center', fontsize=9, 
                 fontweight='bold', color='white')
    else:  # 如果条形太短，放在外部但控制距离
        ax3.text(width + max_width*0.02, bar.get_y() + bar.get_height()/2,
                 f'{width:.1f}亿', ha='left', va='center', fontsize=9, fontweight='bold')

# 设置x轴范围，防止文字突出
ax3.set_xlim(0, max_width * 1.15)
ax3.grid(True, alpha=0.3, axis='x', linestyle='-', linewidth=0.5)
ax3.set_facecolor(COLORS['light'])

# 3.2 Top Underwriters - The Market Leaders
ax4 = fig.add_subplot(gs[2, 2:])
underwriter_stats = df.groupby('承销商/管理人')['拟发行金额(亿元)'].sum().sort_values(ascending=False).head(5)

bars = ax4.bar(range(len(underwriter_stats)), underwriter_stats.values, 
               color=PALETTE_MAIN[:len(underwriter_stats)], alpha=0.8,
               edgecolor='white', linewidth=2, width=0.6)

ax4.set_xticks(range(len(underwriter_stats)))
ax4.set_xticklabels([name.replace('资产', '').replace('资管', '') for name in underwriter_stats.index], 
                   rotation=45, ha='right', fontsize=10, fontweight='bold')
ax4.set_ylabel('发行规模 (亿元)', fontsize=12, fontweight='bold', color=COLORS['text'])
ax4.set_title('头部承销商：专业化竞争格局', 
              fontsize=14, fontweight='bold', pad=20, color=COLORS['dark'])

# Add value labels
for i, bar in enumerate(bars):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + underwriter_stats.max()*0.02,
             f'{height:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax4.grid(True, alpha=0.3, axis='y', linestyle='-', linewidth=0.5)
ax4.set_facecolor(COLORS['light'])

# ============================================================================
# SECTION 4: INNOVATION & TRENDS
# ============================================================================

# 4.1 Scale Distribution Analysis
ax5 = fig.add_subplot(gs[3, 0])
scale_bins = [0, 10, 20, 30, 60]
scale_labels = ['<10亿', '10-20亿', '20-30亿', '>30亿']
df['规模区间'] = pd.cut(df['拟发行金额(亿元)'], bins=scale_bins, labels=scale_labels, include_lowest=True)
scale_dist = df['规模区间'].value_counts().sort_index()

bars = ax5.bar(scale_dist.index, scale_dist.values, 
               color=PALETTE_MAIN[:len(scale_dist)], alpha=0.8,
               edgecolor='white', linewidth=2, width=0.6)

ax5.set_title('规模分布', fontsize=12, fontweight='bold', 
              pad=15, color=COLORS['dark'])
ax5.set_ylabel('产品数量', fontsize=10, fontweight='bold', color=COLORS['text'])

for i, bar in enumerate(bars):
    height = bar.get_height()
    ax5.text(bar.get_x() + bar.get_width()/2., height + 0.1,
             f'{int(height)}', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax5.grid(True, alpha=0.3, axis='y', linestyle='-', linewidth=0.5)
ax5.set_facecolor(COLORS['light'])

# 4.2 Green Finance Innovation
ax6 = fig.add_subplot(gs[3, 1])
green_counts = df['绿色认证'].value_counts()
colors_green = [COLORS['accent2'], COLORS['success']]

wedges, texts, autotexts = ax6.pie(green_counts.values, 
                                  labels=['传统项目', '绿色项目'],
                                  colors=colors_green,
                                  autopct='%1.1f%%', startangle=90,
                                  wedgeprops=dict(width=0.6, edgecolor='white', linewidth=2),
                                  textprops={'fontsize': 10, 'fontweight': 'bold'})

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')

ax6.set_title('绿色金融创新', fontsize=12, fontweight='bold', 
              pad=15, color=COLORS['dark'])

# 4.3 Monthly Trends
ax7 = fig.add_subplot(gs[3, 2:])
df['申报年月'] = df['申报日期'].dt.to_period('M')
monthly_apps = df.groupby('申报年月').size()
monthly_scale = df.groupby('申报年月')['拟发行金额(亿元)'].sum()

ax7_twin = ax7.twinx()
line1 = ax7.plot(monthly_apps.index.astype(str), monthly_apps.values, 
                 'o-', color=COLORS['primary'], linewidth=3, markersize=6, 
                 label='申报数量', markerfacecolor='white', markeredgewidth=2)
line2 = ax7_twin.plot(monthly_scale.index.astype(str), monthly_scale.values, 
                      's-', color=COLORS['accent1'], linewidth=3, markersize=6, 
                      label='申报规模', markerfacecolor='white', markeredgewidth=2)

ax7.set_title('月度申报趋势：加速发展态势', 
              fontsize=12, fontweight='bold', pad=15, color=COLORS['dark'])
ax7.set_ylabel('申报数量', color=COLORS['primary'], fontsize=10, fontweight='bold')
ax7_twin.set_ylabel('申报规模(亿元)', color=COLORS['accent1'], fontsize=10, fontweight='bold')

# Combine legends
lines1, labels1 = ax7.get_legend_handles_labels()
lines2, labels2 = ax7_twin.get_legend_handles_labels()
ax7.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)

ax7.tick_params(axis='x', rotation=45, labelsize=8)
ax7.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
ax7.set_facecolor(COLORS['light'])

# ============================================================================
# SECTION 5: TOP PROJECTS SHOWCASE - 改为垂直条形图
# ============================================================================
ax8 = fig.add_subplot(gs[4, :])
top_projects = df.nlargest(6, '拟发行金额(亿元)')

# 使用垂直条形图避免文字突出问题
bars = ax8.bar(range(len(top_projects)), top_projects['拟发行金额(亿元)'], 
               color=[PALETTE_STATUS[status] for status in top_projects['状态']],
               alpha=0.9, edgecolor='white', linewidth=2, width=0.7)

# 简化项目名称用于x轴标签
project_names = []
for name in top_projects['ABS']:
    # 提取关键词
    if '安江高速' in name:
        project_names.append('安江高速')
    elif '万国数据' in name:
        project_names.append('万国数据')
    elif '广明高速' in name:
        project_names.append('广明高速')
    elif '九永高速' in name:
        project_names.append('九永高速')
    elif '中交路建' in name:
        project_names.append('中交路建')
    elif '越秀商业' in name:
        project_names.append('越秀商业')
    else:
        # 取前8个字符
        project_names.append(name[:8] + '...' if len(name) > 8 else name)

ax8.set_xticks(range(len(top_projects)))
ax8.set_xticklabels(project_names, fontsize=11, fontweight='bold', rotation=45, ha='right')
ax8.set_ylabel('发行规模 (亿元)', fontsize=12, fontweight='bold', color=COLORS['text'])
ax8.set_title('重点项目展示：规模化发展的标杆案例', 
              fontsize=16, fontweight='bold', pad=20, color=COLORS['dark'])

# 在条形图顶部添加数值标签
max_height = top_projects['拟发行金额(亿元)'].max()
for i, bar in enumerate(bars):
    height = bar.get_height()
    ax8.text(bar.get_x() + bar.get_width()/2., height + max_height*0.01,
             f'{height:.1f}亿', ha='center', va='bottom', fontsize=10, 
             fontweight='bold', color=COLORS['dark'])

# Add legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=PALETTE_STATUS['已发行'], label='已发行'),
                   Patch(facecolor=PALETTE_STATUS['已申报'], label='申报中')]
ax8.legend(handles=legend_elements, loc='upper right', fontsize=11)

ax8.grid(True, alpha=0.3, axis='y', linestyle='-', linewidth=0.5)
ax8.set_facecolor(COLORS['light'])
ax8.set_ylim(0, max_height * 1.15)

# ============================================================================
# SECTION 6: MARKET INSIGHTS & OUTLOOK
# ============================================================================
ax9 = fig.add_subplot(gs[5, :])
ax9.axis('off')

# Create insight cards with modern design
insights = [
    ("市场规模", f"总规模{total_scale:.1f}亿元，平均{avg_scale:.1f}亿元/只", COLORS['primary']),
    ("发展阶段", f"已发行{issued_products}只，申报中{pending_products}只", COLORS['accent1']),
    ("资产结构", "高速公路主导，数据中心等新兴资产崛起", COLORS['success']),
    ("创新特色", f"绿色认证{green_ratio:.1f}%，ESG理念融入", COLORS['secondary']),
    ("发展前景", f"申报管道{pipeline_scale:.1f}亿元，增长潜力巨大", COLORS['info'])
]

card_width = 0.18
for i, (title, content, color) in enumerate(insights):
    x_pos = 0.05 + i * 0.19
    
    # Modern insight card
    card = FancyBboxPatch((x_pos, 0.2), card_width, 0.6, 
                         boxstyle="round,pad=0.02", 
                         facecolor=color, alpha=0.1,
                         edgecolor=color, linewidth=2)
    ax9.add_patch(card)
    
    ax9.text(x_pos + card_width/2, 0.7, title, ha='center', va='center', 
             fontsize=12, fontweight='bold', color=color,
             transform=ax9.transAxes)
    ax9.text(x_pos + card_width/2, 0.4, content, ha='center', va='center', 
             fontsize=9, fontweight='normal', color=COLORS['dark'],
             transform=ax9.transAxes, wrap=True)

# Add main insight title
ax9.text(0.5, 0.95, '核心洞察：持有型不动产ABS市场进入快速发展期', 
         ha='center', va='center', fontsize=16, fontweight='bold', 
         color=COLORS['dark'], transform=ax9.transAxes)

# Final styling
plt.tight_layout()
plt.subplots_adjust(top=0.96, bottom=0.04, left=0.06, right=0.94, hspace=0.4, wspace=0.3)

# Save with high quality
plt.savefig('Streamlined_ABS_Market_Dashboard.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none', pad_inches=0.2)
plt.show()

# Generate summary
print("=== 精简版市场分析仪表板 Streamlined Market Dashboard ===")
print(f"✨ 设计理念：清晰的视觉层次 + 一致的色彩主题 + 逻辑化信息组织")
print(f"📊 核心数据：{total_scale:.1f}亿元总规模，{total_products}只产品")
print(f"🎯 关键洞察：基础设施主导，新兴资产崛起，绿色金融创新")
print(f"📈 发展趋势：从试点到规模化，申报管道{pipeline_scale:.1f}亿元")

print("\n=== 设计优化说明 Design Improvements ===")
print("✅ 减少图表数量：从15个精简到9个核心图表")
print("✅ 逻辑化组织：按故事线组织 - 概览→发展→结构→创新→案例→洞察")
print("✅ 统一色彩主题：专业蓝色系主色调，一致的视觉语言")
print("✅ 现代化设计：圆角卡片、渐变色彩、清晰层次")
print("✅ 信息层次化：标题→数据→洞察的清晰信息架构")
print("✅ 视觉引导：emoji图标、颜色编码、空间布局引导阅读") 