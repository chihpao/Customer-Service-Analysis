import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import matplotlib
import matplotlib.font_manager as fm
import os
import platform

# 設定中文字型
def setup_chinese_font():
    """設定中文字型的函數"""
    system = platform.system()
    
    if system == 'Windows':
        # Windows 系統常用中文字型
        font_list = ['Microsoft JhengHei', 'Microsoft YaHei', 'SimHei', 'SimSun', 'NSimSun', 'FangSong', 'KaiTi']
    elif system == 'Darwin':  # macOS
        # macOS 系統常用中文字型
        font_list = ['PingFang TC', 'PingFang SC', 'Heiti TC', 'Heiti SC', 'Hiragino Sans GB', 'STHeiti']
    else:  # Linux 或其他
        # Linux 系統常用中文字型
        font_list = ['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei', 'Droid Sans Fallback']
    
    # 添加通用字型
    font_list.extend(['Arial Unicode MS', 'sans-serif'])
    
    # 尋找可用的字型
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    # 尋找第一個可用的中文字型
    chinese_font = None
    for font in font_list:
        if font in available_fonts:
            chinese_font = font
            break
    
    if chinese_font:
        matplotlib.rcParams['font.sans-serif'] = [chinese_font] + font_list
        matplotlib.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
        return chinese_font
    else:
        # 如果沒有找到中文字型，嘗試使用默認字型
        return None

# 嘗試設定中文字型
try:
    chinese_font = setup_chinese_font()
    if not chinese_font:
        st.warning("未找到可用的中文字型，圖表中的中文可能無法正確顯示")
        
    # 嘗試使用 SimSun 字型檔案
    font_path = os.path.join(os.path.dirname(__file__), 'simsun.ttc')
    if os.path.exists(font_path):
        prop = fm.FontProperties(fname=font_path)
        matplotlib.rcParams['font.sans-serif'] = ['SimSun'] + matplotlib.rcParams['font.sans-serif']
        
    # 從系統字型目錄尋找字型
    if system == 'Windows':
        windows_font_path = 'C:\\Windows\\Fonts\\msjh.ttc'  # 微軟正黑體
        if os.path.exists(windows_font_path):
            prop = fm.FontProperties(fname=windows_font_path)
            matplotlib.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] + matplotlib.rcParams['font.sans-serif']
            
except Exception as e:
    st.warning(f"設定中文字型時發生錯誤: {e}")

def 生成歸類增幅圖表(月份1, 月份2, 前N名, 增幅最大, df1, df2, 歸類欄位, 日期欄位, 顯示折線圖):
    """生成歸類增幅相關的圖表"""
    st.subheader(f"{月份1}月與{月份2}月歸類增幅最大的前{前N名}名")
    增幅資料 = []
    for 歸類, (增幅, 增幅率, 月份1數量, 月份2數量) in 增幅最大:
        增幅資料.append({
            "歸類": 歸類,
            f"{月份1}月": 月份1數量,
            f"{月份2}月": 月份2數量,
            "增幅": 增幅,
            "增幅率": f"{增幅率:.1f}%"
        })
    st.table(pd.DataFrame(增幅資料))
    
    # 創建增幅最大歸類的折線圖
    st.subheader(f"{月份1}月與{月份2}月歸類增幅最大的前{前N名}名趨勢")
    
    # 獲取前N名歸類名稱
    前N名歸類 = [歸類 for 歸類, _ in 增幅最大]
    
    # 分析每個歸類在每天的數量
    日期欄位 = df1.columns[2]  # C 欄是來電日期
    
    # 為每個歸類創建日期範圍內的數量統計
    開始日期 = min(df1[日期欄位].min(), df2[日期欄位].min())
    結束日期 = max(df1[日期欄位].max(), df2[日期欄位].max())
    
    # 創建日期範圍
    日期範圍 = pd.date_range(start=開始日期, end=結束日期)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 為每個歸類創建時間序列數據
    for 歸類 in 前N名歸類:
        # 篩選出該歸類的數據
        df1_歸類 = df1[df1[歸類欄位] == 歸類]
        df2_歸類 = df2[df2[歸類欄位] == 歸類]
        
        # 合併兩個月的數據
        合併數據 = pd.concat([df1_歸類, df2_歸類])
        
        # 按日期分組並計算每天的數量
        日期統計 = 合併數據.groupby(日期欄位).size()
        
        # 創建完整的日期索引，並填充缺失值為0
        完整日期統計 = pd.Series(0, index=日期範圍)
        for 日期, 數量 in 日期統計.items():
            if 日期 in 完整日期統計.index:
                完整日期統計[日期] = 數量
        
        # 繪製折線圖
        ax.plot(完整日期統計.index, 完整日期統計.values, label=歸類, marker='o', linestyle='-')
    
    # 設置圖表屬性
    title_text = f'{月份1}月與{月份2}月歸類增幅最大的前{前N名}名趨勢'
    xlabel_text = '日期'
    ylabel_text = '數量'
    
    # 嘗試使用不同的方式設定字型
    try:
        # 方法 1: 使用 fontproperties
        font_prop = fm.FontProperties(family=['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS', 'sans-serif'])
        ax.set_title(title_text, fontsize=16, fontproperties=font_prop)
        ax.set_xlabel(xlabel_text, fontsize=12, fontproperties=font_prop)
        ax.set_ylabel(ylabel_text, fontsize=12, fontproperties=font_prop)
    except Exception as e:
        # 方法 2: 直接設定字型
        ax.set_title(title_text, fontsize=16)
        ax.set_xlabel(xlabel_text, fontsize=12)
        ax.set_ylabel(ylabel_text, fontsize=12)
        st.warning(f"設定圖表字型時發生錯誤: {e}")
    
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(prop=font_prop if 'font_prop' in locals() else None)
    plt.tight_layout()
    
    # 使用 Streamlit 顯示圖表
    st.pyplot(fig)
    
    # 如果用戶選擇顯示增幅百分比折線圖
    if 顯示折線圖:
        st.subheader(f"{月份1}月與{月份2}月歸類增幅百分比折線圖 (X軸為每週星期一)")
        
        # 創建一個新的圖表
        fig2, ax2 = plt.subplots(figsize=(14, 8))
        
        # 獲取每週星期一的日期範圍
        開始日期_週一 = 開始日期 - pd.Timedelta(days=開始日期.weekday())
        結束日期_週一 = 結束日期 + pd.Timedelta(days=7-結束日期.weekday())
        週一日期範圍 = pd.date_range(start=開始日期_週一, end=結束日期_週一, freq='W-MON')
        
        # 為每個歸類計算每週的增幅百分比
        for 歸類, (增幅, 增幅率, 月份1數量, 月份2數量) in 增幅最大:
            # 篩選出該歸類的數據
            df1_歸類 = df1[df1[歸類欄位] == 歸類]
            df2_歸類 = df2[df2[歸類欄位] == 歸類]
            
            # 計算每週的數量
            週數據 = []
            
            for 週一 in 週一日期範圍:
                週末 = 週一 + pd.Timedelta(days=6)
                
                # 計算月份1該週的數量
                月份1週數量 = len(df1_歸類[(df1_歸類[日期欄位] >= 週一) & (df1_歸類[日期欄位] <= 週末)])
                
                # 計算月份2該週的數量
                月份2週數量 = len(df2_歸類[(df2_歸類[日期欄位] >= 週一) & (df2_歸類[日期欄位] <= 週末)])
                
                # 計算增幅百分比
                if 月份1週數量 > 0:
                    週增幅百分比 = (月份2週數量 - 月份1週數量) / 月份1週數量 * 100
                else:
                    週增幅百分比 = 0 if 月份2週數量 == 0 else 100  # 避免無限大值
                
                週數據.append((週一, 週增幅百分比))
            
            # 繪製折線圖
            週日期 = [日期 for 日期, _ in 週數據]
            週增幅 = [增幅 for _, 增幅 in 週數據]
            
            ax2.plot(週日期, 週增幅, label=歸類, marker='o', linestyle='-')
        
        # 設置圖表屬性
        title_text = f'{月份1}月與{月份2}月歸類增幅百分比 (按週)'
        xlabel_text = '週一日期'
        ylabel_text = '增幅百分比 (%)'
        
        # 嘗試使用不同的方式設定字型
        try:
            # 方法 1: 使用 fontproperties
            font_prop = fm.FontProperties(family=['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS', 'sans-serif'])
            ax2.set_title(title_text, fontsize=16, fontproperties=font_prop)
            ax2.set_xlabel(xlabel_text, fontsize=12, fontproperties=font_prop)
            ax2.set_ylabel(ylabel_text, fontsize=12, fontproperties=font_prop)
        except Exception as e:
            # 方法 2: 直接設定字型
            ax2.set_title(title_text, fontsize=16)
            ax2.set_xlabel(xlabel_text, fontsize=12)
            ax2.set_ylabel(ylabel_text, fontsize=12)
            st.warning(f"設定圖表字型時發生錯誤: {e}")
        
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # 設置Y軸範圍，避免極端值影響圖表可讀性
        y_min = -100
        y_max = 300
        ax2.set_ylim(y_min, y_max)
        
        # 添加水平線表示0%增幅
        ax2.axhline(y=0, color='r', linestyle='-', alpha=0.3)
        
        # 格式化X軸日期標籤
        plt.xticks(rotation=45)
        ax2.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m/%d'))
        
        ax2.legend(prop=font_prop if 'font_prop' in locals() else None)
        plt.tight_layout()
        
        # 使用 Streamlit 顯示圖表
        st.pyplot(fig2)
