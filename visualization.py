import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

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
    ax.set_title(f'{月份1}月與{月份2}月歸類增幅最大的前{前N名}名趨勢', fontsize=16)
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('數量', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    plt.tight_layout()
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
        ax2.set_title(f'{月份1}月與{月份2}月歸類增幅百分比 (按週)', fontsize=16)
        ax2.set_xlabel('週一日期', fontsize=12)
        ax2.set_ylabel('增幅百分比 (%)', fontsize=12)
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
        
        ax2.legend()
        plt.tight_layout()
        st.pyplot(fig2)
