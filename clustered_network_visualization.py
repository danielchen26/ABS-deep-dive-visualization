#!/usr/bin/env python3
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import PathPatch, Circle, Wedge
from matplotlib.path import Path
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 更深的专业配色方案
CLUSTER_COLORS = [
    '#003f5c',  # 深蓝色 - 中投证券
    '#2f4b7c',  # 深蓝紫 - 中信建投  
    '#665191',  # 深紫色 - 华泰证券
    '#a05195',  # 深紫红 - 平安证券
    '#d45087',  # 深红色 - 其他承销商
    '#f95d6a',  # 深橙红 - 绿色ABS
    '#ff7c43',  # 深橙色 - 轨道交通
    '#ffa600',  # 深黄色 - 清洁能源
    '#003d82',  # 深蓝 - 环保设施
    '#1e5631',  # 深绿色 - 数据中心
    '#8b4513',  # 深棕色 - 其他
    '#2e2e2e',  # 深灰色 - 备用
]

def create_bezier_curve(start, end, curvature=0.2):
    """创建简单的弯曲连接线"""
    mid_x = (start[0] + end[0]) / 2
    mid_y = (start[1] + end[1]) / 2
    
    # 轻微向中心弯曲
    control_distance = curvature * np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
    control_x = mid_x * 0.7
    control_y = mid_y * 0.7
    
    vertices = [start, (control_x, control_y), end]
    codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
    return Path(vertices, codes)

def create_circular_network(ax, title):
    """创建圆形网络图（承销商维度）"""
    # 读取数据
    df = pd.read_csv('shanghai_real_estate_abs.csv')
    df.columns = df.columns.str.strip()
    
    # 数据分析和聚类
    clusters = {}
    
    for idx, row in df.iterrows():
        product_name = str(row['Product_Name'])
        underwriter = str(row['Lead_Underwriter']).strip()
        category = str(row['Asset_Category']).strip()
        asset_type = str(row['Underlying_Asset_Type']).strip()
        scale = row['Scale_Billion_Yuan'] if pd.notna(row['Scale_Billion_Yuan']) else 0
        
        # 确定层级
        try:
            scale_value = float(scale) if scale != 'N/A' and str(scale) != 'nan' else 0
        except (ValueError, TypeError):
            scale_value = 0
            
        if scale_value > 15:
            tier = 'inner'
        elif scale_value > 8:
            tier = 'middle'
        else:
            tier = 'outer'
        
        # 聚类策略 - 按承销商聚类，确保7个cluster
        cluster_key = None
        if underwriter == '中投证券':
            cluster_key = 'zhongtou'
        elif underwriter == '中信建投':
            cluster_key = 'zhongxin'
        elif underwriter == '华泰证券':
            cluster_key = 'huatai'
        elif underwriter == '平安证券':
            cluster_key = 'pingan'
        elif underwriter in ['兴业证券', '开源证券', '中山证券', '农银汇理']:
            cluster_key = 'major_underwriters'
        elif underwriter in ['中银证券', '东吴证券', '渤海汇金', '民生证券', '安信证券', '广发证券', '德邦证券', '国联证券']:
            cluster_key = 'other_underwriters'
        elif underwriter not in ['nan', 'N/A'] and underwriter and underwriter.strip():
            cluster_key = 'misc_underwriters'
        else:
            # 对于没有承销商信息的，按资产类型分类
            if '绿色' in category:
                cluster_key = 'green_assets'
            elif '数据中心' in asset_type:
                cluster_key = 'data_center'
            elif '住房' in asset_type or '住宅' in asset_type:
                cluster_key = 'housing_assets'
            else:
                cluster_key = 'other_assets'
        
        cluster_full_key = f"{cluster_key}_{tier}"
        
        if cluster_full_key not in clusters:
            clusters[cluster_full_key] = []
        
        clusters[cluster_full_key].append({
            'name': product_name,
            'underwriter': underwriter,
            'category': category,
            'asset_type': asset_type,
            'issuer': str(row['Issuer']),
            'scale': scale_value,
            'certification': str(row['Third_Party_Certification']),
            'tier': tier,
            'cluster': cluster_key
        })
    
    # 同心圆层级布局
    tier_radii = {'inner': 2.5, 'middle': 4.5, 'outer': 6.5}
    tier_labels = {
        'inner': '核心层 (>15亿元)',
        'middle': '中间层 (8-15亿元)', 
        'outer': '外围层 (<8亿元)'
    }
    
    # 计算cluster分布
    base_clusters = list(set([k.rsplit('_', 1)[0] for k in clusters.keys()]))
    cluster_angles = {}
    
    # 调试输出：显示cluster数量和名称
    print(f"📊 发现 {len(base_clusters)} 个cluster: {base_clusters}")
    
    # 分配角度区间
    angle_per_cluster = 2 * np.pi / len(base_clusters)
    
    for i, base_cluster in enumerate(base_clusters):
        start_angle = i * angle_per_cluster
        end_angle = (i + 1) * angle_per_cluster
        cluster_angles[base_cluster] = {
            'start': start_angle,
            'end': end_angle,
            'center': start_angle + angle_per_cluster / 2
        }
        
        # 绘制cluster区域背景
        color = CLUSTER_COLORS[i % len(CLUSTER_COLORS)]
        for radius_idx, radius in enumerate([2.5, 4.5, 6.5, 7.5]):
            alpha_value = 0.15 - radius_idx * 0.02
            wedge = Wedge((0, 0), radius, np.degrees(start_angle), np.degrees(end_angle),
                         facecolor=color, alpha=alpha_value, zorder=0)
            ax.add_patch(wedge)
            
        # 边界线
        wedge_border = Wedge((0, 0), 7.5, np.degrees(start_angle), np.degrees(end_angle),
                           facecolor='none', edgecolor=color, linewidth=2, alpha=0.7, zorder=1)
        ax.add_patch(wedge_border)
    
    # 绘制同心圆 - 用不同粗细表示层级重要性
    tier_line_widths = {'inner': 4, 'middle': 3, 'outer': 2}
    tier_colors = {'inner': '#000000', 'middle': '#333333', 'outer': '#666666'}
    
    for tier, radius in tier_radii.items():
        line_width = tier_line_widths[tier]
        line_color = tier_colors[tier]
        circle = Circle((0, 0), radius, fill=False, color=line_color, 
                       linewidth=line_width, alpha=0.9, zorder=2)
        ax.add_patch(circle)
    
    # 放置节点
    node_positions = {}
    
    for cluster_key, products in clusters.items():
        base_cluster = cluster_key.rsplit('_', 1)[0]
        tier = cluster_key.rsplit('_', 1)[1]
        radius = tier_radii[tier]
        
        cluster_color = CLUSTER_COLORS[base_clusters.index(base_cluster) % len(CLUSTER_COLORS)]
        
        angle_info = cluster_angles[base_cluster]
        start_angle = angle_info['start']
        end_angle = angle_info['end']
        angle_span = end_angle - start_angle
        
        for j, product in enumerate(products):
            if len(products) == 1:
                angle = start_angle + angle_span / 2
            else:
                margin = angle_span * 0.1
                usable_span = angle_span - 2 * margin
                angle = start_angle + margin + (j / max(1, len(products) - 1)) * usable_span
            
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            node_positions[product['name']] = (x, y)
            
            # 绘制节点
            try:
                scale = product['scale']
                if tier == 'inner':
                    node_size = max(0.18, min(0.40, scale / 35))
                elif tier == 'middle':
                    node_size = max(0.15, min(0.32, scale / 45))
                else:
                    node_size = max(0.10, min(0.25, scale / 55))
            except:
                node_size = 0.15
            
            # 深色阴影
            shadow = Circle((x + 0.03, y - 0.03), node_size, color='#000000', 
                           alpha=0.25, zorder=2)
            ax.add_patch(shadow)
            
            circle = Circle((x, y), node_size, color=cluster_color, 
                           alpha=0.95, zorder=3, edgecolor='white', linewidth=2)
            ax.add_patch(circle)
            
            # 添加标签 - 确保标签在正确的层级位置
            label_distance = radius + 0.4  # 减少距离，让标签更接近对应节点
            label_x = label_distance * np.cos(angle)
            label_y = label_distance * np.sin(angle)
            
            # 简化产品名称
            product_name = product['name']
            if '-' in product_name:
                short_name = product_name.split('-')[-1]
            else:
                short_name = product_name
            
            if len(short_name) > 8:
                short_name = short_name[:6] + '..'
            
            # 添加规模信息
            scale_info = f"\n{product['scale']:.1f}亿" if product['scale'] > 0 else ""
            full_label = short_name + scale_info
            
            # 文字方向 - 重新优化算法确保所有文字都正向
            angle_deg = np.degrees(angle)
            
            # 标准化角度到 0-360
            angle_deg = angle_deg % 360
            
            # 简化逻辑：只要角度在左半边就翻转
            if 90 < angle_deg < 270:
                # 左半边：文字需要翻转以保持可读
                rotation = angle_deg - 180
                ha = 'right'
            else:
                # 右半边：文字保持正常方向
                rotation = angle_deg
                ha = 'left'
            
            # 确保旋转角度在 -90 到 +90 之间
            while rotation > 90:
                rotation -= 180
            while rotation < -90:
                rotation += 180
            
            # 字体大小和颜色 - 不同层级使用不同颜色
            if tier == 'inner':
                fontsize = 9
                fontweight = 'bold'
                text_color = '#000000'  # 最深黑色 - 核心层
                bbox_color = '#ffffff'  # 白色背景
                bbox_alpha = 0.95
            elif tier == 'middle':
                fontsize = 8
                fontweight = 'bold'
                text_color = '#2d2d2d'  # 深灰色 - 中间层
                bbox_color = '#f8f9fa'  # 浅灰背景
                bbox_alpha = 0.9
            else:
                fontsize = 7
                fontweight = 'normal'
                text_color = '#555555'  # 中灰色 - 外围层
                bbox_color = '#f0f0f0'  # 更浅背景
                bbox_alpha = 0.85
            
            ax.text(label_x, label_y, full_label, 
                   ha=ha, va='center', rotation=rotation,
                   fontsize=fontsize, color=text_color, fontweight=fontweight, zorder=4,
                   bbox=dict(boxstyle="round,pad=0.15", facecolor=bbox_color, alpha=bbox_alpha, 
                            edgecolor='#666666', linewidth=0.5))
    
    # 添加连接线 - 修复连接逻辑
    connection_count = 0
    connection_stats = {'underwriter': 0, 'large_scale': 0, 'green_asset': 0}
    print("🔗 正在添加连接线...")
    
    # 获取所有产品用于连接分析
    all_products = []
    for cluster_products in clusters.values():
        all_products.extend(cluster_products)
    
    print(f"📊 总共有 {len(all_products)} 个产品可用于连接")
    
    # 先打印承销商信息用于调试
    print("🔍 承销商信息调试:")
    underwriter_count = {}
    for product in all_products:
        uw = product['underwriter']
        if uw not in underwriter_count:
            underwriter_count[uw] = []
        underwriter_count[uw].append((product['name'][:30], product['tier']))
    
    for uw, products in underwriter_count.items():
        if len(products) > 1:
            print(f"   承销商 '{uw}': {len(products)}个产品")
            for name, tier in products:
                print(f"     - {name}... ({tier})")
    
    # 直接从所有产品中寻找连接，不受cluster限制
    print("🔗 开始连接检查循环...")
    
    # 首先专门寻找承销商连接
    print("🔍 第一轮：专门寻找承销商连接")
    for i, product1 in enumerate(all_products):
        for j, product2 in enumerate(all_products):
            if i >= j:
                continue
            
            # 只检查承销商连接
            underwriter1 = product1['underwriter']
            underwriter2 = product2['underwriter']
            tier1 = product1['tier']
            tier2 = product2['tier']
            
            # 详细承销商检查
            if underwriter1 in ['平安证券', '中投证券', '中信建投']:
                print(f"  🔎 检查产品 {i+1}-{j+1}: '{underwriter1}' vs '{underwriter2}' | 层级: {tier1} vs {tier2}")
                print(f"      承销商相同: {underwriter1 == underwriter2}")
                print(f"      层级不同: {tier1 != tier2}")
                print(f"      承销商有效: {underwriter1 not in ['nan', 'N/A', '', 'None'] and len(underwriter1.strip()) > 2}")
            
            # 承销商连接条件
            if (tier1 != tier2 and 
                underwriter1 == underwriter2 and 
                underwriter1 not in ['nan', 'N/A', '', 'None'] and
                underwriter1.strip() != '' and
                len(underwriter1.strip()) > 2):
                
                print(f"  ✅ 找到承销商连接: '{underwriter1}' - {product1['name'][:20]}...({tier1}) ↔ {product2['name'][:20]}...({tier2})")
                
                pos1 = node_positions.get(product1['name'])
                pos2 = node_positions.get(product2['name'])
                
                if pos1 and pos2:
                    # 实线 - 承销商关系（深蓝色）
                    ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], 
                           color='#003f5c', linewidth=3.5, alpha=1.0, 
                           linestyle='-', zorder=4)
                    print(f"    ✅ 绘制承销商连线: {underwriter1}")
                    connection_stats['underwriter'] += 1
                    connection_count += 1
    
    # 第二轮：其他连接
    print("🔍 第二轮：其他连接（大规模和绿色资产）")
    for i, product1 in enumerate(all_products):
        for j, product2 in enumerate(all_products):
            if i >= j or connection_count >= 25:  # 增加上限
                continue
            
            should_connect = False
            connection_type = None
            
            # 大规模产品连接
            if (product1['scale'] > 15 and product2['scale'] > 15 and 
                connection_stats['large_scale'] < 10):  # 限制数量
                should_connect = True
                connection_type = 'large_scale'
                
            # 绿色资产连接
            elif (product1['tier'] != product2['tier'] and 
                  ('绿色' in str(product1.get('category', '')) and 
                   '绿色' in str(product2.get('category', ''))) and
                  connection_stats['green_asset'] < 6):  # 减少绿色连接数量
                should_connect = True
                connection_type = 'green_asset'
            
            if should_connect:
                pos1 = node_positions.get(product1['name'])
                pos2 = node_positions.get(product2['name'])
                
                if pos1 and pos2:
                    if connection_type == 'large_scale':
                        # 虚线 - 大规模产品关系（紫红色）
                        ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], 
                               color='#d45087', linewidth=3.0, alpha=0.9, 
                               linestyle='--', zorder=3)
                    elif connection_type == 'green_asset':
                        # 点线 - 绿色资产关系（绿色）
                        ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], 
                               color='#31a354', linewidth=2.5, alpha=0.8, 
                               linestyle=':', zorder=3)
                    
                    connection_count += 1
                    connection_stats[connection_type] += 1

    print(f"🔗 连接线统计:")
    print(f"   • 承销商关系: {connection_stats['underwriter']} 条")
    print(f"   • 大规模产品: {connection_stats['large_scale']} 条") 
    print(f"   • 绿色资产: {connection_stats['green_asset']} 条")
    print(f"   • 总计: {connection_count} 条连接线")
    
    # 添加cluster标识
    for base_cluster, angle_info in cluster_angles.items():
        center_angle = angle_info['center']
        label_radius = 9.5
        label_x = label_radius * np.cos(center_angle)
        label_y = label_radius * np.sin(center_angle)
        
        cluster_labels = {
            'zhongtou': '中投证券',
            'zhongxin': '中信建投', 
            'huatai': '华泰证券',
            'pingan': '平安证券',
            'major_underwriters': '主要承销商',
            'other_underwriters': '其他承销商',
            'misc_underwriters': '小型承销商',
            'green_assets': '绿色资产',
            'data_center': '数据中心',
            'housing_assets': '住房资产',
            'other_assets': '其他资产'
        }
        
        cluster_label = cluster_labels.get(base_cluster, base_cluster)
        total_products = sum([len(products) for key, products in clusters.items() 
                             if key.startswith(base_cluster)])
        total_scale = sum([sum([p['scale'] for p in products]) for key, products in clusters.items() 
                          if key.startswith(base_cluster)])
        
        cluster_color = CLUSTER_COLORS[base_clusters.index(base_cluster) % len(CLUSTER_COLORS)]
        
        # 详细的cluster标签
        detailed_label = f'{cluster_label}\n{total_products}个产品\n{total_scale:.1f}亿元'
        
        ax.text(label_x, label_y, detailed_label, 
               ha='center', va='center', fontsize=10, fontweight='bold',
               bbox=dict(boxstyle="round,pad=0.4", 
                        facecolor=cluster_color, 
                        alpha=0.95, edgecolor='white', linewidth=2),
               color='white', zorder=6, linespacing=1.2)
    
    # 添加标题
    ax.text(0, 12.5, title, 
           ha='center', va='center', fontsize=16, fontweight='bold',
           color='#1a1a1a', zorder=6)
    
    # 图例 - 添加层级说明和连线说明
    legend_elements = []
    
    # 层级图例
    tier_legend_labels = [
        ('核心层 (>15亿元)', '#000000', 'inner'),
        ('中间层 (8-15亿元)', '#333333', 'middle'),
        ('外围层 (<8亿元)', '#666666', 'outer')
    ]
    
    for label, color, tier in tier_legend_labels:
        line_width = tier_line_widths[tier]
        legend_elements.append(plt.Line2D([0], [0], color=color, linewidth=line_width*2, 
                                        label=label, alpha=0.9))
    
    # 连线类型图例
    connection_legend = [
        ('承销商关系连线', '#003f5c', '-'),
        ('大规模产品连线', '#d45087', '--'),
        ('绿色资产连线', '#31a354', ':')
    ]
    
    for label, color, linestyle in connection_legend:
        legend_elements.append(plt.Line2D([0], [0], color=color, linewidth=2.5, 
                                        linestyle=linestyle, label=label, alpha=0.8))
    
    # 颜色图例 - 只保留主要的承销商
    color_labels = [
        ('中投证券', '#003f5c'),
        ('中信建投', '#2f4b7c'),
        ('华泰证券', '#665191'),
        ('平安证券', '#a05195'),
        ('主要承销商', '#d45087'),
        ('其他承销商', '#ff7c43')
    ]
    
    for i, (label, color) in enumerate(color_labels):
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                        markerfacecolor=color, markersize=12, label=label))
    
    ax.legend(handles=legend_elements, loc='upper left', 
              bbox_to_anchor=(0.02, 0.98), fontsize=9,
              frameon=True, facecolor='white', edgecolor='#333333', framealpha=0.95,
              title='图例说明', title_fontsize=11, ncol=1)
    
    return len(df), len(base_clusters)

def create_single_network():
    """创建单个圆形网络图"""
    print("🌐 创建承销商维度聚类网络图...")
    
    # 创建图表
    fig, ax = plt.subplots(1, 1, figsize=(16, 16), facecolor='white')
    
    ax.set_facecolor('white')
    total_products, total_clusters = create_circular_network(ax, '上海证券交易所房地产持有型ABS市场\n承销商维度聚类网络分析')
    ax.set_xlim(-14, 14)
    ax.set_ylim(-14, 14)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # 数据来源
    fig.text(0.5, 0.05, 'Data Source: Shanghai Stock Exchange Real Estate ABS Market Analysis | 数据来源：上交所房地产ABS市场统计', 
             ha='center', fontsize=11, color='#666666')
    
    # 统计信息
    stats_text = f"""数据统计
总产品数: {total_products}个
承销商分组: {total_clusters}个
分析维度: 承销商聚类
层级划分: 3层同心圆"""
    
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes,
           fontsize=11, verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle="round,pad=0.5", facecolor='#F8F9FA', 
                    edgecolor='#333333', alpha=0.95, linewidth=1),
           color='#1a1a1a', linespacing=1.5, fontweight='bold')
    
    # 调整布局
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.1)
    
    # 保存图片
    plt.savefig('ABS_Clustered_Network.png', 
                dpi=300, facecolor='white', edgecolor='none', 
                bbox_inches='tight', pad_inches=0.3)
    
    print("✅ 承销商维度聚类网络图已保存为 'ABS_Clustered_Network.png'")
    
    plt.close('all')
    return True

# 主程序
if __name__ == "__main__":
    try:
        create_single_network()
        print("\n🎊 承销商维度聚类网络图创建完成！")
        print("🌟 核心特色:")
        print("   • 🎨 深色专业配色方案")
        print("   • 🔵 三层同心圆结构清晰")
        print("   • 🔍 详细的层级标签展示")
        print("   • 📝 规模信息和统计数据")
        print("   • 🌈 深色调一致性设计")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc() 