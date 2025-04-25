import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
import io
import hashlib
import json
from datetime import datetime
from PIL import Image

# 導入自定義模組
from auth import check_password, user_management
from data_processing import 讀取資料, 自動處理月份資料
from analysis import 分析單月資料, 比較兩月資料, 分析歸類增幅

# 設置頁面配置
st.set_page_config(
    page_title="客服資料分析系統",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 檢查使用者是否已登入
if check_password():
    # 顯示歡迎訊息
    st.sidebar.title("📊 客服資料分析系統")
    st.sidebar.markdown(f"歡迎, **{st.session_state.username_logged}**!")
    
    # 選擇功能
    功能選項 = st.sidebar.selectbox(
        "選擇功能",
        ["讀取資料", "分析單月資料", "比較兩月資料", "分析歸類增幅", "使用者管理"]
    )
    
    # 根據選擇的功能顯示對應的頁面
    if 功能選項 == "讀取資料":
        讀取資料()
    elif 功能選項 == "分析單月資料":
        分析單月資料()
    elif 功能選項 == "比較兩月資料":
        比較兩月資料()
    elif 功能選項 == "分析歸類增幅":
        分析歸類增幅()
    elif 功能選項 == "使用者管理":
        user_management()
