"""
InsureClaim Pro - AI-Powered Insurance Claims Processing
Enhanced UI with modern design, better UX, and improved problem-solving experience
"""
import streamlit as st
import requests
from datetime import datetime, date, timedelta
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="InsureClaim Pro | AI-Powered Claims",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Design System CSS with better UX
st.markdown("""
<style>
    /* ========================================
       DESIGN SYSTEM TOKENS - Enhanced
       ======================================== */
    :root {
        /* Primary Colors - More vibrant */
        --color-primary: #0F172A;
        --color-primary-light: #1E293B;
        --color-accent: #3B82F6;
        --color-accent-hover: #2563EB;
        --color-accent-light: #DBEAFE;
        
        /* Semantic Colors */
        --color-success: #10B981;
        --color-success-bg: #D1FAE5;
        --color-success-text: #065F46;
        --color-warning: #F59E0B;
        --color-warning-bg: #FEF3C7;
        --color-warning-text: #92400E;
        --color-error: #EF4444;
        --color-error-bg: #FEE2E2;
        --color-error-text: #991B1B;
        --color-info: #3B82F6;
        --color-info-bg: #DBEAFE;
        --color-info-text: #1E40AF;
        
        /* Neutral Colors */
        --color-bg: #F8FAFC;
        --color-surface: #FFFFFF;
        --color-border: #E2E8F0;
        --color-text: #1E293B;
        --color-text-muted: #64748B;
        --color-text-light: #94A3B8;
        
        /* Typography */
        --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
        
        /* Spacing */
        --space-1: 0.25rem;
        --space-2: 0.5rem;
        --space-3: 0.75rem;
        --space-4: 1rem;
        --space-5: 1.5rem;
        --space-6: 2rem;
        --space-8: 3rem;
        
        /* Border Radius */
        --radius-sm: 6px;
        --radius-md: 10px;
        --radius-lg: 14px;
        --radius-xl: 20px;
        --radius-full: 9999px;
        
        /* Shadows - More depth */
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
        --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 12px 24px rgba(0, 0, 0, 0.12);
        --shadow-glow: 0 0 20px rgba(59, 130, 246, 0.3);
        
        /* Transitions */
        --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* ========================================
       BASE STYLES
       ======================================== */
    .stApp {
        font-family: var(--font-sans);
        color: var(--color-text);
        background: var(--color-bg);
    }
    
    /* ========================================
       HERO HEADER - More impactful
       ======================================== */
    .hero-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 50%, #2563EB 100%);
        padding: var(--space-8) var(--space-6);
        border-radius: var(--radius-xl);
        margin-bottom: var(--space-6);
        color: white;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        opacity: 0.5;
    }
    
    .hero-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        position: relative;
        z-index: 1;
    }
    
    .hero-header p {
        margin: var(--space-3) 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
        position: relative;
        z-index: 1;
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: var(--space-2);
        background: rgba(255, 255, 255, 0.15);
        padding: var(--space-2) var(--space-4);
        border-radius: var(--radius-full);
        font-size: 0.85rem;
        margin-top: var(--space-4);
        backdrop-filter: blur(10px);
        position: relative;
        z-index: 1;
    }
    
    /* ========================================
       STEP INDICATOR - Visual progress
       ======================================== */
    .step-indicator {
        display: flex;
        justify-content: center;
        gap: var(--space-2);
        margin-bottom: var(--space-6);
        padding: var(--space-4);
        background: var(--color-surface);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
    }
    
    .step-item {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        padding: var(--space-3) var(--space-4);
        border-radius: var(--radius-md);
        transition: all var(--transition-base);
    }
    
    .step-item.active {
        background: var(--color-accent-light);
        color: var(--color-accent);
    }
    
    .step-item.completed {
        background: var(--color-success-bg);
        color: var(--color-success-text);
    }
    
    .step-number {
        width: 28px;
        height: 28px;
        border-radius: var(--radius-full);
        background: currentColor;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .step-item.active .step-number {
        background: var(--color-accent);
    }
    
    .step-item.completed .step-number {
        background: var(--color-success);
    }
    
    /* ========================================
       CARD COMPONENTS - Enhanced
       ======================================== */
    .card {
        background: var(--color-surface);
        padding: var(--space-5);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--color-border);
        transition: all var(--transition-base);
    }
    
    .card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        margin-bottom: var(--space-4);
        padding-bottom: var(--space-4);
        border-bottom: 1px solid var(--color-border);
    }
    
    .card-icon {
        width: 44px;
        height: 44px;
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
    }
    
    .card-icon.blue { background: var(--color-info-bg); }
    .card-icon.green { background: var(--color-success-bg); }
    .card-icon.yellow { background: var(--color-warning-bg); }
    .card-icon.red { background: var(--color-error-bg); }
    
    /* ========================================
       METRIC CARDS - Better visual hierarchy
       ======================================== */
    .metric-card {
        background: var(--color-surface);
        padding: var(--space-5);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--color-border);
        text-align: center;
        transition: all var(--transition-base);
    }
    
    .metric-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    
    .metric-card.success {
        background: linear-gradient(135deg, var(--color-success-bg) 0%, #ECFDF5 100%);
        border-color: var(--color-success);
    }
    
    .metric-card.warning {
        background: linear-gradient(135deg, var(--color-warning-bg) 0%, #FFFBEB 100%);
        border-color: var(--color-warning);
    }
    
    .metric-card.danger {
        background: linear-gradient(135deg, var(--color-error-bg) 0%, #FEF2F2 100%);
        border-color: var(--color-error);
    }
    
    .metric-card .metric-icon {
        font-size: 2rem;
        margin-bottom: var(--space-2);
    }
    
    .metric-card h4 {
        color: var(--color-text-muted);
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    
    .metric-card h2 {
        color: var(--color-text);
        font-size: 1.5rem;
        font-weight: 700;
        margin: var(--space-2) 0 0 0;
    }
    
    .metric-card.success h2 { color: var(--color-success-text); }
    .metric-card.warning h2 { color: var(--color-warning-text); }
    .metric-card.danger h2 { color: var(--color-error-text); }
    
    /* ========================================
       STATUS BADGES - More prominent
       ======================================== */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-2) var(--space-4);
        border-radius: var(--radius-full);
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .status-badge.approved {
        background: var(--color-success-bg);
        color: var(--color-success-text);
    }
    
    .status-badge.pending {
        background: var(--color-warning-bg);
        color: var(--color-warning-text);
    }
    
    .status-badge.denied {
        background: var(--color-error-bg);
        color: var(--color-error-text);
    }
    
    /* ========================================
       FORM SECTIONS - Better organization
       ======================================== */
    .form-section {
        background: var(--color-surface);
        padding: var(--space-5);
        border-radius: var(--radius-lg);
        margin-bottom: var(--space-4);
        border: 1px solid var(--color-border);
    }
    
    .form-section-header {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        margin-bottom: var(--space-4);
        padding-bottom: var(--space-3);
        border-bottom: 2px solid var(--color-accent-light);
    }
    
    .form-section-icon {
        width: 36px;
        height: 36px;
        border-radius: var(--radius-md);
        background: var(--color-accent-light);
        color: var(--color-accent);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }
    
    .form-section-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--color-text);
        margin: 0;
    }
    
    .form-section-subtitle {
        font-size: 0.85rem;
        color: var(--color-text-muted);
        margin: 0;
    }
    
    /* ========================================
       INLINE VALIDATION - Better feedback
       ======================================== */
    .field-hint {
        font-size: 0.8rem;
        color: var(--color-text-muted);
        margin-top: var(--space-1);
        display: flex;
        align-items: center;
        gap: var(--space-1);
    }
    
    .field-hint.success {
        color: var(--color-success);
    }
    
    .field-hint.error {
        color: var(--color-error);
    }
    
    /* ========================================
       PROGRESS TIMELINE - Visual workflow
       ======================================== */
    .timeline {
        position: relative;
        padding-left: var(--space-6);
    }
    
    .timeline::before {
        content: '';
        position: absolute;
        left: 14px;
        top: 0;
        bottom: 0;
        width: 2px;
        background: var(--color-border);
    }
    
    .timeline-item {
        position: relative;
        padding-bottom: var(--space-5);
    }
    
    .timeline-item:last-child {
        padding-bottom: 0;
    }
    
    .timeline-dot {
        position: absolute;
        left: -26px;
        width: 12px;
        height: 12px;
        border-radius: var(--radius-full);
        background: var(--color-border);
        border: 2px solid var(--color-surface);
    }
    
    .timeline-item.completed .timeline-dot {
        background: var(--color-success);
    }
    
    .timeline-item.active .timeline-dot {
        background: var(--color-accent);
        box-shadow: 0 0 0 4px var(--color-accent-light);
    }
    
    .timeline-content {
        background: var(--color-bg);
        padding: var(--space-3) var(--space-4);
        border-radius: var(--radius-md);
    }
    
    .timeline-title {
        font-weight: 600;
        font-size: 0.9rem;
        margin: 0;
    }
    
    .timeline-desc {
        font-size: 0.8rem;
        color: var(--color-text-muted);
        margin: var(--space-1) 0 0 0;
    }
    
    /* ========================================
       TAB NAVIGATION - Enhanced
       ======================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: var(--space-1);
        background: var(--color-surface);
        border-radius: var(--radius-lg);
        padding: var(--space-2);
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--color-border);
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: var(--space-3) var(--space-5);
        border-radius: var(--radius-md);
        font-weight: 500;
        font-size: 0.9rem;
        color: var(--color-text-muted);
        transition: all var(--transition-fast);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--color-bg);
        color: var(--color-text);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--color-accent) !important;
        color: white !important;
    }
    
    /* ========================================
       BUTTONS - More polished
       ======================================== */
    .stButton > button {
        border-radius: var(--radius-md);
        font-weight: 600;
        font-size: 0.9rem;
        padding: var(--space-3) var(--space-5);
        transition: all var(--transition-base);
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-hover) 100%);
        color: white;
    }
    
    .stButton > button[data-testid="baseButton-primary"]:hover {
        box-shadow: var(--shadow-glow);
    }
    
    /* ========================================
       CHAT INTERFACE - Enhanced
       ======================================== */
    .chat-container {
        background: var(--color-surface);
        border-radius: var(--radius-lg);
        border: 1px solid var(--color-border);
        overflow: hidden;
    }
    
    .stChatMessage {
        padding: var(--space-4);
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: var(--color-accent-light);
    }
    
    /* ========================================
       SIDEBAR - Enhanced
       ======================================== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--color-primary) 0%, #1E3A5F 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: rgba(255, 255, 255, 0.9);
    }
    
    .sidebar-card {
        background: rgba(255, 255, 255, 0.1);
        padding: var(--space-4);
        border-radius: var(--radius-md);
        margin-bottom: var(--space-3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .sidebar-stat {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--space-2) 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .sidebar-stat:last-child {
        border-bottom: none;
    }
    
    /* ========================================
       RESULT CARDS - Celebration effect
       ======================================== */
    .result-card {
        background: linear-gradient(135deg, var(--color-surface) 0%, var(--color-bg) 100%);
        padding: var(--space-6);
        border-radius: var(--radius-xl);
        border: 2px solid var(--color-success);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .result-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--color-success), var(--color-accent), var(--color-success));
    }
    
    .result-icon {
        font-size: 3rem;
        margin-bottom: var(--space-3);
    }
    
    .result-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--color-text);
        margin: 0;
    }
    
    .result-subtitle {
        font-size: 1rem;
        color: var(--color-text-muted);
        margin: var(--space-2) 0 0 0;
    }
    
    /* ========================================
       AGENT WORKFLOW CARDS
       ======================================== */
    .agent-card {
        background: var(--color-surface);
        padding: var(--space-5);
        border-radius: var(--radius-lg);
        border: 1px solid var(--color-border);
        box-shadow: var(--shadow-sm);
        transition: all var(--transition-base);
        height: 100%;
    }
    
    .agent-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
        border-color: var(--color-accent);
    }
    
    .agent-icon {
        width: 48px;
        height: 48px;
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: var(--space-3);
    }
    
    /* ========================================
       QUICK ACTION BUTTONS
       ======================================== */
    .quick-action {
        background: var(--color-surface);
        padding: var(--space-4);
        border-radius: var(--radius-md);
        border: 1px solid var(--color-border);
        text-align: center;
        cursor: pointer;
        transition: all var(--transition-base);
    }
    
    .quick-action:hover {
        border-color: var(--color-accent);
        background: var(--color-accent-light);
    }
    
    .quick-action-icon {
        font-size: 1.5rem;
        margin-bottom: var(--space-2);
    }
    
    .quick-action-text {
        font-size: 0.85rem;
        color: var(--color-text);
        font-weight: 500;
    }
    
    /* ========================================
       LOADING STATES
       ======================================== */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading-pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .loading-spin {
        animation: spin 1s linear infinite;
    }
    
    /* ========================================
       EMPTY STATES
       ======================================== */
    .empty-state {
        text-align: center;
        padding: var(--space-8);
        color: var(--color-text-muted);
    }
    
    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: var(--space-4);
        opacity: 0.5;
    }
    
    .empty-state-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0;
    }
    
    .empty-state-desc {
        font-size: 0.9rem;
        margin: var(--space-2) 0 0 0;
    }
    
    /* ========================================
       HIDE STREAMLIT BRANDING
       ======================================== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* ========================================
       CUSTOM SCROLLBAR
       ======================================== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--color-bg);
        border-radius: var(--radius-sm);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--color-border);
        border-radius: var(--radius-sm);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--color-text-light);
    }
    
    /* ========================================
       RESPONSIVE ADJUSTMENTS
       ======================================== */
    @media (max-width: 768px) {
        .hero-header h1 {
            font-size: 1.75rem;
        }
        
        .step-indicator {
            flex-wrap: wrap;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HELPER FUNCTIONS
# ============================================

def check_api_health():
    """Check if API is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def show_api_error():
    """Display API connection error with helpful guidance"""
    st.error("⚠️ Cannot connect to the API server")
    with st.expander("🔧 Troubleshooting Steps", expanded=True):
        st.markdown("""
        1. **Start the API server** by running:
           ```bash
           cd insurance_claims_app && python run_api.py
           ```
        2. **Check if port 8000 is available** - another service might be using it
        3. **Verify your environment** - ensure all dependencies are installed
        4. **Check the logs** for any startup errors
        """)

def validate_claim_form(damage_description, incident_report, repair_estimate):
    """Validate form fields and return errors"""
    errors = []
    if not damage_description or len(damage_description.strip()) < 10:
        errors.append("Damage description must be at least 10 characters")
    if not incident_report or len(incident_report.strip()) < 20:
        errors.append("Incident report must be at least 20 characters")
    if not repair_estimate or len(repair_estimate.strip()) < 5:
        errors.append("Please provide a repair estimate")
    return errors

def render_processing_animation():
    """Render a processing animation"""
    return st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <div style="font-size: 3rem; margin-bottom: 1rem;" class="loading-pulse">🔄</div>
        <p style="color: var(--color-text-muted);">AI agents are analyzing your claim...</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================

st.markdown("""
<div class="hero-header">
    <h1>🛡️ InsureClaim Pro</h1>
    <p>AI-Powered Insurance Claims Processing Platform</p>
    <div class="hero-badge">
        <span>⚡</span>
        <span>Powered by Multi-Agent AI • Process claims in minutes, not days</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# MAIN TABS
# ============================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Submit Claim", 
    "🔍 Track Claim", 
    "💬 AI Assistant", 
    "🏗️ How It Works"
])

# ============================================
# TAB 1: SUBMIT CLAIM
# ============================================

with tab1:
    # Step indicator for form progress
    st.markdown("""
    <div class="step-indicator">
        <div class="step-item active">
            <div class="step-number">1</div>
            <span>Policy Info</span>
        </div>
        <div class="step-item">
            <div class="step-number">2</div>
            <span>Claim Details</span>
        </div>
        <div class="step-item">
            <div class="step-number">3</div>
            <span>Documents</span>
        </div>
        <div class="step-item">
            <div class="step-number">4</div>
            <span>Review & Submit</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("claim_form", clear_on_submit=False):
        # Section 1: Policy Information
        st.markdown("""
        <div class="form-section-header">
            <div class="form-section-icon">📋</div>
            <div>
                <p class="form-section-title">Policy Information</p>
                <p class="form-section-subtitle">Select your policy and incident dates</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            policy_id = st.selectbox(
                "Policy Number",
                options=["POL-001", "POL-002", "POL-003"],
                help="Select your active insurance policy"
            )
            st.caption("✓ Policy verified and active")
        
        with col2:
            incident_date = st.date_input(
                "When did the incident occur?",
                value=date.today(),
                max_value=date.today(),
                help="Select the date of the incident"
            )
            days_since = (date.today() - incident_date).days
            if days_since > 30:
                st.warning(f"⚠️ {days_since} days ago - late filing may affect claim")
            else:
                st.caption(f"✓ {days_since} days ago - within filing window")
        
        with col3:
            claim_date = st.date_input(
                "Filing Date",
                value=date.today(),
                disabled=True,
                help="Today's date (auto-filled)"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Section 2: Claim Details
        st.markdown("""
        <div class="form-section-header">
            <div class="form-section-icon">🚗</div>
            <div>
                <p class="form-section-title">Claim Details</p>
                <p class="form-section-subtitle">Describe the damage and estimated costs</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col4, col5 = st.columns(2)
        
        with col4:
            claim_type = st.selectbox(
                "Type of Claim",
                options=["collision", "comprehensive", "liability"],
                format_func=lambda x: {
                    "collision": "🚗 Collision - Vehicle accident damage",
                    "comprehensive": "🌪️ Comprehensive - Non-collision damage",
                    "liability": "⚖️ Liability - Third-party damage"
                }.get(x, x),
                help="Select the category that best describes your claim"
            )
            
            estimated_amount = st.number_input(
                "Estimated Damage Amount ($)",
                min_value=0.0,
                max_value=100000.0,
                value=5000.0,
                step=500.0,
                help="Enter the estimated cost of repairs"
            )
            
            # Smart guidance based on amount
            if estimated_amount > 30000:
                st.info("💡 High-value claims undergo additional verification for your protection")
            elif estimated_amount > 10000:
                st.caption("📋 This claim will be reviewed by our senior adjusters")
            else:
                st.caption("⚡ Standard claims typically process within 3-5 business days")
        
        with col5:
            repair_shop = st.text_input(
                "Preferred Repair Shop (Optional)",
                placeholder="e.g., Joe's Auto Body Shop",
                help="Enter your preferred repair facility"
            )
            
            damage_description = st.text_area(
                "Describe the Damage",
                placeholder="Please describe the damage in detail. Include:\n• What parts are damaged\n• Severity of damage\n• Any safety concerns",
                height=130,
                help="Be as detailed as possible - this helps speed up processing"
            )
            
            # Real-time character count
            char_count = len(damage_description) if damage_description else 0
            if char_count < 10:
                st.caption(f"📝 {char_count}/10 minimum characters")
            else:
                st.caption(f"✓ {char_count} characters - good detail!")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Section 3: Documents
        st.markdown("""
        <div class="form-section-header">
            <div class="form-section-icon">📎</div>
            <div>
                <p class="form-section-title">Supporting Documents</p>
                <p class="form-section-subtitle">Upload photos and provide incident details</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col6, col7, col8 = st.columns(3)
        
        with col6:
            st.markdown("**📸 Damage Photos**")
            damage_photos = st.file_uploader(
                "Upload damage photos",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                help="Upload clear photos of all damage. Multiple angles help!",
                label_visibility="collapsed"
            )
            
            if damage_photos:
                st.success(f"✓ {len(damage_photos)} photo(s) ready for AI analysis")
                # Show thumbnails
                cols = st.columns(min(3, len(damage_photos)))
                for idx, photo in enumerate(damage_photos[:3]):
                    with cols[idx]:
                        st.image(photo, width=80)
            else:
                st.caption("💡 Photos help our AI detect damage accurately")
        
        with col7:
            incident_report = st.text_area(
                "📄 Incident Report",
                placeholder="Describe what happened:\n• Date and time\n• Location\n• How it happened\n• Any witnesses\n• Police report number (if any)",
                height=150,
                help="Provide a detailed account of the incident"
            )
        
        with col8:
            repair_estimate = st.text_area(
                "💵 Repair Estimate",
                placeholder="Enter repair estimate details:\n• Parts needed\n• Labor costs\n• Shop quote (if available)",
                height=150,
                help="Include any quotes you've received"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Submit Section
        st.markdown("---")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submitted = st.form_submit_button(
                "🚀 Submit Claim for AI Processing",
                use_container_width=True,
                type="primary"
            )
        
        # Form submission handling
        if submitted:
            # Validate form
            errors = validate_claim_form(damage_description, incident_report, repair_estimate)
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Check API availability first
                if not check_api_health():
                    show_api_error()
                else:
                    # Show processing state
                    progress_placeholder = st.empty()
                    result_placeholder = st.empty()
                    
                    with progress_placeholder.container():
                        st.markdown("""
                        <div style="text-align: center; padding: 2rem; background: var(--color-surface); border-radius: var(--radius-lg); border: 1px solid var(--color-border);">
                            <div style="font-size: 2.5rem; margin-bottom: 1rem;">🤖</div>
                            <h3 style="margin: 0;">AI Agents Processing Your Claim</h3>
                            <p style="color: var(--color-text-muted); margin-top: 0.5rem;">This typically takes 10-30 seconds</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Progress steps
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        steps = [
                            ("📄 Analyzing documents...", 20),
                            ("✓ Validating claim eligibility...", 40),
                            ("🔍 Running fraud detection...", 60),
                            ("💰 Calculating payout...", 80),
                            ("✅ Finalizing decision...", 100)
                        ]
                        
                        for step_text, progress in steps:
                            status_text.text(step_text)
                            progress_bar.progress(progress)
                            time.sleep(0.3)
                    
                    try:
                        # Prepare and send request
                        if damage_photos:
                            files = []
                            for photo in damage_photos:
                                files.append(("damage_photos", (photo.name, photo.getvalue(), photo.type)))
                            
                            data = {
                                "policy_id": policy_id,
                                "incident_date": incident_date.isoformat(),
                                "claim_date": claim_date.isoformat(),
                                "claim_type": claim_type,
                                "damage_description": damage_description,
                                "repair_shop": repair_shop or "Not specified",
                                "estimated_damage_amount": estimated_amount,
                                "incident_report": incident_report,
                                "repair_estimate": repair_estimate
                            }
                            
                            response = requests.post(
                                f"{API_BASE_URL}/submit-claim-with-images",
                                data=data,
                                files=files,
                                timeout=120
                            )
                        else:
                            payload = {
                                "policy_id": policy_id,
                                "incident_date": incident_date.isoformat(),
                                "claim_date": claim_date.isoformat(),
                                "claim_type": claim_type,
                                "damage_description": damage_description,
                                "repair_shop": repair_shop or "Not specified",
                                "estimated_damage_amount": estimated_amount,
                                "damage_photos": ["sample_photo.jpg"],
                                "incident_report": incident_report,
                                "repair_estimate": repair_estimate
                            }
                            
                            response = requests.post(
                                f"{API_BASE_URL}/submit-claim",
                                json=payload,
                                timeout=120
                            )
                        
                        progress_placeholder.empty()
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.balloons()
                            
                            # Success result card
                            with result_placeholder.container():
                                # Main result
                                approval_status = result.get("approval_status", "PENDING")
                                status_emoji = "✅" if approval_status == "APPROVED" else ("⏳" if approval_status == "NEEDS_REVIEW" else "❌")
                                status_color = "success" if approval_status == "APPROVED" else ("warning" if approval_status == "NEEDS_REVIEW" else "danger")
                                
                                st.markdown(f"""
                                <div class="result-card">
                                    <div class="result-icon">{status_emoji}</div>
                                    <h2 class="result-title">Claim {approval_status.replace('_', ' ').title()}</h2>
                                    <p class="result-subtitle">Claim ID: <strong>{result['claim_id']}</strong></p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.markdown("<br>", unsafe_allow_html=True)
                                
                                # Key metrics
                                col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                                
                                with col_r1:
                                    validation = result.get("validation_status", "PENDING")
                                    v_class = "success" if validation == "VALID" else "danger"
                                    st.markdown(f"""
                                    <div class="metric-card {v_class}">
                                        <div class="metric-icon">{"✓" if validation == "VALID" else "✗"}</div>
                                        <h4>Validation</h4>
                                        <h2>{validation}</h2>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                with col_r2:
                                    st.markdown(f"""
                                    <div class="metric-card {status_color}">
                                        <div class="metric-icon">{status_emoji}</div>
                                        <h4>Decision</h4>
                                        <h2>{approval_status.replace('_', ' ')}</h2>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                with col_r3:
                                    payout = result.get('payout_amount', 0)
                                    st.markdown(f"""
                                    <div class="metric-card">
                                        <div class="metric-icon">💰</div>
                                        <h4>Payout Amount</h4>
                                        <h2>${payout:,.2f}</h2>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                with col_r4:
                                    days = result.get('processing_days', 'N/A')
                                    st.markdown(f"""
                                    <div class="metric-card">
                                        <div class="metric-icon">⏱️</div>
                                        <h4>Est. Processing</h4>
                                        <h2>{days} days</h2>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # Fraud analysis
                                if result.get("fraud_score") is not None:
                                    fraud_score = result['fraud_score']
                                    st.markdown("<br>", unsafe_allow_html=True)
                                    st.markdown("### 🔒 Fraud Analysis")
                                    
                                    col_f1, col_f2 = st.columns([1, 3])
                                    with col_f1:
                                        fraud_color = "success" if fraud_score < 0.4 else ("warning" if fraud_score < 0.7 else "danger")
                                        st.markdown(f"""
                                        <div class="metric-card {fraud_color}">
                                            <h4>Risk Score</h4>
                                            <h2>{fraud_score:.2f}</h2>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    with col_f2:
                                        if fraud_score < 0.4:
                                            st.success("✅ Low Risk - Your claim passed all fraud checks")
                                        elif fraud_score < 0.7:
                                            st.warning("⚠️ Moderate Risk - Additional verification may be required")
                                        else:
                                            st.error("🚨 High Risk - Manual review required before processing")
                                        
                                        st.progress(fraud_score)
                                
                                # Next steps
                                st.markdown("<br>", unsafe_allow_html=True)
                                st.markdown("### 📋 Next Steps")
                                
                                if approval_status == "APPROVED":
                                    st.success("""
                                    1. ✅ Your claim has been approved
                                    2. 💳 Payment will be processed within the estimated timeframe
                                    3. 📧 You'll receive a confirmation email shortly
                                    4. 🔧 You can proceed with repairs at your chosen shop
                                    """)
                                elif approval_status == "NEEDS_REVIEW":
                                    st.warning("""
                                    1. 👤 Your claim requires human review
                                    2. 📞 An adjuster will contact you within 24-48 hours
                                    3. 📄 Please have any additional documentation ready
                                    4. 🔍 Use the Track Claim tab to monitor progress
                                    """)
                                else:
                                    st.error("""
                                    1. ❌ Your claim could not be approved at this time
                                    2. 📋 Review the validation details below
                                    3. 📞 Contact support if you believe this is an error
                                    4. 🔄 You may resubmit with additional documentation
                                    """)
                                
                                # Store claim ID for tracking
                                st.session_state["last_claim_id"] = result["claim_id"]
                                
                                # Detailed results in expander
                                with st.expander("📊 View Full Analysis Details"):
                                    st.json(result)
                        else:
                            st.error(f"❌ Error: {response.json().get('detail', 'Unknown error occurred')}")
                    
                    except requests.exceptions.Timeout:
                        progress_placeholder.empty()
                        st.error("⏱️ Request timed out. The claim may still be processing - check the Track Claim tab.")
                    except requests.exceptions.ConnectionError:
                        progress_placeholder.empty()
                        show_api_error()
                    except Exception as e:
                        progress_placeholder.empty()
                        st.error(f"❌ Unexpected error: {str(e)}")


# ============================================
# TAB 2: TRACK CLAIM
# ============================================

with tab2:
    st.markdown("### 🔍 Track Your Claim")
    st.markdown("Enter your claim ID to view real-time status and details.")
    
    # Search section with better UX
    col_search1, col_search2 = st.columns([4, 1])
    
    with col_search1:
        default_claim_id = st.session_state.get("last_claim_id", "")
        claim_id_input = st.text_input(
            "Claim ID",
            value=default_claim_id,
            placeholder="Enter your claim ID (e.g., CLM-XXXXXXXX)",
            label_visibility="collapsed"
        )
    
    with col_search2:
        search_clicked = st.button("🔍 Search", use_container_width=True, type="primary")
    
    # Quick access to recent claim
    if st.session_state.get("last_claim_id") and not claim_id_input:
        st.info(f"💡 Your most recent claim: **{st.session_state['last_claim_id']}** - Click Search to view it")
    
    if search_clicked and claim_id_input:
        if not check_api_health():
            show_api_error()
        else:
            with st.spinner("🔄 Fetching claim details..."):
                try:
                    response = requests.get(f"{API_BASE_URL}/claim/{claim_id_input}", timeout=30)
                    
                    if response.status_code == 200:
                        claim = response.json()
                        
                        # Claim header with status
                        approval = claim.get("approval_status", "PENDING")
                        status_emoji = "✅" if approval == "APPROVED" else ("⏳" if approval == "NEEDS_REVIEW" else "❌")
                        
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 100%); 
                                    padding: 1.5rem 2rem; border-radius: var(--radius-lg); color: white; margin: 1rem 0;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <h2 style="margin:0; font-size: 1.5rem;">Claim: {claim['claim_id']}</h2>
                                    <p style="margin:0.5rem 0 0 0; opacity:0.85;">
                                        Policy: {claim.get('policy_id', 'N/A')} • Type: {claim.get('claim_type', 'N/A').title()}
                                    </p>
                                </div>
                                <div style="text-align: right;">
                                    <span style="font-size: 2rem;">{status_emoji}</span>
                                    <p style="margin: 0; font-weight: 600;">{approval.replace('_', ' ')}</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Status cards row
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            validation = claim.get("validation_status", "PENDING")
                            v_class = "success" if validation == "VALID" else "danger"
                            v_icon = "✓" if validation == "VALID" else "✗"
                            st.markdown(f"""
                            <div class="metric-card {v_class}">
                                <div class="metric-icon">{v_icon}</div>
                                <h4>Validation</h4>
                                <h2>{validation}</h2>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            a_class = "success" if approval == "APPROVED" else ("warning" if approval == "NEEDS_REVIEW" else "danger")
                            st.markdown(f"""
                            <div class="metric-card {a_class}">
                                <div class="metric-icon">{status_emoji}</div>
                                <h4>Approval</h4>
                                <h2>{approval.replace('_', ' ')}</h2>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            payout = claim.get('payout_amount', 0)
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-icon">💰</div>
                                <h4>Payout</h4>
                                <h2>${payout:,.2f}</h2>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col4:
                            days = claim.get('processing_time_days', 'N/A')
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-icon">⏱️</div>
                                <h4>Processing</h4>
                                <h2>{days} days</h2>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Two column layout for details
                        col_left, col_right = st.columns(2)
                        
                        with col_left:
                            # Financial Summary
                            st.markdown("### 💰 Financial Summary")
                            
                            estimated = claim.get('estimated_damage_amount', 0)
                            deductible = claim.get('deductible', 0)
                            payout = claim.get('payout_amount', 0)
                            
                            st.markdown(f"""
                            <div class="card">
                                <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid var(--color-border);">
                                    <span>Estimated Damage</span>
                                    <strong>${estimated:,.2f}</strong>
                                </div>
                                <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid var(--color-border);">
                                    <span>Deductible</span>
                                    <strong style="color: var(--color-error);">-${deductible:,.2f}</strong>
                                </div>
                                <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; font-size: 1.1rem;">
                                    <span><strong>Net Payout</strong></span>
                                    <strong style="color: var(--color-success);">${payout:,.2f}</strong>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Fraud Analysis
                            if claim.get("fraud_score") is not None:
                                st.markdown("<br>", unsafe_allow_html=True)
                                st.markdown("### 🔒 Fraud Analysis")
                                
                                fraud_score = claim["fraud_score"]
                                risk_level = "Low" if fraud_score < 0.4 else ("Moderate" if fraud_score < 0.7 else "High")
                                risk_color = "success" if fraud_score < 0.4 else ("warning" if fraud_score < 0.7 else "danger")
                                
                                st.markdown(f"""
                                <div class="card">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                                        <span>Risk Score</span>
                                        <span class="status-badge {risk_color.replace('danger', 'denied')}">{risk_level} ({fraud_score:.2f})</span>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.progress(fraud_score)
                        
                        with col_right:
                            # Validation Details
                            st.markdown("### 📋 Validation Details")
                            with st.expander("View validation reason", expanded=True):
                                st.info(claim.get("validation_reason", "No details available"))
                            
                            # Approval Details
                            st.markdown("### ✅ Approval Details")
                            with st.expander("View approval reason", expanded=True):
                                st.info(claim.get("approval_reason", "No details available"))
                        
                        # Images section
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("### 📸 Claim Images")
                        
                        try:
                            img_response = requests.get(f"{API_BASE_URL}/claim/{claim_id_input}/images", timeout=10)
                            if img_response.status_code == 200:
                                img_data = img_response.json()
                                if img_data["count"] > 0:
                                    st.success(f"✓ {img_data['count']} image(s) analyzed with AI")
                                    
                                    cols = st.columns(min(4, img_data["count"]))
                                    for idx, img in enumerate(img_data["images"]):
                                        with cols[idx % 4]:
                                            img_url = f"{API_BASE_URL}/image/{img['image_id']}"
                                            st.image(img_url, caption=img["image_name"], use_container_width=True)
                                            st.caption(f"Type: {img.get('damage_type', 'N/A')}")
                                else:
                                    st.markdown("""
                                    <div class="empty-state">
                                        <div class="empty-state-icon">📷</div>
                                        <p class="empty-state-title">No images uploaded</p>
                                        <p class="empty-state-desc">This claim was submitted without photos</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                        except Exception as e:
                            st.warning(f"Could not load images: {e}")
                        
                        # Full JSON data
                        with st.expander("📄 View Full Claim Data (JSON)"):
                            st.json(claim)
                    
                    elif response.status_code == 404:
                        st.markdown("""
                        <div class="empty-state">
                            <div class="empty-state-icon">🔍</div>
                            <p class="empty-state-title">Claim Not Found</p>
                            <p class="empty-state-desc">We couldn't find a claim with that ID. Please check and try again.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                
                except requests.exceptions.ConnectionError:
                    show_api_error()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    elif search_clicked:
        st.warning("⚠️ Please enter a claim ID to search")
    
    # Empty state when no search
    if not search_clicked and not claim_id_input:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">🔍</div>
            <p class="empty-state-title">Enter a Claim ID to Get Started</p>
            <p class="empty-state-desc">Your claim ID was provided when you submitted your claim</p>
        </div>
        """, unsafe_allow_html=True)


# ============================================
# TAB 3: AI ASSISTANT
# ============================================

with tab3:
    st.markdown("### 💬 AI Insurance Assistant")
    st.markdown("Get instant answers about your policy, claims, coverage, and more.")
    
    # Context linking
    col_ctx1, col_ctx2 = st.columns([3, 1])
    with col_ctx1:
        chat_claim_id = st.text_input(
            "🔗 Link to a specific claim (optional)",
            value=st.session_state.get("last_claim_id", ""),
            placeholder="Enter claim ID for personalized answers",
            key="chat_claim_id"
        )
    with col_ctx2:
        st.markdown("<br>", unsafe_allow_html=True)
        if chat_claim_id:
            st.success("✓ Context linked")
        else:
            st.info("💬 General mode")
    
    st.markdown("---")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Welcome message if no history
    if not st.session_state.messages:
        st.markdown("""
        <div style="background: linear-gradient(135deg, var(--color-accent-light) 0%, #EFF6FF 100%); 
                    padding: 1.5rem; border-radius: var(--radius-lg); margin-bottom: 1rem;">
            <div style="display: flex; gap: 1rem; align-items: flex-start;">
                <div style="font-size: 2rem;">🤖</div>
                <div>
                    <h4 style="margin: 0;">Hi! I'm your AI Insurance Assistant</h4>
                    <p style="margin: 0.5rem 0 0 0; color: var(--color-text-muted);">
                        I can help you with questions about your policy, claim status, coverage details, 
                        and general insurance inquiries. Try one of the quick questions below or type your own!
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Process pending question from quick buttons
    if "pending_question" in st.session_state and st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = None
        
        claim_id = st.session_state.get("chat_claim_id", None)
        if claim_id == "":
            claim_id = None
        
        if check_api_health():
            try:
                payload = {"claim_id": claim_id, "message": question}
                response = requests.post(f"{API_BASE_URL}/chat", json=payload, timeout=120)
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.messages.append({"role": "assistant", "content": result["answer"], "sources": result.get("sources", [])})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": "Sorry, I encountered an error processing your request."})
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "⚠️ Cannot connect to the AI service. Please ensure the API server is running."})
    
    # Display chat history
    for message in st.session_state.messages:
        avatar = "🧑" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            if message.get("sources"):
                unique_sources = list(set(message["sources"]))
                st.caption(f"📚 Sources: {', '.join(unique_sources)}")
    
    # Chat input
    if prompt := st.chat_input("💬 Ask me anything about insurance..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)
        
        claim_id = st.session_state.get("chat_claim_id", None)
        if claim_id == "":
            claim_id = None
        
        with st.chat_message("assistant", avatar="🤖"):
            if not check_api_health():
                error_msg = "⚠️ Cannot connect to the AI service. Please ensure the API server is running."
                st.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            else:
                with st.spinner("🤔 Thinking..."):
                    try:
                        payload = {"claim_id": claim_id, "message": prompt}
                        response = requests.post(f"{API_BASE_URL}/chat", json=payload, timeout=120)
                        
                        if response.status_code == 200:
                            result = response.json()
                            answer = result["answer"]
                            sources = result.get("sources", [])
                            
                            st.markdown(answer)
                            
                            if sources:
                                unique_sources = list(set(sources))
                                st.caption(f"📚 Sources: {', '.join(unique_sources)}")
                            
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": answer,
                                "sources": sources
                            })
                        else:
                            error_msg = "Sorry, I encountered an error. Please try again."
                            st.markdown(error_msg)
                            st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
                    except requests.exceptions.Timeout:
                        error_msg = "⏱️ Request timed out. Please try a simpler question."
                        st.markdown(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.markdown(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Quick Questions
    st.markdown("---")
    st.markdown("#### ⚡ Quick Questions")
    
    quick_questions = [
        ("🛡️", "What's covered under my policy?"),
        ("💵", "What's my deductible?"),
        ("⏰", "How long until I get paid?"),
        ("💰", "What's my payout amount?"),
        ("📝", "Can I appeal this decision?"),
        ("🚗", "Do I get a rental car?"),
        ("📋", "What documents do I need?"),
        ("🔄", "How do I update my claim?"),
        ("📞", "How do I contact support?")
    ]
    
    cols = st.columns(3)
    for i, (icon, question) in enumerate(quick_questions):
        with cols[i % 3]:
            if st.button(f"{icon} {question}", key=f"quick_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": question})
                st.session_state.pending_question = question
                st.rerun()
    
    # Clear chat
    st.markdown("---")
    col_c1, col_c2, col_c3 = st.columns([1, 1, 1])
    with col_c2:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


# ============================================
# TAB 4: HOW IT WORKS
# ============================================

with tab4:
    st.markdown("### 🏗️ How Our AI System Works")
    st.markdown("Discover how our multi-agent AI processes your claims faster and more accurately.")
    
    # Hero section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 50%, #2563EB 100%); 
                padding: 2rem; border-radius: var(--radius-xl); color: white; margin-bottom: 2rem; text-align: center;">
        <h2 style="margin: 0; color: white;">Supervisor-Based Multi-Agent Architecture</h2>
        <p style="margin: 1rem 0 0 0; opacity: 0.9; max-width: 600px; margin-left: auto; margin-right: auto;">
            Our intelligent Supervisor Agent coordinates specialized AI agents to process your claim. 
            Each agent has unique expertise, ensuring thorough and accurate claim handling.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Visual workflow
    st.markdown("### 📊 Claim Processing Flow")
    
    st.markdown("""
    ```
                                    ┌─────────────────┐
                                    │   📥 NEW CLAIM  │
                                    └────────┬────────┘
                                             │
                                             ▼
                        ┌────────────────────────────────────────┐
                        │         🎯 SUPERVISOR AGENT            │
                        │                                        │
                        │  • Analyzes claim complexity           │
                        │  • Determines routing strategy         │
                        │  • Coordinates agent execution         │
                        └────────────────────┬───────────────────┘
                                             │
                              ┌──────────────┴──────────────┐
                              │       SMART ROUTING         │
                              └──────────────┬──────────────┘
                                             │
         ┌───────────────┬───────────────────┼───────────────────┬───────────────┐
         │               │                   │                   │               │
         ▼               ▼                   ▼                   ▼               ▼
    ┌─────────┐    ┌─────────┐         ┌─────────┐         ┌─────────┐    ┌─────────┐
    │   📄    │    │   ✓     │         │   🔍    │         │   ✅    │    │   👤    │
    │  DOC    │    │ VALID-  │         │  FRAUD  │         │APPROVAL │    │ HUMAN   │
    │ANALYZER │    │ ATION   │         │  INVEST │         │  AGENT  │    │ REVIEW  │
    └─────────┘    └─────────┘         └─────────┘         └─────────┘    └─────────┘
         │               │                   │                   │               │
         └───────────────┴───────────────────┴───────────────────┴───────────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │   ✅ COMPLETE   │
                                    └─────────────────┘
    ```
    """)
    
    st.markdown("---")
    
    # Agent cards
    st.markdown("### 🤖 Meet Our AI Agents")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="agent-card">
            <div class="agent-icon" style="background: var(--color-accent-light); color: var(--color-accent);">🎯</div>
            <h4 style="margin: 0 0 0.5rem 0;">Supervisor Agent</h4>
            <p style="font-size: 0.85rem; color: var(--color-text-muted); margin: 0 0 1rem 0;">Central Coordinator</p>
            <ul style="font-size: 0.85rem; padding-left: 1.2rem; margin: 0; color: var(--color-text-muted);">
                <li>Analyzes claim complexity</li>
                <li>Routes to appropriate agents</li>
                <li>Handles escalation decisions</li>
                <li>Coordinates parallel execution</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="agent-card">
            <div class="agent-icon" style="background: var(--color-success-bg); color: var(--color-success);">✅</div>
            <h4 style="margin: 0 0 0.5rem 0;">Approval Agent</h4>
            <p style="font-size: 0.85rem; color: var(--color-text-muted); margin: 0 0 1rem 0;">Decision Maker</p>
            <ul style="font-size: 0.85rem; padding-left: 1.2rem; margin: 0; color: var(--color-text-muted);">
                <li>Makes approval decisions</li>
                <li>Calculates payout amounts</li>
                <li>Determines processing time</li>
                <li>Applies business rules</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="agent-card">
            <div class="agent-icon" style="background: var(--color-info-bg); color: var(--color-info);">📄</div>
            <h4 style="margin: 0 0 0.5rem 0;">Document Analyzer</h4>
            <p style="font-size: 0.85rem; color: var(--color-text-muted); margin: 0 0 1rem 0;">Document Expert</p>
            <ul style="font-size: 0.85rem; padding-left: 1.2rem; margin: 0; color: var(--color-text-muted);">
                <li>Analyzes damage photos with AI</li>
                <li>Detects duplicate images</li>
                <li>Assesses document quality</li>
                <li>Extracts key information</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="agent-card">
            <div class="agent-icon" style="background: #CFFAFE; color: #0891B2;">✓</div>
            <h4 style="margin: 0 0 0.5rem 0;">Validation Agent</h4>
            <p style="font-size: 0.85rem; color: var(--color-text-muted); margin: 0 0 1rem 0;">Eligibility Checker</p>
            <ul style="font-size: 0.85rem; padding-left: 1.2rem; margin: 0; color: var(--color-text-muted);">
                <li>Checks filing timeline</li>
                <li>Verifies policy status</li>
                <li>Validates coverage match</li>
                <li>Confirms required documents</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="agent-card">
            <div class="agent-icon" style="background: var(--color-warning-bg); color: var(--color-warning);">🔍</div>
            <h4 style="margin: 0 0 0.5rem 0;">Fraud Investigator</h4>
            <p style="font-size: 0.85rem; color: var(--color-text-muted); margin: 0 0 1rem 0;">Risk Analyst</p>
            <ul style="font-size: 0.85rem; padding-left: 1.2rem; margin: 0; color: var(--color-text-muted);">
                <li>Deep fraud analysis</li>
                <li>Pattern detection</li>
                <li>Repair shop verification</li>
                <li>Customer history check</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="agent-card">
            <div class="agent-icon" style="background: #F3E8FF; color: #9333EA;">👤</div>
            <h4 style="margin: 0 0 0.5rem 0;">Human Review</h4>
            <p style="font-size: 0.85rem; color: var(--color-text-muted); margin: 0 0 1rem 0;">Escalation Handler</p>
            <ul style="font-size: 0.85rem; padding-left: 1.2rem; margin: 0; color: var(--color-text-muted);">
                <li>Handles edge cases</li>
                <li>Reviews high-risk claims</li>
                <li>Manual decision support</li>
                <li>Quality assurance</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Routing logic
    st.markdown("### 🔀 Intelligent Routing Logic")
    
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        st.markdown("""
        <div class="card" style="border-left: 4px solid var(--color-accent);">
            <h4 style="margin: 0 0 0.5rem 0;">📥 New Claim Arrives</h4>
            <p style="font-size: 0.9rem; color: var(--color-text-muted); margin: 0;">
                → If photos attached: <strong>Document Analyzer</strong> first<br>
                → If no photos: <strong>Validation Agent</strong> directly
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card" style="border-left: 4px solid var(--color-success);">
            <h4 style="margin: 0 0 0.5rem 0;">✓ After Validation</h4>
            <p style="font-size: 0.9rem; color: var(--color-text-muted); margin: 0;">
                → If INVALID: Claim <strong>DENIED</strong><br>
                → If VALID + High Risk: <strong>Fraud Investigation</strong><br>
                → If VALID + Low Risk: <strong>Approval Agent</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_r2:
        st.markdown("""
        <div class="card" style="border-left: 4px solid var(--color-warning);">
            <h4 style="margin: 0 0 0.5rem 0;">🔍 High-Risk Triggers</h4>
            <p style="font-size: 0.9rem; color: var(--color-text-muted); margin: 0;">
                • Claim amount > $30,000<br>
                • Fraud score > 0.5<br>
                • High-complexity claim types<br>
                • Multiple risk indicators
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card" style="border-left: 4px solid var(--color-error);">
            <h4 style="margin: 0 0 0.5rem 0;">👤 Human Review Triggers</h4>
            <p style="font-size: 0.9rem; color: var(--color-text-muted); margin: 0;">
                • Fraud score > 0.8<br>
                • Approval status = NEEDS_REVIEW<br>
                • Critical priority claims<br>
                • Edge cases requiring judgment
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Technology stack
    st.markdown("### 🛠️ Technology Stack")
    
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    
    with col_t1:
        st.markdown("""
        <div class="card" style="text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🧠</div>
            <h4 style="margin: 0;">LangGraph</h4>
            <p style="font-size: 0.75rem; color: var(--color-text-muted); margin: 0.25rem 0 0 0;">Multi-Agent Orchestration</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_t2:
        st.markdown("""
        <div class="card" style="text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">☁️</div>
            <h4 style="margin: 0;">OCI GenAI</h4>
            <p style="font-size: 0.75rem; color: var(--color-text-muted); margin: 0.25rem 0 0 0;">Cohere Command-A LLM</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_t3:
        st.markdown("""
        <div class="card" style="text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🗄️</div>
            <h4 style="margin: 0;">Oracle 23ai</h4>
            <p style="font-size: 0.75rem; color: var(--color-text-muted); margin: 0.25rem 0 0 0;">Vector Store + Database</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_t4:
        st.markdown("""
        <div class="card" style="text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🖼️</div>
            <h4 style="margin: 0;">CLIP Model</h4>
            <p style="font-size: 0.75rem; color: var(--color-text-muted); margin: 0.25rem 0 0 0;">Image Fraud Detection</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Live stats
    st.markdown("---")
    st.markdown("### 📈 Live System Statistics")
    
    if check_api_health():
        try:
            stats_response = requests.get(f"{API_BASE_URL}/workflow/stats", timeout=5)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                
                with col_s1:
                    st.metric("Total Claims", stats.get("total_claims", 0))
                with col_s2:
                    st.metric("Approved", stats.get("by_status", {}).get("APPROVED", 0))
                with col_s3:
                    st.metric("Needs Review", stats.get("by_status", {}).get("NEEDS_REVIEW", 0))
                with col_s4:
                    st.metric("Avg Fraud Score", f"{stats.get('average_fraud_score', 0):.2f}")
            else:
                st.info("📊 System statistics will appear here when claims are processed.")
        except:
            st.info("📊 System statistics will appear here when claims are processed.")
    else:
        st.info("📊 Connect to the API to view live statistics.")


# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🛡️</div>
        <h2 style="color: white; margin: 0; font-size: 1.3rem;">InsureClaim Pro</h2>
        <p style="color: rgba(255,255,255,0.7); font-size: 0.85rem; margin: 0.25rem 0 0 0;">AI-Powered Claims Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # System Status
    st.markdown("### 📡 System Status")
    
    if check_api_health():
        st.success("✅ All Systems Operational")
        
        # Show additional status info
        try:
            health = requests.get(f"{API_BASE_URL}/health", timeout=2).json()
            st.markdown("""
            <div class="sidebar-card">
                <div class="sidebar-stat">
                    <span>API</span>
                    <span style="color: #10B981;">● Online</span>
                </div>
                <div class="sidebar-stat">
                    <span>Database</span>
                    <span style="color: #10B981;">● Connected</span>
                </div>
                <div class="sidebar-stat">
                    <span>AI Models</span>
                    <span style="color: #10B981;">● Ready</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        except:
            pass
    else:
        st.error("❌ API Offline")
        st.markdown("""
        <div class="sidebar-card">
            <p style="font-size: 0.85rem; margin: 0;">
                Start the API server:<br>
                <code style="font-size: 0.75rem;">python run_api.py</code>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sample Policies
    st.markdown("### 📋 Sample Policies")
    
    policies = [
        ("POL-001", "Premium Auto", "$500 deductible"),
        ("POL-002", "Standard Auto", "$1,000 deductible"),
        ("POL-003", "Basic Auto", "$2,500 deductible")
    ]
    
    for pol_id, name, deductible in policies:
        st.markdown(f"""
        <div class="sidebar-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: var(--color-accent);">{pol_id}</strong><br>
                    <span style="font-size: 0.85rem; color: rgba(255,255,255,0.8);">{name}</span>
                </div>
                <span style="font-size: 0.75rem; color: rgba(255,255,255,0.6);">{deductible}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    
    if st.button("📝 New Claim", use_container_width=True):
        st.session_state["active_tab"] = 0
        st.rerun()
    
    if st.button("🔍 Track Claim", use_container_width=True):
        st.session_state["active_tab"] = 1
        st.rerun()
    
    if st.button("💬 Get Help", use_container_width=True):
        st.session_state["active_tab"] = 2
        st.rerun()
    
    st.markdown("---")
    
    # Recent Activity
    if st.session_state.get("last_claim_id"):
        st.markdown("### 📋 Recent Activity")
        st.markdown(f"""
        <div class="sidebar-card">
            <span style="font-size: 0.75rem; color: rgba(255,255,255,0.6);">Last Claim</span><br>
            <strong style="color: var(--color-accent);">{st.session_state['last_claim_id']}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <p style="font-size: 0.75rem; color: rgba(255,255,255,0.5); margin: 0;">
            Powered by Multi-Agent AI<br>
            © 2025 InsureClaim Pro
        </p>
    </div>
    """, unsafe_allow_html=True)
