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

# 認證相關函數
def check_password():
    """檢查使用者輸入的密碼是否正確"""
    def password_entered():
        """驗證輸入的使用者名稱和密碼"""
        if st.session_state["username"] in st.session_state["users"] and \
           st.session_state["users"][st.session_state["username"]]["password"] == \
           hashlib.sha256(str.encode(st.session_state["password"])).hexdigest():
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # 不要在 session state 中儲存密碼
            st.session_state["username_logged"] = st.session_state["username"]
            st.session_state["user_role"] = st.session_state["users"][st.session_state["username"]]["role"]
        else:
            st.session_state["password_correct"] = False

    # 載入使用者資料
    if "users" not in st.session_state:
        try:
            # 嘗試從檔案載入使用者資料
            users_file = os.path.join(os.path.dirname(__file__), "users.json")
            if os.path.exists(users_file):
                with open(users_file, "r") as f:
                    st.session_state["users"] = json.load(f)
            else:
                # 如果檔案不存在，創建預設使用者
                st.session_state["users"] = {
                    "admin": {
                        "password": hashlib.sha256(str.encode("admin123")).hexdigest(),
                        "role": "admin"
                    }
                }
                # 儲存預設使用者資料
                with open(users_file, "w") as f:
                    json.dump(st.session_state["users"], f)
        except Exception as e:
            # 如果發生錯誤，使用硬編碼的預設使用者
            st.session_state["users"] = {
                "admin": {
                    "password": hashlib.sha256(str.encode("admin123")).hexdigest(),
                    "role": "admin"
                }
            }

    # 檢查是否已經登入
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
        
    # 如果尚未登入，顯示登入表單
    if not st.session_state["password_correct"]:
        st.title("客服資料分析系統 - 登入")
        st.markdown("請輸入您的使用者名稱和密碼")
        
        # 創建登入表單
        with st.form("login_form"):
            st.text_input("使用者名稱", key="username")
            st.text_input("密碼", type="password", key="password")
            st.form_submit_button("登入", on_click=password_entered)
        
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("😕 使用者名稱或密碼錯誤")
        
        # 顯示預設帳號資訊
        st.info("預設帳號: admin / 密碼: admin123")
        
        return False
    else:
        # 顯示歡迎訊息和登出按鈕
        col1, col2 = st.sidebar.columns([3, 1])
        col1.write(f"歡迎, {st.session_state['username_logged']} ({st.session_state['user_role']})")
        if col2.button("登出"):
            for key in ["password_correct", "username_logged", "user_role"]:
                if key in st.session_state:
                    del st.session_state[key]
            return False
        return True

# 使用者管理功能 (僅限管理員)
def user_management():
    st.header("使用者管理")
    
    if st.session_state["user_role"] != "admin":
        st.error("您沒有權限訪問此頁面")
        return
    
    st.subheader("現有使用者")
    users_df = pd.DataFrame([
        {
            "使用者名稱": username,
            "角色": user_info["role"]
        }
        for username, user_info in st.session_state["users"].items()
    ])
    st.dataframe(users_df)
    
    st.subheader("新增使用者")
    with st.form("add_user_form"):
        new_username = st.text_input("使用者名稱")
        new_password = st.text_input("密碼", type="password")
        new_role = st.selectbox("角色", ["user", "admin"])
        
        if st.form_submit_button("新增使用者"):
            if new_username and new_password:
                if new_username in st.session_state["users"]:
                    st.error(f"使用者 {new_username} 已存在")
                else:
                    st.session_state["users"][new_username] = {
                        "password": hashlib.sha256(str.encode(new_password)).hexdigest(),
                        "role": new_role
                    }
                    # 儲存使用者資料
                    try:
                        users_file = os.path.join(os.path.dirname(__file__), "users.json")
                        with open(users_file, "w") as f:
                            json.dump(st.session_state["users"], f)
                        st.success(f"已新增使用者 {new_username}")
                        st.experimental_rerun()
                    except Exception as e:
                        st.warning(f"無法儲存使用者資料到檔案: {e}")
                        st.success(f"已新增使用者 {new_username} (僅在本次會話中有效)")
            else:
                st.error("使用者名稱和密碼不能為空")
    
    st.subheader("刪除使用者")
    with st.form("delete_user_form"):
        del_username = st.selectbox("選擇要刪除的使用者", 
                                   [u for u in st.session_state["users"].keys() 
                                    if u != st.session_state["username_logged"]])
        
        if st.form_submit_button("刪除使用者"):
            if del_username:
                del st.session_state["users"][del_username]
                # 儲存使用者資料
                try:
                    users_file = os.path.join(os.path.dirname(__file__), "users.json")
                    with open(users_file, "w") as f:
                        json.dump(st.session_state["users"], f)
                    st.success(f"已刪除使用者 {del_username}")
                    st.experimental_rerun()
                except Exception as e:
                    st.warning(f"無法儲存使用者資料到檔案: {e}")
                    st.success(f"已刪除使用者 {del_username} (僅在本次會話中有效)")

# 設定中文字型
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

# 設定頁面配置
st.set_page_config(
    page_title="客服資料分析系統",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 檢查密碼
if check_password():
    # 設定標題
    st.title("📊 客服資料分析系統")
    st.markdown("---")

    # 初始化 session state
    if 'df' not in st.session_state:
        st.session_state.df = None
    if '月份資料字典' not in st.session_state:
        st.session_state.月份資料字典 = {}
    if '分析結果' not in st.session_state:
        st.session_state.分析結果 = {}

    # 側邊欄 - 功能選單
    with st.sidebar:
        st.header("功能選單")
        
        # 管理員可以看到使用者管理選項
        if st.session_state["user_role"] == "admin":
            功能選項 = st.radio(
                "請選擇功能",
                ["讀取資料", "篩選月份資料", "分析單月資料", "比較兩月資料", "分析歸類增幅", "使用者管理"]
            )
        else:
            功能選項 = st.radio(
                "請選擇功能",
                ["讀取資料", "篩選月份資料", "分析單月資料", "比較兩月資料", "分析歸類增幅"]
            )
        
        st.markdown("---")
        st.markdown("### 資料狀態")
        
        if st.session_state.df is not None:
            st.success(f"已讀取資料，共 {len(st.session_state.df)} 筆")
        else:
            st.warning("尚未讀取資料")
        
        if st.session_state.月份資料字典:
            st.success(f"已篩選月份: {list(st.session_state.月份資料字典.keys())}")
        else:
            st.warning("尚未篩選月份資料")

# 讀取資料功能
def 讀取資料():
    st.header("📂 讀取資料")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        上傳檔案 = st.file_uploader("上傳Excel檔案", type=["xlsx", "xls"])
        
    with col2:
        使用預設檔案 = st.checkbox("使用預設檔案")
        
    if 上傳檔案 is not None:
        try:
            # 讀取上傳的檔案
            xls = pd.ExcelFile(上傳檔案)
            st.info(f"Excel 檔案中的工作表: {xls.sheet_names}")
            
            工作表名稱 = st.selectbox("選擇要讀取的工作表", xls.sheet_names)
            
            if st.button("讀取選定的工作表"):
                df = pd.read_excel(上傳檔案, sheet_name=工作表名稱)
                st.session_state.df = df
                st.success(f"成功讀取「{工作表名稱}」工作表，共 {len(df)} 筆資料")
                
                # 顯示資料預覽
                st.subheader("資料預覽")
                st.dataframe(df.head(10))
                
                # 顯示欄位資訊
                st.subheader("欄位資訊")
                for i, col in enumerate(df.columns):
                    st.text(f"[{i}] {col} (對應英文字母: {chr(65+i)}欄)")
        
        except Exception as e:
            st.error(f"讀取資料時發生錯誤: {e}")
    
    elif 使用預設檔案:
        try:
            預設檔案路徑 = r"c:\Entrance\A-Work\300-簡報與報告\310-客服簡報與分析報告\313-客服自動化分析\客服紀錄_工程雲端服務網_114.xlsx"
            
            if os.path.exists(預設檔案路徑):
                xls = pd.ExcelFile(預設檔案路徑)
                st.info(f"Excel 檔案中的工作表: {xls.sheet_names}")
                
                工作表名稱 = st.selectbox("選擇要讀取的工作表", xls.sheet_names)
                
                if st.button("讀取選定的工作表"):
                    df = pd.read_excel(預設檔案路徑, sheet_name=工作表名稱)
                    st.session_state.df = df
                    st.success(f"成功讀取「{工作表名稱}」工作表，共 {len(df)} 筆資料")
                    
                    # 顯示資料預覽
                    st.subheader("資料預覽")
                    st.dataframe(df.head(10))
                    
                    # 顯示欄位資訊
                    st.subheader("欄位資訊")
                    for i, col in enumerate(df.columns):
                        st.text(f"[{i}] {col} (對應英文字母: {chr(65+i)}欄)")
            else:
                st.error(f"找不到預設檔案: {預設檔案路徑}")
        
        except Exception as e:
            st.error(f"讀取預設檔案時發生錯誤: {e}")
    
    else:
        st.info("請上傳Excel檔案或選擇使用預設檔案")

# 篩選月份資料功能
def 篩選月份資料():
    st.header("🔍 篩選月份資料")
    
    if st.session_state.df is None:
        st.error("請先讀取資料！")
        return
    
    df = st.session_state.df
    
    # 確認月份欄位
    月份欄位 = df.columns[1]  # B 欄是月份
    st.info(f"月份欄位名稱: {月份欄位}")
    
    # 顯示 B 欄（月份）的前 10 個值
    st.subheader(f"B 欄（{月份欄位}）的前 10 個值:")
    st.write(df.iloc[:10, 1])
    
    # 選擇要篩選的月份
    月份 = st.slider("選擇要篩選的月份", 1, 12, 1)
    
    if st.button("篩選資料"):
        # 篩選指定月份的資料
        月份資料 = df[df.iloc[:, 1].dt.month == 月份]
        
        if len(月份資料) > 0:
            st.session_state.月份資料字典[月份] = 月份資料
            st.success(f"篩選出的 {月份} 月份資料筆數: {len(月份資料)}")
            
            # 顯示資料預覽
            st.subheader("資料預覽")
            st.dataframe(月份資料.head(10))
            
            # 提供下載選項
            output = io.BytesIO()
            月份資料.to_excel(output, index=False)
            output.seek(0)
            
            st.download_button(
                label=f"下載 {月份} 月資料",
                data=output,
                file_name=f"{月份}月資料.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning(f"沒有 {月份} 月份的資料")

# 分析單月資料功能
def 分析單月資料():
    st.header("📈 分析單月資料")
    
    if not st.session_state.月份資料字典:
        st.error("請先篩選月份資料！")
        return
    
    # 選擇要分析的月份
    月份 = st.selectbox("選擇要分析的月份", list(st.session_state.月份資料字典.keys()))
    
    if st.button("開始分析"):
        df = st.session_state.月份資料字典[月份]
        
        # 確認欄位名稱
        模組欄位 = df.columns[8]  # I 欄是模組
        歸類欄位 = df.columns[13]  # N 欄是歸類
        
        st.info(f"模組欄位名稱: {模組欄位}")
        st.info(f"歸類欄位名稱: {歸類欄位}")
        
        # 計算各模組的數量
        模組統計 = df[模組欄位].value_counts()
        
        # 計算各歸類的數量
        歸類統計 = df[歸類欄位].value_counts()
        
        # 顯示模組統計
        st.subheader(f"{月份}月各{模組欄位}數量統計")
        st.dataframe(模組統計)
        
        # 顯示歸類統計
        st.subheader(f"{月份}月各{歸類欄位}數量統計")
        st.dataframe(歸類統計)
        
        # 創建模組分析圖表
        st.subheader(f"{月份}月各{模組欄位}數量統計圖")
        fig1, ax1 = plt.subplots(figsize=(12, 6))
        模組統計.head(10).plot(kind='bar', ax=ax1)
        ax1.set_title(f'{月份}月各{模組欄位}數量統計 (前10名)', fontsize=16)
        ax1.set_xlabel(f'{模組欄位}', fontsize=12)
        ax1.set_ylabel('數量', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig1)
        
        # 創建歸類分析圖表
        st.subheader(f"{月份}月各{歸類欄位}數量統計圖")
        fig2, ax2 = plt.subplots(figsize=(14, 7))
        歸類統計.head(15).plot(kind='bar', ax=ax2)
        ax2.set_title(f'{月份}月各{歸類欄位}數量統計 (前15名)', fontsize=16)
        ax2.set_xlabel(f'{歸類欄位}', fontsize=12)
        ax2.set_ylabel('數量', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig2)
        
        # 創建交叉分析熱力圖
        st.subheader(f"{月份}月{模組欄位}-{歸類欄位}交叉分析")
        交叉表 = pd.crosstab(df[模組欄位], df[歸類欄位])
        
        # 只選擇前10個模組和前10個歸類進行熱力圖分析
        top_模組 = 模組統計.head(10).index
        top_歸類 = 歸類統計.head(10).index
        交叉表_篩選 = 交叉表.loc[交叉表.index.intersection(top_模組), 交叉表.columns.intersection(top_歸類)]
        
        fig3, ax3 = plt.subplots(figsize=(16, 12))
        sns.heatmap(交叉表_篩選, cmap="YlGnBu", annot=True, fmt='g', ax=ax3)
        ax3.set_title(f'{月份}月{模組欄位}-{歸類欄位}交叉分析', fontsize=16)
        plt.tight_layout()
        st.pyplot(fig3)
        
        # 提供下載選項
        output = io.BytesIO()
        交叉表.to_excel(output)
        output.seek(0)
        
        st.download_button(
            label=f"下載 {月份}月_{模組欄位}{歸類欄位}交叉分析.xlsx",
            data=output,
            file_name=f"{月份}月_{模組欄位}{歸類欄位}交叉分析.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# 比較兩月資料功能
def 比較兩月資料():
    st.header("🔄 比較兩月資料")
    
    if len(st.session_state.月份資料字典) < 2:
        st.error("請先篩選至少兩個月份的資料！")
        return
    
    # 選擇要比較的月份
    col1, col2 = st.columns(2)
    
    with col1:
        月份1 = st.selectbox("選擇第一個月份", list(st.session_state.月份資料字典.keys()), key="月份1")
    
    with col2:
        # 過濾掉已選擇的第一個月份
        可選月份 = [m for m in st.session_state.月份資料字典.keys() if m != 月份1]
        月份2 = st.selectbox("選擇第二個月份", 可選月份, key="月份2")
    
    if st.button("開始比較"):
        df1 = st.session_state.月份資料字典[月份1]
        df2 = st.session_state.月份資料字典[月份2]
        
        # 確認欄位名稱
        模組欄位 = df1.columns[8]  # I 欄是模組
        歸類欄位 = df1.columns[13]  # N 欄是歸類
        
        # 計算各模組的數量
        月份1模組統計 = df1[模組欄位].value_counts()
        月份2模組統計 = df2[模組欄位].value_counts()
        
        # 計算各歸類的數量
        月份1歸類統計 = df1[歸類欄位].value_counts()
        月份2歸類統計 = df2[歸類欄位].value_counts()
        
        # 創建模組比較圖
        st.subheader(f"{月份1}月與{月份2}月{模組欄位}比較")
        模組比較 = pd.DataFrame({
            f'{月份1}月': 月份1模組統計,
            f'{月份2}月': 月份2模組統計
        })
        模組比較.fillna(0, inplace=True)
        模組比較 = 模組比較.sort_values(by=f'{月份2}月', ascending=False)
        
        st.dataframe(模組比較.head(10))
        
        fig1, ax1 = plt.subplots(figsize=(14, 8))
        模組比較.head(10).plot(kind='bar', ax=ax1)
        ax1.set_title(f'{月份1}月與{月份2}月{模組欄位}比較 (前10名)', fontsize=16)
        ax1.set_xlabel(f'{模組欄位}', fontsize=12)
        ax1.set_ylabel('數量', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig1)
        
        # 創建歸類比較圖
        st.subheader(f"{月份1}月與{月份2}月{歸類欄位}比較")
        歸類比較 = pd.DataFrame({
            f'{月份1}月': 月份1歸類統計,
            f'{月份2}月': 月份2歸類統計
        })
        歸類比較.fillna(0, inplace=True)
        歸類比較 = 歸類比較.sort_values(by=f'{月份2}月', ascending=False)
        
        st.dataframe(歸類比較.head(10))
        
        fig2, ax2 = plt.subplots(figsize=(14, 8))
        歸類比較.head(10).plot(kind='bar', ax=ax2)
        ax2.set_title(f'{月份1}月與{月份2}月{歸類欄位}比較 (前10名)', fontsize=16)
        ax2.set_xlabel(f'{歸類欄位}', fontsize=12)
        ax2.set_ylabel('數量', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig2)
        
        # 計算總體變化
        月份1總數 = len(df1)
        月份2總數 = len(df2)
        總變化 = 月份2總數 - 月份1總數
        總變化率 = (總變化 / 月份1總數) * 100
        
        st.subheader("總體變化分析")
        col1, col2, col3 = st.columns(3)
        col1.metric(f"{月份1}月總數", f"{月份1總數}")
        col2.metric(f"{月份2}月總數", f"{月份2總數}")
        col3.metric("變化", f"{總變化} ({總變化率:.1f}%)")
        
        # 找出增加最多和減少最多的模組
        模組變化 = {}
        for 模組 in set(月份1模組統計.index).union(set(月份2模組統計.index)):
            月份1數量 = 月份1模組統計.get(模組, 0)
            月份2數量 = 月份2模組統計.get(模組, 0)
            變化 = 月份2數量 - 月份1數量
            變化率 = (變化 / 月份1數量 * 100) if 月份1數量 > 0 else float('inf')
            模組變化[模組] = (變化, 變化率, 月份1數量, 月份2數量)
        
        # 排序並找出前5名增加和減少的模組
        排序模組 = sorted(模組變化.items(), key=lambda x: x[1][0], reverse=True)
        增加最多 = 排序模組[:5]
        減少最多 = 排序模組[-5:]
        
        st.subheader(f"增加最多的5個{模組欄位}")
        增加資料 = []
        for 模組, (變化, 變化率, 月份1數量, 月份2數量) in 增加最多:
            增加資料.append({
                "模組": 模組,
                f"{月份1}月": 月份1數量,
                f"{月份2}月": 月份2數量,
                "變化": 變化,
                "變化率": f"{變化率:.1f}%"
            })
        st.table(pd.DataFrame(增加資料))
        
        st.subheader(f"減少最多的5個{模組欄位}")
        減少資料 = []
        for 模組, (變化, 變化率, 月份1數量, 月份2數量) in reversed(減少最多):
            減少資料.append({
                "模組": 模組,
                f"{月份1}月": 月份1數量,
                f"{月份2}月": 月份2數量,
                "變化": 變化,
                "變化率": f"{變化率:.1f}%"
            })
        st.table(pd.DataFrame(減少資料))

# 分析歸類增幅功能
def 分析歸類增幅():
    st.header("📊 分析歸類增幅")
    
    if len(st.session_state.月份資料字典) < 2:
        st.error("請先篩選至少兩個月份的資料！")
        return
    
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
    
    if st.button("開始分析"):
        df1 = st.session_state.月份資料字典[月份1]
        df2 = st.session_state.月份資料字典[月份2]
        
        # 確認歸類欄位名稱
        歸類欄位 = df1.columns[13]  # N 欄是歸類
        
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

# 根據選擇的功能顯示對應的頁面
if 功能選項 == "讀取資料":
    讀取資料()
elif 功能選項 == "篩選月份資料":
    篩選月份資料()
elif 功能選項 == "分析單月資料":
    分析單月資料()
elif 功能選項 == "比較兩月資料":
    比較兩月資料()
elif 功能選項 == "分析歸類增幅":
    分析歸類增幅()
elif 功能選項 == "使用者管理":
    user_management()
