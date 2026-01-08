"""
Streamlit Frontend for Insurance Claims Processing
Enhanced UI with modern design
"""
import streamlit as st
import requests
from datetime import datetime, date
import json

# Configuration
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="InsureClaim Pro | AI-Powered Claims",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1E3A5F;
        --secondary-color: #3498db;
        --success-color: #27ae60;
        --warning-color: #f39c12;
        --danger-color: #e74c3c;
        --light-bg: #f8f9fa;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #3498db;
        margin-bottom: 1rem;
    }
    
    .metric-card.success { border-left-color: #27ae60; }
    .metric-card.warning { border-left-color: #f39c12; }
    .metric-card.danger { border-left-color: #e74c3c; }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .status-approved { background: #d4edda; color: #155724; }
    .status-pending { background: #fff3cd; color: #856404; }
    .status-denied { background: #f8d7da; color: #721c24; }
    .status-valid { background: #d4edda; color: #155724; }
    .status-invalid { background: #f8d7da; color: #721c24; }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f8f9fa;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: #1E3A5F !important;
        color: white !important;
    }
    
    /* Form styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Chat styling */
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 0.5rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E3A5F 0%, #2C5282 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    /* Progress indicator */
    .progress-step {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .step-circle {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #3498db;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 1rem;
    }
    
    .step-circle.completed { background: #27ae60; }
    .step-circle.pending { background: #bdc3c7; }
    
    /* Info cards */
    .info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #a1a1a1;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🛡️ InsureClaim Pro</h1>
    <p>AI-Powered Insurance Claims Processing Platform</p>
</div>
""", unsafe_allow_html=True)

# Create tabs with icons
tab1, tab2, tab3 = st.tabs(["📝 Submit Claim", "🔍 Track Claim", "💬 AI Assistant"])

# Tab 1: Submit Claim
with tab1:
    st.markdown("### 📋 New Claim Submission")
    st.markdown("Complete the form below to submit your insurance claim. Our AI system will process it instantly.")
    
    with st.form("claim_form"):
        # Policy & Dates Section
        st.markdown("#### 📌 Policy Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            policy_id = st.selectbox(
                "Select Policy",
                options=["POL-001", "POL-002", "POL-003"],
                help="Choose your active policy"
            )
        
        with col2:
            incident_date = st.date_input(
                "📅 Incident Date",
                value=date.today(),
                help="When did the incident occur?"
            )
        
        with col3:
            claim_date = st.date_input(
                "📅 Filing Date",
                value=date.today(),
                help="Today's date"
            )
        
        st.markdown("---")
        
        # Claim Details Section
        st.markdown("#### 🚗 Claim Details")
        col4, col5 = st.columns(2)
        
        with col4:
            claim_type = st.selectbox(
                "Claim Type",
                options=["collision", "comprehensive", "liability"],
                format_func=lambda x: x.title(),
                help="Select the type of claim"
            )
            
            estimated_amount = st.number_input(
                "💰 Estimated Damage ($)",
                min_value=0.0,
                max_value=100000.0,
                value=5000.0,
                step=100.0,
                help="Estimated cost of repairs"
            )
        
        with col5:
            repair_shop = st.text_input(
                "🔧 Repair Shop",
                placeholder="Enter preferred repair shop (optional)"
            )
            
            damage_description = st.text_area(
                "📝 Damage Description",
                placeholder="Describe the damage in detail...",
                height=100
            )
        
        st.markdown("---")
        
        # Documents Section
        st.markdown("#### 📎 Required Documents")
        col6, col7, col8 = st.columns(3)
        
        with col6:
            st.markdown("**📸 Damage Photos**")
            damage_photos = st.file_uploader(
                "Upload images",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                help="Upload clear photos of the damage",
                label_visibility="collapsed"
            )
            if damage_photos:
                st.success(f"✓ {len(damage_photos)} photo(s) uploaded")
        
        with col7:
            incident_report = st.text_area(
                "📄 Incident Report",
                placeholder="Describe what happened, when, where, and any witnesses...",
                height=120
            )
        
        with col8:
            repair_estimate = st.text_area(
                "💵 Repair Estimate",
                placeholder="Enter repair estimate details from the shop...",
                height=120
            )
        
        st.markdown("---")
        
        # Submit Button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submitted = st.form_submit_button("🚀 Submit Claim for Processing", use_container_width=True, type="primary")
        
        if submitted:
            if not damage_description:
                st.error("⚠️ Please provide a damage description")
            elif not incident_report:
                st.error("⚠️ Please provide an incident report")
            elif not repair_estimate:
                st.error("⚠️ Please provide a repair estimate")
            else:
                with st.spinner("🔄 Processing your claim with AI analysis..."):
                    try:
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
                                "repair_shop": repair_shop or "Unknown",
                                "estimated_damage_amount": estimated_amount,
                                "incident_report": incident_report,
                                "repair_estimate": repair_estimate
                            }
                            
                            response = requests.post(
                                f"{API_BASE_URL}/submit-claim-with-images",
                                data=data,
                                files=files
                            )
                        else:
                            payload = {
                                "policy_id": policy_id,
                                "incident_date": incident_date.isoformat(),
                                "claim_date": claim_date.isoformat(),
                                "claim_type": claim_type,
                                "damage_description": damage_description,
                                "repair_shop": repair_shop or "Unknown",
                                "estimated_damage_amount": estimated_amount,
                                "damage_photos": ["sample_photo.jpg"],
                                "incident_report": incident_report,
                                "repair_estimate": repair_estimate
                            }
                            
                            response = requests.post(f"{API_BASE_URL}/submit-claim", json=payload)
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            st.balloons()
                            st.success("🎉 Claim submitted and processed successfully!")
                            
                            if damage_photos:
                                st.info(f"🔍 {len(damage_photos)} image(s) analyzed with CLIP AI for fraud detection")
                            
                            # Results in cards
                            st.markdown("### 📊 Claim Results")
                            
                            col_r1, col_r2, col_r3 = st.columns(3)
                            
                            with col_r1:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h4 style="margin:0;color:#666;">Claim ID</h4>
                                    <h2 style="margin:0.5rem 0;color:#1E3A5F;">{result["claim_id"]}</h2>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col_r2:
                                status_class = "success" if result["validation_status"] == "VALID" else "danger"
                                st.markdown(f"""
                                <div class="metric-card {status_class}">
                                    <h4 style="margin:0;color:#666;">Validation</h4>
                                    <h2 style="margin:0.5rem 0;">{result["validation_status"]}</h2>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col_r3:
                                approval_class = "success" if result["approval_status"] == "APPROVED" else ("warning" if result["approval_status"] == "NEEDS_REVIEW" else "danger")
                                st.markdown(f"""
                                <div class="metric-card {approval_class}">
                                    <h4 style="margin:0;color:#666;">Approval</h4>
                                    <h2 style="margin:0.5rem 0;">{result["approval_status"]}</h2>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            col_r4, col_r5, col_r6 = st.columns(3)
                            
                            with col_r4:
                                st.metric("💰 Payout Amount", f"${result['payout_amount']:,.2f}")
                            with col_r5:
                                st.metric("📉 Deductible", f"${result['deductible']:,.2f}")
                            with col_r6:
                                st.metric("⏱️ Processing Days", result["processing_days"])
                            
                            # Fraud Score
                            if result.get("fraud_score"):
                                fraud_score = result['fraud_score']
                                st.markdown("### 🔒 Fraud Analysis")
                                col_f1, col_f2 = st.columns([1, 3])
                                with col_f1:
                                    st.metric("Risk Score", f"{fraud_score:.2f}")
                                with col_f2:
                                    if fraud_score >= 0.8:
                                        st.error("⚠️ High Risk - Manual review required")
                                    elif fraud_score >= 0.4:
                                        st.warning("⚡ Moderate Risk - Flagged for monitoring")
                                    else:
                                        st.success("✅ Low Risk - Auto-approved")
                            
                            st.session_state["last_claim_id"] = result["claim_id"]
                        else:
                            st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                    except requests.exceptions.ConnectionError:
                        st.error("⚠️ Cannot connect to API server. Please ensure the backend is running.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")


# Tab 2: Track Claim
with tab2:
    st.markdown("### 🔍 Track Your Claim")
    st.markdown("Enter your claim ID to view the current status and details.")
    
    col_search1, col_search2 = st.columns([3, 1])
    
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
    
    if search_clicked and claim_id_input:
        with st.spinner("🔄 Fetching claim details..."):
            try:
                response = requests.get(f"{API_BASE_URL}/claim/{claim_id_input}")
                
                if response.status_code == 200:
                    claim = response.json()
                    
                    # Claim Header
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1E3A5F 0%, #2C5282 100%); 
                                padding: 1.5rem; border-radius: 12px; color: white; margin: 1rem 0;">
                        <h2 style="margin:0;">Claim: {claim['claim_id']}</h2>
                        <p style="margin:0.5rem 0 0 0; opacity:0.9;">Policy: {claim.get('policy_id', 'N/A')} | Type: {claim.get('claim_type', 'N/A').title()}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Status Cards
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        validation = claim.get("validation_status", "PENDING")
                        icon = "✅" if validation == "VALID" else "❌"
                        st.markdown(f"""
                        <div class="metric-card {'success' if validation == 'VALID' else 'danger'}">
                            <h4 style="margin:0;color:#666;">Validation</h4>
                            <h2 style="margin:0.5rem 0;">{icon} {validation}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        approval = claim.get("approval_status", "PENDING")
                        icon = "✅" if approval == "APPROVED" else ("⏳" if approval == "NEEDS_REVIEW" else "❌")
                        status_class = "success" if approval == "APPROVED" else ("warning" if approval == "NEEDS_REVIEW" else "danger")
                        st.markdown(f"""
                        <div class="metric-card {status_class}">
                            <h4 style="margin:0;color:#666;">Approval</h4>
                            <h2 style="margin:0.5rem 0;">{icon} {approval}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4 style="margin:0;color:#666;">Payout</h4>
                            <h2 style="margin:0.5rem 0;color:#27ae60;">${claim.get('payout_amount', 0):,.2f}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4 style="margin:0;color:#666;">Processing</h4>
                            <h2 style="margin:0.5rem 0;">{claim.get('processing_time_days', 'N/A')} days</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Financial Details
                    st.markdown("### 💰 Financial Summary")
                    col_f1, col_f2, col_f3 = st.columns(3)
                    
                    with col_f1:
                        st.metric("Estimated Damage", f"${claim.get('estimated_damage_amount', 0):,.2f}")
                    with col_f2:
                        st.metric("Deductible", f"${claim.get('deductible', 0):,.2f}")
                    with col_f3:
                        st.metric("Net Payout", f"${claim.get('payout_amount', 0):,.2f}", 
                                  delta=f"-${claim.get('deductible', 0):,.2f} deductible")
                    
                    # Fraud Analysis
                    if claim.get("fraud_score"):
                        fraud_score = claim["fraud_score"]
                        st.markdown("### 🔒 Fraud Analysis")
                        
                        col_fraud1, col_fraud2 = st.columns([1, 4])
                        with col_fraud1:
                            # Color based on risk
                            if fraud_score < 0.4:
                                st.success(f"**{fraud_score:.2f}**")
                            elif fraud_score < 0.7:
                                st.warning(f"**{fraud_score:.2f}**")
                            else:
                                st.error(f"**{fraud_score:.2f}**")
                        
                        with col_fraud2:
                            progress_color = "green" if fraud_score < 0.4 else ("orange" if fraud_score < 0.7 else "red")
                            st.progress(fraud_score, text=f"Risk Level: {'Low' if fraud_score < 0.4 else ('Moderate' if fraud_score < 0.7 else 'High')}")
                    
                    # Details Sections
                    col_det1, col_det2 = st.columns(2)
                    
                    with col_det1:
                        with st.expander("📋 Validation Details", expanded=True):
                            st.info(claim.get("validation_reason", "No details available"))
                    
                    with col_det2:
                        with st.expander("✅ Approval Details", expanded=True):
                            st.info(claim.get("approval_reason", "No details available"))
                    
                    # Images Section
                    with st.expander("📸 Claim Images"):
                        try:
                            img_response = requests.get(f"{API_BASE_URL}/claim/{claim_id_input}/images")
                            if img_response.status_code == 200:
                                img_data = img_response.json()
                                if img_data["count"] > 0:
                                    st.success(f"Found {img_data['count']} image(s) with AI embeddings")
                                    
                                    cols = st.columns(min(3, img_data["count"]))
                                    for idx, img in enumerate(img_data["images"]):
                                        with cols[idx % 3]:
                                            img_url = f"{API_BASE_URL}/image/{img['image_id']}"
                                            st.image(img_url, caption=img["image_name"], use_container_width=True)
                                            st.caption(f"Type: {img['damage_type']}")
                                else:
                                    st.info("No images stored for this claim")
                        except Exception as e:
                            st.warning(f"Could not load images: {e}")
                    
                    # Full Details
                    with st.expander("📄 Full Claim Data (JSON)"):
                        st.json(claim)
                
                elif response.status_code == 404:
                    st.error("❌ Claim not found. Please check the claim ID and try again.")
                else:
                    st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
            
            except requests.exceptions.ConnectionError:
                st.error("⚠️ Cannot connect to API server. Please ensure the backend is running.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    elif search_clicked:
        st.warning("⚠️ Please enter a claim ID to search")


# Tab 3: Chatbot
with tab3:
    st.markdown("### 💬 AI Insurance Assistant")
    st.markdown("Ask questions about your policy, claim status, coverage, or any insurance-related queries.")
    
    # Claim ID input
    col_chat1, col_chat2 = st.columns([3, 1])
    with col_chat1:
        chat_claim_id = st.text_input(
            "🔗 Link to Claim (Optional)",
            value=st.session_state.get("last_claim_id", ""),
            placeholder="Enter claim ID for personalized answers",
            key="chat_claim_id"
        )
    with col_chat2:
        st.markdown("<br>", unsafe_allow_html=True)
        if chat_claim_id:
            st.success("✓ Linked")
        else:
            st.info("General mode")
    
    st.markdown("---")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Process pending question from quick buttons
    if "pending_question" in st.session_state and st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = None
        
        claim_id = st.session_state.get("chat_claim_id", None)
        if claim_id == "":
            claim_id = None
        
        try:
            payload = {"claim_id": claim_id, "message": question}
            response = requests.post(f"{API_BASE_URL}/chat", json=payload, timeout=120)
            if response.status_code == 200:
                result = response.json()
                st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
            else:
                st.session_state.messages.append({"role": "assistant", "content": "Sorry, I encountered an error."})
        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "🤖"):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("💬 Ask me anything about insurance..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)
        
        claim_id = st.session_state.get("chat_claim_id", None)
        if claim_id == "":
            claim_id = None
        
        with st.chat_message("assistant", avatar="🤖"):
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
                        
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        error_msg = "Sorry, I encountered an error. Please try again."
                        st.markdown(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                
                except requests.exceptions.ConnectionError:
                    error_msg = "⚠️ Cannot connect to API server."
                    st.markdown(error_msg)
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.markdown(error_msg)
    
    # Quick Questions Section
    st.markdown("---")
    st.markdown("#### ⚡ Quick Questions")
    
    quick_questions = [
        ("🛡️", "What's covered under my policy?"),
        ("💵", "What's my deductible?"),
        ("⏰", "When will I get paid?"),
        ("💰", "What's the payout amount?"),
        ("📝", "Can I appeal this decision?"),
        ("🚗", "Do I get a rental car?")
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
    col_clear1, col_clear2, col_clear3 = st.columns([1, 1, 1])
    with col_clear2:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# Enhanced Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="color: white; margin: 0;">🛡️</h1>
        <h2 style="color: white; margin: 0.5rem 0;">InsureClaim Pro</h2>
        <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">AI-Powered Claims Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # API Status
    st.markdown("### 📡 System Status")
    try:
        health = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if health.status_code == 200:
            st.success("✅ All Systems Operational")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ API Offline")
    
    st.markdown("---")
    
    # Policy Info
    st.markdown("### 📋 Sample Policies")
    
    st.markdown("""
    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
        <strong style="color: #3498db;">POL-001</strong><br>
        <span style="color: rgba(255,255,255,0.8); font-size: 0.85rem;">Comprehensive • $50K • $500 ded.</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
        <strong style="color: #f39c12;">POL-002</strong><br>
        <span style="color: rgba(255,255,255,0.8); font-size: 0.85rem;">Collision • $30K • $1000 ded.</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
        <strong style="color: #e74c3c;">POL-003</strong><br>
        <span style="color: rgba(255,255,255,0.8); font-size: 0.85rem;">Liability • Inactive</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Features
    st.markdown("### ✨ Features")
    st.markdown("""
    <ul style="color: rgba(255,255,255,0.9); padding-left: 1.2rem;">
        <li>🤖 AI-Powered Processing</li>
        <li>📸 Image Fraud Detection</li>
        <li>💬 Smart Chatbot</li>
        <li>⚡ Instant Decisions</li>
        <li>🔒 Secure & Compliant</li>
    </ul>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    <div style="text-align: center; color: rgba(255,255,255,0.6); font-size: 0.8rem;">
        <p>Powered by Oracle 23ai & OCI GenAI</p>
        <p>v2.0 • © 2026</p>
    </div>
    """, unsafe_allow_html=True)
