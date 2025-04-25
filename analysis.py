import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def 分析單月資料():
    """分析單一月份的資料"""
    st.header("📊 分析單月資料")
    
    if st.session_state.df is None:
        st.error("請先讀取資料！")
        return
    
    # 確保月份資料字典存在
    if '月份資料字典' not in st.session_state:
        st.session_state.月份資料字典 = {}
    
    # 如果月份資料字典為空，嘗試重新處理月份資料
    if not st.session_state.月份資料字典 and 'df' in st.session_state and st.session_state.df is not None:
        from data_processing import 自動處理月份資料
        自動處理月份資料(st.session_state.df)
    
    # 選擇要分析的月份
    月份選項 = list(st.session_state.月份資料字典.keys())
    
    if not 月份選項:
        st.warning("沒有可用的月份資料！")
        return
    
    選擇的月份 = st.selectbox("選擇要分析的月份", 月份選項)
    
    if st.button("開始分析"):
        df = st.session_state.月份資料字典[選擇的月份]
        
        # 顯示基本統計資訊
        st.subheader(f"{選擇的月份}月資料統計")
        st.write(f"資料筆數: {len(df)}")
        
        # 檢查是否有日期欄位（第3欄，索引為2）
        if len(df.columns) > 2:
            日期欄位 = df.columns[2]
            
            # 嘗試轉換為日期類型
            try:
                if not pd.api.types.is_datetime64_any_dtype(df[日期欄位]):
                    df[日期欄位] = pd.to_datetime(df[日期欄位])
                
                # 顯示日期範圍
                最早日期 = df[日期欄位].min()
                最晚日期 = df[日期欄位].max()
                st.write(f"資料日期範圍: {最早日期.strftime('%Y-%m-%d')} 至 {最晚日期.strftime('%Y-%m-%d')}")
                
                # 按日期分組統計
                日期統計 = df.groupby(df[日期欄位].dt.date).size()
                
                # 創建日期統計圖表
                fig, ax = plt.subplots(figsize=(14, 6))
                日期統計.plot(kind='bar', ax=ax)
                
                # 設定圖表標題和軸標籤的字型
                try:
                    # 導入字型管理模組
                    import matplotlib.font_manager as fm
                    
                    # 創建字型屬性
                    font_prop = fm.FontProperties(family=['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS', 'sans-serif'])
                    
                    # 設定標題和軸標籤
                    ax.set_title(f"{選擇的月份}月每日來電數量", fontsize=16, fontproperties=font_prop)
                    ax.set_xlabel("日期", fontsize=12, fontproperties=font_prop)
                    ax.set_ylabel("數量", fontsize=12, fontproperties=font_prop)
                    
                    # 設定 x 軸標籤的字型
                    for label in ax.get_xticklabels():
                        label.set_fontproperties(font_prop)
                except Exception as e:
                    # 如果設定字型失敗，使用默認設定
                    ax.set_title(f"{選擇的月份}月每日來電數量", fontsize=16)
                    ax.set_xlabel("日期", fontsize=12)
                    ax.set_ylabel("數量", fontsize=12)
                    st.warning(f"設定圖表字型時發生錯誤: {e}")
                
                ax.tick_params(axis='x', rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
            except Exception as e:
                st.warning(f"處理日期資料時發生錯誤: {e}")
        
        # 檢查是否有歸類欄位（第14欄，索引為13）
        if len(df.columns) > 13:
            歸類欄位 = df.columns[13]
            
            # 計算歸類統計
            歸類統計 = df[歸類欄位].value_counts()
            
            # 顯示歸類統計表格
            st.subheader(f"{選擇的月份}月歸類統計")
            st.write(f"歸類數量: {len(歸類統計)}")
            
            # 創建歸類統計表格
            歸類資料 = []
            for 歸類, 數量 in 歸類統計.items():
                歸類資料.append({
                    "歸類": 歸類,
                    "數量": 數量,
                    "百分比": f"{數量 / len(df) * 100:.1f}%"
                })
            
            st.table(pd.DataFrame(歸類資料))
            
            # 創建歸類統計圖表
            fig, ax = plt.subplots(figsize=(14, 8))
            歸類統計.plot(kind='bar', ax=ax)
            
            # 設定圖表標題和軸標籤的字型
            try:
                # 導入字型管理模組
                import matplotlib.font_manager as fm
                
                # 創建字型屬性
                font_prop = fm.FontProperties(family=['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS', 'sans-serif'])
                
                # 設定標題和軸標籤
                ax.set_title(f"{選擇的月份}月歸類統計", fontsize=16, fontproperties=font_prop)
                ax.set_xlabel("歸類", fontsize=12, fontproperties=font_prop)
                ax.set_ylabel("數量", fontsize=12, fontproperties=font_prop)
                
                # 設定 x 軸標籤的字型
                for label in ax.get_xticklabels():
                    label.set_fontproperties(font_prop)
            except Exception as e:
                # 如果設定字型失敗，使用默認設定
                ax.set_title(f"{選擇的月份}月歸類統計", fontsize=16)
                ax.set_xlabel("歸類", fontsize=12)
                ax.set_ylabel("數量", fontsize=12)
                st.warning(f"設定圖表字型時發生錯誤: {e}")
                
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            
            # 創建歸類佔比圓餅圖
            fig, ax = plt.subplots(figsize=(10, 10))
            歸類統計.plot(kind='pie', ax=ax, autopct='%1.1f%%')
            ax.set_title(f"{選擇的月份}月歸類佔比", fontsize=16)
            ax.set_ylabel("")
            plt.tight_layout()
            st.pyplot(fig)

def 比較兩月資料():
    """比較兩個月份的資料"""
    st.header("📊 比較兩月資料")
    
    if st.session_state.df is None:
        st.error("請先讀取資料！")
        return
    
    # 確保月份資料字典存在
    if '月份資料字典' not in st.session_state:
        st.session_state.月份資料字典 = {}
    
    # 如果月份資料字典為空，嘗試重新處理月份資料
    if not st.session_state.月份資料字典 and 'df' in st.session_state and st.session_state.df is not None:
        from data_processing import 自動處理月份資料
        自動處理月份資料(st.session_state.df)
        
    # 再次檢查月份資料字典
    if len(st.session_state.月份資料字典) < 2:
        # 如果仍然少於兩個月，手動創建月份資料
        df = st.session_state.df
        
        # 檢查是否有月份欄位（第2欄，索引為1）
        if len(df.columns) > 1:
            月份欄位 = df.columns[1]
            
            # 嘗試轉換為日期類型並提取月份
            try:
                if pd.api.types.is_datetime64_any_dtype(df[月份欄位]):
                    df['月份數字'] = df[月份欄位].dt.month
                else:
                    df['月份數字'] = pd.to_datetime(df[月份欄位]).dt.month
                
                所有月份 = df['月份數字'].dropna().unique()
                所有月份 = sorted([int(m) for m in 所有月份 if pd.notna(m)])
                
                for 月份 in 所有月份:
                    月份資料 = df[df['月份數字'] == 月份].copy()
                    if not 月份資料.empty:
                        st.session_state.月份資料字典[月份] = 月份資料
            except Exception as e:
                st.warning(f"轉換月份時發生錯誤: {e}")
        
        # 如果仍然少於兩個月，則將資料分成兩半
        if len(st.session_state.月份資料字典) < 2:
            # 確保月份資料字典中至少有一個項目
            if len(st.session_state.月份資料字典) == 0:
                # 如果沒有月份資料，則使用所有資料
                st.session_state.月份資料字典[1] = st.session_state.df
                st.info("無法偵測到月份資料，將使用所有資料進行分析")
            
            # 如果只有一個月份，則將資料分成兩半來模擬兩個月份
            if len(st.session_state.月份資料字典) == 1:
                單月鍵值 = list(st.session_state.月份資料字典.keys())[0]
                單月資料 = st.session_state.月份資料字典[單月鍵值]
                資料總數 = len(單月資料)
                
                # 將資料分成兩半
                前半部分 = 單月資料.iloc[:int(資料總數/2)]
                後半部分 = 單月資料.iloc[int(資料總數/2):]
                
                # 將分割的資料加入月份資料字典
                st.session_state.月份資料字典.clear()
                st.session_state.月份資料字典[1] = 前半部分
                st.session_state.月份資料字典[2] = 後半部分
                
                st.info("由於只有一個月份的資料，系統已自動將資料分成兩半來模擬兩個月份")
    
    # 選擇要比較的月份
    col1, col2 = st.columns(2)
    
    with col1:
        月份1 = st.selectbox("選擇第一個月份", list(st.session_state.月份資料字典.keys()), key="比較月份1")
    
    with col2:
        # 過濾掉已選擇的第一個月份
        可選月份 = [m for m in st.session_state.月份資料字典.keys() if m != 月份1]
        月份2 = st.selectbox("選擇第二個月份", 可選月份, key="比較月份2")
    
    if st.button("開始比較"):
        df1 = st.session_state.月份資料字典[月份1]
        df2 = st.session_state.月份資料字典[月份2]
        
        # 顯示基本統計資訊
        st.subheader(f"{月份1}月與{月份2}月資料比較")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(label=f"{月份1}月資料筆數", value=len(df1))
        
        with col2:
            st.metric(label=f"{月份2}月資料筆數", value=len(df2))
        
        with col3:
            增減 = len(df2) - len(df1)
            增減率 = 增減 / len(df1) * 100 if len(df1) > 0 else 0
            st.metric(label="資料筆數增減", value=增減, delta=f"{增減率:.1f}%")
        
        # 檢查是否有歸類欄位（第14欄，索引為13）
        if len(df1.columns) > 13 and len(df2.columns) > 13:
            歸類欄位 = df1.columns[13]
            
            # 計算歸類統計
            月份1歸類統計 = df1[歸類欄位].value_counts()
            月份2歸類統計 = df2[歸類欄位].value_counts()
            
            # 顯示歸類統計表格
            st.subheader(f"{月份1}月與{月份2}月歸類比較")
            
            # 創建歸類比較表格
            歸類比較 = {}
            for 歸類 in set(月份1歸類統計.index).union(set(月份2歸類統計.index)):
                月份1數量 = 月份1歸類統計.get(歸類, 0)
                月份2數量 = 月份2歸類統計.get(歸類, 0)
                增減 = 月份2數量 - 月份1數量
                增減率 = (增減 / 月份1數量 * 100) if 月份1數量 > 0 else float('inf')
                
                歸類比較[歸類] = {
                    f"{月份1}月": 月份1數量,
                    f"{月份2}月": 月份2數量,
                    "增減": 增減,
                    "增減率": f"{增減率:.1f}%" if 增減率 != float('inf') else "N/A"
                }
            
            # 轉換為DataFrame並排序
            歸類比較_df = pd.DataFrame(歸類比較).T
            歸類比較_df = 歸類比較_df.sort_values(by=f"{月份2}月", ascending=False)
            
            st.table(歸類比較_df)
            
            # 創建歸類比較圖表
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # 設置x軸位置
            x = range(len(歸類比較_df))
            width = 0.35
            
            # 繪製長條圖
            ax.bar([i - width/2 for i in x], 歸類比較_df[f"{月份1}月"], width, label=f"{月份1}月")
            ax.bar([i + width/2 for i in x], 歸類比較_df[f"{月份2}月"], width, label=f"{月份2}月")
            
            # 設置圖表屬性
            ax.set_title(f"{月份1}月與{月份2}月歸類比較", fontsize=16)
            ax.set_xlabel("歸類", fontsize=12)
            ax.set_ylabel("數量", fontsize=12)
            ax.set_xticks(x)
            ax.set_xticklabels(歸類比較_df.index, rotation=45, ha='right')
            ax.legend()
            
            plt.tight_layout()
            st.pyplot(fig)

def 分析歸類增幅():
    """分析歸類增幅"""
    st.header("📊 分析歸類增幅")
    
    if st.session_state.df is None:
        st.error("請先讀取資料！")
        return
    
    # 確保月份資料字典存在
    if '月份資料字典' not in st.session_state:
        st.session_state.月份資料字典 = {}
    
    # 如果月份資料字典為空，嘗試重新處理月份資料
    if not st.session_state.月份資料字典 and 'df' in st.session_state and st.session_state.df is not None:
        from data_processing import 自動處理月份資料
        自動處理月份資料(st.session_state.df)
        
    # 再次檢查月份資料字典
    if len(st.session_state.月份資料字典) < 2:
        # 如果仍然少於兩個月，手動創建月份資料
        df = st.session_state.df
        
        # 檢查是否有月份欄位（第2欄，索引為1）
        if len(df.columns) > 1:
            月份欄位 = df.columns[1]
            
            # 嘗試轉換為日期類型並提取月份
            try:
                if pd.api.types.is_datetime64_any_dtype(df[月份欄位]):
                    df['月份數字'] = df[月份欄位].dt.month
                else:
                    df['月份數字'] = pd.to_datetime(df[月份欄位]).dt.month
                
                所有月份 = df['月份數字'].dropna().unique()
                所有月份 = sorted([int(m) for m in 所有月份 if pd.notna(m)])
                
                for 月份 in 所有月份:
                    月份資料 = df[df['月份數字'] == 月份].copy()
                    if not 月份資料.empty:
                        st.session_state.月份資料字典[月份] = 月份資料
            except Exception as e:
                st.warning(f"轉換月份時發生錯誤: {e}")
        
        # 如果仍然少於兩個月，則將資料分成兩半
        if len(st.session_state.月份資料字典) < 2:
            # 確保月份資料字典中至少有一個項目
            if len(st.session_state.月份資料字典) == 0:
                # 如果沒有月份資料，則使用所有資料
                st.session_state.月份資料字典[1] = st.session_state.df
                st.info("無法偵測到月份資料，將使用所有資料進行分析")
            
            # 如果只有一個月份，則將資料分成兩半來模擬兩個月份
            if len(st.session_state.月份資料字典) == 1:
                單月鍵值 = list(st.session_state.月份資料字典.keys())[0]
                單月資料 = st.session_state.月份資料字典[單月鍵值]
                資料總數 = len(單月資料)
                
                # 將資料分成兩半
                前半部分 = 單月資料.iloc[:int(資料總數/2)]
                後半部分 = 單月資料.iloc[int(資料總數/2):]
                
                # 將分割的資料加入月份資料字典
                st.session_state.月份資料字典.clear()
                st.session_state.月份資料字典[1] = 前半部分
                st.session_state.月份資料字典[2] = 後半部分
                
                st.info("由於只有一個月份的資料，系統已自動將資料分成兩半來模擬兩個月份")
    
    # 選擇要比較的月份
    col1, col2 = st.columns(2)
    
    with col1:
        月份1 = st.selectbox("選擇第一個月份", list(st.session_state.月份資料字典.keys()), key="增幅月份1")
    
    with col2:
        # 過濾掉已選擇的第一個月份
        可選月份 = [m for m in st.session_state.月份資料字典.keys() if m != 月份1]
        月份2 = st.selectbox("選擇第二個月份", 可選月份, key="增幅月份2")
    
    # 選擇要顯示的前N名
    前N名 = st.slider("選擇要顯示的前N名歸類數量", 1, 10, 3)
    
    # 添加折線圖選項
    顯示折線圖 = st.checkbox("顯示增幅百分比折線圖", value=True)
    
    if st.button("開始分析"):
        df1 = st.session_state.月份資料字典[月份1]
        df2 = st.session_state.月份資料字典[月份2]
        
        # 確認歸類欄位名稱
        歸類欄位 = df1.columns[13]  # N 欄是歸類
        日期欄位 = df1.columns[1]   # B 欄是日期
        
        # 計算各歸類的數量
        月份1歸類統計 = df1[歸類欄位].value_counts()
        月份2歸類統計 = df2[歸類欄位].value_counts()
        
        # 計算歸類增幅
        歸類增幅 = {}
        for 歸類 in set(月份1歸類統計.index).union(set(月份2歸類統計.index)):
            月份1數量 = 月份1歸類統計.get(歸類, 0)
            月份2數量 = 月份2歸類統計.get(歸類, 0)
            增幅 = 月份2數量 - 月份1數量
            增幅率 = (增幅 / 月份1數量 * 100) if 月份1數量 > 0 else float('inf')
            歸類增幅[歸類] = (增幅, 增幅率, 月份1數量, 月份2數量)
        
        # 排序並找出增幅最大的前N名歸類
        排序歸類 = sorted(歸類增幅.items(), key=lambda x: x[1][0], reverse=True)
        增幅最大 = 排序歸類[:前N名]
        
        from visualization import 生成歸類增幅圖表
        生成歸類增幅圖表(月份1, 月份2, 前N名, 增幅最大, df1, df2, 歸類欄位, 日期欄位, 顯示折線圖)
