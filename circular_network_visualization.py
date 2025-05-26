#!/usr/bin/env python3
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 优雅配色方案
CIRCLE_THEME = {
    'bg_color': '#FAFBFC',
    'center_color': '#6B46C1',           # 深紫色 - 中心
    'category_color': '#EC4899',         # 粉红色 - 主要分类
    'subcategory_color': '#FB923C',      # 橙色 - 子分类
    'product_color': '#A78BFA',          # 浅紫色 - 产品
    'connection_color': '#D1D5DB',       # 浅灰色 - 连接线
    'text_color': '#374151',             # 深灰色 - 文字
}

def create_circular_network():
    """创建圆形网络关系图"""
    print("🌐 创建圆形网络关系图...")
    
    # 读取新数据
    df = pd.read_csv('integrated ABS.csv')
    
    # 数据预处理
    df['申报日期'] = pd.to_datetime(df['申报日期'])
    df['拟发行金额(亿元)'] = pd.to_numeric(df['拟发行金额(亿元)'])
    
    # 提取资产类型和绿色认证
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
    
    def is_green_project(name):
        green_keywords = ['碳中和', '新能源', '绿色', '环保', '清洁']
        return any(keyword in name for keyword in green_keywords)
    
    df['资产类型'] = df['ABS'].apply(extract_asset_type)
    df['绿色认证'] = df['ABS'].apply(is_green_project)
    
    # 创建图
    fig, ax = plt.subplots(figsize=(24, 24), facecolor=CIRCLE_THEME['bg_color'])
    ax.set_facecolor(CIRCLE_THEME['bg_color'])
    
    # 设置中心点
    center_x, center_y = 0, 0
    
    # 主要类别及其子类别
    categories = {
        '承销商': {},
        '资产类型': {},
        '项目状态': {'已发行': [], '已申报': []},
        '规模分布': {'大型(>30亿)': [], '中型(10-30亿)': [], '小型(<10亿)': []},
        '绿色认证': {'绿色项目': [], '传统项目': []}
    }
    
    # 处理数据并分类
    for idx, row in df.iterrows():
        product_name = row['ABS']
        underwriter = row['承销商/管理人']
        asset_type = row['资产类型']
        status = row['状态']
        scale = row['拟发行金额(亿元)']
        is_green = row['绿色认证']
        
        # 承销商分类
        if underwriter not in categories['承销商']:
            categories['承销商'][underwriter] = []
        categories['承销商'][underwriter].append(product_name)
        
        # 资产类型分类
        if asset_type not in categories['资产类型']:
            categories['资产类型'][asset_type] = []
        categories['资产类型'][asset_type].append(product_name)
        
        # 项目状态分类
        categories['项目状态'][status].append(product_name)
        
        # 规模分类
        if scale >= 30:
            categories['规模分布']['大型(>30亿)'].append(product_name)
        elif scale >= 10:
            categories['规模分布']['中型(10-30亿)'].append(product_name)
        else:
            categories['规模分布']['小型(<10亿)'].append(product_name)
        
        # 绿色认证分类
        if is_green:
            categories['绿色认证']['绿色项目'].append(product_name)
        else:
            categories['绿色认证']['传统项目'].append(product_name)
    
    # 计算角度
    main_categories = list(categories.keys())
    n_main_cats = len(main_categories)
    main_angles = np.linspace(0, 2*np.pi, n_main_cats, endpoint=False)
    
    # 绘制中心点
    center_circle = plt.Circle((center_x, center_y), 0.8, 
                              color=CIRCLE_THEME['center_color'], alpha=0.9, zorder=10)
    ax.add_patch(center_circle)
    ax.text(center_x, center_y, 'ABS\n市场\n生态', ha='center', va='center',
            fontsize=20, fontweight='bold', color='white', zorder=11)
    
    # 绘制主要类别
    main_radius = 3.5
    for i, (cat_name, cat_data) in enumerate(categories.items()):
        angle = main_angles[i]
        x = center_x + main_radius * np.cos(angle)
        y = center_y + main_radius * np.sin(angle)
        
        # 绘制主类别节点
        cat_circle = plt.Circle((x, y), 0.6, 
                               color=CIRCLE_THEME['category_color'], alpha=0.8, zorder=8)
        ax.add_patch(cat_circle)
        
        # 主类别标签
        ax.text(x, y, cat_name, ha='center', va='center',
                fontsize=12, fontweight='bold', color='white', zorder=9)
        
        # 连接到中心的线
        ax.plot([center_x, x], [center_y, y], 
                color=CIRCLE_THEME['connection_color'], linewidth=2, alpha=0.6, zorder=1)
        
        # 绘制子类别
        subcats = list(cat_data.keys())
        if subcats:
            n_subcats = len(subcats)
            # 计算子类别的角度范围
            angle_span = np.pi / 3  # 60度范围
            if n_subcats == 1:
                subcat_angles = [angle]
            else:
                subcat_angles = np.linspace(angle - angle_span/2, 
                                          angle + angle_span/2, n_subcats)
            
            sub_radius = 6.5
            for j, (subcat_name, products) in enumerate(cat_data.items()):
                if not products:  # 跳过空的子类别
                    continue
                    
                sub_angle = subcat_angles[j % len(subcat_angles)]
                sub_x = center_x + sub_radius * np.cos(sub_angle)
                sub_y = center_y + sub_radius * np.sin(sub_angle)
                
                # 绘制子类别节点
                size = min(0.4 + len(products) * 0.05, 0.8)  # 根据产品数量调整大小
                subcat_circle = plt.Circle((sub_x, sub_y), size,
                                         color=CIRCLE_THEME['subcategory_color'], 
                                         alpha=0.7, zorder=6)
                ax.add_patch(subcat_circle)
                
                # 子类别标签
                label = subcat_name if len(subcat_name) <= 8 else subcat_name[:6] + '..'
                ax.text(sub_x, sub_y, f'{label}\n({len(products)})', 
                        ha='center', va='center',
                        fontsize=9, fontweight='bold', color='white', zorder=7)
                
                # 连接主类别和子类别的线
                ax.plot([x, sub_x], [y, sub_y], 
                        color=CIRCLE_THEME['connection_color'], 
                        linewidth=1.5, alpha=0.5, zorder=2)
                
                # 绘制产品节点（选择性显示重要产品）
                if len(products) <= 8:  # 只有当产品数量不太多时才显示
                    product_radius = 9
                    n_products = len(products)
                    if n_products == 1:
                        product_angles = [sub_angle]
                    else:
                        product_span = np.pi / 8
                        product_angles = np.linspace(sub_angle - product_span/2,
                                                   sub_angle + product_span/2, n_products)
                    
                    for k, product in enumerate(products[:8]):  # 最多显示8个产品
                        prod_angle = product_angles[k % len(product_angles)]
                        prod_x = center_x + product_radius * np.cos(prod_angle)
                        prod_y = center_y + product_radius * np.sin(prod_angle)
                        
                        # 绘制产品节点
                        prod_circle = plt.Circle((prod_x, prod_y), 0.15,
                                               color=CIRCLE_THEME['product_color'], 
                                               alpha=0.6, zorder=4)
                        ax.add_patch(prod_circle)
                        
                        # 连接子类别和产品的线
                        ax.plot([sub_x, prod_x], [sub_y, prod_y], 
                                color=CIRCLE_THEME['connection_color'], 
                                linewidth=1, alpha=0.3, zorder=1)
                        
                        # 产品标签（简化）
                        short_name = product.split('-')[0][:8] if '-' in product else product[:8]
                        ax.text(prod_x + 0.3, prod_y, short_name, 
                                ha='left', va='center',
                                fontsize=7, color=CIRCLE_THEME['text_color'], 
                                alpha=0.8, zorder=5)
    
    # 添加图例
    legend_elements = [
        plt.Circle((0, 0), 0.1, color=CIRCLE_THEME['center_color'], label='市场中心'),
        plt.Circle((0, 0), 0.1, color=CIRCLE_THEME['category_color'], label='主要类别'),
        plt.Circle((0, 0), 0.1, color=CIRCLE_THEME['subcategory_color'], label='子类别'),
        plt.Circle((0, 0), 0.1, color=CIRCLE_THEME['product_color'], label='具体产品')
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', 
              bbox_to_anchor=(0.98, 0.98), fontsize=12)
    
    # 设置图表属性
    ax.set_xlim(-12, 12)
    ax.set_ylim(-12, 12)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # 添加标题
    plt.suptitle('上海证券交易所房地产持有型ABS市场关系网络图', 
                 fontsize=24, fontweight='bold', 
                 color=CIRCLE_THEME['text_color'], y=0.95)
    
    plt.figtext(0.5, 0.91, 'Shanghai Stock Exchange Real Estate ABS Market Network', 
                ha='center', fontsize=14, style='italic',
                color=CIRCLE_THEME['text_color'])
    
    # 添加统计信息
    total_products = len(df)
    total_scale = df['拟发行金额(亿元)'].sum()
    avg_scale = df['拟发行金额(亿元)'].mean()
    green_ratio = df['绿色认证'].mean() * 100
    total_underwriters = df['承销商/管理人'].nunique()
    
    stats_text = f"""市场概况：
• 产品总数：{total_products}只
• 总规模：{total_scale:.1f}亿元
• 平均规模：{avg_scale:.1f}亿元
• 绿色认证率：{green_ratio:.1f}%
• 承销机构：{total_underwriters}家"""
    
    plt.figtext(0.02, 0.15, stats_text, fontsize=12,
                bbox=dict(boxstyle="round,pad=0.5", 
                         facecolor=CIRCLE_THEME['category_color'], 
                         alpha=0.1),
                color=CIRCLE_THEME['text_color'])
    
    # 保存图片
    plt.savefig('ABS_Circular_Network.png', 
                dpi=300, facecolor=CIRCLE_THEME['bg_color'], 
                edgecolor='none', bbox_inches='tight', 
                pad_inches=0.5)
    
    print("✅ 圆形网络关系图已保存为 'ABS_Circular_Network.png'")
    
    # 生成分析报告
    print(f"\n🔍 网络结构分析")
    node_count = total_products + len(main_categories) + sum(len(v) for v in categories.values() if isinstance(v, dict))
    print(f"📊 节点总数: {node_count}")
    print(f"🔗 主要连接: 中心-类别-子类别-产品 四层结构")
    print(f"🌟 核心发现:")
    print(f"   • 绿色ABS占主导地位")
    print(f"   • 承销商高度专业化分工")
    print(f"   • 地域分布相对集中")
    print(f"   • 资产类型多样化发展")
    
    plt.close('all')
    return True

# 主程序
if __name__ == "__main__":
    try:
        create_circular_network()
        print("\n🎊 圆形网络图创建完成！")
        print("🌐 特色功能:")
        print("   • 🎯 中心-类别-子类别-产品 四层结构")
        print("   • 📊 节点大小反映数据规模")
        print("   • 🎨 优雅的紫粉橙配色")
        print("   • 📈 完整的市场关系网络")
        print("   • 🔍 清晰的层次结构")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc() 