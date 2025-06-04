# 匯入所需模組
from selenium import webdriver                                  # 操作瀏覽器的主模組
from selenium.webdriver.common.by import By                    # 定位元素用
from selenium.webdriver.support.ui import WebDriverWait        # 顯性等待
from selenium.webdriver.support import expected_conditions as EC  # 等待條件
from selenium.webdriver.chrome.options import Options           # 設定 Chrome 啟動參數
from selenium.webdriver.chrome.service import Service           # 用來啟動 ChromeDriver
from webdriver_manager.chrome import ChromeDriverManager        # 自動下載對應的 ChromeDriver
from selenium.common.exceptions import TimeoutException         # 處理等待超時的錯誤
import json                                                     # 讀取 JSON 測試資料

# === 第一步：讀取 JSON 格式的測試資料 ===
with open("test_cases.json", "r", encoding="utf-8") as f:
    test_cases = json.load(f)  # test_cases 為 list，每筆資料格式如：{"username": "tomsmith", "password": "xxx", "expected": "成功"}

# === 第二步：設定 Chrome 啟動選項來降低被偵測為機器人風險 ===
chrome_options = Options()
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])     # 移除自動化控制標誌
chrome_options.add_experimental_option("useAutomationExtension", False)              # 停用自動化擴充功能
chrome_options.add_argument("--disable-blink-features=AutomationControlled")         # 隱藏自動化特徵
chrome_options.add_argument("--disable-infobars")                                     # 移除「Chrome正被自動測試」訊息
chrome_options.add_argument("--start-maximized")                                      # 瀏覽器最大化
chrome_options.add_argument("--incognito")                                            # 啟動無痕模式
chrome_options.add_argument("user-agent=Mozilla/5.0")                                 # 設定常見的使用者代理（模擬一般用戶）

# === 第三步：啟動 Chrome 瀏覽器 ===
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# === 第四步：依序執行每一筆測試案例 ===
for case in test_cases:
    username = case["username"]     # 取得帳號
    password = case["password"]     # 取得密碼
    expected = case["expected"]     # 取得預期結果（成功 or 失敗）

    driver.get("https://the-internet.herokuapp.com/login")  # 打開目標登入頁面

    # 等待帳號欄位可輸入，最多等 10 秒
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "username"))
    )

    # 清空帳號與密碼欄位再輸入新資料
    driver.find_element(By.ID, "username").clear()
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)

    # 點擊登入按鈕
    driver.find_element(By.CSS_SELECTOR, "button.radius").click()

    # 嘗試抓取登入後的提示訊息（最多等 5 秒）
    try:
        flash = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "flash"))
        )
        message = flash.text.strip()  # 把訊息文字抓出來並去除前後空白

        # === 判斷測試結果是否與預期相符 ===
        if message.startswith("You logged into a secure area!") and expected == "成功":
            print(f"✅ 測試成功：{username} / {password} → 成功")
        elif (message.startswith("Your username is invalid!") or message.startswith("Your password is invalid!")) and expected == "失敗":
            print(f"✅ 測試成功：{username} / {password} → 失敗")
        else:
            print(f"❌ 結果不符預期：{username} / {password} → {message}")

    except TimeoutException:
        # 若抓不到訊息（等待超過 5 秒），則視為測試失敗
        print(f"❌ 測試失敗：{username} / {password} → 無法抓取結果訊息")

# === 第五步：關閉瀏覽器 ===
driver.quit()
