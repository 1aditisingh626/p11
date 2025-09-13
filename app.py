# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import os


# ---------- File Paths ----------
DATA_DIR = "Data"
USERS_FILE = os.path.join(DATA_DIR, "users_db.xlsx")
VENDORS_FILE = os.path.join(DATA_DIR, "vendors_db.xlsx")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products_db.xlsx")
COMPLAINTS_FILE = os.path.join(DATA_DIR, "complaints_db.xlsx")
REVIEWS_FILE = os.path.join(DATA_DIR, "rexiews_db.xlsx")
# ---------- Helper Functions ----------

def load_data(file_path):
    return pd.read_excel(file_path)

def save_data(df, file_path):
    df.to_excel(file_path, index=False)

def generate_new_id(df, column_name, prefix):
    if df.empty:
        return f"{prefix}001"
    else:
        nums = df[column_name].str.replace(prefix, "").astype(int)
        new_num = nums.max() + 1
        return f"{prefix}{new_num:03d}"

# Load all data
users_df = load_data(USERS_FILE)
vendors_df = load_data(VENDORS_FILE)
products_df = load_data(PRODUCTS_FILE)
complaints_df = load_data(COMPLAINTS_FILE)
reviews_df = load_data(REVIEWS_FILE)

# ---------- Pages ----------



def page_home():
    st.title("🌟 Customer Feedback & Analytics Hub")
    st.markdown("""
    <h3 style='text-align:center; color:#16A085; font-family:Arial;'>
    Submit complaints • Track status • Vendor insights • Analytics
    </h3>
    """, unsafe_allow_html=True)

    # ----------------- About Section -----------------
    st.markdown(
        """
        <div style="
            background-color:#f8f9fc;
            padding:20px;
            border-radius:10px;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
            text-align:center;
            font-family: 'Trebuchet MS', sans-serif;
        ">
            <h2 style='color:#4e73df;'>About This Website</h2>
            <p style='font-size:16px; color:#5a5c69;'>
                Welcome to our Customer Feedback Platform! This platform allows Indian customers to:
            </p>
            <ul style='text-align:left; display:inline-block; color:#5a5c69;'>
                <li>Submit complaints about products and services</li>
                <li>Submit reviews and ratings</li>
                <li>Track complaint status in real-time</li>
                <li>View vendor performance and analytics</li>
                <li>Get insights through KPIs and charts</li>
            </ul>
            <p style='font-style:italic; color:#858796;'>Empowering customers and vendors through transparency and data-driven insights.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ----------------- Compute KPIs -----------------
    total_complaints = len(complaints_df)
    resolved_complaints = complaints_df[complaints_df['complaint_status'].str.lower() == 'resolved'].shape[0]
    pending_complaints = complaints_df[complaints_df['complaint_status'].str.lower() == 'pending'].shape[0]
    avg_rating = reviews_df['rating'].mean() if not reviews_df.empty else 0
    total_users = len(users_df)
    total_vendors = len(vendors_df)

    # Top 5 most insightful KPIs
    kpi_data = [
        ("Total Complaints", total_complaints, "#f6c23e"),
        ("Resolved Complaints", resolved_complaints, "#1cc88a"),
        ("Pending Complaints", pending_complaints, "#e74a3b"),
        ("Average Rating", round(avg_rating, 2), "#36b9cc"),
        ("Total Users", total_users, "#858796"),
    ]
    # ----------------- Quick Stats (smaller KPI cards) -----------------
    st.markdown("### Quick Stats")
    cols = st.columns(len(kpi_data))
    for col, (title, value, color) in zip(cols, kpi_data):
        col.markdown(
            f"""
            <div style="
                background-color:{color};
                padding:10px;
                border-radius:8px;
                box-shadow: 1px 1px 3px rgba(0,0,0,0.2);
                text-align:center;
            ">
                <h5 style='color:white; margin:5px 0;'>{title}</h5>
                <h3 style='color:white; margin:0;'>{value}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ----------------- Recent Complaints -----------------
    st.markdown("### 📝 Recent Complaints")
    if not complaints_df.empty:
        recent_complaints = complaints_df.sort_values("complaint_date", ascending=False).head(5)
        # Replace IDs with names
        recent_complaints_display = recent_complaints.copy()
        recent_complaints_display["user_id"] = recent_complaints_display["user_id"].map(
            dict(zip(users_df["user_id"], users_df["name"]))
        )
        recent_complaints_display["product_id"] = recent_complaints_display["product_id"].map(
            dict(zip(products_df["product_id"], products_df["product_name"]))
        )
        recent_complaints_display["vendor_id"] = recent_complaints_display["vendor_id"].map(
            dict(zip(vendors_df["vendor_id"], vendors_df["vendor_name"]))
        )
        st.dataframe(recent_complaints_display[["complaint_id","user_id","product_id","vendor_id","complaint_status"]])
    else:
        st.info("No complaints yet.")

# ---------- Submit Complaint ----------
def page_submit_complaint():
    st.subheader("📝 Submit a Complaint")

    # Option to select existing user or enter new one
    user_choice = st.radio("Select User Option", ["Existing User", "New User"])
    if user_choice == "Existing User":
        user_name = st.selectbox("Select User", users_df['name'])
        user_id = users_df[users_df['name'] == user_name]['user_id'].values[0]
    else:
        user_name = st.text_input("Enter Your Name")
        if user_name.strip() != "":
            # Generate new user_id
            new_user_id = generate_new_id(users_df, "user_id", "U")
            users_df.loc[len(users_df)] = {
                "user_id": new_user_id,
                "name": user_name,
                "state": "Unknown"  # default
            }
            save_data(users_df, USERS_FILE)
            user_id = new_user_id
        else:
            st.warning("Please enter a valid name")
            return

    # Select product by name
    product_name = st.selectbox("Select Product", products_df['product_name'])
    product_row = products_df[products_df['product_name'] == product_name].iloc[0]
    product_id = product_row['product_id']
    vendor_id = product_row['vendor_id']
    fssai_code = product_row.get('fssai_code', 'N/A')   # <-- fetch FSSAI Code

    # Display vendor + FSSAI info
    vendor_name = vendors_df[vendors_df['vendor_id'] == vendor_id]['vendor_name'].values[0]
    st.text(f"Vendor: {vendor_name}")
    st.text(f"FSSAI Code: {fssai_code}")   # <-- show FSSAI code

    complaint_text = st.text_area("Your Complaint")
    complaint_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    complaint_status = st.selectbox("Status", ["Pending", "Resolved"])

    if st.button("Submit Complaint"):
        new_id = generate_new_id(complaints_df, "complaint_id", "C")
        new_row = {
            "complaint_id": new_id,
            "user_id": user_id,
            "product_id": product_id,
            "vendor_id": vendor_id,
            "fssai_code": fssai_code,     # <-- save FSSAI code with complaint
            "complaint_text": complaint_text,
            "complaint_status": complaint_status,
            "complaint_priority": complaint_priority,
            "complaint_date": datetime.now(),
            "complaint_image_url": ""
        }
        complaints_df.loc[len(complaints_df)] = new_row
        save_data(complaints_df, COMPLAINTS_FILE)
        st.success("Complaint submitted successfully!")


# ---------- Submit Review ----------
def page_submit_review():
    st.subheader("📝 Submit a Review")

    # Option to select existing user or enter new one
    user_choice = st.radio("Select User Option", ["Existing User", "New User"])
    if user_choice == "Existing User":
        user_name = st.selectbox("Select User", users_df['name'])
        user_id = users_df[users_df['name']==user_name]['user_id'].values[0]
    else:
        user_name = st.text_input("Enter Your Name")
        if user_name.strip() != "":
            # Generate new user_id
            new_user_id = generate_new_id(users_df, "user_id", "U")
            users_df.loc[len(users_df)] = {
                "user_id": new_user_id,
                "name": user_name,
                "state": "Unknown"  # default, can be extended later
            }
            save_data(users_df, USERS_FILE)
            user_id = new_user_id
        else:
            st.warning("Please enter a valid name")
            return

    # Select product by name
    product_name = st.selectbox("Select Product", products_df['product_name'])
    product_row = products_df[products_df['product_name']==product_name].iloc[0]
    product_id = product_row['product_id']
    vendor_id = product_row['vendor_id']

    # Display vendor name for info
    vendor_name = vendors_df[vendors_df['vendor_id']==vendor_id]['vendor_name'].values[0]
    st.text(f"Vendor: {vendor_name}")

    rating = st.slider("Rating (1-5)", 1, 5, 5)
    review_text = st.text_area("Your Review")
    review_sentiment = st.selectbox("Sentiment", ["Positive", "Neutral", "Negative"])

    if st.button("Submit Review"):
        new_id = generate_new_id(reviews_df, "review_id", "R")
        new_row = {
            "review_id": new_id,
            "user_id": user_id,
            "product_id": product_id,
            "vendor_id": vendor_id,
            "rating": rating,
            "review_text": review_text,
            "review_date": datetime.now(),
            "review_sentiment": review_sentiment
        }
        reviews_df.loc[len(reviews_df)] = new_row
        save_data(reviews_df, REVIEWS_FILE)
        st.success("Review submitted successfully!")


# ---------- Track Complaints ----------
def page_track_complaints():
    st.subheader("📊 Track Complaints")

    # Display complaints with user, product, and vendor names instead of IDs
    display_df = complaints_df.copy()
    display_df['user_name'] = display_df['user_id'].map(dict(zip(users_df['user_id'], users_df['name'])))
    display_df['product_name'] = display_df['product_id'].map(
        dict(zip(products_df['product_id'], products_df['product_name'])))
    display_df['vendor_name'] = display_df['vendor_id'].map(
        dict(zip(vendors_df['vendor_id'], vendors_df['vendor_name'])))

    display_df = display_df[['complaint_id', 'user_name', 'product_name', 'vendor_name',
                             'complaint_text', 'complaint_status', 'complaint_priority', 'complaint_date']]

    # Show the complaints table
    st.dataframe(display_df)

    # Select a complaint to update
    selected_id = st.selectbox("Select Complaint to Update Status", display_df['complaint_id'])
    current_status = complaints_df.loc[complaints_df['complaint_id'] == selected_id, 'complaint_status'].values[0]

    new_status = st.selectbox("Update Status", ["Pending", "Resolved"], index=0 if current_status == "Pending" else 1)

    if st.button("Update Status"):
        complaints_df.loc[complaints_df['complaint_id'] == selected_id, 'complaint_status'] = new_status
        save_data(complaints_df, COMPLAINTS_FILE)
        st.success(f"Complaint {selected_id} status updated to {new_status}!")


# ---------- Vendor Dashboard ----------
# ---------- Vendor Dashboard ----------
def page_vendor_dashboard():
    st.subheader("🏭 Vendor Dashboard")

    # Select a vendor
    vendor_name = st.selectbox("Select Vendor", vendors_df['vendor_name'])
    vendor_row = vendors_df[vendors_df['vendor_name'] == vendor_name].iloc[0]
    vendor_id = vendor_row['vendor_id']

    # Filter complaints and reviews
    vendor_complaints = complaints_df[complaints_df['vendor_id'] == vendor_id]
    vendor_reviews = reviews_df[reviews_df['vendor_id'] == vendor_id]

    # Calculate KPIs
    total_complaints = vendor_complaints.shape[0]
    resolved_complaints = vendor_complaints[vendor_complaints['complaint_status'] == 'Resolved'].shape[0]
    pending_complaints = total_complaints - resolved_complaints
    avg_rating = round(vendor_reviews['rating'].dropna().mean(), 2) if not vendor_reviews.empty else 0

    # Compact KPI cards
    kpi_html = f"""
    <div style="display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap;">
        <div style="flex:1; min-width:90px; background-color:#3498db; color:white; padding:10px; border-radius:10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); text-align:center;">
            <h4>Total Complaints</h4>
            <h2>{total_complaints}</h2>
        </div>
        <div style="flex:1; min-width:90px; background-color:#2ecc71; color:white; padding:10px; border-radius:10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); text-align:center;">
            <h4>Resolved</h4>
            <h2>{resolved_complaints}</h2>
        </div>
        <div style="flex:1; min-width:90px; background-color:#e67e22; color:white; padding:10px; border-radius:10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); text-align:center;">
            <h4>Pending</h4>
            <h2>{pending_complaints}</h2>
        </div>
        <div style="flex:1; min-width:90px; background-color:#9b59b6; color:white; padding:10px; border-radius:10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); text-align:center;">
            <h4>Avg. Rating</h4>
            <h2>{avg_rating}</h2>
        </div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)
    st.markdown("---")

    # Detailed complaints and reviews
    st.subheader("Complaints")
    if not vendor_complaints.empty:
        display_complaints = vendor_complaints[['complaint_id', 'user_id', 'product_id', 'complaint_text', 'complaint_status', 'complaint_priority', 'complaint_date']]
        st.dataframe(display_complaints)
    else:
        st.write("No complaints for this vendor.")

    st.subheader("Reviews")
    if not vendor_reviews.empty:
        display_reviews = vendor_reviews[['review_id', 'user_id', 'product_id', 'rating', 'review_text', 'review_sentiment', 'review_date']]
        st.dataframe(display_reviews)
    else:
        st.write("No reviews for this vendor.")


# ---------- Analytics Page ----------
import plotly.express as px
# ---------- Analytics Page ----------
def page_analytics():
    st.subheader("📈 Analytics Dashboard")

    # KPIs
    total_complaints = complaints_df.shape[0]
    resolved_complaints = complaints_df[complaints_df['complaint_status'] == 'Resolved'].shape[0]
    pending_complaints = total_complaints - resolved_complaints
    avg_rating = round(reviews_df['rating'].mean(), 2) if not reviews_df.empty else 0
    total_users = users_df.shape[0]
    total_vendors = vendors_df.shape[0]

    kpis = [
        {"label": "Total Complaints", "value": total_complaints, "color": "#FF6B6B"},
        {"label": "Resolved Complaints", "value": resolved_complaints, "color": "#1DD1A1"},
        {"label": "Pending Complaints", "value": pending_complaints, "color": "#FDCB6E"},
        {"label": "Average Rating", "value": avg_rating, "color": "#5DADE2"},
        {"label": "Total Users", "value": total_users, "color": "#A29BFE"}
    ]

    cols = st.columns(len(kpis))
    for idx, kpi in enumerate(kpis):
        cols[idx].markdown(f"""
        <div style='padding:10px; text-align:center; border-radius:10px; 
                        background-color:{kpi['color']}; box-shadow: 2px 2px 5px gray;'>
            <h4 style='margin:0; font-size:18px;'>{kpi['label']}</h4>
            <h3 style='margin:0; font-size:24px;'>{kpi['value']}</h3>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Top 5 products by complaints
    top_products = complaints_df.groupby("product_id").size().sort_values(ascending=False).head(5)
    top_products = top_products.reset_index().merge(products_df[['product_id', 'product_name']], on='product_id')
    fig1 = px.bar(top_products, x='product_name', y=0, color='product_name', title="Top 5 Products by Complaints")
    st.plotly_chart(fig1, use_container_width=True)

    # Top 5 vendors by complaints
    top_vendors = complaints_df.groupby("vendor_id").size().sort_values(ascending=False).head(5)
    top_vendors = top_vendors.reset_index().merge(vendors_df[['vendor_id', 'vendor_name']], on='vendor_id')
    fig2 = px.bar(top_vendors, x='vendor_name', y=0, color='vendor_name', title="Top 5 Vendors by Complaints")
    st.plotly_chart(fig2, use_container_width=True)

    # Top 5 products by average rating
    if not reviews_df.empty:
        top_rated = reviews_df.groupby("product_id")['rating'].mean().sort_values(ascending=False).head(5)
        top_rated = top_rated.reset_index().merge(products_df[['product_id', 'product_name']], on='product_id')
        fig3 = px.bar(top_rated, x='product_name', y='rating', color='product_name', title="Top 5 Products by Rating")
        st.plotly_chart(fig3, use_container_width=True)


# ---------- Chatbot Page ----------

# ---------- Chatbot FAQs ----------
faq = {
    # English
    "en": {
        "hello": "Hello! How can I help you today?",
        "hi": "Hi there! How can I assist you?",
        "help": "You can submit complaints, reviews, track complaints, view analytics, or get vendor info.",
        "submit complaint": "Go to 'Submit Complaint' page to lodge a new complaint.",
        "submit review": "Go to 'Submit Review' page to add a product review.",
        "track complaints": "Go to 'Track Complaints' page to see complaint status.",
        "vendor dashboard": "Go to 'Vendor Dashboard' page to see vendor stats.",
        "analytics": "Go to 'Analytics' page to view KPIs and charts.",
        "quick stats": "Total complaints, resolved complaints, pending complaints, avg. ratings, total users, total vendors.",
        "thank you": "You're welcome!",
        "bye": "Goodbye! Have a great day!"
    },

    # Hindi
    "hi": {
        "hello": "नमस्ते! मैं आपकी कैसे मदद कर सकता हूँ?",
        "hi": "हाय! मैं आपकी कैसे सहायता करूँ?",
        "help": "आप शिकायत दर्ज कर सकते हैं, समीक्षा जोड़ सकते हैं, शिकायतें ट्रैक कर सकते हैं, एनालिटिक्स देख सकते हैं, या विक्रेता जानकारी प्राप्त कर सकते हैं।",
        "submit complaint": "नया शिकायत दर्ज करने के लिए 'Submit Complaint' पेज पर जाएँ।",
        "submit review": "उत्पाद समीक्षा जोड़ने के लिए 'Submit Review' पेज पर जाएँ।",
        "track complaints": "'Track Complaints' पेज पर जाकर शिकायत स्थिति देखें।",
        "vendor dashboard": "'Vendor Dashboard' पेज पर जाकर विक्रेता आँकड़े देखें।",
        "analytics": "KPIs और चार्ट देखने के लिए 'Analytics' पेज पर जाएँ।",
        "quick stats": "कुल शिकायतें, हल की गई शिकायतें, लंबित शिकायतें, औसत रेटिंग, कुल उपयोगकर्ता, कुल विक्रेता।",
        "thank you": "आपका स्वागत है!",
        "bye": "अलविदा! आपका दिन शुभ हो!"
    }
}


def chatbot_response(user_input, lang="en"):
    user_input = user_input.lower()

    # Match keywords in FAQ
    for key in faq[lang].keys():
        if key in user_input:
            return faq[lang][key]

    # Default response if no match
    if lang == "hi":
        return "माफ़ कीजिये, मैं इसे समझ नहीं पाया। कृपया पुनः प्रयास करें।"
    return "Sorry, I didn't understand that. Please try again."


def page_chatbot():
    st.subheader("💬 Chatbot Support")

    # Language selection
    lang = st.radio("Select Language / भाषा चुनें", ["English", "Hindi"], horizontal=True)
    lang_code = "en" if lang == "English" else "hi"

    st.markdown("**Example Questions / उदाहरण प्रश्न:**")

    # FAQ section using expander (scrollable & compact)
    with st.expander("Click to see example questions / उदाहरण प्रश्न देखें"):
        example_questions = list(faq[lang_code].keys())[:8]  # top 8 FAQ
        for question in example_questions:
            if st.button(question.capitalize(), key=f"faq_{question}"):
                response = faq[lang_code][question]
                st.text_area("Chatbot Response / चैटबॉट जवाब", value=response, height=100)

    # User input for custom questions
    user_input = st.text_input("Type your question here / यहाँ अपना प्रश्न लिखें")
    if st.button("Send", key="send_custom"):
        if user_input.strip() != "":
            response = chatbot_response(user_input, lang_code)
            st.text_area("Chatbot Response / चैटबॉट जवाब", value=response, height=100)
        else:
            st.warning("Please type a question / कृपया एक प्रश्न टाइप करें")


def page_powerbi():
    st.subheader("📊 Power BI Dashboard")

    st.markdown("Paste your Power BI report embed link below (or see the demo):")

    # Input textbox for Power BI link
    powerbi_link = st.text_input("Power BI Embed Link")

    # Default demo dashboard link (replace with any valid embed link)
    demo_link = "https://app.powerbi.com/view?r=eyJrIjoiZDEyMzQ1Ni0xMjM0LTQ1NjctOTg3Ni0xMjM0NTY3ODkwMTIiLCJrZXkiOiJhYmNkZWYxMjMifQ%3D%3D"

    final_link = powerbi_link if powerbi_link else demo_link

    try:
        # Embed the Power BI report in an iframe
        st.markdown(
            f"""
            <iframe 
                width="100%" 
                height="600" 
                src="{final_link}" 
                frameborder="0" 
                allowFullScreen="true">
            </iframe>
            """,
            unsafe_allow_html=True
        )
        if not powerbi_link:
            st.info("Showing demo Power BI dashboard. Paste your own link above to view your report.")
    except Exception as e:
        st.error(f"Error displaying dashboard: {e}")

# ---------- Sidebar ----------
page = st.sidebar.selectbox("Go to", [
    "Home",
    "Submit Complaint",
    "Submit Review",
    "Track Complaint",
    "Vendor Dashboard",
    "Analytics",
    "Chatbot",
    "Power BI"
])

# ---------- Page Routing ----------
if page == "Home":
    page_home()
elif page == "Submit Complaint":
    page_submit_complaint()
elif page == "Submit Review":
    page_submit_review()
elif page == "Track Complaint":
    page_track_complaints()
elif page == "Vendor Dashboard":
    page_vendor_dashboard()
elif page == "Analytics":
    page_analytics()
elif page == "Chatbot":
    page_chatbot()
elif page == "Power BI":
    page_powerbi()