#!/usr/bin/env python3
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体 - 使用简单有效的方法
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 优雅的紫粉橙配色方案 - 参考地图风格
ELEGANT_THEME = {
    # 主背景色
    'bg_primary': '#F8F9FA',           # 浅灰白背景
    'bg_secondary': '#FFFFFF',         # 纯白卡片背景
    'bg_accent': '#F5F5F5',           # 浅灰强调背景
    
    # 主色调 - 紫粉橙渐变
    'purple_deep': '#6B46C1',         # 深紫色
    'purple_medium': '#8B5CF6',       # 中紫色
    'purple_light': '#A78BFA',        # 浅紫色
    'pink_deep': '#EC4899',           # 深粉色
    'pink_medium': '#F472B6',         # 中粉色
    'pink_light': '#FBCFE8',          # 浅粉色
    'orange_deep': '#EA580C',         # 深橙色
    'orange_medium': '#FB923C',       # 中橙色
    'orange_light': '#FED7AA',        # 浅橙色
    
    # 辅助色
    'gray_dark': '#374151',           # 深灰文字
    'gray_medium': '#6B7280',         # 中灰文字
    'gray_light': '#D1D5DB',          # 浅灰边框
    'green': '#10B981',               # 绿色（用于正面指标）
    'blue': '#3B82F6',                # 蓝色（用于中性指标）
}

def create_elegant_dashboard():
    """创建优雅简洁的可视化仪表板"""
    print("🎨 创建优雅主题可视化...")
    
    # 读取数据
    df = pd.read_csv('shanghai_real_estate_abs.csv')
    df.columns = df.columns.str.strip()
    df['Scale_Billion_Yuan'] = pd.to_numeric(df['Scale_Billion_Yuan'], errors='coerce')
    df['Issuance_Date'] = pd.to_datetime(df['Issuance_Date'], errors='coerce')
    df['Year'] = df['Issuance_Date'].dt.year
    
    # 数据预处理
    yearly_data = df.groupby('Year').agg({
        'Scale_Billion_Yuan': 'sum',
        'Product_Name': 'count'
    }).reset_index()
    yearly_data = yearly_data.dropna()
    yearly_data['Cumulative_Scale'] = yearly_data['Scale_Billion_Yuan'].cumsum()
    
    # 地域分布处理
    regions = []
    for issuer in df['Issuer']:
        if '北京' in str(issuer):
            regions.append('北京')
        elif '上海' in str(issuer):
            regions.append('上海')
        elif '广州' in str(issuer) or '广东' in str(issuer):
            regions.append('广东')
        elif '江苏' in str(issuer) or '无锡' in str(issuer) or '南通' in str(issuer) or '南京' in str(issuer):
            regions.append('江苏')
        elif '武汉' in str(issuer):
            regions.append('湖北')
        else:
            regions.append('其他')
    
    # 创建主图表
    fig = plt.figure(figsize=(20, 14), facecolor=ELEGANT_THEME['bg_primary'])
    
    # 简洁的主标题
    fig.suptitle('上海证券交易所房地产持有型ABS市场分析', 
                 fontsize=24, color=ELEGANT_THEME['gray_dark'], 
                 fontweight='bold', y=0.95)
    
    # 英文副标题
    fig.text(0.5, 0.91, 'Shanghai Stock Exchange Real Estate Holding ABS Market Analysis', 
             ha='center', fontsize=14, color=ELEGANT_THEME['gray_medium'], 
             style='italic')
    
    # 创建网格布局 (3x3)
    gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3, 
                         left=0.08, right=0.95, top=0.85, bottom=0.1)
    
    # 1. 市场发展趋势
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.set_facecolor(ELEGANT_THEME['bg_secondary'])
    
    # 简洁的线图
    ax1.plot(yearly_data['Year'], yearly_data['Scale_Billion_Yuan'], 
             color=ELEGANT_THEME['purple_deep'], linewidth=3, marker='o', 
             markersize=8, markerfacecolor=ELEGANT_THEME['pink_deep'],
             markeredgecolor='white', markeredgewidth=2)
    
    # 填充区域
    ax1.fill_between(yearly_data['Year'], yearly_data['Scale_Billion_Yuan'], 
                    alpha=0.3, color=ELEGANT_THEME['purple_light'])
    
    ax1.set_title('市场发展趋势', color=ELEGANT_THEME['gray_dark'], 
                 fontsize=16, pad=20, fontweight='bold')
    ax1.set_xlabel('年份', color=ELEGANT_THEME['gray_medium'], fontsize=12)
    ax1.set_ylabel('发行规模 (十亿元)', color=ELEGANT_THEME['gray_medium'], fontsize=12)
    ax1.grid(True, alpha=0.3, color=ELEGANT_THEME['gray_light'], linestyle='-')
    ax1.tick_params(colors=ELEGANT_THEME['gray_medium'], labelsize=11)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # 2. 资产类别分布
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.set_facecolor(ELEGANT_THEME['bg_secondary'])
    
    asset_counts = df['Asset_Category'].value_counts()
    colors = [ELEGANT_THEME['purple_deep'], ELEGANT_THEME['pink_deep'], 
              ELEGANT_THEME['orange_deep'], ELEGANT_THEME['purple_medium']]
    
    wedges, texts, autotexts = ax2.pie(asset_counts.values, labels=asset_counts.index,
                                      autopct='%1.1f%%', colors=colors,
                                      wedgeprops=dict(width=0.6, edgecolor='white', linewidth=2),
                                      textprops={'color': ELEGANT_THEME['gray_dark'], 
                                               'fontsize': 10},
                                      startangle=90)
    
    ax2.set_title('资产类别分布', color=ELEGANT_THEME['gray_dark'], 
                 fontsize=16, pad=20, fontweight='bold')
    
    # 3. 承销商分布
    ax3 = fig.add_subplot(gs[1, :2])
    ax3.set_facecolor(ELEGANT_THEME['bg_secondary'])
    
    underwriter_counts = df['Lead_Underwriter'].value_counts().head(6)
    colors_bars = [ELEGANT_THEME['purple_deep'], ELEGANT_THEME['pink_deep'], 
                   ELEGANT_THEME['orange_deep'], ELEGANT_THEME['purple_medium'],
                   ELEGANT_THEME['pink_medium'], ELEGANT_THEME['orange_medium']]
    
    bars = ax3.barh(range(len(underwriter_counts)), underwriter_counts.values,
                   color=colors_bars[:len(underwriter_counts)],
                   alpha=0.8, edgecolor='white', linewidth=1, height=0.7)
    
    ax3.set_yticks(range(len(underwriter_counts)))
    ax3.set_yticklabels(underwriter_counts.index, color=ELEGANT_THEME['gray_dark'], 
                       fontsize=11)
    ax3.set_title('主承销商分布', color=ELEGANT_THEME['gray_dark'], 
                 fontsize=16, pad=20, fontweight='bold')
    ax3.set_xlabel('产品数量', color=ELEGANT_THEME['gray_medium'], fontsize=12)
    ax3.grid(True, alpha=0.3, color=ELEGANT_THEME['gray_light'], axis='x', linestyle='-')
    ax3.tick_params(colors=ELEGANT_THEME['gray_medium'], labelsize=11)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    
    # 添加数值标签
    for i, v in enumerate(underwriter_counts.values):
        ax3.text(v + 0.05, i, str(v), va='center', ha='left', 
                color=ELEGANT_THEME['gray_dark'], fontweight='bold', fontsize=11)
    
    # 4. 绿色认证比例
    ax4 = fig.add_subplot(gs[1, 2])
    ax4.set_facecolor(ELEGANT_THEME['bg_secondary'])
    
    green_cert = df['Third_Party_Certification'].apply(
        lambda x: '绿色认证' if pd.notna(x) and '绿色' in str(x) else '传统产品'
    )
    cert_counts = green_cert.value_counts()
    colors_cert = [ELEGANT_THEME['green'], ELEGANT_THEME['gray_medium']]
    
    wedges, texts, autotexts = ax4.pie(cert_counts.values, labels=cert_counts.index,
                                      autopct='%1.1f%%', colors=colors_cert,
                                      wedgeprops=dict(edgecolor='white', linewidth=2),
                                      textprops={'color': ELEGANT_THEME['gray_dark'], 
                                               'fontsize': 11},
                                      startangle=90)
    
    ax4.set_title('绿色认证比例', color=ELEGANT_THEME['gray_dark'], 
                 fontsize=16, pad=20, fontweight='bold')
    
    # 5. 发行规模分布
    ax5 = fig.add_subplot(gs[2, 0])
    ax5.set_facecolor(ELEGANT_THEME['bg_secondary'])
    
    scale_data = df[df['Scale_Billion_Yuan'].notna()]['Scale_Billion_Yuan']
    n, bins, patches = ax5.hist(scale_data, bins=6, alpha=0.8, 
                               edgecolor='white', linewidth=1,
                               color=ELEGANT_THEME['purple_medium'])
    
    ax5.set_title('规模分布', color=ELEGANT_THEME['gray_dark'], 
                 fontsize=16, pad=20, fontweight='bold')
    ax5.set_xlabel('发行规模 (十亿元)', color=ELEGANT_THEME['gray_medium'], fontsize=12)
    ax5.set_ylabel('产品数量', color=ELEGANT_THEME['gray_medium'], fontsize=12)
    ax5.grid(True, alpha=0.3, color=ELEGANT_THEME['gray_light'], axis='y', linestyle='-')
    ax5.tick_params(colors=ELEGANT_THEME['gray_medium'], labelsize=11)
    ax5.spines['top'].set_visible(False)
    ax5.spines['right'].set_visible(False)
    
    # 6. 地域分布
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.set_facecolor(ELEGANT_THEME['bg_secondary'])
    
    region_counts = pd.Series(regions).value_counts()
    colors_region = [ELEGANT_THEME['purple_deep'], ELEGANT_THEME['pink_deep'], 
                     ELEGANT_THEME['orange_deep'], ELEGANT_THEME['purple_medium'], 
                     ELEGANT_THEME['pink_medium']]
    
    bars = ax6.bar(range(len(region_counts)), region_counts.values,
                  color=colors_region[:len(region_counts)],
                  alpha=0.8, edgecolor='white', linewidth=1, width=0.8)
    
    ax6.set_xticks(range(len(region_counts)))
    ax6.set_xticklabels(region_counts.index, rotation=45, 
                       color=ELEGANT_THEME['gray_dark'], fontsize=11)
    ax6.set_title('地域分布', color=ELEGANT_THEME['gray_dark'], 
                 fontsize=16, pad=20, fontweight='bold')
    ax6.set_ylabel('产品数量', color=ELEGANT_THEME['gray_medium'], fontsize=12)
    ax6.grid(True, alpha=0.3, color=ELEGANT_THEME['gray_light'], axis='y', linestyle='-')
    ax6.tick_params(colors=ELEGANT_THEME['gray_medium'], labelsize=11)
    ax6.spines['top'].set_visible(False)
    ax6.spines['right'].set_visible(False)
    
    # 7. 核心指标面板
    ax7 = fig.add_subplot(gs[2, 2])
    ax7.set_facecolor(ELEGANT_THEME['bg_secondary'])
    ax7.axis('off')
    
    # 计算关键指标
    total_scale = df['Scale_Billion_Yuan'].sum()
    green_count = len(df[df['Third_Party_Certification'].str.contains('绿色', na=False)])
    green_rate = green_count/len(df)*100
    
    # 创建简洁的指标卡片
    metrics = [
        ("总规模", f"{total_scale:.1f}亿元", ELEGANT_THEME['purple_deep']),
        ("产品数", f"{len(df)}只", ELEGANT_THEME['pink_deep']),
        ("绿色率", f"{green_rate:.1f}%", ELEGANT_THEME['green']),
        ("平均规模", f"{df['Scale_Billion_Yuan'].mean():.1f}亿元", ELEGANT_THEME['orange_deep'])
    ]
    
    for i, (label, value, color) in enumerate(metrics):
        x = 0.1 + (i % 2) * 0.45
        y = 0.7 - (i // 2) * 0.4
        
        # 简洁的背景框
        rect = Rectangle((x-0.05, y-0.1), 0.35, 0.2,
                        facecolor=color, alpha=0.1,
                        edgecolor=color, linewidth=1)
        ax7.add_patch(rect)
        
        # 文字
        ax7.text(x + 0.125, y + 0.02, label, fontsize=12, ha='center', va='center', 
                color=ELEGANT_THEME['gray_dark'], fontweight='bold')
        ax7.text(x + 0.125, y - 0.04, value, fontsize=14, ha='center', va='center', 
                color=color, fontweight='bold')
    
    ax7.set_title('核心指标', color=ELEGANT_THEME['gray_dark'], 
                 fontsize=16, pad=20, fontweight='bold')
    ax7.set_xlim(0, 1)
    ax7.set_ylim(0, 1)
    
    # 保存图像
    plt.savefig('ABS_Elegant_Dashboard.png', 
                dpi=300, facecolor=ELEGANT_THEME['bg_primary'], 
                edgecolor='none', bbox_inches='tight', 
                pad_inches=0.3)
    
    print("✅ 优雅仪表板已保存为 'ABS_Elegant_Dashboard.png'")
    
    # 生成分析报告
    print(f"\n📊 市场分析摘要")
    print(f"💰 市场总规模: {total_scale:.2f} 十亿元")
    print(f"📈 产品数量: {len(df)} 只")
    print(f"🌱 绿色认证率: {green_rate:.1f}%")
    print(f"📊 平均规模: {df['Scale_Billion_Yuan'].mean():.2f}亿元")
    print(f"🏆 最大单只规模: {df['Scale_Billion_Yuan'].max():.2f}亿元")
    print(f"📅 发行时间跨度: {df['Year'].min()}-{df['Year'].max()}年")
    
    plt.close('all')
    return True

# 主程序
if __name__ == "__main__":
    try:
        create_elegant_dashboard()
        print("\n🎊 优雅可视化完成！")
        print("🎨 设计特色:")
        print("   • ✅ 简洁优雅的紫粉橙配色")
        print("   • 🎯 清晰的中文字体显示")
        print("   • 📐 简化的图表设计")
        print("   • 🌸 柔和的视觉效果")
        print("   • 📊 专业的数据呈现")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc() 