"""
Streamlit Frontend for Insurance Claims Processing
"""
import streamlit as st
import requests
from datetime import datetime, date
import json

# Configuration
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Insurance Claims Portal",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { padding: 10px 20px; }
    .success-box { padding: 20px; background-color: #d4edda; border-radius: 10px; margin: 10px 0; }
    .error-box { padding: 20px; background-color: #f8d7da; border-radius: 10px; margin: 10px 0; }
    .info-box { padding: 20px; background-color: #cce5ff; border-radius: 10px; margin: 10px 0; }
    .warning-box { padding: 20px; background-color: #fff3cd; border-radius: 10px; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🚗 Insurance Claims Portal")
st.markdown("---")

# Create tabs
tab1, tab2, tab3 = st.tabs(["📝 Submit Claim", "🔍 Track Claim", "💬 Chatbot"])

# Tab 1: Submit Claim
with tab1:
    st.header("Submit New Claim")
    
    with st.form("claim_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            policy_id = st.selectbox(
                "Policy ID",
                options=["POL-001", "POL-002", "POL-003"],
                help="Select your policy"
            )
            
            incident_date = st.date_input(
                "Incident Date",
                value=date.today(),
                help="Date when the incident occurred"
            )
            
            claim_type = st.selectbox(
                "Claim Type",
                options=["collision", "comprehensive", "liability"],
                help="Type of claim"
            )
            
            estimated_amount = st.number_input(
                "Estimated Damage Amount ($)",
                min_value=0.0,
                max_value=100000.0,
                value=5000.0,
                step=100.0
            )
        
        with col2:
            claim_date = st.date_input(
                "Claim Filing Date",
                value=date.today(),
                help="Date you are filing this claim"
            )
            
            repair_shop = st.text_input(
                "Repair Shop (Optional)",
                placeholder="Enter repair shop name"
            )
            
            damage_description = st.text_area(
                "Damage Description",
                placeholder="Describe the damage in detail...",
                height=100
            )
        
        st.subheader("Required Documents")
        col3, col4, col5 = st.columns(3)
        
        with col3:
            damage_photos = st.file_uploader(
                "Damage Photos",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                help="Upload photos of the damage"
            )
        
        with col4:
            incident_report = st.text_area(
                "Incident Report",
                placeholder="Describe what happened...",
                height=100
            )
        
        with col5:
            repair_estimate = st.text_area(
                "Repair Estimate",
                placeholder="Enter repair estimate details...",
                height=100
            )
        
        submitted = st.form_submit_button("🚀 Submit Claim", use_container_width=True)
        
        if submitted:
            if not damage_description:
                st.error("Please provide a damage description")
            elif not incident_report:
                st.error("Please provide an incident report")
            elif not repair_estimate:
                st.error("Please provide a repair estimate")
            else:
                with st.spinner("Processing your claim (this may take a moment for image analysis)..."):
                    try:
                        # Check if we have actual images to upload
                        if damage_photos:
                            # Use multipart form endpoint with actual images
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
                            # Use JSON endpoint without images
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
                            
                            st.success("✅ Claim submitted successfully!")
                            
                            # Show image vectorization info
                            if damage_photos:
                                st.info(f"📸 {len(damage_photos)} image(s) vectorized and stored in Oracle 23ai for fraud detection")
                            
                            # Display results
                            st.subheader("Claim Results")
                            
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                st.metric("Claim ID", result["claim_id"])
                                st.metric("Validation Status", result["validation_status"])
                                st.metric("Approval Status", result["approval_status"])
                            
                            with col_b:
                                st.metric("Payout Amount", f"${result['payout_amount']:,.2f}")
                                st.metric("Deductible", f"${result['deductible']:,.2f}")
                                st.metric("Processing Days", result["processing_days"])
                            
                            if result.get("fraud_score"):
                                fraud_score = result['fraud_score']
                                if fraud_score >= 0.8:
                                    st.error(f"⚠️ Fraud Score: {fraud_score:.2f} (High Risk - Possible duplicate images detected)")
                                elif fraud_score >= 0.4:
                                    st.warning(f"Fraud Score: {fraud_score:.2f} (Moderate Risk)")
                                else:
                                    st.success(f"Fraud Score: {fraud_score:.2f} (Low Risk)")
                            
                            st.info(f"**Validation:** {result['validation_reason']}")
                            st.info(f"**Approval:** {result['approval_reason']}")
                            
                            # Store claim ID in session
                            st.session_state["last_claim_id"] = result["claim_id"]
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                    except requests.exceptions.ConnectionError:
                        st.error("⚠️ Cannot connect to API server. Please ensure the backend is running.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# Tab 2: Track Claim
with tab2:
    st.header("Track Your Claim")
    
    # Pre-fill with last claim ID if available
    default_claim_id = st.session_state.get("last_claim_id", "")
    
    claim_id_input = st.text_input(
        "Enter Claim ID",
        value=default_claim_id,
        placeholder="CLM-XXXXXXXX"
    )
    
    if st.button("🔍 Track Claim", use_container_width=True):
        if claim_id_input:
            with st.spinner("Fetching claim details..."):
                try:
                    response = requests.get(f"{API_BASE_URL}/claim/{claim_id_input}")
                    
                    if response.status_code == 200:
                        claim = response.json()
                        
                        st.subheader(f"Claim: {claim['claim_id']}")
                        
                        # Status cards
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            status_color = "🟢" if claim.get("validation_status") == "VALID" else "🔴"
                            st.metric("Validation Status", f"{status_color} {claim.get('validation_status', 'PENDING')}")
                        
                        with col2:
                            approval = claim.get("approval_status", "PENDING")
                            if approval == "APPROVED":
                                status_color = "🟢"
                            elif approval == "DENIED":
                                status_color = "🔴"
                            else:
                                status_color = "🟡"
                            st.metric("Approval Status", f"{status_color} {approval}")
                        
                        with col3:
                            st.metric("Processing Days", claim.get("processing_time_days", "N/A"))
                        
                        st.markdown("---")
                        
                        # Financial details
                        col4, col5, col6 = st.columns(3)
                        
                        with col4:
                            st.metric("Estimated Damage", f"${claim.get('estimated_damage_amount', 0):,.2f}")
                        
                        with col5:
                            st.metric("Deductible", f"${claim.get('deductible', 0):,.2f}")
                        
                        with col6:
                            st.metric("Payout Amount", f"${claim.get('payout_amount', 0):,.2f}")
                        
                        # Fraud score
                        if claim.get("fraud_score"):
                            fraud_score = claim["fraud_score"]
                            if fraud_score < 0.4:
                                st.success(f"Fraud Score: {fraud_score:.2f} (Low Risk)")
                            elif fraud_score < 0.7:
                                st.warning(f"Fraud Score: {fraud_score:.2f} (Moderate Risk)")
                            else:
                                st.error(f"Fraud Score: {fraud_score:.2f} (High Risk)")
                        
                        # Validation results
                        st.subheader("Validation Details")
                        st.info(claim.get("validation_reason", "No details available"))
                        
                        # Approval reason
                        st.subheader("Approval Details")
                        st.info(claim.get("approval_reason", "No details available"))
                        
                        # Claim details expander
                        with st.expander("📋 Full Claim Details"):
                            st.json(claim)
                        
                        # Show claim images
                        with st.expander("📸 Claim Images"):
                            try:
                                img_response = requests.get(f"{API_BASE_URL}/claim/{claim_id_input}/images")
                                if img_response.status_code == 200:
                                    img_data = img_response.json()
                                    if img_data["count"] > 0:
                                        st.write(f"Found {img_data['count']} image(s) stored with CLIP embeddings")
                                        for img in img_data["images"]:
                                            col_img, col_info = st.columns([1, 2])
                                            with col_img:
                                                # Display image
                                                img_url = f"{API_BASE_URL}/image/{img['image_id']}"
                                                st.image(img_url, caption=img["image_name"], width=200)
                                            with col_info:
                                                st.write(f"**Image ID:** {img['image_id']}")
                                                st.write(f"**Damage Type:** {img['damage_type']}")
                                                st.write(f"**Uploaded:** {img['created_at']}")
                                    else:
                                        st.info("No images stored for this claim")
                            except Exception as e:
                                st.warning(f"Could not load images: {e}")
                    
                    elif response.status_code == 404:
                        st.error("Claim not found. Please check the claim ID.")
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                
                except requests.exceptions.ConnectionError:
                    st.error("⚠️ Cannot connect to API server. Please ensure the backend is running.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a claim ID")

# Tab 3: Chatbot
with tab3:
    st.header("Insurance Assistant Chatbot")
    
    # Claim ID for context
    chat_claim_id = st.text_input(
        "Claim ID (Optional - for claim-specific questions)",
        value=st.session_state.get("last_claim_id", ""),
        placeholder="CLM-XXXXXXXX",
        key="chat_claim_id"
    )
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Process pending question from quick buttons (must be before display)
    if "pending_question" in st.session_state and st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = None
        
        # Get claim_id from session state
        claim_id = st.session_state.get("chat_claim_id", None)
        if claim_id == "":
            claim_id = None
        
        # Make API call
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
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your claim or policy..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get claim_id from session state
        claim_id = st.session_state.get("chat_claim_id", None)
        if claim_id == "":
            claim_id = None
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    payload = {
                        "claim_id": claim_id,
                        "message": prompt
                    }
                    
                    response = requests.post(f"{API_BASE_URL}/chat", json=payload, timeout=120)
                    
                    if response.status_code == 200:
                        result = response.json()
                        answer = result["answer"]
                        sources = result.get("sources", [])
                        
                        st.markdown(answer)
                        
                        if sources:
                            st.caption(f"📚 Sources: {', '.join(sources)}")
                        
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        error_msg = "Sorry, I encountered an error. Please try again."
                        st.markdown(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                
                except requests.exceptions.ConnectionError:
                    error_msg = "⚠️ Cannot connect to API server. Please ensure the backend is running."
                    st.markdown(error_msg)
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.markdown(error_msg)
    
    # Quick question buttons
    st.markdown("---")
    st.subheader("Quick Questions")
    
    col1, col2, col3 = st.columns(3)
    
    quick_questions = [
        "What's covered under my policy?",
        "What's my deductible?",
        "When will I get paid?",
        "What's the payout amount?",
        "Can I appeal this decision?",
        "Do I get a rental car?"
    ]
    
    for i, question in enumerate(quick_questions):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.button(question, key=f"quick_{i}", use_container_width=True):
                # Add user message and set pending question
                st.session_state.messages.append({"role": "user", "content": question})
                st.session_state.pending_question = question
                st.rerun()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This portal allows you to:
    - **Submit** new insurance claims
    - **Track** existing claims
    - **Chat** with our AI assistant
    
    ---
    
    **Sample Policies:**
    - `POL-001`: Comprehensive ($50K limit, $500 deductible)
    - `POL-002`: Collision ($30K limit, $1000 deductible)
    - `POL-003`: Liability (Inactive)
    
    ---
    
    **API Status:**
    """)
    
    try:
        health = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if health.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ API Offline")
    
    st.markdown("---")
    st.caption("Insurance Claims Processing v1.0")
