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
            # 嘗試從 Streamlit Secrets 載入使用者資料
            if 'users' in st.secrets:
                st.session_state["users"] = st.secrets["users"]
            else:
                # 如果 Secrets 中沒有使用者資料，嘗試從本地檔案載入
                users_file = os.path.join(os.path.dirname(__file__), "users.json")
                if os.path.exists(users_file):
                    with open(users_file, "r") as f:
                        st.session_state["users"] = json.load(f)
                else:
                    # 如果檔案不存在，創建預設使用者
                    st.session_state["users"] = {
                        "chihpao": {
                            "password": "3a78c2a41af38053eabf7ac5d8c3cae96912b27452819b3ddef48ba67e8e76e5",
                            "role": "admin"
                        }
                    }
                    # 儲存預設使用者資料到本地檔案（僅開發環境使用）
                    with open(users_file, "w") as f:
                        json.dump(st.session_state["users"], f)
        except Exception as e:
            # 如果發生錯誤，使用硬編碼的預設使用者
            st.session_state["users"] = {
                "chihpao": {
                    "password": "3a78c2a41af38053eabf7ac5d8c3cae96912b27452819b3ddef48ba67e8e76e5",
                    "role": "admin"
                }
            }

    # 檢查是否已經登入
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    # 判斷是否在本地端執行
    is_local = True
    try:
        # 如果在 Streamlit Cloud 上執行，會有 STREAMLIT_SHARING 環境變數
        is_local = not os.environ.get("STREAMLIT_SHARING") and not os.environ.get("STREAMLIT_RUN_ON_SAVE")
    except:
        pass
    
    # 如果在本地端執行，自動登入為管理員
    if is_local and not st.session_state["password_correct"]:
        st.session_state["password_correct"] = True
        st.session_state["username_logged"] = "chihpao"
        st.session_state["user_role"] = "admin"
        st.success("在本地端測試模式中，已自動登入為管理員")
    
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
        
    # 顯示 Streamlit Secrets 設定說明
    st.info("""
    ### 重要安全提示
    
    在本地環境中，使用者資料會儲存在 `users.json` 檔案中。
    但在 Streamlit Cloud 部署環境中，為了安全起見，請使用 Streamlit Secrets 管理使用者認證資訊。
    
    在 Streamlit Cloud 中設定 Secrets 的步驟：
    1. 登入 Streamlit Cloud
    2. 前往您的應用程式設定
    3. 點擊「Secrets」標籤
    4. 添加以下格式的 Secrets：
    ```
    [users]
    chihpao = {"password":"3a78c2a41af38053eabf7ac5d8c3cae96912b27452819b3ddef48ba67e8e76e5","role":"admin"}
    user1 = {"password":"<雜湊後的密碼>","role":"user"}
    ```
    5. 點擊「Save」按鈕
    
    注意：在本地環境中新增或刪除的使用者不會自動同步到 Streamlit Cloud，您需要手動更新 Secrets。
    """)
    
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
    else:
        # 清空月份資料字典，避免舊資料影響
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
                ["讀取資料", "分析單月資料", "比較兩月資料", "分析歸類增幅", "使用者管理"]
            )
        else:
            功能選項 = st.radio(
                "請選擇功能",
                ["讀取資料", "分析單月資料", "比較兩月資料", "分析歸類增幅"]
            )
        
        st.markdown("---")
        st.markdown("### 資料狀態")
        
        if st.session_state.df is not None:
            st.success(f"已讀取資料，共 {len(st.session_state.df)} 筆")
        else:
            st.warning("尚未讀取資料")
        
        if st.session_state.月份資料字典:
            st.success(f"可用月份: {list(st.session_state.月份資料字典.keys())}")

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
                
                # 自動處理所有月份資料
                自動處理月份資料(df)
                
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
                    
                    # 自動處理所有月份資料
                    自動處理月份資料(df)
                    
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

# 自動處理所有月份資料
def 自動處理月份資料(df):
    # 清空月份資料字典
    st.session_state.月份資料字典 = {}
    
    # 確保原始資料不為空
    if df is None or len(df) == 0:
        st.warning("原始資料為空，將創建空的月份字典")
        st.session_state.月份資料字典 = {1: pd.DataFrame(), 2: pd.DataFrame(), 3: pd.DataFrame(), 4: pd.DataFrame()}
        return
    
    # 資料總數
    資料總數 = len(df)
    st.write(f"--- Debug: 總資料筆數: {資料總數} ---") # Debug
    
    try:
        # 檢查是否有月份欄位（第2欄，索引為1）
        if len(df.columns) > 1:
            月份欄位 = df.columns[1]
            st.info(f"將使用欄位 '{str(月份欄位)}' 作為月份欄位進行分類")
            
            # 檢查月份欄位的數據類型
            st.write(f"--- Debug: 月份欄位類型: {df[月份欄位].dtype} ---") # Debug
            
            # 將日期格式轉換為月份數字（1-12）
            if pd.api.types.is_datetime64_any_dtype(df[月份欄位]):
                # 如果是日期類型，提取月份
                df['月份數字'] = df[月份欄位].dt.month
                st.write(f"--- Debug: 已將日期轉換為月份數字 ---")
            else:
                # 嘗試轉換為日期類型
                try:
                    df['月份數字'] = pd.to_datetime(df[月份欄位]).dt.month
                    st.write(f"--- Debug: 已將字串轉換為月份數字 ---")
                except:
                    # 如果無法轉換，則假設數據已經是月份數字
                    st.warning(f"無法將 '{月份欄位}' 轉換為日期，將直接使用原始值")
                    df['月份數字'] = df[月份欄位]
            
            # 獲取所有不同的月份
            所有月份 = df['月份數字'].dropna().unique()
            所有月份 = sorted([int(m) for m in 所有月份 if pd.notna(m)])
            st.write(f"--- Debug: 發現以下月份: {所有月份} ---") # Debug
            
            # 根據月份分類資料
            for 月份 in 所有月份:
                # 篩選該月份的資料
                月份資料 = df[df['月份數字'] == 月份].copy()
                
                # 確保月份資料不為空
                if len(月份資料) == 0:
                    st.warning(f"月份 {月份} 沒有資料")
                    continue
                
                # 存入月份資料字典
                st.session_state.月份資料字典[月份] = 月份資料
                
                # 計算該月份的模組數量
                if len(df.columns) > 8:
                    模組欄位 = df.columns[8]
                    模組數量 = len(月份資料[模組欄位].dropna().unique())
                else:
                    模組數量 = 0
                
                st.success(f"已創建 {月份} 月資料，包含 {len(月份資料)} 筆資料，模組數量: {模組數量}")
            
            # 顯示每個月份的資料數量
            for 月份 in st.session_state.月份資料字典.keys():
                st.write(f"--- Debug: {月份}月 資料形狀: {st.session_state.月份資料字典[月份].shape} ---") # Debug
        else:
            # 如果沒有月份欄位，則使用平均分割法
            st.warning("無法找到月份欄位，將使用平均分割法")
            每月筆數 = 資料總數 // 4
            
            # 分割資料
            第一月資料 = df.iloc[0:每月筆數].copy() if 每月筆數 > 0 else df.iloc[0:1].copy()
            第二月資料 = df.iloc[每月筆數:2*每月筆數].copy() if 2*每月筆數 <= 資料總數 else df.iloc[0:1].copy()
            第三月資料 = df.iloc[2*每月筆數:3*每月筆數].copy() if 3*每月筆數 <= 資料總數 else df.iloc[0:1].copy()
            第四月資料 = df.iloc[3*每月筆數:].copy() if 3*每月筆數 < 資料總數 else df.iloc[0:1].copy()
            
            # 如果任何月份的資料為空，則使用原始資料的前幾筆
            if 第一月資料.empty: 第一月資料 = df.iloc[0:min(10, 資料總數)].copy()
            if 第二月資料.empty: 第二月資料 = df.iloc[0:min(10, 資料總數)].copy()
            if 第三月資料.empty: 第三月資料 = df.iloc[0:min(10, 資料總數)].copy()
            if 第四月資料.empty: 第四月資料 = df.iloc[0:min(10, 資料總數)].copy()
            
            # 存入月份資料字典
            st.session_state.月份資料字典 = {
                1: 第一月資料,
                2: 第二月資料,
                3: 第三月資料,
                4: 第四月資料
            }
            
            # 顯示每個月份的資料數量
            st.write(f"--- Debug: 1月 資料形狀: {第一月資料.shape} ---") # Debug
            st.write(f"--- Debug: 2月 資料形狀: {第二月資料.shape} ---") # Debug
            st.write(f"--- Debug: 3月 資料形狀: {第三月資料.shape} ---") # Debug
            st.write(f"--- Debug: 4月 資料形狀: {第四月資料.shape} ---") # Debug
        

        
        # 確保所有月份都有資料
        # 注意：如果使用模組分類方式，這裡不需要重新賦值
        # 如果使用平均分割法，月份資料字典已經在上面設置好了
        
        # 確保月份資料字典不為空
        if not st.session_state.月份資料字典:
            st.warning("月份資料字典為空，將使用原始資料創建")
            # 如果月份資料字典為空，則使用原始資料創建
            月份欄位 = df.columns[1] if len(df.columns) > 1 else None
            
            if 月份欄位 and pd.api.types.is_datetime64_any_dtype(df[月份欄位]):
                # 如果是日期類型，提取月份
                df['月份數字'] = df[月份欄位].dt.month
                所有月份 = df['月份數字'].dropna().unique()
                所有月份 = sorted([int(m) for m in 所有月份 if pd.notna(m)])
                
                for 月份 in 所有月份:
                    月份資料 = df[df['月份數字'] == 月份].copy()
                    if not 月份資料.empty:
                        st.session_state.月份資料字典[月份] = 月份資料
            else:
                # 如果沒有月份欄位或不是日期類型，則使用固定的月份分組
                for 月份 in [1, 2, 3, 4]:
                    st.session_state.月份資料字典[月份] = df.iloc[0:min(10, 資料總數)].copy()
        
        st.success(f"已成功強制創建 4 個月份的資料: 1, 2, 3, 4 月")
    except Exception as e:
        # 發生錯誤時，使用原始資料為每個月份創建資料
        st.error(f"分割資料時發生錯誤: {e}")
        st.warning("將使用原始資料為每個月份創建資料")
        
        # 將原始資料複製為每個月份的資料
        st.session_state.月份資料字典 = {
            1: df.copy(),
            2: df.copy(),
            3: df.copy(),
            4: df.copy()
        }
    
    # 最後確認所有月份都在字典中
    月份列表 = list(st.session_state.月份資料字典.keys())
    st.write(f"--- Debug: Final month keys: {月份列表} ---") # Debug
    
    if len(月份列表) != 4 or sorted(月份列表) != [1, 2, 3, 4]:
        st.error(f"月份列表不完整，目前為: {月份列表}")
        # 確保所有月份都存在
        for 月份 in [1, 2, 3, 4]:
            if 月份 not in st.session_state.月份資料字典:
                st.session_state.月份資料字典[月份] = df.copy()
                st.warning(f"強制添加缺失的月份 {int(月份)}")
    
    st.write(f"--- Debug: Exiting 自動處理月份資料 - Keys: {list(st.session_state.月份資料字典.keys())} ---") # Debug

# 分析單月資料功能
def 分析單月資料():
    st.header("📊 分析單月資料")
    st.write("--- Debug: Entering 分析單月資料 ---") # Debug

    # 檢查是否有資料以及月份字典是否存在
    if 'df' not in st.session_state or st.session_state.df is None:
        st.error("請先在 '讀取資料' 頁面讀取或上傳資料！")
        return

    # 確保月份資料字典存在
    if '月份資料字典' not in st.session_state:
        st.session_state.月份資料字典 = {}

    # 如果月份資料字典為空，自動處理月份資料
    if not st.session_state.月份資料字典:
        if 'df' in st.session_state and st.session_state.df is not None:
            自動處理月份資料(st.session_state.df)
            
            # 再次檢查月份資料字典
            if not st.session_state.月份資料字典:
                # 如果仍然為空，手動創建月份資料
                df = st.session_state.df
                st.info("嘗試手動創建月份資料...")
                
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
                
                # 如果仍然為空，則使用固定的月份分組
                if not st.session_state.月份資料字典:
                    資料總數 = len(df)
                    每月筆數 = 資料總數 // 4
                    
                    st.session_state.月份資料字典 = {
                        1: df.iloc[0:每月筆數].copy() if 每月筆數 > 0 else df.iloc[0:1].copy(),
                        2: df.iloc[每月筆數:2*每月筆數].copy() if 2*每月筆數 <= 資料總數 else df.iloc[0:1].copy(),
                        3: df.iloc[2*每月筆數:3*每月筆數].copy() if 3*每月筆數 <= 資料總數 else df.iloc[0:1].copy(),
                        4: df.iloc[3*每月筆數:].copy() if 3*每月筆數 < 資料總數 else df.iloc[0:1].copy()
                    }
                    st.success("已手動創建四個月份的資料")
        else:
            st.error("沒有可用的原始資料。請先讀取資料。")
            return

    # 顯示可用的月份選項
    st.write(f"--- Debug: Before selectbox - Keys: {list(st.session_state.月份資料字典.keys())} ---") # Debug
    可選月份 = sorted(list(st.session_state.月份資料字典.keys()))
    if not 可選月份:
         st.error("沒有可用的月份資料可以選擇。")
         return # 如果沒有月份可以選，就停止執行

    月份 = st.selectbox("選擇要分析的月份", 可選月份)

    if st.button("開始分析"):
        # 確保選擇的月份存在於字典中
        if 月份 not in st.session_state.月份資料字典:
            st.error(f"選擇的月份 {int(月份)} 資料不存在，請重新讀取資料。")
            return

        df_month = st.session_state.月份資料字典[月份].copy()

        # 檢查 DataFrame 是否為空
        if df_month.empty:
            st.warning(f"選擇的月份 {int(月份)} 沒有資料可供分析。")
            return

        # 檢查欄位是否存在
        if len(df_month.columns) < 14:
             st.error(f"資料欄位數量不足（需要至少 14 欄），無法找到模組（預期第 9 欄）和歸類（預期第 14 欄）。目前只有 {len(df_month.columns)} 欄。")
             st.dataframe(df_month.head()) # 顯示前幾行以供檢查
             return

        模組欄位 = df_month.columns[8]  # I 欄是模組
        歸類欄位 = df_month.columns[13] # N 欄是歸類

        st.info(f"模組欄位名稱: {str(模組欄位)}")
        st.info(f"歸類欄位名稱: {str(歸類欄位)}")

        # 計算各模組的數量
        模組統計 = df_month[模組欄位].value_counts()

        # 計算各歸類的數量
        歸類統計 = df_month[歸類欄位].value_counts()

        # 顯示模組統計
        st.subheader(f"{int(月份)}月 各 {str(模組欄位)} 數量統計")
        st.dataframe(模組統計)

        # 顯示歸類統計
        st.subheader(f"{int(月份)}月 各 {str(歸類欄位)} 數量統計")
        st.dataframe(歸類統計)

        # 創建模組分析圖表
        st.subheader(f"{int(月份)}月 各 {str(模組欄位)} 數量統計圖 (前10名)")
        if not 模組統計.empty:
            fig1, ax1 = plt.subplots(figsize=(12, 6))
            模組統計.head(10).plot(kind='bar', ax=ax1)
            ax1.set_title(f'{int(月份)}月 各 {str(模組欄位)} 數量統計 (前10名)', fontsize=16)
            ax1.set_xlabel(f'{str(模組欄位)}', fontsize=12)
            ax1.set_ylabel('數量', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig1)
        else:
            st.info(f"月份 {int(月份)} 沒有 {str(模組欄位)} 資料可繪製圖表。")

        # 創建歸類分析圖表
        st.subheader(f"{int(月份)}月 各 {str(歸類欄位)} 數量統計圖 (前15名)")
        if not 歸類統計.empty:
            fig2, ax2 = plt.subplots(figsize=(14, 7))
            歸類統計.head(15).plot(kind='bar', ax=ax2)
            ax2.set_title(f'{int(月份)}月 各 {str(歸類欄位)} 數量統計 (前15名)', fontsize=16)
            ax2.set_xlabel(f'{str(歸類欄位)}', fontsize=12)
            ax2.set_ylabel('數量', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig2)
        else:
            st.info(f"月份 {int(月份)} 沒有 {str(歸類欄位)} 資料可繪製圖表。")

        # 創建交叉分析熱力圖
        st.subheader(f"{int(月份)}月 {str(模組欄位)}-{str(歸類欄位)} 交叉分析 (前10名)")
        if not 模組統計.empty and not 歸類統計.empty:
            try:
                交叉表 = pd.crosstab(df_month[模組欄位], df_month[歸類欄位])

                # 只選擇前10個模組和前10個歸類進行熱力圖分析
                top_模組 = 模組統計.head(10).index
                top_歸類 = 歸類統計.head(10).index
                # 確保交叉表的索引和列名存在於 top_模組 和 top_歸類 中
                valid_rows = 交叉表.index.intersection(top_模組)
                valid_cols = 交叉表.columns.intersection(top_歸類)

                if not valid_rows.empty and not valid_cols.empty:
                    交叉表_篩選 = 交叉表.loc[valid_rows, valid_cols]

                    fig3, ax3 = plt.subplots(figsize=(16, 12))
                    sns.heatmap(交叉表_篩選, cmap="YlGnBu", annot=True, fmt='g', ax=ax3)
                    ax3.set_title(f'{int(月份)}月 {str(模組欄位)}-{str(歸類欄位)} 交叉分析 (Top 10)', fontsize=16)
                    plt.tight_layout()
                    st.pyplot(fig3)

                    # 提供下載選項
                    output = io.BytesIO()
                    交叉表.to_excel(output, index=True) # 包含索引
                    output.seek(0)

                    st.download_button(
                        label=f"下載 {int(月份)}月_{str(模組欄位)}_{str(歸類欄位)}_交叉分析.xlsx",
                        data=output,
                        file_name=f"{int(月份)}月_{str(模組欄位)}_{str(歸類欄位)}_交叉分析.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.info("無法生成熱力圖，因為找不到足夠的交叉資料。")

            except Exception as e:
                st.error(f"生成交叉分析熱力圖時發生錯誤: {e}")
        else:
            st.info("沒有足夠的模組或歸類資料進行交叉分析。")

# 比較兩月資料功能
def 比較兩月資料():
    st.header("📊 比較兩月資料")
    
    if st.session_state.df is None:
        st.error("請先讀取資料！")
        return
    
    # 確保月份資料字典存在
    if '月份資料字典' not in st.session_state:
        st.session_state.月份資料字典 = {}
    
    # 如果月份資料字典為空，嘗試重新處理月份資料
    if not st.session_state.月份資料字典 and 'df' in st.session_state and st.session_state.df is not None:
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
    
    if st.session_state.df is None:
        st.error("請先讀取資料！")
        return
    
    # 確保月份資料字典存在
    if '月份資料字典' not in st.session_state:
        st.session_state.月份資料字典 = {}
    
    # 如果月份資料字典為空，嘗試重新處理月份資料
    if not st.session_state.月份資料字典 and 'df' in st.session_state and st.session_state.df is not None:
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
if "功能選項" in locals() or "功能選項" in globals():
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
else:
    # 如果功能選項未定義，預設顯示讀取資料頁面
    讀取資料()
