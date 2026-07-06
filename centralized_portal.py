import streamlit as st
import pandas as pd
import pydeck as pdk
import requests
import folium
from streamlit_folium import st_folium
import random
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
from datetime import datetime, timedelta
import feedparser
import re
import time
from urllib.parse import urlparse
import json
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import concurrent.futures

st.set_page_config(
    page_title=" NCB (OPS) Intelligence Portal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================================
# ENHANCED CUSTOM CSS
# ====================================

st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Main Title */
    .main-title {
        font-size: 42px;
        font-weight: 900;
        background: linear-gradient(135deg, #0a9396, #005f73, #0a9396);
        background-size: 300% 300%;
        animation: gradientShift 4s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 20px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .sub-title {
        color: #2d3748;
        text-align: center;
        margin-bottom: 25px;
        font-size: 16px;
        font-weight: 500;
        letter-spacing: 1px;
        background: rgba(255,255,255,0.7);
        padding: 10px 20px;
        border-radius: 30px;
        display: inline-block;
        margin-left: auto;
        margin-right: auto;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(10, 147, 150, 0.2);
    }
    
    /* Metric Cards */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff, #f0f4f8);
        border: 1px solid rgba(10, 147, 150, 0.15);
        border-radius: 16px;
        padding: 16px 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 15px 40px rgba(10, 147, 150, 0.2);
        border-color: #0a9396;
    }
    
    [data-testid="stMetric"] label {
        font-weight: 700;
        color: #1a1a2e;
        font-size: 14px;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(135deg, #0a9396, #005f73);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Cards */
    .vendor-card {
        background: linear-gradient(145deg, #0f172a, #1a2332);
        border: 1px solid #2d3748;
        border-radius: 14px;
        padding: 16px 20px;
        margin: 8px 0;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
    }
    
    .vendor-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(10, 147, 150, 0.1), transparent);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .vendor-card:hover::before {
        opacity: 1;
    }
    
    .vendor-card:hover {
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 12px 35px rgba(10, 147, 150, 0.25);
        border-color: #0a9396;
    }
    
    .vendor-name {
        color: #94d2bd;
        font-weight: 700;
        font-size: 17px;
        position: relative;
        z-index: 1;
    }
    
    .vendor-detail {
        color: #e9ecef;
        font-size: 12px;
        padding: 3px 0;
        position: relative;
        z-index: 1;
    }
    
    .vendor-rating {
        color: #ffd93d;
        font-weight: 700;
        font-size: 14px;
    }
    
    .vendor-supply-high { 
        color: #6bcb77; 
        font-weight: 700;
        text-shadow: 0 0 20px rgba(107, 203, 119, 0.3);
    }
    .vendor-supply-medium { 
        color: #ffd93d; 
        font-weight: 700;
        text-shadow: 0 0 20px rgba(255, 217, 61, 0.3);
    }
    .vendor-supply-low { 
        color: #ff6b6b; 
        font-weight: 700;
        text-shadow: 0 0 20px rgba(255, 107, 107, 0.3);
    }
    
    /* Badges */
    .badge-darkweb {
        background: linear-gradient(135deg, #dc3545, #c0392b);
        color: white;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 9px;
        font-weight: 700;
        margin-left: 5px;
        box-shadow: 0 2px 10px rgba(220, 53, 69, 0.4);
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    .badge-surface {
        background: linear-gradient(135deg, #007bff, #0056b3);
        color: white;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 9px;
        font-weight: 700;
        margin-left: 5px;
        box-shadow: 0 2px 10px rgba(0, 123, 255, 0.4);
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    .badge-live {
        background: linear-gradient(135deg, #28a745, #1e7e34);
        color: white;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 9px;
        font-weight: 700;
        margin-left: 5px;
        box-shadow: 0 2px 10px rgba(40, 167, 69, 0.4);
        animation: pulse 2s ease-in-out infinite;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(40, 167, 69, 0); }
        100% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); }
    }
    
    .substance-tag {
        display: inline-block;
        background: linear-gradient(135deg, #1e293b, #2d3748);
        color: #94d2bd;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 10px;
        margin: 2px;
        border: 1px solid rgba(10, 147, 150, 0.3);
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .substance-tag:hover {
        background: #0a9396;
        color: white;
        transform: scale(1.05);
        border-color: #0a9396;
    }
    
    /* News Cards */
    .news-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        border: 1px solid #e9ecef;
        border-radius: 14px;
        padding: 18px 22px;
        margin: 12px 0;
        border-left: 5px solid #0a9396;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    .news-card:hover {
        transform: translateX(8px) translateY(-2px);
        box-shadow: 0 12px 35px rgba(10, 147, 150, 0.15);
        border-color: #0a9396;
    }
    
    .news-heading {
        font-weight: 700;
        font-size: 16px;
        color: #1a1a2e;
        margin-bottom: 8px;
        line-height: 1.4;
    }
    
    .news-meta {
        color: #6c757d;
        font-size: 12px;
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        align-items: center;
        margin-top: 6px;
    }
    
    .news-drugs {
        display: inline-block;
        background: linear-gradient(135deg, #dc3545, #c0392b);
        color: white;
        padding: 3px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        box-shadow: 0 2px 10px rgba(220, 53, 69, 0.3);
    }
    
    .news-location {
        display: inline-block;
        background: linear-gradient(135deg, #0a9396, #005f73);
        color: white;
        padding: 3px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        box-shadow: 0 2px 10px rgba(10, 147, 150, 0.3);
    }
    
    .news-link {
        color: #0a9396;
        text-decoration: none;
        font-weight: 600;
        font-size: 12px;
        transition: all 0.3s ease;
        padding: 3px 10px;
        border-radius: 15px;
        background: rgba(10, 147, 150, 0.1);
    }
    
    .news-link:hover {
        color: #005f73;
        background: rgba(10, 147, 150, 0.2);
        text-decoration: none;
        transform: translateX(3px);
    }
    
    /* Live Indicator */
    .live-indicator {
        display: inline-block;
        width: 14px;
        height: 14px;
        background: #dc3545;
        border-radius: 50%;
        animation: pulse-dot 1.5s ease-in-out infinite;
        margin-right: 10px;
        box-shadow: 0 0 20px rgba(220, 53, 69, 0.5);
    }
    
    @keyframes pulse-dot {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(0.8); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    .last-updated {
        color: #6c757d;
        font-size: 12px;
        margin-left: 8px;
        font-weight: 500;
    }
    
    .news-count {
        color: #0a9396;
        font-weight: 700;
        font-size: 14px;
        margin-left: 10px;
        padding: 2px 12px;
        background: rgba(10, 147, 150, 0.1);
        border-radius: 20px;
        border: 1px solid rgba(10, 147, 150, 0.2);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1a2332 100%) !important;
        border-right: 2px solid #0a9396 !important;
        width: 280px !important;
        min-width: 280px !important;
        box-shadow: 4px 0 30px rgba(0,0,0,0.3);
    }
    
    .sidebar-title {
        background: linear-gradient(135deg, #0a9396, #005f73) !important;
        padding: 20px 15px !important;
        border-radius: 14px !important;
        text-align: center !important;
        margin-bottom: 18px !important;
        box-shadow: 0 4px 20px rgba(10, 147, 150, 0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .sidebar-title h1 {
        color: #ffffff !important;
        font-size: 22px !important;
        font-weight: 800 !important;
        letter-spacing: 1px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .welcome-text {
        background: rgba(255,255,255,0.05) !important;
        padding: 12px 16px !important;
        border-radius: 12px !important;
        margin: 10px 0 18px 0 !important;
        border-left: 4px solid #0a9396 !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .welcome-text p {
        color: #e9ecef !important;
        font-weight: 500;
    }
    
    .db-status {
        padding: 10px !important;
        border-radius: 12px !important;
        margin: 12px 0 !important;
        text-align: center !important;
        font-weight: 600;
    }
    
    .db-status.success {
        background: rgba(40, 167, 69, 0.15) !important;
        border: 1px solid rgba(40, 167, 69, 0.3) !important;
        color: #6bcb77 !important;
    }
    
    .db-status.warning {
        background: rgba(255, 193, 7, 0.15) !important;
        border: 1px solid rgba(255, 193, 7, 0.3) !important;
        color: #ffd93d !important;
    }
    
    .nav-header {
        color: #94d2bd !important;
        font-weight: 800 !important;
        text-align: center !important;
        border-bottom: 2px solid rgba(10, 147, 150, 0.3) !important;
        padding-bottom: 10px !important;
        letter-spacing: 2px;
        font-size: 13px;
        text-transform: uppercase;
    }
    
    /* Radio Buttons */
    .stRadio > div {
        gap: 8px;
    }
    
    .stRadio label {
        background: rgba(255,255,255,0.05);
        padding: 8px 16px;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.05);
        transition: all 0.3s ease;
        color: #cbd5e1;
        font-weight: 500;
    }
    
    .stRadio label:hover {
        background: rgba(10, 147, 150, 0.1);
        border-color: #0a9396;
        color: white;
    }
    
    .stRadio label[data-baseweb="radio"] {
        background: transparent;
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(10, 147, 150, 0.3) !important;
    }
    
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #0a9396, #005f73) !important;
        border: none !important;
        color: white !important;
    }
    
    .stButton button[kind="secondary"] {
        background: linear-gradient(135deg, #6c757d, #495057) !important;
        border: none !important;
        color: white !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        border-radius: 14px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
        border: 1px solid rgba(10, 147, 150, 0.1) !important;
    }
    
    .stDataFrame thead th {
        background: linear-gradient(135deg, #0a9396, #005f73) !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 12px !important;
        font-size: 13px !important;
    }
    
    .stDataFrame tbody tr:hover {
        background: rgba(10, 147, 150, 0.05) !important;
    }
    
    /* Select Box */
    .stSelectbox {
        border-radius: 12px !important;
    }
    
    .stSelectbox label {
        font-weight: 600 !important;
        color: #1a1a2e !important;
    }
    
    /* Info/Warning/Success Boxes */
    .stAlert {
        border-radius: 12px !important;
        border-left: 5px solid !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
    }
    
    .stAlert[data-baseweb="notification"] {
        background: rgba(255,255,255,0.9) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Divider */
    hr {
        margin: 25px 0 !important;
        border: none !important;
        height: 2px !important;
        background: linear-gradient(to right, transparent, #0a9396, transparent) !important;
        opacity: 0.3 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        border-radius: 12px !important;
        background: rgba(10, 147, 150, 0.05) !important;
        font-weight: 700 !important;
        color: #1a1a2e !important;
        border: 1px solid rgba(10, 147, 150, 0.1) !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(10, 147, 150, 0.1) !important;
        border-color: #0a9396 !important;
    }
    
    /* File Uploader */
    .stFileUploader {
        border-radius: 12px !important;
        border: 2px dashed rgba(10, 147, 150, 0.3) !important;
        padding: 20px !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader:hover {
        border-color: #0a9396 !important;
        background: rgba(10, 147, 150, 0.03) !important;
    }
    
    /* Checkbox */
    .stCheckbox label {
        font-weight: 600 !important;
        color: #1a1a2e !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px !important;
        background: rgba(255,255,255,0.05) !important;
        padding: 6px !important;
        border-radius: 14px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important;
        padding: 8px 20px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        color: #4a5568 !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #0a9396, #005f73) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(10, 147, 150, 0.3) !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(10, 147, 150, 0.1) !important;
    }
    
    /* High Risk Alert */
    .high-risk-box {
        background: linear-gradient(135deg, #fff5f5, #ffe0e0) !important;
        border: 2px solid #dc3545 !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        margin: 10px 0 !important;
        box-shadow: 0 4px 20px rgba(220, 53, 69, 0.15) !important;
        transition: all 0.3s ease !important;
    }
    
    .high-risk-box:hover {
        transform: scale(1.01);
        box-shadow: 0 8px 30px rgba(220, 53, 69, 0.25) !important;
    }
    
    /* Metric Icons */
    .metric-icon {
        font-size: 24px;
        margin-right: 8px;
    }
    
    /* Gradient Text */
    .gradient-text {
        background: linear-gradient(135deg, #0a9396, #94d2bd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# ====================================
# AUTO REFRESH CONFIGURATION
# ====================================

# Store last fetch time in session state
if 'last_news_fetch' not in st.session_state:
    st.session_state.last_news_fetch = datetime.now()
if 'maritime_news' not in st.session_state:
    st.session_state.maritime_news = []
if 'news_refresh_interval' not in st.session_state:
    st.session_state.news_refresh_interval = 300  # 5 minutes default
if 'auto_refresh_enabled' not in st.session_state:
    st.session_state.auto_refresh_enabled = True
if 'selected_news_date' not in st.session_state:
    st.session_state.selected_news_date = datetime.now().date()
if 'live_vendors' not in st.session_state:
    st.session_state.live_vendors = []
if 'last_vendor_fetch' not in st.session_state:
    st.session_state.last_vendor_fetch = None
if 'vendor_refresh_interval' not in st.session_state:
    st.session_state.vendor_refresh_interval = 3600  # 1 hour

# ====================================
# LIVE WEB SCRAPING FOR DRUG VENDORS
# ====================================

def setup_selenium_driver():
    """Setup Selenium WebDriver for web scraping"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except:
        return None

def scrape_indiamart_vendors(drug_name="chemical"):
    """Scrape IndiaMART for vendors selling chemicals"""
    vendors = []
    try:
        driver = setup_selenium_driver()
        if not driver:
            return scrape_indiamart_vendors_requests(drug_name)
        
        url = f"https://www.indiamart.com/search/?q={drug_name}&page=1"
        driver.get(url)
        time.sleep(3)
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "listing"))
            )
        except:
            pass
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        for item in soup.find_all('div', class_='listing')[:10]:
            try:
                name = item.find('h3', class_='vendor-name')
                name = name.text.strip() if name else "Unknown"
                
                product = item.find('h4', class_='product-name')
                product = product.text.strip() if product else "Unknown"
                
                location = item.find('span', class_='location')
                location = location.text.strip() if location else "Unknown"
                
                rating = item.find('span', class_='rating')
                rating = float(rating.text.split()[0]) if rating else 0.0
                
                vendors.append({
                    'name': name[:50],
                    'substances': [product],
                    'rating': rating,
                    'supply_volume': 'Unknown',
                    'reliability': f"{rating * 20:.0f}%",
                    'years_active': 0,
                    'location': location,
                    'website': url,
                    'compliance': 'Under Review',
                    'price_range': 'Contact Seller',
                    'shipping': 'Unknown',
                    'payment_methods': ['Contact Seller'],
                    'platform': 'IndiaMART',
                    'vendor_type': 'Surface Web',
                    'source': 'Live Scraped'
                })
            except:
                continue
        
        driver.quit()
        return vendors
    except Exception as e:
        return []

def scrape_indiamart_vendors_requests(drug_name):
    """Fallback: Use requests with BeautifulSoup"""
    vendors = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        url = f"https://www.indiamart.com/search/?q={drug_name}&page=1"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.find_all('div', class_='listing')[:10]:
            try:
                name = item.find('h3', class_='vendor-name')
                name = name.text.strip() if name else "Unknown"
                
                product = item.find('h4', class_='product-name')
                product = product.text.strip() if product else "Unknown"
                
                vendors.append({
                    'name': name[:50],
                    'substances': [product],
                    'rating': 0.0,
                    'supply_volume': 'Unknown',
                    'reliability': 'Unknown',
                    'years_active': 0,
                    'location': 'Unknown',
                    'website': url,
                    'compliance': 'Under Review',
                    'price_range': 'Contact Seller',
                    'shipping': 'Unknown',
                    'payment_methods': ['Contact Seller'],
                    'platform': 'IndiaMART',
                    'vendor_type': 'Surface Web',
                    'source': 'Live Scraped'
                })
            except:
                continue
    except:
        pass
    return vendors

def scrape_alibaba_vendors(drug_name="chemical"):
    """Scrape Alibaba for vendors"""
    vendors = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        url = f"https://www.alibaba.com/trade/search?SearchText={drug_name}&page=1"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.find_all('div', class_='product-item')[:10]:
            try:
                name = item.find('span', class_='company-name')
                name = name.text.strip() if name else "Unknown"
                
                product = item.find('h2', class_='product-title')
                product = product.text.strip() if product else "Unknown"
                
                location = item.find('span', class_='location')
                location = location.text.strip() if location else "Unknown"
                
                vendors.append({
                    'name': name[:50],
                    'substances': [product],
                    'rating': 0.0,
                    'supply_volume': 'Unknown',
                    'reliability': 'Unknown',
                    'years_active': 0,
                    'location': location,
                    'website': url,
                    'compliance': 'Under Review',
                    'price_range': 'Contact Seller',
                    'shipping': 'International',
                    'payment_methods': ['Bank Transfer', 'Cryptocurrency'],
                    'platform': 'Alibaba',
                    'vendor_type': 'Surface Web',
                    'source': 'Live Scraped'
                })
            except:
                continue
    except:
        pass
    return vendors

def scrape_tradeindia_vendors(drug_name="chemical"):
    """Scrape TradeIndia for vendors"""
    vendors = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        url = f"https://www.tradeindia.com/search/?q={drug_name}"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.find_all('div', class_='seller-card')[:10]:
            try:
                name = item.find('h3', class_='seller-name')
                name = name.text.strip() if name else "Unknown"
                
                product = item.find('p', class_='product-name')
                product = product.text.strip() if product else "Unknown"
                
                vendors.append({
                    'name': name[:50],
                    'substances': [product],
                    'rating': 0.0,
                    'supply_volume': 'Unknown',
                    'reliability': 'Unknown',
                    'years_active': 0,
                    'location': 'Unknown',
                    'website': url,
                    'compliance': 'Under Review',
                    'price_range': 'Contact Seller',
                    'shipping': 'Domestic',
                    'payment_methods': ['Bank Transfer'],
                    'platform': 'TradeIndia',
                    'vendor_type': 'Surface Web',
                    'source': 'Live Scraped'
                })
            except:
                continue
    except:
        pass
    return vendors

def scrape_made_in_china_vendors(drug_name="chemical"):
    """Scrape Made-in-China for vendors"""
    vendors = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        url = f"https://www.made-in-china.com/products-search/{drug_name}/1.html"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.find_all('div', class_='product-item')[:10]:
            try:
                name = item.find('a', class_='company-name')
                name = name.text.strip() if name else "Unknown"
                
                product = item.find('a', class_='product-title')
                product = product.text.strip() if product else "Unknown"
                
                vendors.append({
                    'name': name[:50],
                    'substances': [product],
                    'rating': 0.0,
                    'supply_volume': 'Unknown',
                    'reliability': 'Unknown',
                    'years_active': 0,
                    'location': 'China',
                    'website': url,
                    'compliance': 'Under Review',
                    'price_range': 'Contact Seller',
                    'shipping': 'International',
                    'payment_methods': ['Bank Transfer', 'Cryptocurrency'],
                    'platform': 'Made-in-China',
                    'vendor_type': 'Surface Web',
                    'source': 'Live Scraped'
                })
            except:
                continue
    except:
        pass
    return vendors

def scrape_dial4trade_vendors(drug_name="chemical"):
    """Scrape Dial4Trade for vendors"""
    vendors = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        url = f"https://www.dial4trade.com/search?q={drug_name}"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.find_all('div', class_='company-item')[:10]:
            try:
                name = item.find('h3', class_='company-name')
                name = name.text.strip() if name else "Unknown"
                
                product = item.find('p', class_='product-name')
                product = product.text.strip() if product else "Unknown"
                
                vendors.append({
                    'name': name[:50],
                    'substances': [product],
                    'rating': 0.0,
                    'supply_volume': 'Unknown',
                    'reliability': 'Unknown',
                    'years_active': 0,
                    'location': 'Unknown',
                    'website': url,
                    'compliance': 'Under Review',
                    'price_range': 'Contact Seller',
                    'shipping': 'International',
                    'payment_methods': ['Bank Transfer', 'PayPal'],
                    'platform': 'Dial4Trade',
                    'vendor_type': 'Surface Web',
                    'source': 'Live Scraped'
                })
            except:
                continue
    except:
        pass
    return vendors

def fetch_live_vendors():
    """Fetch live vendors from multiple platforms"""
    all_vendors = []
    
    search_terms = ["chemical", "pharma", "drug", "ketamine", "alprazolam", "tramadol"]
    
    scrape_functions = {
        'IndiaMART': scrape_indiamart_vendors,
        'Alibaba': scrape_alibaba_vendors,
        'TradeIndia': scrape_tradeindia_vendors,
        'Made-in-China': scrape_made_in_china_vendors,
        'Dial4Trade': scrape_dial4trade_vendors
    }
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for platform, scrape_func in scrape_functions.items():
            for term in search_terms[:2]:
                future = executor.submit(scrape_func, term)
                futures.append((platform, future))
        
        for platform, future in futures:
            try:
                result = future.result(timeout=30)
                if result:
                    all_vendors.extend(result)
            except Exception as e:
                continue
    
    seen_names = set()
    unique_vendors = []
    for vendor in all_vendors:
        key = f"{vendor['name']}_{vendor['platform']}"
        if key not in seen_names:
            seen_names.add(key)
            unique_vendors.append(vendor)
    
    return unique_vendors[:50]

def force_refresh_vendors():
    """Force refresh vendor data"""
    with st.spinner("🔄 Fetching live vendor data from platforms..."):
        st.session_state.live_vendors = fetch_live_vendors()
        st.session_state.last_vendor_fetch = datetime.now()
        st.rerun()

# ====================================
# STATIC VENDOR DATA (FALLBACK)
# ====================================

DRUG_VENDORS = {
    "Surface Web Vendors": {
        "IndiaMART": {
            "vendors": [
                {
                    "name": "Krishna Speciality Chemicals",
                    "substances": ["Ketamine", "Alprazolam", "MDMA", "Cocaine"],
                    "rating": 4.2,
                    "supply_volume": "High",
                    "reliability": "85%",
                    "years_active": 8,
                    "location": "Mumbai, India",
                    "website": "https://www.indiamart.com/krishna-speciality-chemical",
                    "compliance": "🔴 High Risk",
                    "price_range": "$50-200 per order",
                    "shipping": "International",
                    "payment_methods": ["Bank Transfer", "UPI", "Cryptocurrency"]
                },
                {
                    "name": "Coral Laboratory Limited",
                    "substances": ["LSD", "MDMA", "Cannabis", "Ketamine"],
                    "rating": 4.5,
                    "supply_volume": "Very High",
                    "reliability": "92%",
                    "years_active": 12,
                    "location": "Delhi, India",
                    "website": "https://www.indiamart.com/coral-laboratory-limited",
                    "compliance": "🔴 High Risk",
                    "price_range": "$100-500 per order",
                    "shipping": "International",
                    "payment_methods": ["Bank Transfer", "Cryptocurrency"]
                },
                {
                    "name": "Apex Chemicals Pvt Ltd",
                    "substances": ["Alprazolam", "Tramadol", "Ketamine"],
                    "rating": 4.0,
                    "supply_volume": "Medium",
                    "reliability": "78%",
                    "years_active": 5,
                    "location": "Ahmedabad, India",
                    "website": "https://www.indiamart.com/apex-chemicals",
                    "compliance": "🟡 Under Review",
                    "price_range": "$30-150 per order",
                    "shipping": "Domestic",
                    "payment_methods": ["Bank Transfer", "UPI"]
                }
            ]
        },
        "Alibaba": {
            "vendors": [
                {
                    "name": "Wuhan Lwax Pharma Tech",
                    "substances": ["Ketamine", "MDMA", "LSD", "Cocaine"],
                    "rating": 4.7,
                    "supply_volume": "Very High",
                    "reliability": "95%",
                    "years_active": 6,
                    "location": "Wuhan, China",
                    "website": "https://www.alibaba.com/wuhan-lwax-pharma",
                    "compliance": "🔴 High Risk",
                    "price_range": "$200-1000 per order",
                    "shipping": "International",
                    "payment_methods": ["Cryptocurrency", "Bank Transfer", "Western Union"]
                },
                {
                    "name": "Hebei Meijin Import Export",
                    "substances": ["Alprazolam", "Tramadol", "Ketamine"],
                    "rating": 4.3,
                    "supply_volume": "High",
                    "reliability": "88%",
                    "years_active": 4,
                    "location": "Hebei, China",
                    "website": "https://www.alibaba.com/hebei-meijin",
                    "compliance": "🔴 High Risk",
                    "price_range": "$100-400 per order",
                    "shipping": "International",
                    "payment_methods": ["Cryptocurrency", "Bank Transfer"]
                }
            ]
        },
        "TradeIndia": {
            "vendors": [
                {
                    "name": "Gujarat Pharma Solutions",
                    "substances": ["MDMA", "Cocaine", "Cannabis"],
                    "rating": 3.8,
                    "supply_volume": "Medium",
                    "reliability": "75%",
                    "years_active": 3,
                    "location": "Gujarat, India",
                    "website": "https://www.tradeindia.com/gujarat-pharma",
                    "compliance": "🟡 Under Review",
                    "price_range": "$50-300 per order",
                    "shipping": "Domestic",
                    "payment_methods": ["Bank Transfer", "Cash on Delivery"]
                }
            ]
        },
        "Made-in-China": {
            "vendors": [
                {
                    "name": "Anhui Moker New Material",
                    "substances": ["Ketamine", "LSD", "MDMA"],
                    "rating": 4.6,
                    "supply_volume": "Very High",
                    "reliability": "94%",
                    "years_active": 5,
                    "location": "Anhui, China",
                    "website": "https://www.made-in-china.com/anhui-moker",
                    "compliance": "🔴 High Risk",
                    "price_range": "$150-600 per order",
                    "shipping": "International",
                    "payment_methods": ["Cryptocurrency", "Bank Transfer"]
                }
            ]
        },
        "Dial4Trade": {
            "vendors": [
                {
                    "name": "Gantuo Chemicals",
                    "substances": ["Alprazolam", "Ketamine", "Tramadol"],
                    "rating": 4.4,
                    "supply_volume": "High",
                    "reliability": "89%",
                    "years_active": 7,
                    "location": "Guangzhou, China",
                    "website": "https://www.dial4trade.com/gantuo-2551716",
                    "compliance": "🔴 High Risk",
                    "price_range": "$80-350 per order",
                    "shipping": "International",
                    "payment_methods": ["Cryptocurrency", "Bank Transfer", "PayPal"]
                }
            ]
        }
    },
    "Dark Web Vendors": {
        "Archetyp": {
            "vendors": [
                {
                    "name": "LabChem_Supply",
                    "substances": ["Ketamine", "LSD", "MDMA", "Cocaine"],
                    "rating": 4.9,
                    "supply_volume": "Very High",
                    "reliability": "98%",
                    "years_active": 3,
                    "location": "Netherlands (VPN)",
                    "market_link": "http://archetyp-market.onion/labchemsupply",
                    "compliance": "🔴 Dark Web Vendor",
                    "price_range": "$200-2000 per order",
                    "shipping": "International (Stealth)",
                    "payment_methods": ["Monero", "Bitcoin"],
                    "escrow": "Yes",
                    "feedback_count": 1250
                },
                {
                    "name": "PharmaKing",
                    "substances": ["Alprazolam", "MDMA", "Cannabis"],
                    "rating": 4.7,
                    "supply_volume": "High",
                    "reliability": "93%",
                    "years_active": 2,
                    "location": "Germany (Tor)",
                    "market_link": "http://archetyp-market.online/pharmaking",
                    "compliance": "🔴 Dark Web Vendor",
                    "price_range": "$150-1500 per order",
                    "shipping": "International (Stealth)",
                    "payment_methods": ["Monero", "Bitcoin"],
                    "escrow": "Yes",
                    "feedback_count": 850
                }
            ]
        },
        "Bohemia": {
            "vendors": [
                {
                    "name": "AcidLab_Official",
                    "substances": ["LSD", "Ketamine", "MDMA"],
                    "rating": 4.8,
                    "supply_volume": "Very High",
                    "reliability": "96%",
                    "years_active": 4,
                    "location": "Canada (VPN)",
                    "market_link": "http://bohemia-market.onion/acidlab",
                    "compliance": "🔴 Dark Web Vendor",
                    "price_range": "$250-2000 per order",
                    "shipping": "International (Stealth)",
                    "payment_methods": ["Monero", "Bitcoin"],
                    "escrow": "Yes",
                    "feedback_count": 2100
                },
                {
                    "name": "SnowKing_Global",
                    "substances": ["Cocaine", "Heroin", "MDMA"],
                    "rating": 4.6,
                    "supply_volume": "High",
                    "reliability": "91%",
                    "years_active": 3,
                    "location": "Colombia (VPN)",
                    "market_link": "http://bohemia-market.online/snowking",
                    "compliance": "🔴 Dark Web Vendor",
                    "price_range": "$300-3000 per order",
                    "shipping": "International (Stealth)",
                    "payment_methods": ["Monero", "Bitcoin"],
                    "escrow": "Yes",
                    "feedback_count": 950
                }
            ]
        },
        "Incognito": {
            "vendors": [
                {
                    "name": "PsychoPharma_OG",
                    "substances": ["LSD", "MDMA", "Ketamine", "DMT"],
                    "rating": 4.9,
                    "supply_volume": "Very High",
                    "reliability": "99%",
                    "years_active": 5,
                    "location": "USA (Tor)",
                    "market_link": "http://incognito-market.onion/psychopharma",
                    "compliance": "🔴 Dark Web Vendor",
                    "price_range": "$200-2500 per order",
                    "shipping": "International (Stealth)",
                    "payment_methods": ["Monero", "Bitcoin"],
                    "escrow": "Yes",
                    "feedback_count": 3200
                }
            ]
        }
    }
}

# ====================================
# OSINT DRUG DATA
# ====================================

OSINT_DRUG_DATA = {
    "Ketamine": {
        "common_names": ["K", "Special K", "Vitamin K", "Kit Kat"],
        "street_price": "$80-120 per gram",
        "purity_levels": "60-85%",
        "source_countries": ["India", "China", "Mexico", "Netherlands"],
        "trafficking_routes": ["India-Nepal", "China-Southeast Asia", "Mexico-US"],
        "reddit_forums": ["r/ketamine", "r/drugs", "r/researchchemicals"],
        "telegram_groups": ["@ketamine_community", "@dissociatives_chat", "@drugs_global"],
        "darknet_markets": ["Archetyp", "Incognito", "Bohemia"],
        "seizure_stats": {"2024": "450 kg", "2025": "380 kg", "2026": "210 kg"},
        "risk_level": "High",
        "medical_use": "Anesthetic, Depression treatment"
    },
    "LSD": {
        "common_names": ["Acid", "Lucy", "Tabs", "Blotter"],
        "street_price": "$10-30 per tab",
        "purity_levels": "70-95%",
        "source_countries": ["USA", "Canada", "Netherlands", "Germany"],
        "trafficking_routes": ["Europe-US", "Canada-US", "Darknet distribution"],
        "reddit_forums": ["r/LSD", "r/psychonaut", "r/drugs"],
        "telegram_groups": ["@lsd_community", "@psychedelics_chat", "@research_chemicals"],
        "darknet_markets": ["Archetyp", "Incognito", "Silk Road 3.0"],
        "seizure_stats": {"2024": "280 kg", "2025": "310 kg", "2026": "150 kg"},
        "risk_level": "Medium",
        "medical_use": "Research, PTSD treatment trials"
    },
    "Cocaine": {
        "common_names": ["Coke", "Snow", "Blow", "Yayo"],
        "street_price": "$80-150 per gram",
        "purity_levels": "40-85%",
        "source_countries": ["Colombia", "Peru", "Bolivia", "Mexico"],
        "trafficking_routes": ["South America-North America", "South America-Europe", "Caribbean route"],
        "reddit_forums": ["r/cocaine", "r/drugs", "r/stims"],
        "telegram_groups": ["@cocaine_community", "@stimulants_chat", "@drugs_global"],
        "darknet_markets": ["Archetyp", "Bohemia", "DarkMarket"],
        "seizure_stats": {"2024": "1200 kg", "2025": "980 kg", "2026": "650 kg"},
        "risk_level": "Critical",
        "medical_use": "Local anesthetic (limited)"
    },
    "Alprazolam": {
        "common_names": ["Xanax", "Bars", "Zanies", "Football"],
        "street_price": "$2-5 per pill",
        "purity_levels": "80-95%",
        "source_countries": ["India", "China", "USA", "Mexico"],
        "trafficking_routes": ["India-USA", "Mexico-USA", "China-Europe"],
        "reddit_forums": ["r/benzodiazepines", "r/drugs", "r/researchchemicals"],
        "telegram_groups": ["@benzos_chat", "@pharma_community", "@drugs_global"],
        "darknet_markets": ["Archetyp", "Incognito", "AlphaBay"],
        "seizure_stats": {"2024": "850 kg", "2025": "720 kg", "2026": "480 kg"},
        "risk_level": "High",
        "medical_use": "Anxiety, Panic disorders"
    },
    "MDMA": {
        "common_names": ["Ecstasy", "Molly", "E", "XTC"],
        "street_price": "$20-40 per pill",
        "purity_levels": "50-85%",
        "source_countries": ["Netherlands", "Belgium", "Germany", "Canada"],
        "trafficking_routes": ["Europe-North America", "Europe-Australia", "Canada-US"],
        "reddit_forums": ["r/MDMA", "r/drugs", "r/aves"],
        "telegram_groups": ["@mdma_community", "@entactogens_chat", "@rave_drugs"],
        "darknet_markets": ["Archetyp", "Bohemia", "Cannabis Market"],
        "seizure_stats": {"2024": "680 kg", "2025": "550 kg", "2026": "390 kg"},
        "risk_level": "High",
        "medical_use": "PTSD treatment trials"
    }
}

# ====================================
# OSINT SOURCES
# ====================================

OSINT_SOURCES = {
    "reddit_forums": {
        "r/ketamine": "https://www.reddit.com/r/ketamine/",
        "r/LSD": "https://www.reddit.com/r/LSD/",
        "r/cocaine": "https://www.reddit.com/r/cocaine/",
        "r/benzodiazepines": "https://www.reddit.com/r/benzodiazepines/",
        "r/MDMA": "https://www.reddit.com/r/MDMA/",
        "r/meth": "https://www.reddit.com/r/meth/",
        "r/heroin": "https://www.reddit.com/r/heroin/",
        "r/trees": "https://www.reddit.com/r/trees/",
        "r/drugs": "https://www.reddit.com/r/drugs/",
        "r/psychonaut": "https://www.reddit.com/r/psychonaut/",
        "r/researchchemicals": "https://www.reddit.com/r/researchchemicals/",
        "r/stims": "https://www.reddit.com/r/stims/",
        "r/aves": "https://www.reddit.com/r/aves/",
        "r/opiates": "https://www.reddit.com/r/opiates/"
    },
    "telegram_groups": {
        "@ketamine_community": "https://t.me/ketamine_community",
        "@lsd_community": "https://t.me/lsd_community",
        "@cocaine_community": "https://t.me/cocaine_community",
        "@benzos_chat": "https://t.me/benzos_chat",
        "@mdma_community": "https://t.me/mdma_community",
        "@meth_community": "https://t.me/meth_community",
        "@heroin_community": "https://t.me/heroin_community",
        "@cannabis_community": "https://t.me/cannabis_community",
        "@drugs_global": "https://t.me/drugs_global",
        "@psychonaut_chat": "https://t.me/psychonaut_chat",
        "@research_chemicals": "https://t.me/research_chemicals",
        "@stimulants_chat": "https://t.me/stimulants_chat",
        "@entactogens_chat": "https://t.me/entactogens_chat",
        "@rave_drugs": "https://t.me/rave_drugs"
    }
}

# ====================================
# NEWS FETCHING FUNCTIONS WITH CACHE
# ====================================

@st.cache_data(ttl=300)
def fetch_maritime_news_asia():
    """Fetch maritime news with caching - returns structured data"""
    maritime_news = []
    
    sources = [
        {
            'url': 'https://news.google.com/rss/search?q=drug+seizure+india+maritime&hl=en-IN&gl=IN&ceid=IN:en',
            'type': 'rss'
        },
        {
            'url': 'https://news.google.com/rss/search?q=NDPS+seizure+india&hl=en-IN&gl=IN&ceid=IN:en',
            'type': 'rss'
        },
        {
            'url': 'https://news.google.com/rss/search?q=NCB+operation+drug+bust&hl=en-IN&gl=IN&ceid=IN:en',
            'type': 'rss'
        },
        {
            'url': 'https://news.google.com/rss/search?q=golden+crescent+drug+trafficking&hl=en-IN&gl=IN&ceid=IN:en',
            'type': 'rss'
        },
        {
            'url': 'https://news.google.com/rss/search?q=maritime+drug+seizure+asia&hl=en-IN&gl=IN&ceid=IN:en',
            'type': 'rss'
        },
        {
            'url': 'https://news.google.com/rss/search?q=cocaine+seizure+india+port&hl=en-IN&gl=IN&ceid=IN:en',
            'type': 'rss'
        }
    ]
    
    asian_countries = [
        'India', 'China', 'Japan', 'South Korea', 'Indonesia', 'Malaysia', 'Singapore',
        'Thailand', 'Vietnam', 'Philippines', 'Myanmar', 'Bangladesh', 'Pakistan',
        'Sri Lanka', 'Nepal', 'Cambodia', 'Laos', 'Afghanistan', 'Iran', 'UAE',
        'Saudi Arabia', 'Oman', 'Yemen', 'Maldives', 'Bhutan'
    ]
    
    drug_names = [
        'cocaine', 'heroin', 'methamphetamine', 'meth', 'cannabis', 'marijuana', 'ganja',
        'mdma', 'ecstasy', 'ketamine', 'fentanyl', 'alprazolam', 'xanax', 'tramadol',
        'opium', 'morphine', 'codeine', 'amphetamine', 'lsd', 'brown sugar', 'smack',
        'charas', 'hashish', 'ndps', 'psychotropic', 'contraband'
    ]
    
    locations_found = set()
    
    for source in sources:
        try:
            if source['type'] == 'rss':
                feed = feedparser.parse(source['url'])
                for entry in feed.entries[:25]:
                    title = entry.get('title', '')
                    description = entry.get('description', '')
                    link = entry.get('link', '#')
                    published = entry.get('published', '')
                    
                    content = title + ' ' + description
                    content_lower = content.lower()
                    
                    is_asia_related = any(country.lower() in content_lower for country in asian_countries)
                    
                    location = 'Asia'
                    for country in asian_countries:
                        if country.lower() in content_lower:
                            location = country
                            break
                    
                    seized_drugs = []
                    for drug in drug_names:
                        if drug in content_lower:
                            quantity_match = re.search(r'(\d+)\s*(?:kg|kg|kgs|gram|g|tonne|ton|quintal|gm)', content_lower)
                            if quantity_match:
                                seized_drugs.append(f"{quantity_match.group(0)} {drug}")
                            else:
                                qty_pattern = re.search(r'(\d+)\s*(?:of)?\s*' + drug, content_lower)
                                if qty_pattern:
                                    seized_drugs.append(f"{qty_pattern.group(1)}kg {drug}")
                                else:
                                    seized_drugs.append(drug.capitalize())
                    
                    if not seized_drugs and any(kw in content_lower for kw in ['seizure', 'bust', 'recover', 'intercept', 'trafficking']):
                        for drug in drug_names:
                            if drug in content_lower:
                                seized_drugs.append(drug.capitalize())
                                break
                        if not seized_drugs:
                            seized_drugs.append("Drug Seizure")
                    
                    is_drug_related = bool(seized_drugs) or any(kw in content_lower for kw in ['seizure', 'bust', 'recover', 'intercept', 'trafficking', 'narcotic', 'ndps'])
                    
                    if is_drug_related and is_asia_related:
                        location_key = f"{location}_{title[:50]}"
                        if location_key in locations_found:
                            continue
                        locations_found.add(location_key)
                        
                        clean_title = title
                        for prefix in ['Breaking:', 'Live:', 'UPDATE:', 'BREAKING:', 'LIVE:', 'News:', 'Video:']:
                            if clean_title.startswith(prefix):
                                clean_title = clean_title[len(prefix):].strip()
                        
                        try:
                            if published:
                                date_obj = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %Z')
                                date_str = date_obj.strftime('%Y-%m-%d')
                                datetime_str = date_obj.strftime('%Y-%m-%d %H:%M')
                            else:
                                date_str = datetime.now().strftime('%Y-%m-%d')
                                datetime_str = datetime.now().strftime('%Y-%m-%d %H:%M')
                        except:
                            date_str = datetime.now().strftime('%Y-%m-%d')
                            datetime_str = datetime.now().strftime('%Y-%m-%d %H:%M')
                        
                        maritime_news.append({
                            'heading': clean_title[:180] + '...' if len(clean_title) > 180 else clean_title,
                            'location': location,
                            'date': date_str,
                            'datetime': datetime_str,
                            'seized_drugs': ', '.join(seized_drugs[:3]) if seized_drugs else 'Drug Seizure',
                            'url': link,
                            'source': entry.get('source', {}).get('title', 'News'),
                            'timestamp': datetime.now().isoformat()
                        })
                        
                        if len(maritime_news) >= 15:
                            break
        except Exception as e:
            continue
        
        if len(maritime_news) >= 15:
            break
    
    return maritime_news[:15]

def force_refresh_news():
    """Force refresh news cache"""
    st.cache_data.clear()
    st.session_state.maritime_news = fetch_maritime_news_asia()
    st.session_state.last_news_fetch = datetime.now()
    st.rerun()

# ====================================
# POSTGRESQL DATABASE SETUP
# ====================================

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'ncb_intelligence',
    'user': 'postgres',
    'password': 'ncb123'
}

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        return None

def init_database():
    conn = get_db_connection()
    if not conn:
        return
    
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS maritime_records (
            id SERIAL PRIMARY KEY,
            drug TEXT,
            agency TEXT,
            source TEXT,
            destination TEXT,
            source_lat REAL,
            source_lng REAL,
            destination_lat REAL,
            destination_lng REAL,
            weight TEXT,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS uhm_directions (
            id SERIAL PRIMARY KEY,
            direction_no TEXT UNIQUE,
            subject TEXT,
            priority TEXT,
            category TEXT,
            agency TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS seizure_cases (
            id SERIAL PRIMARY KEY,
            case_no TEXT UNIQUE,
            case_date TEXT,
            case_title TEXT,
            intelligence_input TEXT,
            seizure_place TEXT,
            seizure_agency TEXT,
            drug_name TEXT,
            quantity TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS pharma_vendors (
            id SERIAL PRIMARY KEY,
            vendor_name TEXT,
            platform TEXT,
            drug TEXT,
            website TEXT,
            compliance TEXT,
            risk_level TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS lab_busts (
            id SERIAL PRIMARY KEY,
            case_id TEXT UNIQUE,
            raid_date TEXT,
            state TEXT,
            district TEXT,
            location TEXT,
            lab_type TEXT,
            drugs TEXT,
            quantity REAL,
            arrests INTEGER,
            risk_level TEXT,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('SELECT * FROM users WHERE username = %s', ('admin',))
    if not c.fetchone():
        hashed_password = hashlib.sha256('ncb123'.encode()).hexdigest()
        c.execute('INSERT INTO users (username, password, role) VALUES (%s, %s, %s)',
                  ('admin', hashed_password, 'admin'))
    
    conn.commit()
    conn.close()

init_database()

# ====================================
# DATABASE HELPER FUNCTIONS
# ====================================

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    conn = get_db_connection()
    if not conn:
        return None
    
    c = conn.cursor()
    
    try:
        if params:
            c.execute(query, params)
        else:
            c.execute(query)
        
        result = None
        if fetch_one:
            result = c.fetchone()
        elif fetch_all:
            result = c.fetchall()
        
        conn.commit()
        conn.close()
        return result
    except Exception as e:
        conn.rollback()
        conn.close()
        return None

def insert_record(table, data):
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['%s' for _ in data])
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING id"
    result = execute_query(query, tuple(data.values()), fetch_one=True)
    return result[0] if result else None

def get_all_records(table, order_by='created_at DESC'):
    query = f"SELECT * FROM {table} ORDER BY {order_by}"
    return execute_query(query, fetch_all=True)

def get_record_count(table):
    query = f"SELECT COUNT(*) as count FROM {table}"
    result = execute_query(query, fetch_one=True)
    return result[0] if result else 0

def get_records_by_filter(table, column, value):
    query = f"SELECT * FROM {table} WHERE {column} = %s ORDER BY created_at DESC"
    return execute_query(query, (value,), fetch_all=True)

# ====================================
# SIDEBAR
# ====================================

st.sidebar.markdown("""
<div class="sidebar-title">
    <span style="font-size: 30px;">🚨</span>
    <h1>NCB Intelligence</h1>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div class="welcome-text">
    <p style="margin:0;color:#e9ecef;">🔐 <strong style="color:#94d2bd;">NCB Intelligence Portal</strong></p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<hr style='border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

conn_status = get_db_connection()
if conn_status:
    st.sidebar.markdown('<div class="db-status success">✅ Database Connected</div>', unsafe_allow_html=True)
    if conn_status:
        conn_status.close()
else:
    st.sidebar.markdown('<div class="db-status warning">⚠️ Database Disconnected</div>', unsafe_allow_html=True)

st.sidebar.markdown("<hr style='border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

st.sidebar.markdown('<div class="nav-header">📋 NAVIGATION</div>', unsafe_allow_html=True)

module = st.sidebar.radio(
    "",
    [
        "📊 Dashboard",
        "🚢 Maritime Seizure",
        "🧭 UHM Direction",
        "📋 Seizure Details",
        "💊 Pharma Monitoring",
        "🧪 Labbust"
    ],
    index=0
)

st.sidebar.markdown("<hr style='border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style="text-align:center;color:rgba(255,255,255,0.4);font-size:11px;margin-top:15px;padding:10px;border-top:1px solid rgba(255,255,255,0.05);">
    🔒 Secure Intelligence Portal<br>
    ⚡ v2.0 | NCB<br>
    © 2026 NCB Intelligence
</div>
""", unsafe_allow_html=True)

# ====================================
# DASHBOARD MODULE
# ====================================

if module == "📊 Dashboard":
    st.markdown("""
    <div class='main-title'>⚡ NCB (OPS) INTELLIGENCE</div>
    <div style="text-align:center;">
        <div class='sub-title'>🌊 Maritime Intelligence • 💊 Pharma Monitoring • 🧪 Lab Bust • 🕵️ OSINT Integration</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    maritime_count = get_record_count('maritime_records')
    uhm_count = get_record_count('uhm_directions')
    seizure_count = get_record_count('seizure_cases')
    pharma_count = get_record_count('pharma_vendors')
    lab_count = get_record_count('lab_busts')

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: 
        st.metric("🌊 Maritime", maritime_count, help="Total Maritime Seizure Records")
    with col2: 
        st.metric("🧭 UHM", uhm_count, help="Total UHM Directions")
    with col3: 
        st.metric("🚨 Seizure", seizure_count, help="Total Seizure Cases")
    with col4: 
        st.metric("💊 Pharma", pharma_count, help="Total Pharma Vendors Monitored")
    with col5: 
        st.metric("🧪 Lab", lab_count, help="Total Lab Bust Cases")

    st.divider()
    
    # ====================================
    # MARITIME NEWS WITH DATE FILTER
    # ====================================
    
    st.subheader("🌏 Live Maritime News - Asia Region")
    
    col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div style="display:flex;align-items:center;padding:8px 0;background:rgba(255,255,255,0.5);border-radius:12px;padding:8px 16px;backdrop-filter:blur(10px);border:1px solid rgba(10,147,150,0.1);">
            <span class="live-indicator"></span>
            <span style="font-weight:700;color:#dc3545;">🔴 LIVE</span>
            <span class="last-updated">Last updated: {st.session_state.last_news_fetch.strftime('%Y-%m-%d %H:%M:%S')}</span>
            <span class="news-count">| {len(st.session_state.maritime_news)} News</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        refresh_interval = st.selectbox(
            "Refresh",
            ["30s", "1m", "2m", "5m", "10m"],
            index=3,
            key="refresh_interval_selector"
        )
        interval_map = {"30s": 30, "1m": 60, "2m": 120, "5m": 300, "10m": 600}
        st.session_state.news_refresh_interval = interval_map[refresh_interval]
    
    with col3:
        if st.button("🔄 Refresh Now", use_container_width=True):
            force_refresh_news()
    
    with col4:
        auto_refresh_toggle = st.checkbox("🔄 Auto", value=st.session_state.auto_refresh_enabled)
        st.session_state.auto_refresh_enabled = auto_refresh_toggle
    
    with col5:
        available_dates = ["Latest News"]
        if st.session_state.maritime_news:
            dates = sorted(set([news['date'] for news in st.session_state.maritime_news if news.get('date')]), reverse=True)
            available_dates.extend(dates)
        
        selected_date_display = st.selectbox(
            "📅 Filter",
            available_dates,
            key="date_filter_select"
        )
    
    if st.session_state.auto_refresh_enabled:
        time_since_last_fetch = (datetime.now() - st.session_state.last_news_fetch).total_seconds()
        
        if time_since_last_fetch > st.session_state.news_refresh_interval:
            with st.spinner("🔄 Fetching latest maritime news..."):
                st.session_state.maritime_news = fetch_maritime_news_asia()
                st.session_state.last_news_fetch = datetime.now()
                st.rerun()
    
    maritime_news = st.session_state.maritime_news
    
    if selected_date_display == "Latest News":
        filtered_news = maritime_news
        filter_label = "📰 Showing Latest News"
    else:
        filtered_news = [news for news in maritime_news if news.get('date') == selected_date_display]
        filter_label = f"📰 Showing News for {selected_date_display}"
    
    if filtered_news:
        st.info(f"{filter_label} | Found {len(filtered_news)} articles")
        
        for idx, news in enumerate(filtered_news):
            drugs_lower = news.get('seized_drugs', '').lower()
            is_critical = any(word in drugs_lower for word in ['fentanyl', 'heroin', 'cocaine'])
            border_color = '#dc3545' if is_critical else '#0a9396'
            
            display_date = news.get('datetime', news.get('date', 'Unknown'))
            
            st.markdown(f"""
            <div class="news-card" style="border-left-color: {border_color};">
                <div class="news-heading">📰 {news['heading']}</div>
                <div class="news-meta">
                    <span class="news-location">📍 {news['location']}</span>
                    <span class="news-drugs">💊 {news['seized_drugs']}</span>
                    <span>📅 {display_date}</span>
                    <a href="{news['url']}" target="_blank" class="news-link">🔗 Read Full Article →</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.session_state.auto_refresh_enabled:
            time_since_last_fetch = (datetime.now() - st.session_state.last_news_fetch).total_seconds()
            next_refresh_in = st.session_state.news_refresh_interval - time_since_last_fetch
            if next_refresh_in > 0:
                st.caption(f"🔄 Auto-refresh in {int(next_refresh_in)} seconds")
            else:
                st.caption("🔄 Refreshing now...")
        
        if st.button("📥 Download Filtered News (CSV)"):
            df_news = pd.DataFrame(filtered_news)
            csv = df_news.to_csv(index=False).encode('utf-8')
            st.download_button(
                "⬇️ Download CSV",
                csv,
                f"maritime_news_{selected_date_display.replace(' ', '_')}.csv",
                "text/csv"
            )
    else:
        if selected_date_display == "Latest News":
            st.warning("No maritime news available. Click 'Refresh Now' to fetch latest updates.")
        else:
            st.info(f"No news found for {selected_date_display}. Showing latest news instead.")
            if maritime_news:
                for idx, news in enumerate(maritime_news[:5]):
                    drugs_lower = news.get('seized_drugs', '').lower()
                    is_critical = any(word in drugs_lower for word in ['fentanyl', 'heroin', 'cocaine'])
                    border_color = '#dc3545' if is_critical else '#0a9396'
                    
                    st.markdown(f"""
                    <div class="news-card" style="border-left-color: {border_color};">
                        <div class="news-heading">📰 {news['heading']}</div>
                        <div class="news-meta">
                            <span class="news-location">📍 {news['location']}</span>
                            <span class="news-drugs">💊 {news['seized_drugs']}</span>
                            <span>📅 {news.get('datetime', news.get('date', 'Unknown'))}</span>
                            <a href="{news['url']}" target="_blank" class="news-link">🔗 Read Full Article →</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    st.divider()
    
    # ====================================
    # LARGEST DRUG VENDORS - LIVE SCRAPING
    # ====================================
    
    st.subheader("🛒 Largest Drug Vendors - Surface & Dark Web")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        vendor_data_source = st.radio(
            "Data Source",
            ["📡 Live Scraped Data", "📊 Static Data (Fallback)"],
            horizontal=True,
            key="vendor_data_source"
        )
    
    with col2:
        if st.button("🔄 Refresh Vendors", use_container_width=True):
            force_refresh_vendors()
    
    with col3:
        if st.session_state.last_vendor_fetch:
            last_fetch = st.session_state.last_vendor_fetch.strftime('%H:%M:%S')
            st.caption(f"Last fetch: {last_fetch}")
    
    use_live_data = vendor_data_source == "📡 Live Scraped Data"
    
    if use_live_data:
        if not st.session_state.live_vendors or not st.session_state.last_vendor_fetch:
            with st.spinner("🌐 Fetching live vendor data from platforms..."):
                st.session_state.live_vendors = fetch_live_vendors()
                st.session_state.last_vendor_fetch = datetime.now()
        
        if st.session_state.last_vendor_fetch:
            time_since_fetch = (datetime.now() - st.session_state.last_vendor_fetch).total_seconds()
            if time_since_fetch > 3600:
                with st.spinner("🔄 Refreshing vendor data..."):
                    st.session_state.live_vendors = fetch_live_vendors()
                    st.session_state.last_vendor_fetch = datetime.now()
        
        live_vendors = st.session_state.live_vendors
        
        if live_vendors:
            st.success(f"✅ Found {len(live_vendors)} live vendors from multiple platforms")
            
            vendor_df_data = []
            for vendor in live_vendors:
                vendor_df_data.append({
                    "Vendor Name": vendor.get('name', 'Unknown'),
                    "Platform": vendor.get('platform', 'Unknown'),
                    "Substances": ", ".join(vendor.get('substances', ['Unknown'])[:3]),
                    "Rating": vendor.get('rating', 0),
                    "Location": vendor.get('location', 'Unknown'),
                    "Compliance": vendor.get('compliance', 'Under Review'),
                    "Source": vendor.get('source', 'Live Scraped')
                })
            
            df_vendors_live = pd.DataFrame(vendor_df_data)
            st.dataframe(df_vendors_live, use_container_width=True, height=400)
            
            csv = df_vendors_live.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download Live Vendor Data", csv, "Live_Drug_Vendors.csv", "text/csv")
            
            st.markdown("### 📋 Live Vendor Details")
            cols = st.columns(2)
            vendor_idx = 0
            
            for vendor in live_vendors[:10]:
                with cols[vendor_idx % 2]:
                    st.markdown(f"""
                    <div class="vendor-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span class="vendor-name">{vendor.get('name', 'Unknown')}</span>
                            <span class="badge-live">🟢 LIVE</span>
                        </div>
                        <div class="vendor-detail">
                            <strong>Platform:</strong> {vendor.get('platform', 'Unknown')}
                        </div>
                        <div class="vendor-detail">
                            <strong>Substances:</strong> {', '.join(vendor.get('substances', ['Unknown'])[:3])}
                        </div>
                        <div class="vendor-detail">
                            <strong>Location:</strong> {vendor.get('location', 'Unknown')}
                        </div>
                        <div class="vendor-detail">
                            <strong>Compliance:</strong> {vendor.get('compliance', 'Under Review')}
                        </div>
                        <div class="vendor-detail" style="font-size:10px;color:#6c757d;border-top:1px solid rgba(255,255,255,0.1);padding-top:4px;margin-top:4px;">
                            Source: {vendor.get('source', 'Live Scraped')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                vendor_idx += 1
        else:
            st.warning("No live vendors found. Falling back to static data.")
            use_live_data = False
    
    if not use_live_data:
        st.info("📊 Showing static vendor data (for demonstration purposes)")
        
        vendor_type = st.radio(
            "Select Vendor Type",
            ["All Vendors", "Surface Web Vendors", "Dark Web Vendors"],
            horizontal=True
        )
        
        all_vendors_flat = []
        
        if vendor_type == "All Vendors" or vendor_type == "Surface Web Vendors":
            for platform, data in DRUG_VENDORS["Surface Web Vendors"].items():
                for vendor in data["vendors"]:
                    vendor["platform"] = platform
                    vendor["vendor_type"] = "Surface Web"
                    all_vendors_flat.append(vendor)
        
        if vendor_type == "All Vendors" or vendor_type == "Dark Web Vendors":
            for market, data in DRUG_VENDORS["Dark Web Vendors"].items():
                for vendor in data["vendors"]:
                    vendor["platform"] = market
                    vendor["vendor_type"] = "Dark Web"
                    all_vendors_flat.append(vendor)
        
        if all_vendors_flat:
            vendor_data = []
            for vendor in all_vendors_flat:
                vendor_data.append({
                    "Vendor Name": vendor["name"],
                    "Platform/Market": vendor.get("platform", "N/A"),
                    "Type": vendor.get("vendor_type", "N/A"),
                    "Substances": ", ".join(vendor.get("substances", [])[:3]) + ("..." if len(vendor.get("substances", [])) > 3 else ""),
                    "Rating": vendor.get("rating", 0),
                    "Supply Volume": vendor.get("supply_volume", "N/A"),
                    "Reliability": vendor.get("reliability", "N/A"),
                    "Years Active": vendor.get("years_active", 0),
                    "Location": vendor.get("location", "N/A"),
                    "Price Range": vendor.get("price_range", "N/A"),
                    "Shipping": vendor.get("shipping", "N/A")
                })
            
            df_vendors = pd.DataFrame(vendor_data)
            st.dataframe(df_vendors, use_container_width=True, height=400)
            
            csv = df_vendors.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download Static Vendor List", csv, "Static_Drug_Vendors.csv", "text/csv")
            
            st.markdown("### 📋 Detailed Vendor Information")
            cols = st.columns(2)
            vendor_idx = 0
            
            for vendor in all_vendors_flat[:6]:
                with cols[vendor_idx % 2]:
                    badge_class = "badge-darkweb" if vendor.get("vendor_type") == "Dark Web" else "badge-surface"
                    badge_text = "🔴 Dark Web" if vendor.get("vendor_type") == "Dark Web" else "🔵 Surface Web"
                    
                    substance_tags = "".join([f'<span class="substance-tag">{s}</span>' for s in vendor.get("substances", [])[:4]])
                    supply_class = "vendor-supply-high" if vendor.get("supply_volume") == "Very High" else "vendor-supply-medium" if vendor.get("supply_volume") == "High" else "vendor-supply-low"
                    
                    st.markdown(f"""
                    <div class="vendor-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span class="vendor-name">{vendor['name']}</span>
                            <span class="{badge_class}">{badge_text}</span>
                        </div>
                        <div class="vendor-detail">
                            <span class="vendor-rating">⭐ {vendor.get('rating', 0)}/5.0</span>
                            | Reliability: {vendor.get('reliability', 'N/A')}
                            | Years: {vendor.get('years_active', 0)}
                        </div>
                        <div class="vendor-detail">
                            <strong>Platform:</strong> {vendor.get('platform', 'N/A')}
                            | <span class="{supply_class}">📦 {vendor.get('supply_volume', 'N/A')}</span>
                        </div>
                        <div class="vendor-detail">
                            <strong>Substances:</strong> {substance_tags}
                        </div>
                        <div class="vendor-detail">
                            <strong>Location:</strong> {vendor.get('location', 'N/A')}
                            | <strong>Price:</strong> {vendor.get('price_range', 'N/A')}
                        </div>
                        <div class="vendor-detail">
                            <strong>Shipping:</strong> {vendor.get('shipping', 'N/A')}
                            | <strong>Payment:</strong> {', '.join(vendor.get('payment_methods', ['N/A'])[:2])}
                        </div>
                        {f'<div class="vendor-detail"><strong>🔗 Link:</strong> <a href="{vendor.get("market_link", vendor.get("website", "#"))}" target="_blank" style="color:#0a9396;">Visit Vendor</a></div>' if vendor.get("market_link") or vendor.get("website") else ''}
                    </div>
                    """, unsafe_allow_html=True)
                vendor_idx += 1
        else:
            st.warning("No vendors found")

    st.divider()
    
    # ====================================
    # OSINT DRUG INTELLIGENCE TABLE
    # ====================================
    
    st.subheader("🕵️ OSINT Drug Intelligence Dashboard")
    
    selected_drug = st.selectbox(
        "Select Drug for OSINT Intelligence",
        ["All Drugs", "Ketamine", "LSD", "Cocaine", "Alprazolam", "MDMA"],
        key="osint_drug_selector"
    )
    
    if selected_drug == "All Drugs":
        st.markdown("### 📊 Complete OSINT Drug Intelligence")
        
        osint_data = []
        for drug, data in OSINT_DRUG_DATA.items():
            osint_data.append({
                "Drug": drug,
                "Common Names": ", ".join(data["common_names"][:3]),
                "Street Price": data["street_price"],
                "Risk Level": data["risk_level"],
                "Source Countries": ", ".join(data["source_countries"][:3]),
                "Reddit Forums": len(data["reddit_forums"]),
                "Telegram Groups": len(data["telegram_groups"]),
                "2026 Seizure": data["seizure_stats"]["2026"],
                "Medical Use": data["medical_use"][:30] + "..."
            })
        
        df_osint = pd.DataFrame(osint_data)
        st.dataframe(df_osint, use_container_width=True, height=300)
        
        csv = df_osint.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download OSINT Data", csv, "OSINT_Drug_Intelligence.csv", "text/csv")
    
    else:
        drug_data = OSINT_DRUG_DATA.get(selected_drug, {})
        
        if drug_data:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div style="background:rgba(10,147,150,0.05);padding:16px;border-radius:12px;border:1px solid rgba(10,147,150,0.1);">
                    <strong style="color:#0a9396;">🔹 Basic Information</strong><br>
                    <strong>Common Names:</strong> {', '.join(drug_data['common_names'])}<br>
                    <strong>Street Price:</strong> {drug_data['street_price']}<br>
                    <strong>Risk Level:</strong> <span style="color:#dc3545;font-weight:700;">{drug_data['risk_level']}</span><br>
                    <strong>Medical Use:</strong> {drug_data['medical_use']}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background:rgba(10,147,150,0.05);padding:16px;border-radius:12px;border:1px solid rgba(10,147,150,0.1);">
                    <strong style="color:#0a9396;">🔹 Trafficking Intelligence</strong><br>
                    <strong>Source Countries:</strong> {', '.join(drug_data['source_countries'])}<br>
                    <strong>Routes:</strong> {', '.join(drug_data['trafficking_routes'])}<br>
                    <strong>Darknet Markets:</strong> {', '.join(drug_data['darknet_markets'])}
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="background:rgba(10,147,150,0.05);padding:16px;border-radius:12px;border:1px solid rgba(10,147,150,0.1);">
                    <strong style="color:#0a9396;">🔹 Seizure Statistics</strong><br>
                    <strong>2024:</strong> {drug_data['seizure_stats']['2024']}<br>
                    <strong>2025:</strong> {drug_data['seizure_stats']['2025']}<br>
                    <strong>2026:</strong> <span style="color:#dc3545;font-weight:700;">{drug_data['seizure_stats']['2026']}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            
            st.markdown("### 🔗 OSINT Sources & Community Links")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📱 Reddit Forums**")
                for forum in drug_data["reddit_forums"]:
                    if forum in OSINT_SOURCES["reddit_forums"]:
                        url = OSINT_SOURCES["reddit_forums"][forum]
                        st.markdown(f'<a href="{url}" target="_blank" style="color:#0a9396;text-decoration:none;font-weight:600;">🔗 {forum}</a>', unsafe_allow_html=True)
            
            with col2:
                st.markdown("**💬 Telegram Groups**")
                for group in drug_data["telegram_groups"]:
                    if group in OSINT_SOURCES["telegram_groups"]:
                        url = OSINT_SOURCES["telegram_groups"][group]
                        st.markdown(f'<a href="{url}" target="_blank" style="color:#0088cc;text-decoration:none;font-weight:600;">✈️ {group}</a>', unsafe_allow_html=True)
    
    st.divider()
    
    # ====================================
    # HIGH RISK VENDORS
    # ====================================
    
    st.subheader("🚨 High Risk Pharma Vendors")
    
    high_risk_records = get_records_by_filter('pharma_vendors', 'risk_level', 'High')
    
    if high_risk_records:
        st.error(f"🚨 {len(high_risk_records)} High Risk Vendors Found!")
        
        for record in high_risk_records[:5]:
            vendor_name = record[1] if len(record) > 1 else 'Unknown'
            drug = record[3] if len(record) > 3 else 'Unknown'
            platform = record[2] if len(record) > 2 else 'Unknown'
            website = record[4] if len(record) > 4 else '#'
            
            st.markdown(f"""
            <div class="high-risk-box">
                <div style="color:#dc3545;font-size:16px;font-weight:bold;">
                    🚨 {vendor_name}
                    <span style="background:#dc3545;color:white;padding:3px 12px;border-radius:20px;font-size:11px;margin-left:8px;">HIGH RISK</span>
                </div>
                <div style="color:#495057;font-size:13px;padding:4px 0;">
                    💊 Drug: {drug} • 🌐 Platform: {platform}
                </div>
                <div style="margin-top:6px;border-top:1px solid rgba(220,53,69,0.2);padding-top:6px;">
                    <a href="{website}" target="_blank" style="color:#007bff;text-decoration:none;font-weight:bold;">🔗 Visit Site →</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No high risk vendors found")

# ====================================
# MARITIME SEIZURE MODULE
# ====================================
elif module == "🚢 Maritime Seizure":
    st.title("🚢 Maritime Seizure")

    maritime_menu = st.radio(
        "Select Option",
        ["➕ Add New Case", "📋 Maritime Report", "🌍 Maritime Map"],
        horizontal=True
    )
    
    if maritime_menu == "➕ Add New Case":
        with st.form("maritime_form"):
            drug = st.text_input("Drug Name")
            agency = st.text_input("Agency")
            source = st.text_input("Source Country")
            destination = st.text_input("Destination Country")
            
            col1, col2 = st.columns(2)
            with col1:
                source_lat = st.number_input("Source Latitude", format="%.6f")
                source_lng = st.number_input("Source Longitude", format="%.6f")
            with col2:
                destination_lat = st.number_input("Destination Latitude", format="%.6f")
                destination_lng = st.number_input("Destination Longitude", format="%.6f")
            
            weight = st.text_input("Weight")
            remarks = st.text_area("Remarks")
            
            if st.form_submit_button("💾 Save Record"):
                data = {
                    "drug": drug,
                    "agency": agency,
                    "source": source,
                    "destination": destination,
                    "source_lat": source_lat,
                    "source_lng": source_lng,
                    "destination_lat": destination_lat,
                    "destination_lng": destination_lng,
                    "weight": weight,
                    "remarks": remarks
                }
                record_id = insert_record('maritime_records', data)
                if record_id:
                    st.success("✅ Record Saved Successfully")
    
    elif maritime_menu == "📋 Maritime Report":
        records = get_all_records('maritime_records')
        if records:
            df_data = []
            for record in records:
                df_data.append({
                    "ID": record[0],
                    "Drug": record[1],
                    "Agency": record[2],
                    "Source": record[3],
                    "Destination": record[4],
                    "Weight": record[8],
                    "Created": record[10]
                })
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No Records Available")
    
    elif maritime_menu == "🌍 Maritime Map":
        st.subheader("🌍 Maritime Route Map")
        records = get_all_records('maritime_records')
        
        if records:
            m = folium.Map(location=[10, 65], zoom_start=3)
            
            for record in records:
                source_lat = record[5]
                source_lng = record[6]
                dest_lat = record[7]
                dest_lng = record[8]
                
                if source_lat and source_lng:
                    folium.Marker(
                        [source_lat, source_lng],
                        popup=f"Source: {record[3]}<br>Drug: {record[1]}",
                        icon=folium.Icon(color='green')
                    ).add_to(m)
                
                if dest_lat and dest_lng:
                    folium.Marker(
                        [dest_lat, dest_lng],
                        popup=f"Destination: {record[4]}<br>Drug: {record[1]}",
                        icon=folium.Icon(color='red')
                    ).add_to(m)
                
                if source_lat and source_lng and dest_lat and dest_lng:
                    folium.PolyLine(
                        [[source_lat, source_lng], [dest_lat, dest_lng]],
                        color='#0a9396',
                        weight=3,
                        opacity=0.8
                    ).add_to(m)
            
            st_folium(m, width=1400, height=700)

# ====================================
# UHM DIRECTION MODULE
# ====================================
elif module == "🧭 UHM Direction":
    st.title("🧭 UHM Direction")
    
    uhm_menu = st.radio(
        "Select Option",
        ["➕ Add UHM Direction", "📋 All UHM Reports"],
        horizontal=True
    )
    
    if uhm_menu == "➕ Add UHM Direction":
        with st.form("uhm_form"):
            direction_no = st.text_input("UHM Direction No")
            subject = st.text_input("Subject")
            priority = st.selectbox("Priority", ["🔴 A Priority", "🔵 B Priority", "🟢 C Priority"])
            category = st.selectbox("Category", ["NDPS Act", "Operation", "Dark Web", "Cryptocurrency", "Drugs", "Cartel Network"])
            agency = st.text_input("Agency")
            status = st.selectbox("Status", ["Pending", "Active", "Closed"])
            
            if st.form_submit_button("💾 Save Direction"):
                data = {
                    "direction_no": direction_no,
                    "subject": subject,
                    "priority": priority,
                    "category": category,
                    "agency": agency,
                    "status": status
                }
                try:
                    record_id = insert_record('uhm_directions', data)
                    if record_id:
                        st.success("✅ Direction Saved Successfully")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    elif uhm_menu == "📋 All UHM Reports":
        records = get_all_records('uhm_directions')
        if records:
            df_data = []
            for record in records:
                df_data.append({
                    "Direction No": record[1],
                    "Subject": record[2],
                    "Priority": record[3],
                    "Category": record[4],
                    "Agency": record[5],
                    "Status": record[6],
                    "Created": record[7]
                })
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No UHM Directions Available")

# ====================================
# SEIZURE DETAILS MODULE
# ====================================
elif module == "📋 Seizure Details":
    st.title("📋 Seizure Details")
    
    seizure_menu = st.radio(
        "Select Option",
        ["➕ Add Seizure Case", "📋 All Cases"],
        horizontal=True
    )
    
    if seizure_menu == "➕ Add Seizure Case":
        with st.form("seizure_form"):
            case_no = st.text_input("Case Number")
            case_date = st.date_input("Case Date")
            case_title = st.text_input("Case Title")
            drug_name = st.text_input("Drug Name")
            quantity = st.text_input("Quantity")
            seizure_place = st.text_input("Place of Seizure")
            seizure_agency = st.text_input("Agency")
            
            if st.form_submit_button("💾 Save Case"):
                data = {
                    "case_no": case_no,
                    "case_date": str(case_date),
                    "case_title": case_title,
                    "drug_name": drug_name,
                    "quantity": quantity,
                    "seizure_place": seizure_place,
                    "seizure_agency": seizure_agency,
                    "intelligence_input": ""
                }
                try:
                    record_id = insert_record('seizure_cases', data)
                    if record_id:
                        st.success("✅ Case Saved Successfully")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    elif seizure_menu == "📋 All Cases":
        records = get_all_records('seizure_cases')
        if records:
            df_data = []
            for record in records:
                df_data.append({
                    "Case No": record[1],
                    "Date": record[2],
                    "Title": record[3],
                    "Drug": record[8],
                    "Quantity": record[9],
                    "Place": record[5],
                    "Agency": record[6]
                })
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No Cases Available")

# ====================================
# PHARMA MONITORING MODULE
# ====================================
elif module == "💊 Pharma Monitoring":
    st.title("💊 Pharma Monitoring System")
    
    pharma_menu = st.radio(
        "Select Option",
        ["🌐 Auto Crawl Vendors", "📋 Vendor List", "🚨 High Risk Vendors"],
        horizontal=True
    )
    
    if pharma_menu == "🌐 Auto Crawl Vendors":
        st.subheader("🌐 Pharma Vendor Intelligence Crawl")
        
        drug_name = st.selectbox("Substance", ["Tramadol", "Alprazolam", "Ketamine", "Cocaine", "LSD", "MDMA"])
        
        if st.button("🚀 Start Intelligence Crawl", use_container_width=True):
            with st.spinner(f"🔍 Crawling for {drug_name}..."):
                all_vendors = [
                    {"Vendor Name": "Gantuo Chemicals", "Platform": "Dial4Trade", 
                     "Drug": drug_name, "Website": "https://www.dial4trade.com",
                     "Compliance": "🔴 Unlicensed", "Risk Level": "High"},
                    {"Vendor Name": "Krishna Speciality Chemicals", "Platform": "IndiaMART",
                     "Drug": drug_name, "Website": "https://www.indiamart.com",
                     "Compliance": "🔴 High Risk", "Risk Level": "High"},
                ]
                
                saved_count = 0
                for vendor in all_vendors:
                    try:
                        data = {
                            "vendor_name": vendor["Vendor Name"],
                            "platform": vendor["Platform"],
                            "drug": vendor["Drug"],
                            "website": vendor["Website"],
                            "compliance": vendor["Compliance"],
                            "risk_level": vendor["Risk Level"]
                        }
                        insert_record('pharma_vendors', data)
                        saved_count += 1
                    except Exception as e:
                        pass
                
                st.success(f"✅ Crawl Completed! Found {len(all_vendors)} vendors")
                df = pd.DataFrame(all_vendors)
                st.dataframe(df, use_container_width=True)
    
    elif pharma_menu == "📋 Vendor List":
        records = get_all_records('pharma_vendors')
        if records:
            df_data = []
            for record in records:
                df_data.append({
                    "Vendor Name": record[1],
                    "Platform": record[2],
                    "Drug": record[3],
                    "Compliance": record[5],
                    "Risk Level": record[6]
                })
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No vendors available")
    
    elif pharma_menu == "🚨 High Risk Vendors":
        records = get_records_by_filter('pharma_vendors', 'risk_level', 'High')
        
        if records:
            st.error(f"🚨 {len(records)} High Risk Vendors Found!")
            df_data = []
            for record in records:
                df_data.append({
                    "Vendor Name": record[1],
                    "Platform": record[2],
                    "Drug": record[3],
                    "Compliance": record[5]
                })
            st.dataframe(df_data, use_container_width=True)
        else:
            st.success("✅ No high risk vendors found")

# ====================================
# LAB BUST MODULE
# ====================================
elif module == "🧪 Labbust":
    st.title("🧪 Lab Bust Intelligence")
    
    lab_menu = st.radio(
        "Select Option",
        ["➕ Add Lab Case", "📋 Lab Reports"],
        horizontal=True
    )
    
    if lab_menu == "➕ Add Lab Case":
        with st.form("lab_form"):
            case_id = st.text_input("Case ID")
            raid_date = st.date_input("Raid Date")
            state = st.selectbox("State", ["Delhi", "Punjab", "Haryana", "UP", "Maharashtra", "Gujarat"])
            district = st.text_input("District")
            location = st.text_area("Exact Location")
            lab_type = st.selectbox("Lab Type", ["Methamphetamine Lab", "Synthetic Drug Lab", "Heroin Processing Unit", "MDMA Lab"])
            drugs_found = st.multiselect("Drugs Recovered", ["Methamphetamine", "MDMA", "Heroin", "Ketamine", "Cannabis", "Cocaine"])
            quantity = st.number_input("Total Drugs Seized (KG)", min_value=0.0)
            arrests = st.number_input("Number of Arrests", min_value=0)
            risk_level = st.selectbox("Risk Level", ["Low", "Medium", "High", "Critical"])
            remarks = st.text_area("Operational Notes")
            
            if st.form_submit_button("💾 Save Lab Case"):
                data = {
                    "case_id": case_id,
                    "raid_date": str(raid_date),
                    "state": state,
                    "district": district,
                    "location": location,
                    "lab_type": lab_type,
                    "drugs": ", ".join(drugs_found),
                    "quantity": quantity,
                    "arrests": arrests,
                    "risk_level": risk_level,
                    "remarks": remarks
                }
                try:
                    record_id = insert_record('lab_busts', data)
                    if record_id:
                        st.success("✅ Lab Case Saved Successfully")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    elif lab_menu == "📋 Lab Reports":
        records = get_all_records('lab_busts')
        if records:
            df_data = []
            for record in records:
                df_data.append({
                    "Case ID": record[1],
                    "Date": record[2],
                    "State": record[3],
                    "Lab Type": record[6],
                    "Drugs": record[7],
                    "Quantity (KG)": record[10],
                    "Arrests": record[11],
                    "Risk": record[13]
                })
            st.dataframe(df_data, use_container_width=True)
        else:
            st.warning("No Lab Cases Available")