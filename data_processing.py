import streamlit as st
import pandas as pd
import io
from datetime import datetime

def 讀取資料():
    """讀取Excel檔案並處理資料"""
    st.header("📊 讀取資料")
    
    # 上傳檔案
    uploaded_file = st.file_uploader("請上傳Excel檔案", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            # 讀取Excel檔案
            df = pd.read_excel(uploaded_file, sheet_name="電話資訊彙整表")
            
            # 顯示資料預覽
            st.subheader("資料預覽")
            st.dataframe(df.head())
            
            # 顯示資料統計
            st.subheader("資料統計")
            st.write(f"總資料筆數: {len(df)}")
            
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
                except Exception as e:
                    st.warning(f"轉換日期時發生錯誤: {e}")
            
            # 檢查是否有歸類欄位（第14欄，索引為13）
            if len(df.columns) > 13:
                歸類欄位 = df.columns[13]
                
                # 顯示歸類統計
                歸類統計 = df[歸類欄位].value_counts()
                st.write(f"歸類數量: {len(歸類統計)}")
            
            # 將資料儲存到session state
            st.session_state.df = df
            
            # 處理月份資料
            自動處理月份資料(df)
            
            st.success("資料讀取成功！")
            
            # 顯示下載處理後的資料按鈕
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name="處理後資料", index=False)
            
            output.seek(0)
            
            st.download_button(
                label="下載處理後的資料",
                data=output,
                file_name=f"處理後資料_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"讀取資料時發生錯誤: {e}")
    else:
        # 如果沒有上傳檔案，檢查session state中是否已有資料
        if "df" in st.session_state and st.session_state.df is not None:
            st.info("使用已載入的資料")
            df = st.session_state.df
            
            # 顯示資料預覽
            st.subheader("資料預覽")
            st.dataframe(df.head())
            
            # 顯示資料統計
            st.subheader("資料統計")
            st.write(f"總資料筆數: {len(df)}")
        else:
            st.info("請上傳Excel檔案")

def 自動處理月份資料(df):
    """根據日期自動處理月份資料"""
    # 初始化月份資料字典
    if "月份資料字典" not in st.session_state:
        st.session_state.月份資料字典 = {}
    
    # 檢查是否有月份欄位（第2欄，索引為1）
    if len(df.columns) > 1:
        月份欄位 = df.columns[1]
        
        # 嘗試轉換為日期類型並提取月份
        try:
            # 檢查是否已經有月份數字欄位
            if '月份數字' not in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[月份欄位]):
                    df['月份數字'] = df[月份欄位].dt.month
                else:
                    # 嘗試將月份欄位轉換為日期類型
                    try:
                        df['月份數字'] = pd.to_datetime(df[月份欄位]).dt.month
                    except:
                        # 如果無法轉換，嘗試從字串中提取月份
                        try:
                            # 嘗試從字串中提取月份（例如：'113年2月'）
                            df['月份數字'] = df[月份欄位].str.extract(r'(\d+)月').astype(float)
                        except:
                            st.warning(f"無法從 {月份欄位} 欄位提取月份，將使用預設分組")
            
            # 如果成功提取月份，按月份分組
            if '月份數字' in df.columns:
                所有月份 = df['月份數字'].dropna().unique()
                所有月份 = sorted([int(m) for m in 所有月份 if pd.notna(m)])
                
                for 月份 in 所有月份:
                    月份資料 = df[df['月份數字'] == 月份].copy()
                    if not 月份資料.empty:
                        st.session_state.月份資料字典[月份] = 月份資料
                
                if 所有月份:
                    st.write(f"已自動處理月份資料: {', '.join(map(str, 所有月份))}")
                else:
                    st.warning("未找到有效的月份資料")
            else:
                st.warning("無法創建月份數字欄位")
        except Exception as e:
            st.warning(f"處理月份資料時發生錯誤: {e}")
    else:
        st.warning("資料欄位不足，無法處理月份資料")
