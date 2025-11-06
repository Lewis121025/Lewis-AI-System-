"""Lewis AI System - 优化版前端界面"""

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

# Pixel Art Design System - 8px Grid, Pastel Colors, Glassmorphism
pixel_style = """
<style>
/* Import pixel fonts */
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap');

/* CRITICAL: Force sidebar to be visible - Must come first! */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
[data-testid="stSidebar"],
.css-1d391kg,
.st-emotion-cache-1d391kg {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: relative !important;
    left: 0 !important;
    transform: none !important;
}

/* Hide Streamlit default elements */
#MainMenu {display: none !important;}
.stDeployButton {display: none !important;}
footer {display: none !important;}
/* Keep sidebar collapse button visible */
/* .stActionButton {display: none !important;} */
header {display: none !important;}
.stToolbar {display: none !important;}
div[data-testid="stDecoration"] {display: none !important;}
div[data-testid="stStatusWidget"] {display: none !important;}
.reportview-container .main .block-container {max-width: 100% !important; padding: 16px 24px;}

/* Ensure sidebar collapse/expand buttons are visible and styled */
button[kind="header"],
button[data-testid="baseButton-header"],
button[data-testid="collapsedControl"],
.stActionButton button,
section[data-testid="stSidebar"] button[kind="header"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: var(--color-bg-secondary) !important;
    color: var(--color-pixel-blue) !important;
    border: 1px solid var(--color-border) !important;
    border-radius: 0 !important;
    transition: all 0.2s ease !important;
}

button[kind="header"]:hover,
button[data-testid="baseButton-header"]:hover,
button[data-testid="collapsedControl"]:hover,
.stActionButton button:hover {
    background: var(--color-bg-hover) !important;
    border-color: var(--color-pixel-blue) !important;
    box-shadow: 0 0 8px rgba(78, 201, 176, 0.3) !important;
}

/* Sidebar collapse icon styling */
section[data-testid="stSidebar"] button svg,
button[data-testid="collapsedControl"] svg {
    color: var(--color-pixel-blue) !important;
    fill: var(--color-pixel-blue) !important;
}

/* CSS Variables - VSCode Light Theme Color Palette */
:root {
    /* Copilot CLI Dark Terminal Theme */
    --color-bg-primary: #1E1E1E;
    --color-bg-secondary: #252526;
    --color-bg-tertiary: #2D2D30;
    --color-bg-hover: #2A2D2E;
    --color-bg-active: #37373D;
    
    /* Copilot CLI Color Palette */
    --color-pixel-blue: #4EC9B0;      /* Light cyan - pixel art text */
    --color-pixel-purple: #C586C0;   /* Purple - robot/accents */
    --color-pixel-green: #6A9955;    /* Green - status indicators */
    --color-pixel-yellow: #DCDCAA;   /* Yellow - highlights */
    --color-success: #4EC9B0;         /* Success states */
    --color-error: #F48771;          /* Errors */
    --color-warning: #DCDCAA;        /* Warnings */
    --color-info: #569CD6;           /* Info blue */
    --color-accent: #4EC9B0;         /* Main accent */
    
    /* Text Colors - Terminal Style */
    --color-text-primary: #D4D4D4;
    --color-text-secondary: #858585;
    --color-text-tertiary: #6A6A6A;
    --color-text-inverse: #FFFFFF;
    --color-text-pixel: #4EC9B0;  /* Light cyan for pixel art text */
    
    /* Borders */
    --color-border: #3E3E42;
    --color-border-hover: #4E4E52;
    --color-border-focus: #4EC9B0;
    
    /* Shadows - Subtle for light theme */
    --shadow-soft: 0 1px 3px rgba(0, 0, 0, 0.08);
    --shadow-medium: 0 2px 6px rgba(0, 0, 0, 0.1);
    --shadow-strong: 0 4px 12px rgba(0, 0, 0, 0.12);
    --shadow-inset: inset 0 1px 2px rgba(0, 0, 0, 0.05);
    
    /* Border radius */
    --radius-small: 4px;
    --radius-medium: 8px;
    
    /* Spacing - 8px grid system */
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
}

/* Global Background - Copilot CLI Dark Terminal */
.stApp {
    background: var(--color-bg-primary) !important;
    font-family: 'VT323', 'Press Start 2P', 'Courier New', monospace !important;
    font-size: 20px !important;
    color: var(--color-text-primary) !important;
}

/* Main content area */
.main .block-container {
    background: transparent !important;
}

/* Copilot CLI Style Cards - Terminal Box */
.pixel-card {
    background: var(--color-bg-secondary) !important;
    border: 1px solid var(--color-border) !important;
    border-radius: 0 !important;
    padding: var(--spacing-lg) !important;
    margin: var(--spacing-md) 0 !important;
    box-shadow: none !important;
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    color: var(--color-text-primary) !important;
}

.pixel-card::before {
    content: '┌';
    position: absolute;
    top: 8px;
    left: 8px;
    color: var(--color-pixel-blue);
    font-family: 'Courier New', monospace;
    font-size: 16px;
    line-height: 1;
}

.pixel-card::after {
    content: '└';
    position: absolute;
    bottom: 8px;
    left: 8px;
    color: var(--color-pixel-blue);
    font-family: 'Courier New', monospace;
    font-size: 16px;
    line-height: 1;
}


/* Copilot CLI card variants */
.pixel-card.purple {
    border-color: var(--color-pixel-blue) !important;
}

.pixel-card.orange {
    border-color: var(--color-pixel-purple) !important;
}

.pixel-card.green {
    border-color: var(--color-pixel-green) !important;
}

.pixel-card {
    animation: fade-in-up 0.5s ease-out;
}

.pixel-card:hover {
    border-color: var(--color-pixel-blue) !important;
    background: var(--color-bg-hover) !important;
    box-shadow: 0 0 0 1px var(--color-pixel-blue) !important;
}

@keyframes pixel-border-shimmer {
    0% { background-position: 0% 0%; }
    100% { background-position: 200% 0%; }
}

/* Copilot CLI Style Buttons - Terminal Style */
.stButton > button {
    background: var(--color-bg-secondary) !important;
    color: var(--color-pixel-blue) !important;
    border: 1px solid var(--color-pixel-blue) !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    font-family: 'VT323', 'Press Start 2P', 'Courier New', monospace !important;
    font-size: 20px !important;
    font-weight: normal !important;
    padding: 10px 24px !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative;
    overflow: hidden;
    letter-spacing: 1px !important;
    image-rendering: pixelated;
    text-shadow: 0 0 4px var(--color-pixel-blue);
}

.stButton > button::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(78, 201, 176, 0.1);
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
}

.stButton > button::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(0, 122, 204, 0.1);
    transform: translate(-50%, -50%);
    transition: width 0.4s, height 0.4s;
}

.stButton > button:hover::before {
    width: 300px;
    height: 300px;
}

.stButton > button:hover {
    background: var(--color-bg-hover) !important;
    border-color: var(--color-pixel-blue) !important;
    box-shadow: 0 0 8px rgba(78, 201, 176, 0.3) !important;
    color: var(--color-pixel-blue) !important;
    text-shadow: 0 0 8px var(--color-pixel-blue);
}

.stButton > button:hover::after {
    opacity: 1;
}

.stButton > button:hover::after {
    opacity: 1;
}

.stButton > button:active {
    transform: translateY(0) scale(0.98) !important;
    box-shadow: var(--shadow-inset) !important;
}

.stButton > button:focus-visible {
    outline: 2px solid var(--color-info) !important;
    outline-offset: 2px !important;
}

/* Primary button - Copilot CLI Style */
.stButton > button[kind="primary"] {
    background: var(--color-bg-secondary) !important;
    color: var(--color-pixel-blue) !important;
    border: 2px solid var(--color-pixel-blue) !important;
    box-shadow: 0 0 12px rgba(78, 201, 176, 0.4) !important;
    text-shadow: 0 0 8px var(--color-pixel-blue), 0 0 16px var(--color-pixel-blue);
}

.stButton > button[kind="primary"]:hover {
    background: rgba(78, 201, 176, 0.15) !important;
    box-shadow: 0 0 16px rgba(78, 201, 176, 0.6) !important;
    text-shadow: 0 0 12px var(--color-pixel-blue), 0 0 24px var(--color-pixel-blue);
}

/* Copilot CLI Style Form Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select {
    background: var(--color-bg-secondary) !important;
    color: var(--color-text-primary) !important;
    border: 1px solid var(--color-border) !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    font-family: 'VT323', 'Courier New', monospace !important;
    font-size: 18px !important;
    padding: 10px 16px !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    letter-spacing: 0.5px !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > select:focus {
    outline: none !important;
    border-color: var(--color-pixel-blue) !important;
    box-shadow: 0 0 0 1px var(--color-pixel-blue), 0 0 8px rgba(78, 201, 176, 0.3) !important;
    background: var(--color-bg-hover) !important;
}

/* Labels */
.stTextInput > label,
.stTextArea > label,
.stSelectbox > label,
.stSlider > label,
.stCheckbox > label {
    color: var(--color-text-primary) !important;
    font-family: 'VT323', 'Press Start 2P', monospace !important;
    font-weight: normal !important;
    font-size: 20px !important;
    letter-spacing: 1px !important;
}

/* Sidebar - Copilot CLI Style - Force Visible */
section[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: var(--color-bg-secondary) !important;
    border-right: 1px solid var(--color-border) !important;
    min-width: 250px !important;
    width: auto !important;
}

section[data-testid="stSidebar"] > div {
    background: transparent !important;
    display: block !important;
    visibility: visible !important;
}

/* Collapsed sidebar button */
button[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 9999 !important;
}

.stSidebar .stMarkdown,
.stSidebar .stTextInput > label,
.stSidebar .stCheckbox > label,
.stSidebar .stSlider > label {
    color: var(--color-text-primary) !important;
    font-family: 'VT323', 'Press Start 2P', monospace !important;
    font-size: 18px !important;
}

/* Status Messages - Copilot CLI Terminal Style */
.stSuccess,
.stWarning,
.stError,
.stInfo {
    font-family: 'VT323', 'Courier New', monospace !important;
    font-size: 18px !important;
    letter-spacing: 1px !important;
    border-radius: 0 !important;
    box-shadow: none !important;
}

.stSuccess {
    background: var(--color-bg-secondary) !important;
    border-left: 2px solid var(--color-pixel-green) !important;
    color: var(--color-pixel-green) !important;
    transition: all 0.2s ease !important;
}

.stSuccess:hover {
    border-left-color: var(--color-pixel-blue) !important;
    background: var(--color-bg-hover) !important;
}

.stWarning {
    background: var(--color-bg-secondary) !important;
    border-left: 2px solid var(--color-pixel-yellow) !important;
    color: var(--color-pixel-yellow) !important;
    transition: all 0.2s ease !important;
}

.stWarning:hover {
    border-left-color: var(--color-pixel-blue) !important;
    background: var(--color-bg-hover) !important;
}

.stError {
    background: var(--color-bg-secondary) !important;
    border-left: 2px solid var(--color-error) !important;
    color: var(--color-error) !important;
    transition: all 0.2s ease !important;
}

.stError:hover {
    border-left-color: var(--color-pixel-blue) !important;
    background: var(--color-bg-hover) !important;
}

.stInfo {
    background: var(--color-bg-secondary) !important;
    border-left: 2px solid var(--color-info) !important;
    color: var(--color-info) !important;
    transition: all 0.2s ease !important;
}

.stInfo:hover {
    border-left-color: var(--color-pixel-blue) !important;
    background: var(--color-bg-hover) !important;
}

/* Headings - Copilot CLI Pixel Art Style */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Press Start 2P', 'VT323', monospace !important;
    font-weight: normal !important;
    line-height: 1.4 !important;
    letter-spacing: 2px !important;
    color: var(--color-text-primary) !important;
}

h1 {
    font-size: 36px !important;
    color: var(--color-pixel-blue) !important;
    text-shadow: 
        2px 2px 0px rgba(0, 0, 0, 0.8),
        0 0 8px var(--color-pixel-blue),
        0 0 16px var(--color-pixel-blue);
    image-rendering: pixelated;
}

h2 {
    font-size: 28px !important;
    color: var(--color-pixel-blue) !important;
    text-shadow: 0 0 4px var(--color-pixel-blue);
}

h3 {
    font-size: 24px !important;
    color: var(--color-pixel-blue) !important;
    text-shadow: 0 0 4px var(--color-pixel-blue);
}

h4 {
    font-size: 22px !important;
    color: var(--color-text-primary) !important;
}

/* Status Badge - Copilot CLI Terminal Style */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    background: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    border-radius: 0;
    font-size: 18px;
    font-weight: normal;
    font-family: 'VT323', 'Courier New', monospace !important;
    color: var(--color-text-primary);
    transition: all 0.2s ease;
    position: relative;
    letter-spacing: 1px;
    box-shadow: none;
}

.status-badge::before {
    content: '●';
    width: 8px;
    height: 8px;
    border-radius: 0;
    background: transparent;
    color: var(--color-pixel-green);
    font-size: 12px;
    line-height: 1;
    animation: pixel-pulse 2s ease-in-out infinite;
    text-shadow: 0 0 4px var(--color-pixel-green);
}

.status-badge.online::before {
    color: var(--color-pixel-green);
    text-shadow: 0 0 4px var(--color-pixel-green), 0 0 8px var(--color-pixel-green);
    animation: pixel-pulse 2s ease-in-out infinite;
}

.status-badge.offline::before {
    color: var(--color-error);
    text-shadow: 0 0 4px var(--color-error);
    animation: none;
}

.status-badge:hover {
    background: var(--color-bg-hover);
    border-color: var(--color-pixel-blue);
    box-shadow: 0 0 0 1px var(--color-pixel-blue);
}

@keyframes pixel-pulse {
    0%, 100% {
        opacity: 1;
        transform: scale(1);
    }
    50% {
        opacity: 0.7;
        transform: scale(0.9);
    }
}

/* Enhanced Pixel Art Loader with Multiple Animations */
@keyframes pixel-bounce {
    0%, 80%, 100% {
        transform: scale(0) translateY(0);
        opacity: 0.5;
    }
    40% {
        transform: scale(1) translateY(-8px);
        opacity: 1;
    }
}

@keyframes pixel-rotate {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes pixel-shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

.pixel-loader {
    width: 32px;
    height: 32px;
    position: relative;
    margin: 16px auto;
}

.pixel-loader::before,
.pixel-loader::after {
    content: '';
    position: absolute;
    width: 8px;
    height: 8px;
    background: var(--color-pixel-blue);
    border-radius: 0;
    image-rendering: pixelated;
    animation: pixel-bounce 1.4s infinite ease-in-out both;
    box-shadow: 0 0 4px var(--color-pixel-blue), 0 0 8px var(--color-pixel-blue);
}

.pixel-loader::before {
    left: 0;
    animation-delay: -0.32s;
}

.pixel-loader::after {
    right: 0;
    animation-delay: 0.32s;
}

/* Pixel Art Icons - CSS Generated */
.pixel-icon-brain {
    width: 24px;
    height: 24px;
    display: inline-block;
    image-rendering: pixelated;
    background: 
        linear-gradient(to right, var(--color-pixel-blue) 0%, var(--color-pixel-blue) 25%, transparent 25%),
        linear-gradient(to right, var(--color-pixel-blue) 0%, var(--color-pixel-blue) 25%, transparent 25%),
        linear-gradient(to right, var(--color-pixel-blue) 0%, var(--color-pixel-blue) 50%, transparent 50%),
        linear-gradient(to right, var(--color-pixel-blue) 0%, var(--color-pixel-blue) 50%, transparent 50%),
        var(--color-pixel-blue);
    background-size: 6px 6px, 6px 6px, 12px 6px, 12px 6px, 24px 24px;
    background-position: 0 0, 18px 0, 0 6px, 0 12px, 0 0;
    animation: pixel-shimmer 2s linear infinite;
    background-repeat: no-repeat;
    filter: drop-shadow(0 0 4px var(--color-pixel-blue));
}

.pixel-icon-plan {
    width: 24px;
    height: 24px;
    display: inline-block;
    image-rendering: pixelated;
    background: 
        linear-gradient(to right, var(--color-info) 0%, var(--color-info) 100%),
        linear-gradient(to right, var(--color-info) 0%, var(--color-info) 100%),
        linear-gradient(to right, var(--color-info) 0%, var(--color-info) 100%);
    background-size: 20px 2px, 16px 2px, 12px 2px;
    background-position: 2px 4px, 2px 10px, 2px 16px;
    background-repeat: no-repeat;
    filter: drop-shadow(0 0 4px var(--color-info));
}

.pixel-icon-execute {
    width: 24px;
    height: 24px;
    display: inline-block;
    image-rendering: pixelated;
    background: 
        linear-gradient(45deg, transparent 40%, var(--color-pixel-purple) 40%, var(--color-pixel-purple) 60%, transparent 60%),
        linear-gradient(-45deg, transparent 40%, var(--color-pixel-purple) 40%, var(--color-pixel-purple) 60%, transparent 60%);
    background-size: 12px 12px, 12px 12px;
    background-position: 6px 6px, 6px 6px;
    animation: pixel-rotate 2s linear infinite;
    filter: drop-shadow(0 0 4px var(--color-pixel-purple));
}

.pixel-icon-critic {
    width: 24px;
    height: 24px;
    display: inline-block;
    image-rendering: pixelated;
    background: 
        radial-gradient(circle, var(--color-pixel-green) 30%, transparent 30%),
        linear-gradient(to right, var(--color-pixel-green) 0%, var(--color-pixel-green) 100%);
    background-size: 8px 8px, 2px 8px;
    background-position: 8px 8px, 11px 8px;
    background-repeat: no-repeat;
    filter: drop-shadow(0 0 4px var(--color-pixel-green));
}

/* Additional Hover Effects */
.stSelectbox > div > div > select:hover,
.stSlider > div > div > div:hover {
    border-color: var(--color-border-hover) !important;
    background: var(--color-bg-hover) !important;
}

/* Checkbox Animation */
.stCheckbox > label {
    transition: all 0.2s ease !important;
}

.stCheckbox > label:hover {
    color: var(--color-pixel-blue) !important;
    transform: translateX(2px);
}

/* Smooth scroll behavior */
html {
    scroll-behavior: smooth;
}

/* Respect reduced motion preference */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
    
    html {
        scroll-behavior: auto;
    }
}

/* Code blocks with Animation */
.stCodeBlock {
    background: var(--color-bg-secondary) !important;
    border: 1px solid var(--color-border) !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    transition: all 0.3s ease !important;
    position: relative;
    overflow: hidden;
    font-family: 'VT323', 'Courier New', monospace !important;
    font-size: 16px !important;
    letter-spacing: 0.5px !important;
    color: var(--color-text-primary) !important;
}

.stCodeBlock::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0, 122, 204, 0.05), transparent);
    animation: pixel-scan 3s linear infinite;
}

.stCodeBlock:hover {
    border-color: var(--color-pixel-blue) !important;
    box-shadow: 0 0 0 1px var(--color-pixel-blue);
}

@keyframes pixel-scan {
    0% { left: -100%; }
    100% { left: 100%; }
}

/* Expander with Animation */
.stExpander {
    background: var(--color-bg-secondary) !important;
    border: 1px solid var(--color-border) !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    transition: all 0.3s ease !important;
    color: var(--color-text-primary) !important;
}

.stExpander:hover {
    border-color: var(--color-pixel-blue) !important;
    box-shadow: 0 0 0 1px var(--color-pixel-blue);
    background: var(--color-bg-hover) !important;
}

/* Fade-in animation for cards */
@keyframes fade-in-up {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Slide-in animation */
@keyframes slide-in-right {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.stSuccess,
.stWarning,
.stError,
.stInfo {
    animation: slide-in-right 0.3s ease-out;
}

/* Divider with Animation */
hr {
    border: none !important;
    border-top: 1px solid var(--color-border) !important;
    margin: 24px 0 !important;
    position: relative;
    overflow: hidden;
}

hr::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--color-pixel-blue), transparent);
    animation: pixel-scan 2s linear infinite;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .reportview-container .main .block-container {
        padding: 8px 16px !important;
    }
}

/* Focus indicators for accessibility */
*:focus-visible {
    outline: 1px solid var(--color-pixel-blue) !important;
    outline-offset: 1px !important;
    box-shadow: 0 0 4px rgba(78, 201, 176, 0.5) !important;
}
</style>

<script>
// 确保侧边栏和控制按钮始终可见
(function() {
    function ensureSidebarVisible() {
        // 1. 确保侧边栏本身可见
        const sidebar = document.querySelector('section[data-testid="stSidebar"]');
        if (sidebar) {
            sidebar.style.display = 'block';
            sidebar.style.visibility = 'visible';
            sidebar.style.opacity = '1';
            sidebar.style.minWidth = '250px';
        }
        
        // 2. 确保所有控制按钮可见
        const buttonSelectors = [
            'button[kind="header"]',
            'button[data-testid="baseButton-header"]',
            'button[data-testid="collapsedControl"]',
            '.stActionButton button',
            'section[data-testid="stSidebar"] button[kind="header"]',
            '[data-testid="collapsedControl"]'
        ];
        
        buttonSelectors.forEach(selector => {
            const buttons = document.querySelectorAll(selector);
            buttons.forEach(btn => {
                if (btn) {
                    btn.style.display = 'flex';
                    btn.style.visibility = 'visible';
                    btn.style.opacity = '1';
                    btn.style.pointerEvents = 'auto';
                    btn.style.zIndex = '9999';
                }
            });
        });
        
        // 3. 确保折叠状态下的展开按钮可见
        const collapsedControl = document.querySelector('[data-testid="collapsedControl"]');
        if (collapsedControl) {
            collapsedControl.style.display = 'flex';
            collapsedControl.style.visibility = 'visible';
            collapsedControl.style.opacity = '1';
        }
    }
    
    // 页面加载完成后立即执行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', ensureSidebarVisible);
    } else {
        ensureSidebarVisible();
    }
    
    // 定期检查（每500ms）
    setInterval(ensureSidebarVisible, 500);
    
    // 监听DOM变化
    const observer = new MutationObserver(ensureSidebarVisible);
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['style', 'class']
    });
})();
</script>
"""
st.markdown(pixel_style, unsafe_allow_html=True)

# Copilot CLI Style Hero Section
st.markdown("""
<div class="pixel-card" style="text-align: center; padding: 32px 24px; margin-bottom: 32px; border-color: #4EC9B0 !important;">
    <div style="margin-bottom: 16px; color: #D4D4D4; font-family: 'Courier New', monospace; font-size: 14px;">
        Welcome to
    </div>
    <h1 style="font-size: 48px; margin: 0 0 20px 0; color: #4EC9B0; font-family: 'Press Start 2P', monospace; letter-spacing: 4px; text-shadow: 2px 2px 0px rgba(0, 0, 0, 0.8), 0 0 8px #4EC9B0, 0 0 16px #4EC9B0; image-rendering: pixelated; display: inline-block; position: relative;">
        LEWIS AI SYSTEM
    </h1>
    <p style="color: #858585; margin: 12px 0; font-size: 18px; font-family: 'Courier New', monospace; letter-spacing: 1px;">
        三层自治人工智能系统 v2.0
    </p>
    <div style="display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; margin-top: 20px;">
        <span class="status-badge online" style="border-color: #3E3E42; color: #D4D4D4;">● Perceptor Online</span>
        <span class="status-badge online" style="border-color: #3E3E42; color: #D4D4D4;">● Planner Online</span>
        <span class="status-badge online" style="border-color: #3E3E42; color: #D4D4D4;">● Executor Online</span>
        <span class="status-badge online" style="border-color: #3E3E42; color: #D4D4D4;">● Critic Online</span>
    </div>
</div>
""", unsafe_allow_html=True)

if "task_history" not in st.session_state:
    st.session_state.task_history = []

if "active_task" not in st.session_state:
    st.session_state.active_task = None


def api_headers(token: str) -> Dict[str, str]:
    """拼装 API 请求头，附带令牌（若输入）。"""
    return {"Authorization": f"Bearer {token}"} if token else {}


def create_task(api_url: str, token: str, goal: str, name: str, sync: bool) -> Dict[str, Any]:
    """调用后端创建任务，可以根据 sync 参数决定是否阻塞执行。"""
    # 对于同步模式，增加超时时间；异步模式使用较短超时
    timeout = 300 if sync else 30
    response = requests.post(
        f"{api_url}/tasks",
        json={"goal": goal, "name": name or None, "sync": sync},
        headers=api_headers(token),
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def fetch_status(api_url: str, token: str, task_id: str) -> Dict[str, Any]:
    """轮询任务状态，返回编排器记录的进度信息。"""
    response = requests.get(f"{api_url}/tasks/{task_id}", headers=api_headers(token), timeout=30)
    response.raise_for_status()
    return response.json()


def display_enhanced_results(result_summary):
    """显示增强的任务结果"""
    st.markdown("## 📋 任务执行结果")
    
    # 获取 Critic 评审结果
    verdict_data = result_summary.get("verdict", {})
    verdict = verdict_data.get("verdict", "unknown")
    score = verdict_data.get("score", 0)
    
    # 显示评审结果
    if verdict == "approve":
        st.success(f"✅ 任务已通过审核 (评分: {score:.2f}/1.0)")
    else:
        st.warning(f"⚠️ 需要改进 (评分: {score:.2f}/1.0)")
    
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
    """获取任务事件流，展示每个步骤的执行情况与返回数据。"""
    response = requests.get(
        f"{api_url}/tasks/{task_id}/events",
        headers=api_headers(token),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


# System Status Cards with Glassmorphism
st.markdown("### System Status")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="pixel-card purple">
        <h3 style="margin: 0 0 12px 0; font-size: 26px; display: flex; align-items: center; gap: 10px; font-family: 'Press Start 2P', monospace; letter-spacing: 2px; color: #4EC9B0; text-shadow: 0 0 4px #4EC9B0;">
            <span class="pixel-icon-brain"></span> Perceptor
        </h3>
        <p style="color: #858585; font-size: 18px; margin: 10px 0; font-family: 'Courier New', monospace; letter-spacing: 1px;">
            Perception and understanding layer
        </p>
        <div class="pixel-loader"></div>
        <span class="status-badge online" style="border-color: #3E3E42; color: #D4D4D4;">● Online</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="pixel-card" style="border-color: #569CD6 !important;">
        <h3 style="margin: 0 0 12px 0; font-size: 26px; display: flex; align-items: center; gap: 10px; font-family: 'Press Start 2P', monospace; letter-spacing: 2px; color: #569CD6; text-shadow: 0 0 4px #569CD6;">
            <span class="pixel-icon-plan"></span> Planner
        </h3>
        <p style="color: #858585; font-size: 18px; margin: 10px 0; font-family: 'Courier New', monospace; letter-spacing: 1px;">
            Task planning and orchestration
        </p>
        <div class="pixel-loader"></div>
        <span class="status-badge online" style="border-color: #3E3E42; color: #D4D4D4;">● Online</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="pixel-card orange">
        <h3 style="margin: 0 0 12px 0; font-size: 26px; display: flex; align-items: center; gap: 10px; font-family: 'Press Start 2P', monospace; letter-spacing: 2px; color: #C586C0; text-shadow: 0 0 4px #C586C0;">
            <span class="pixel-icon-execute"></span> Executor
        </h3>
        <p style="color: #858585; font-size: 18px; margin: 10px 0; font-family: 'Courier New', monospace; letter-spacing: 1px;">
            Code generation and execution
        </p>
        <div class="pixel-loader"></div>
        <span class="status-badge online" style="border-color: #3E3E42; color: #D4D4D4;">● Online</span>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="pixel-card green">
        <h3 style="margin: 0 0 12px 0; font-size: 26px; display: flex; align-items: center; gap: 10px; font-family: 'Press Start 2P', monospace; letter-spacing: 2px; color: #6A9955; text-shadow: 0 0 4px #6A9955;">
            <span class="pixel-icon-critic"></span> Critic
        </h3>
        <p style="color: #858585; font-size: 18px; margin: 10px 0; font-family: 'Courier New', monospace; letter-spacing: 1px;">
            Quality review and feedback
        </p>
        <div class="pixel-loader"></div>
        <span class="status-badge online" style="border-color: #3E3E42; color: #D4D4D4;">● Online</span>
    </div>
    """, unsafe_allow_html=True)

# Sidebar Configuration with Glassmorphism
with st.sidebar:
    st.markdown("""
    <div class="pixel-card" style="margin-bottom: 16px;">
        <h3 style="margin: 0; font-size: 18px;">⚙️ System Config</h3>
    </div>
    """, unsafe_allow_html=True)
    
    api_base = st.text_input("🌐 Backend URL", value="http://localhost:8002")
    api_token = st.text_input("🔑 API Token", value="change-me", type="password")
    sync_mode = st.checkbox("⏱️ Sync Mode", value=False, help="Wait for task completion (may timeout for long tasks)")
    poll_interval = st.slider("🔄 Refresh (sec)", 1, 10, 2)
    
    # 检查队列状态
    try:
        queue_status = requests.get(
            f"{api_base}/queue/status",
            headers=api_headers(api_token),
            timeout=5,
        )
        if queue_status.status_code == 200:
            status_data = queue_status.json()
            if not status_data.get("redis_available"):
                st.warning("⚠️ Redis 不可用，异步任务将回退到同步执行")
            elif status_data.get("workers_running", 0) == 0:
                st.warning("⚠️ 没有 Worker 在运行！异步任务将无法执行。请运行 `start_worker.bat` 或 `python start_worker.py`")
            else:
                st.success(f"✅ 队列正常 ({status_data.get('workers_running', 0)} 个 Worker)")
    except Exception:
        pass  # 忽略状态检查错误，不影响主流程
    
    st.markdown("""
    <div class="pixel-card" style="margin: 16px 0;">
        <h3 style="margin: 0; font-size: 18px;">🎯 Quick Tasks</h3>
    </div>
    """, unsafe_allow_html=True)
    
    quick_tasks = [
        ("👋 Hello World", "Write a 'Hello World' Program"),
        ("🌤️ 杭州天气", "查询杭州天气"),
        ("🔍 网络搜索", "搜索人工智能最新进展"),
        ("🐍 Python教程", "Search for Python best practices 2024"),
        ("📊 数据分析", "Create a simple data analysis script"),
    ]
    
    for task_name, task_goal in quick_tasks:
        if st.button(task_name, key=f"quick_{task_name}"):
            st.session_state.quick_task = task_goal

# Task Creation Section
st.markdown("### Launch New Task")

# 如果有快速任务被选中，预填充表单
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
        task_name = st.text_input("任务名称", placeholder="可选，便于识别")
        submitted = st.form_submit_button("▶️ 开始执行", use_container_width=True, type="primary")

if submitted:
    if not goal.strip():
        st.error("⚠️ 请输入任务描述")
    else:
        with st.spinner("🔄 正在提交任务给AI系统..."):
            try:
                result = create_task(api_base, api_token, goal.strip(), task_name.strip(), sync_mode)
                task_id = result["task_id"]
                st.session_state.active_task = task_id
                st.session_state.task_history.append(task_id)
                if sync_mode:
                    st.success(f"✅ 任务已完成: {task_id}")
                else:
                    st.success(f"✅ 任务已提交: {task_id} (正在后台执行)")
                st.rerun()
            except requests.Timeout:
                st.error("⏱️ 请求超时：任务执行时间过长。建议取消勾选 'Sync Mode' 使用异步模式，或稍后通过任务ID查询状态。")
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
        st.error(f"❌ 获取状态失败: {exc.response.text}")
    except Exception as exc:
        st.error(f"❌ 状态查询错误: {exc}")

    if status_data:
        # 状态显示
        status = status_data['status']
        status_color = {
            'running': '🟡 进行中',
            'completed': '✅ 已完成', 
            'failed': '❌ 失败',
            'pending': '⏳ 等待中'
        }.get(status, f'🔄 {status}')
        
        st.markdown(f"""
        **状态:** {status_color}  
        **开始时间:** {status_data.get('started_at', 'N/A')}  
        **结束时间:** {status_data.get('finished_at', 'N/A')}
        """)
        
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
        st.error(f"❌ 无法加载事件日志: {exc}")

    if status_data and status_data["status"] not in {"completed", "failed", "cancelled"}:
        st.info("🔄 任务执行中，页面将自动刷新...")
        time.sleep(poll_interval)
        st.rerun()


def display_enhanced_results(result_summary):
    """显示增强的任务结果"""
    st.markdown("## 📋 任务执行结果")
    
    # 获取 Critic 评审结果
    verdict_data = result_summary.get("verdict", {})
    verdict = verdict_data.get("verdict", "unknown")
    score = verdict_data.get("score", 0)
    
    # 显示评审结果
    if verdict == "approve":
        st.success(f"✅ 任务已通过审核 (评分: {score:.2f}/1.0)")
    else:
        st.warning(f"⚠️ 需要改进 (评分: {score:.2f}/1.0)")
    
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


if st.session_state.task_history:
    st.markdown("### 📚 历史任务")
    recent_tasks = list(reversed(st.session_state.task_history[-5:]))
    
    cols = st.columns(min(len(recent_tasks), 5))
    for idx, task_id in enumerate(recent_tasks):
        with cols[idx]:
            if st.button(f"📋 {task_id[:8]}...", key=f"history_{task_id}", use_container_width=True):
                st.session_state.active_task = task_id
                st.rerun()

# Footer with VSCode Style
st.markdown("---")
st.markdown("""
<div class="pixel-card" style="text-align: center; padding: 24px; margin-top: 32px;">
    <p style="color: #666666; margin: 0; font-size: 20px; font-family: 'VT323', monospace; letter-spacing: 1px;">🤖 Lewis AI System v2.0 | 三层自治人工智能系统</p>
    <p style="color: #999999; font-size: 18px; margin: 10px 0 0 0; font-family: 'VT323', monospace; letter-spacing: 1px;">
        Powered by FastAPI + Streamlit | 支持智能搜索、代码生成、质量评审
    </p>
</div>
""", unsafe_allow_html=True)
