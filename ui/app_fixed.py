"""Lewis AI System - GitHub Style UI"""

from __future__ import annotations

import time
from typing import Any, Dict, List

import requests
import streamlit as st

# 页面配置
st.set_page_config(
    page_title="Lewis AI System - 智能助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Lewis AI System - 三层自治人工智能系统"
    }
)

# 强制确保侧边栏可见
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'expanded'

# Kimi Style Design System
kimi_style = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
@import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&display=swap');

/* Hide Streamlit default elements */
#MainMenu {display: none !important;}
.stDeployButton {display: none !important;}
footer {display: none !important;}
.stActionButton {display: none !important;}
header {display: none !important;}
.stToolbar {display: none !important;}
div[data-testid="stDecoration"] {display: none !important;}
div[data-testid="stStatusWidget"] {display: none !important;}
.reportview-container .main .block-container {max-width: 1200px !important; padding: 40px 24px !important;}

/* Kimi Dark Theme Variables */
:root {
    --color-bg: #050a1f;
    --bg-gradient: radial-gradient(120% 120% at 5% 0%, rgba(108, 122, 255, 0.32) 0%, rgba(5, 10, 31, 0) 55%), radial-gradient(120% 120% at 95% 10%, rgba(94, 236, 255, 0.28) 0%, rgba(5, 10, 31, 0) 55%), linear-gradient(180deg, #050a1f 0%, #090d2b 60%, #060818 100%);
    --color-surface: rgba(18, 22, 52, 0.78);
    --color-surface-soft: rgba(18, 22, 52, 0.6);
    --color-border: rgba(255, 255, 255, 0.12);
    --color-border-soft: rgba(255, 255, 255, 0.08);
    --color-text-primary: #f4f7ff;
    --color-text-secondary: rgba(244, 247, 255, 0.75);
    --color-text-tertiary: rgba(244, 247, 255, 0.55);
    --color-primary: #80f0ff;
    --color-primary-strong: #58a6ff;
    --color-highlight: #c778ff;
    --color-success: #62ffc6;
    --shadow-sm: 0 12px 28px rgba(8, 12, 36, 0.35);
    --shadow-md: 0 18px 45px rgba(8, 12, 36, 0.45);
    --blur-soft: 18px;
    --radius-sm: 12px;
    --radius-md: 20px;
    --radius-lg: 32px;
    --radius-pill: 999px;
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 40px;
    --transition: all 0.3s ease;
}

/* Global Styles */
.stApp {
    min-height: 100vh !important;
    background-color: var(--color-bg) !important;
    background-image: var(--bg-gradient) !important;
    font-family: 'VT323', 'Press Start 2P', monospace !important;
    font-size: 18px !important;
    line-height: 1.4 !important;
    color: var(--color-text-primary) !important;
    overflow-x: hidden !important;
    position: relative !important;
}

.stApp::before {
    content: '' !important;
    position: fixed !important;
    inset: 0 !important;
    pointer-events: none !important;
    background: radial-gradient(45% 55% at 50% 0%, rgba(120, 189, 255, 0.16) 0%, rgba(5, 10, 31, 0) 72%) !important;
    opacity: 0.9 !important;
    z-index: -1 !important;
}

.main .block-container {
    background: transparent !important;
    position: relative !important;
    z-index: 1 !important;
}

/* Pixel Style Cards */
.github-card {
    background: var(--color-surface) !important;
    border: 2px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 0 !important;
    padding: clamp(var(--spacing-lg), 2vw, var(--spacing-xl)) !important;
    margin: var(--spacing-lg) 0 !important;
    backdrop-filter: blur(var(--blur-soft)) !important;
    box-shadow: 4px 4px 0px rgba(0, 0, 0, 0.4) !important;
    transition: var(--transition) !important;
    position: relative !important;
    overflow: hidden !important;
}

.github-card::after {
    content: '' !important;
    position: absolute !important;
    inset: 0 !important;
    border-radius: inherit !important;
    border: 1px solid rgba(255, 255, 255, 0.04) !important;
    opacity: 0 !important;
    transition: var(--transition) !important;
    pointer-events: none !important;
}

.github-card:hover {
    transform: translate(-2px, -2px) !important;
    box-shadow: 6px 6px 0px rgba(0, 0, 0, 0.5) !important;
    border-color: var(--color-primary) !important;
}

.github-card:hover::after {
    opacity: 1 !important;
}

/* Pixel Typography */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Press Start 2P', 'VT323', monospace !important;
    font-weight: 400 !important;
    line-height: 1.2 !important;
    color: var(--color-text-primary) !important;
    text-shadow: 2px 2px 0px rgba(0, 0, 0, 0.5) !important;
}

h1 {
    font-size: clamp(16px, 4vw, 24px) !important;
    font-weight: 400 !important;
    line-height: 1.2 !important;
    margin-bottom: var(--spacing-lg) !important;
    letter-spacing: 2px !important;
}

h2 {
    font-size: clamp(12px, 2.5vw, 16px) !important;
    font-weight: 400 !important;
    margin-bottom: var(--spacing-md) !important;
    padding-bottom: 0 !important;
    border-bottom: none !important;
    color: var(--color-text-primary) !important;
    letter-spacing: 1px !important;
}

h3 {
    font-size: clamp(10px, 2vw, 14px) !important;
    font-weight: 400 !important;
    margin-bottom: var(--spacing-sm) !important;
    color: var(--color-text-primary) !important;
    letter-spacing: 1px !important;
}

p {
    font-family: 'VT323', monospace !important;
    font-size: 18px !important;
    margin-bottom: var(--spacing-md) !important;
    color: var(--color-text-secondary) !important;
    line-height: 1.3 !important;
}

.text-gradient {
    background: linear-gradient(120deg, var(--color-primary) 0%, var(--color-highlight) 50%, var(--color-primary-strong) 100%) !important;
    -webkit-background-clip: text !important;
    background-clip: text !important;
    color: transparent !important;
}

/* Pixel Style Buttons */
.stButton > button {
    background: rgba(255, 255, 255, 0.05) !important;
    color: var(--color-text-primary) !important;
    border: 2px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 0 !important;
    padding: var(--spacing-md) var(--spacing-xl) !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    font-family: 'VT323', monospace !important;
    transition: var(--transition) !important;
    backdrop-filter: blur(var(--blur-soft)) !important;
    cursor: pointer !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    box-shadow: 4px 4px 0px rgba(0, 0, 0, 0.3) !important;
}

.stButton > button:hover {
    border-color: var(--color-primary) !important;
    background: rgba(128, 240, 255, 0.1) !important;
    box-shadow: 6px 6px 0px rgba(0, 0, 0, 0.4) !important;
    transform: translate(-2px, -2px) !important;
}

.stButton > button[kind="primary"] {
    background: var(--color-primary) !important;
    color: #020614 !important;
    border: 2px solid var(--color-primary) !important;
    font-weight: 400 !important;
    box-shadow: 4px 4px 0px rgba(0, 0, 0, 0.4) !important;
}

.stButton > button[kind="primary"]:hover {
    background: var(--color-highlight) !important;
    border-color: var(--color-highlight) !important;
    transform: translate(-2px, -2px) !important;
    box-shadow: 6px 6px 0px rgba(0, 0, 0, 0.5) !important;
}

/* Pixel Form Elements */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select {
    background: rgba(7, 9, 30, 0.8) !important;
    color: var(--color-text-primary) !important;
    border: 2px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 0 !important;
    padding: var(--spacing-md) !important;
    font-size: 16px !important;
    line-height: 1.3 !important;
    font-family: 'VT323', monospace !important;
    transition: var(--transition) !important;
    backdrop-filter: blur(var(--blur-soft)) !important;
    box-shadow: 2px 2px 0px rgba(0, 0, 0, 0.3) !important;
}

.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: var(--color-text-tertiary) !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > select:focus {
    outline: none !important;
    border-color: var(--color-primary) !important;
    box-shadow: 4px 4px 0px rgba(128, 240, 255, 0.3) !important;
    transform: translate(-2px, -2px) !important;
}

.stTextInput > label,
.stTextArea > label,
.stSelectbox > label,
.stSlider > label,
.stCheckbox > label {
    color: var(--color-text-primary) !important;
    font-family: 'VT323', monospace !important;
    font-weight: 400 !important;
    font-size: 16px !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(7, 9, 30, 0.72) !important;
    border-right: 2px solid var(--color-border-soft) !important;
    backdrop-filter: blur(var(--blur-soft)) !important;
    min-width: 300px !important;
}

section[data-testid="stSidebar"] > div {
    background: transparent !important;
}

/* Sidebar Toggle Button - ALWAYS visible and functional */
button[data-testid="collapsedControl"] {
    background: var(--color-primary) !important;
    color: #020614 !important;
    border: 2px solid var(--color-primary) !important;
    border-radius: 0 !important;
    width: 50px !important;
    height: 50px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    position: fixed !important;
    top: 20px !important;
    left: 20px !important;
    z-index: 999999 !important;
    box-shadow: 4px 4px 0px rgba(0, 0, 0, 0.4) !important;
    font-family: 'VT323', monospace !important;
    font-size: 20px !important;
    opacity: 1 !important;
    visibility: visible !important;
    pointer-events: auto !important;
}

button[data-testid="collapsedControl"]:hover {
    background: var(--color-highlight) !important;
    border-color: var(--color-highlight) !important;
    transform: translate(-2px, -2px) !important;
    box-shadow: 6px 6px 0px rgba(0, 0, 0, 0.5) !important;
}

/* Force the collapsed control to always be visible */
.stApp button[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important;
    z-index: 999999 !important;
}

/* Override any hiding styles */
div[data-testid="stSidebarNav"] button[data-testid="collapsedControl"],
section[data-testid="stSidebar"] + button[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important;
    top: 20px !important;
    left: 20px !important;
    z-index: 999999 !important;
}

/* Sidebar content styling */
.stSidebar .stMarkdown,
.stSidebar .stTextInput > label,
.stSidebar .stCheckbox > label,
.stSidebar .stSlider > label {
    color: var(--color-text-primary) !important;
    font-family: 'VT323', monospace !important;
    font-size: 16px !important;
}

/* Sidebar headers */
.stSidebar h3 {
    color: var(--color-primary) !important;
    font-family: 'Press Start 2P', monospace !important;
    font-size: 12px !important;
    margin-bottom: 16px !important;
    text-shadow: 2px 2px 0px rgba(0, 0, 0, 0.5) !important;
}

/* Force sidebar to be visible when expanded */
section[data-testid="stSidebar"][aria-expanded="true"] {
    width: 300px !important;
    transform: translateX(0) !important;
}

/* Ensure sidebar toggle works */
section[data-testid="stSidebar"][aria-expanded="false"] {
    width: 0 !important;
    transform: translateX(-100%) !important;
    transition: all 0.3s ease !important;
}

/* Status Messages */
.stSuccess {
    background: rgba(98, 255, 198, 0.1) !important;
    border-left: 4px solid var(--color-success) !important;
    color: var(--color-success) !important;
    border-radius: var(--radius-md) !important;
    padding: var(--spacing-md) !important;
    backdrop-filter: blur(var(--blur-soft)) !important;
}

.stWarning {
    background: rgba(255, 193, 7, 0.1) !important;
    border-left: 4px solid #ffc107 !important;
    color: #ffc107 !important;
    border-radius: var(--radius-md) !important;
    padding: var(--spacing-md) !important;
    backdrop-filter: blur(var(--blur-soft)) !important;
}

.stError {
    background: rgba(248, 81, 73, 0.1) !important;
    border-left: 4px solid #f85149 !important;
    color: #f85149 !important;
    border-radius: var(--radius-md) !important;
    padding: var(--spacing-md) !important;
    backdrop-filter: blur(var(--blur-soft)) !important;
}

.stInfo {
    background: rgba(128, 240, 255, 0.1) !important;
    border-left: 4px solid var(--color-primary) !important;
    color: var(--color-primary) !important;
    border-radius: var(--radius-md) !important;
    padding: var(--spacing-md) !important;
    backdrop-filter: blur(var(--blur-soft)) !important;
}

/* Status Badge */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-xs);
    padding: 6px 16px;
    font-size: 14px;
    font-weight: 500;
    border-radius: var(--radius-pill);
    background: rgba(255, 255, 255, 0.05);
    color: var(--color-text-secondary);
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.03);
    font-family: 'Manrope', -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Noto Sans", sans-serif;
}

.status-badge::before {
    content: '';
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--color-text-secondary);
    box-shadow: 0 0 0 4px rgba(98, 255, 198, 0.15);
}

.status-badge.online {
    color: var(--color-success);
    border-color: rgba(98, 255, 198, 0.25);
}

.status-badge.online::before {
    background: var(--color-success);
}

/* Code Blocks */
.stCodeBlock {
    background: var(--color-canvas-subtle) !important;
    border: 1px solid var(--color-border-default) !important;
    border-radius: 6px !important;
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace !important;
}

/* Expander */
.stExpander {
    background: var(--color-canvas-default) !important;
    border: 1px solid var(--color-border-default) !important;
    border-radius: 6px !important;
}

/* Focus indicators */
*:focus-visible {
    outline: 2px solid var(--color-accent-fg) !important;
    outline-offset: 2px !important;
}

/* Additional sidebar fix */
.stApp > div:first-child {
    display: flex !important;
}

/* Ensure main content adjusts when sidebar is visible */
.main .block-container {
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}
</style>

<script>
// Force sidebar toggle button to ALWAYS be visible
function ensureToggleButtonVisible() {
    const toggleButton = document.querySelector('[data-testid="collapsedControl"]');
    if (toggleButton) {
        // Force all visibility styles
        toggleButton.style.display = 'flex';
        toggleButton.style.visibility = 'visible';
        toggleButton.style.opacity = '1';
        toggleButton.style.position = 'fixed';
        toggleButton.style.top = '20px';
        toggleButton.style.left = '20px';
        toggleButton.style.zIndex = '999999';
        toggleButton.style.width = '50px';
        toggleButton.style.height = '50px';
        toggleButton.style.pointerEvents = 'auto';
        
        // Apply pixel styling
        toggleButton.style.background = '#80f0ff';
        toggleButton.style.color = '#020614';
        toggleButton.style.border = '2px solid #80f0ff';
        toggleButton.style.borderRadius = '0';
        toggleButton.style.boxShadow = '4px 4px 0px rgba(0, 0, 0, 0.4)';
        toggleButton.style.fontFamily = 'VT323, monospace';
        toggleButton.style.fontSize = '20px';
        
        // Ensure it's always clickable
        toggleButton.style.cursor = 'pointer';
        
        // Add hover effect
        toggleButton.addEventListener('mouseenter', function() {
            this.style.background = '#c778ff';
            this.style.borderColor = '#c778ff';
            this.style.transform = 'translate(-2px, -2px)';
            this.style.boxShadow = '6px 6px 0px rgba(0, 0, 0, 0.5)';
        });
        
        toggleButton.addEventListener('mouseleave', function() {
            this.style.background = '#80f0ff';
            this.style.borderColor = '#80f0ff';
            this.style.transform = 'translate(0, 0)';
            this.style.boxShadow = '4px 4px 0px rgba(0, 0, 0, 0.4)';
        });
    }
}

// Run immediately when page loads
document.addEventListener('DOMContentLoaded', ensureToggleButtonVisible);

// Monitor continuously for the toggle button
setInterval(ensureToggleButtonVisible, 500);

// Also monitor when sidebar state changes
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.type === 'attributes' && mutation.attributeName === 'aria-expanded') {
            setTimeout(ensureToggleButtonVisible, 100);
        }
    });
});

// Start observing sidebar changes
setTimeout(function() {
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    if (sidebar) {
        observer.observe(sidebar, { attributes: true });
    }
}, 1000);
</script>
"""
st.markdown(kimi_style, unsafe_allow_html=True)

# Emergency Sidebar Toggle Button (backup)
st.markdown("""
<div id="emergency-sidebar-toggle" style="position: fixed; top: 80px; left: 20px; z-index: 999998;">
    <button onclick="toggleSidebar()" style="
        background: #c778ff; 
        color: #020614; 
        border: 2px solid #c778ff; 
        border-radius: 0; 
        width: 50px; 
        height: 30px; 
        font-family: 'VT323', monospace; 
        font-size: 12px; 
        cursor: pointer;
        box-shadow: 2px 2px 0px rgba(0, 0, 0, 0.4);
        display: none;
    ">MENU</button>
</div>

<script>
function toggleSidebar() {
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    if (sidebar) {
        const isExpanded = sidebar.getAttribute('aria-expanded') === 'true';
        sidebar.setAttribute('aria-expanded', !isExpanded);
        if (!isExpanded) {
            sidebar.style.transform = 'translateX(0)';
            sidebar.style.width = '300px';
        } else {
            sidebar.style.transform = 'translateX(-100%)';
            sidebar.style.width = '0';
        }
    }
}

// Show emergency button if main toggle is not visible
setInterval(function() {
    const mainToggle = document.querySelector('[data-testid="collapsedControl"]');
    const emergencyToggle = document.getElementById('emergency-sidebar-toggle');
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    
    if (emergencyToggle && sidebar) {
        const sidebarCollapsed = sidebar.getAttribute('aria-expanded') === 'false';
        const mainToggleVisible = mainToggle && mainToggle.offsetParent !== null;
        
        if (sidebarCollapsed && !mainToggleVisible) {
            emergencyToggle.querySelector('button').style.display = 'block';
        } else {
            emergencyToggle.querySelector('button').style.display = 'none';
        }
    }
}, 1000);
</script>

# Kimi Style Hero Section
st.markdown("""
<div class="github-card" style="text-align: center; padding: clamp(40px, 6vw, 72px) 24px; position: relative;">
    <div style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 16px; border-radius: 999px; background: rgba(128, 240, 255, 0.08); border: 1px solid rgba(128, 240, 255, 0.18); color: var(--color-primary); font-size: 14px; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 24px;">
        Multi-Agent Autonomy
    </div>
    <h1 style="margin-bottom: 16px;">
        <span class="text-gradient">Lewis AI System</span>
    </h1>
    <p style="font-size: clamp(18px, 2.6vw, 24px); color: var(--color-text-secondary); max-width: 680px; margin: 0 auto 40px;">
        三层自治人工智能系统 - 研究规划与执行的智能协作平台
    </p>
    <div style="display: flex; gap: 8px; justify-content: center; flex-wrap: wrap;">
        <span class="status-badge online">Perceptor Online</span>
        <span class="status-badge online">Planner Online</span>
        <span class="status-badge online">Executor Online</span>
        <span class="status-badge online">Critic Online</span>
    </div>
</div>
""", unsafe_allow_html=True)

if "task_history" not in st.session_state:
    st.session_state.task_history = []

if "active_task" not in st.session_state:
    st.session_state.active_task = None


def api_headers(token: str) -> Dict[str, str]:
    """拼装 API 请求头, 附带令牌(若输入)."""
    return {"Authorization": f"Bearer {token}"} if token else {}


def create_task(api_url: str, token: str, goal: str, name: str, sync: bool) -> Dict[str, Any]:
    """调用后端创建任务, 可以根据 sync 参数决定是否阻塞执行."""
    response = requests.post(
        f"{api_url}/tasks",
        json={"goal": goal, "name": name or None, "sync": sync},
        headers=api_headers(token),
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def fetch_status(api_url: str, token: str, task_id: str) -> Dict[str, Any]:
    """轮询任务状态, 返回编排器记录的进度信息."""
    response = requests.get(f"{api_url}/tasks/{task_id}", headers=api_headers(token), timeout=30)
    response.raise_for_status()
    return response.json()


def display_enhanced_results(result_summary):
    """显示增强的任务结果"""
    st.markdown("## 任务执行结果")
    
    # 获取 Critic 评审结果
    verdict_data = result_summary.get("verdict", {})
    verdict = verdict_data.get("verdict", "unknown")
    score = verdict_data.get("score", 0)
    
    # 显示评审结果
    if verdict == "approve":
        st.success(f"任务已通过审核 (评分: {score:.2f}/1.0)")
    else:
        st.warning(f"需要改进 (评分: {score:.2f}/1.0)")
    
    # 显示问题和建议
    issues = verdict_data.get("issues", [])
    recommendations = verdict_data.get("recommendations", [])
    
    col1, col2 = st.columns(2)
    
    with col1:
        if issues:
            st.markdown("#### ⚠️ 发现的问题")
            for issue in issues:
                st.markdown(f"- {issue}")
    
    with col2:
        if recommendations:
            st.markdown("#### 💡 改进建议")
            for rec in recommendations:
                st.markdown(f"- {rec}")
    
    # 提取执行结果
    execution_log = result_summary.get("execution", [])
    
    # 查找不同类型的输出
    writer_results = []
    researcher_results = []
    
    for entry in execution_log:
        agent_name = entry.get("agent", "")
        response_output = entry.get("response", {}).get("output", {})
        
        if agent_name == "Writer" and response_output:
            writer_results.append(response_output)
        elif agent_name == "Researcher" and response_output:
            researcher_results.append(response_output)
    
    # 显示搜索结果
    if researcher_results:
        st.markdown("### 🔍 搜索结果")
        for result in researcher_results:
            query = result.get("query", "")
            search_results = result.get("results", [])
            summary = result.get("summary", "")
            
            st.markdown(f"**搜索查询:** {query}")
            
            if summary:
                st.info(f"**AI 总结:** {summary}")
            
            if search_results:
                st.markdown("**搜索结果:**")
                for i, item in enumerate(search_results, 1):
                    title = item.get("title", "")
                    link = item.get("link", "")
                    snippet = item.get("snippet", "")
                    
                    with st.container():
                        st.markdown(f"**{i}. {title}**")
                        st.markdown(f"🔗 [链接]({link})")
                        st.caption(snippet)
                        st.divider()
    
    # 显示代码结果
    if writer_results:
        latest_writer = writer_results[-1]
        code = latest_writer.get("code", "")
        sandbox_result = latest_writer.get("sandbox", {})
        
        if code:
            st.markdown("### 💻 生成的代码")
            st.code(code, language="python")
        
        if sandbox_result and sandbox_result.get("success"):
            output = sandbox_result.get("stdout", "")
            if output:
                st.markdown("### 🖥️ 执行输出")
                st.code(output, language="text")
    
    # 完整执行日志（可展开）
    with st.expander("📊 详细执行日志"):
        st.json(result_summary)


def display_event_log(events):
    """显示事件日志"""
    with st.expander("📜 执行日志", expanded=False):
        for event in events:
            event_type = event.get('event_type', '')
            created_at = event.get('created_at', '')
            
            # 为不同类型的事件添加图标
            icon = {
                'perception_completed': '🧠',
                'planning_completed': '📋', 
                'writer_completed': '✍️',
                'researcher_completed': '🔍',
                'critic_completed': '🎯',
                'task_failed': '❌'
            }.get(event_type, '📝')
            
            st.markdown(f"**{icon} [{created_at}] {event_type}**")
            
            payload = event.get("payload", {})
            if payload and event_type == 'researcher_completed':
                output = payload.get('output', {})
                if output:
                    query = output.get('query', '')
                    num_results = output.get('num_results', 0)
                    st.markdown(f"   - 搜索查询: {query}")
                    st.markdown(f"   - 结果数量: {num_results}")
            elif payload:
                with st.expander(f"查看 {event_type} 详情"):
                    st.json(payload)


def fetch_events(api_url: str, token: str, task_id: str) -> List[Dict[str, Any]]:
    """获取任务事件流, 展示每个步骤的执行情况与返回数据."""
    response = requests.get(
        f"{api_url}/tasks/{task_id}/events",
        headers=api_headers(token),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


# System Status Cards
st.markdown("### SYSTEM STATUS")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("**PERCEPTOR**")
    st.markdown("Perception layer")
    st.success("Online")

with col2:
    st.markdown("**PLANNER**") 
    st.markdown("Task planning")
    st.success("Online")

with col3:
    st.markdown("**EXECUTOR**")
    st.markdown("Code execution")
    st.success("Online")

with col4:
    st.markdown("**CRITIC**")
    st.markdown("Quality review")
    st.success("Online")

# Sidebar Configuration
with st.sidebar:
    st.markdown("### SYSTEM CONFIG")
    
    # 添加侧边栏重置提示
    st.info("TIP: If sidebar disappears, refresh the page (F5)")
    
    api_base = st.text_input("BACKEND URL", value="http://127.0.0.1:8002")
    api_token = st.text_input("API TOKEN", value="change-me", type="password")
    sync_mode = st.checkbox("SYNC MODE", value=True, help="Wait for task completion")
    poll_interval = st.slider("REFRESH (SEC)", 1, 10, 2)
    
    st.markdown("### QUICK TASKS")
    
    quick_tasks = [
        ("Hello World", "Write a 'Hello World' Program"),
        ("Weather Query", "查询杭州天气"),
        ("Web Search", "搜索人工智能最新进展"),
        ("Python Tutorial", "Search for Python best practices 2024"),
        ("Data Analysis", "Create a simple data analysis script"),
    ]
    
    for task_name, task_goal in quick_tasks:
        if st.button(task_name, key=f"quick_{task_name}"):
            st.session_state.quick_task = task_goal

# Task Creation Section
st.markdown("### Launch New Task")

# 如果有快速任务被选中, 预填充表单
initial_goal = st.session_state.get("quick_task", "")
if initial_goal:
    st.session_state.quick_task = ""  # 清除状态

with st.form("task_form"):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        goal = st.text_area(
            "任务描述", 
            value=initial_goal,
            height=120, 
            placeholder="例如：使用google search查询杭州天气\n或：Write a Python script to calculate fibonacci numbers"
        )
    
    with col2:
        task_name = st.text_input("任务名称", placeholder="可选, 便于识别")
        submitted = st.form_submit_button("开始执行", use_container_width=True, type="primary")

if submitted:
    if not goal.strip():
        st.error("请输入任务描述")
    else:
        with st.spinner("正在提交任务给AI系统..."):
            try:
                result = create_task(api_base, api_token, goal.strip(), task_name.strip(), sync_mode)
                task_id = result["task_id"]
                st.session_state.active_task = task_id
                st.session_state.task_history.append(task_id)
                st.success(f"✅ 任务已提交: {task_id}")
                st.rerun()
            except requests.HTTPError as exc:
                st.error(f"❌ API 错误: {exc.response.text}")
            except Exception as exc:
                st.error(f"❌ 提交失败: {exc}")

# 活动任务显示
active_task = st.session_state.active_task

if active_task:
    st.markdown(f"### 📋 当前任务: `{active_task}`")
    
    # 获取任务状态
    status_data = None
    try:
        status_data = fetch_status(api_base, api_token, active_task)
    except requests.HTTPError as exc:
        st.error(f"获取状态失败: {exc.response.text}")
    except Exception as exc:
        st.error(f"状态查询错误: {exc}")

    if status_data:
        # 状态显示
        status = status_data['status']
        status_color = {
            'running': 'RUNNING',
            'completed': 'COMPLETED', 
            'failed': 'FAILED',
            'pending': 'PENDING'
        }.get(status, status.upper())
        
        st.markdown(f"**状态:** {status_color}")
        st.markdown(f"**开始时间:** {status_data.get('started_at', 'N/A')}")
        st.markdown(f"**结束时间:** {status_data.get('finished_at', 'N/A')}")
        
        # 结果展示（优化版）
        if status_data.get("result_summary") and status == 'completed':
            display_enhanced_results(status_data["result_summary"])
        elif status_data.get("result_summary"):
            # For non-completed tasks, show summary as before
            with st.expander("Result Summary", expanded=True):
                st.json(status_data["result_summary"])
        
        if status_data.get("error_message"):
            st.error(status_data["error_message"])

    try:
        events = fetch_events(api_base, api_token, active_task)
        display_event_log(events)
    except Exception as exc:
        st.error(f"无法加载事件日志: {exc}")

    if status_data and status_data["status"] not in {"completed", "failed", "cancelled"}:
        st.info("任务执行中, 页面将自动刷新...")
        time.sleep(poll_interval)
        st.rerun()


if st.session_state.task_history:
    st.markdown("### 历史任务")
    recent_tasks = list(reversed(st.session_state.task_history[-5:]))
    
    cols = st.columns(min(len(recent_tasks), 5))
    for idx, task_id in enumerate(recent_tasks):
        with cols[idx]:
            if st.button(f"TASK {task_id[:8]}...", key=f"history_{task_id}", use_container_width=True):
                st.session_state.active_task = task_id
                st.rerun()

# Footer
st.markdown("---")
st.markdown("---")
st.markdown("**Lewis AI System v2.0** | 三层自治人工智能系统")
st.caption("Powered by FastAPI + Streamlit | 支持智能搜索、代码生成、质量评审")
