import streamlit as st
import hashlib
import os
import json
import pandas as pd

def check_password():
    """檢查使用者輸入的密碼是否正確"""
    # 本地端自動登入功能
    # 直接設定管理員資訊並返回 True
    st.session_state["username_logged"] = "chihpao"
    st.session_state["user_role"] = "admin"
    
    # 載入使用者資料（為了使用者管理功能）
    if "users" not in st.session_state:
        try:
            # 嘗試從本地檔案載入使用者資料
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
                # 儲存預設使用者資料到本地檔案
                with open(users_file, "w") as f:
                    json.dump(st.session_state["users"], f)
        except Exception as e:
            # 如果發生錯誤，直接使用預設使用者
            st.warning(f"載入使用者資料時發生錯誤，使用預設使用者: {e}")
            st.session_state["users"] = {
                "chihpao": {
                    "password": "3a78c2a41af38053eabf7ac5d8c3cae96912b27452819b3ddef48ba67e8e76e5",
                    "role": "admin"
                }
            }
    
    return True

def user_management():
    """使用者管理頁面"""
    st.header("👥 使用者管理")
    
    # 檢查是否為管理員
    if "user_role" not in st.session_state or st.session_state["user_role"] != "admin":
        st.error("您沒有權限訪問此頁面！")
        return
    
    # 顯示現有使用者
    st.subheader("現有使用者")
    
    # 創建使用者資料表
    使用者資料 = []
    for username, user_info in st.session_state["users"].items():
        使用者資料.append({
            "使用者名稱": username,
            "角色": user_info["role"]
        })
    
    st.table(pd.DataFrame(使用者資料))
    
    # 添加新使用者
    st.subheader("添加新使用者")
    
    with st.form("add_user_form"):
        new_username = st.text_input("使用者名稱")
        new_password = st.text_input("密碼", type="password")
        new_role = st.selectbox("角色", ["user", "admin"])
        
        submitted = st.form_submit_button("添加")
        
        if submitted:
            if new_username in st.session_state["users"]:
                st.error("使用者名稱已存在！")
            elif not new_username or not new_password:
                st.error("使用者名稱和密碼不能為空！")
            else:
                # 添加新使用者
                st.session_state["users"][new_username] = {
                    "password": hashlib.sha256(str.encode(new_password)).hexdigest(),
                    "role": new_role
                }
                
                # 儲存使用者資料到本地檔案
                users_file = os.path.join(os.path.dirname(__file__), "users.json")
                with open(users_file, "w") as f:
                    json.dump(st.session_state["users"], f)
                
                st.success(f"使用者 {new_username} 已成功添加！")
                st.experimental_rerun()
    
    # 刪除使用者
    st.subheader("刪除使用者")
    
    with st.form("delete_user_form"):
        username_to_delete = st.selectbox("選擇要刪除的使用者", list(st.session_state["users"].keys()))
        
        submitted = st.form_submit_button("刪除")
        
        if submitted:
            if username_to_delete == st.session_state["username_logged"]:
                st.error("您不能刪除自己的帳號！")
            else:
                # 刪除使用者
                del st.session_state["users"][username_to_delete]
                
                # 儲存使用者資料到本地檔案
                users_file = os.path.join(os.path.dirname(__file__), "users.json")
                with open(users_file, "w") as f:
                    json.dump(st.session_state["users"], f)
                
                st.success(f"使用者 {username_to_delete} 已成功刪除！")
                st.experimental_rerun()
