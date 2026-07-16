import streamlit as st

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Dewi Tri Lestari | Data Portfolio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling tweaks
st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        background-color: #EEF2F6;
        color: #1E293B;
        border-radius: 0.375rem;
        font-size: 0.85rem;
        font-weight: 500;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# 2. SIDEBAR NAVIGATION & CONTACT QUICK LINKS
with st.sidebar:
    st.markdown("## Navigation")
    page = st.radio("Go to", ["Home & About", "Experience & Education", "Projects Gallery", "Contact Me"])
    
    st.markdown("---")
    st.markdown("### Quick Links")
    st.markdown("🔗 [LinkedIn](https://www.linkedin.com/in/dewitrilestari/)")
    st.markdown("💻 [GitHub Portfolio](https://github.com/dewitrilestari/Portofolio)")
    st.markdown("✉️ [Email](mailto:dewitrilestari135@gmail.com)")
    st.markdown("📞 [WhatsApp](https://wa.me/6285643468310)")
    
    st.markdown("---")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cv_file_path = os.path.join(current_dir, "CV.pdf")

    # Safely read and serve the PDF
    try:
        with open(cv_file_path, "rb") as f:
            pdf_data = f.read()
    except FileNotFoundError:
        pdf_data = b"CV file not found on server."

    # In your sidebar or wherever you place the button:
    st.download_button(
        label="📄 Download Full CV",
        data=pdf_data,
        file_name="Dewi_Tri_Lestari_CV.pdf",
        mime="application/pdf"
    )

# 3. PAGE CONTENT CONTEXT

# --- PAGE: HOME & ABOUT ---
if page == "Home & About":
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        st.title("Dewi Tri Lestari")
        st.subheader("Data Analyst & Data Science Enthusiast")
        
        st.markdown("""
        A recent **Geophysics graduate from Gadjah Mada University** with a passion for pursuing a professional track in business management, analytical systems, and scalable operations. Highly adaptive and disciplined with proven capabilities directing cross-functional teams and operational timelines.
        
        I specialize in turning unstructured telemetry and data records into clear, actionable business strategies using Python, SQL frameworks, and intuitive Business Intelligence layouts.
        """)
        
        st.markdown("### Core Focus Areas")
        c1, c2, c3 = st.columns(3)
        c1.metric(label="UGM Cumulative GPA", value="3.75 / 4.00")
        c2.metric(label="Max Dataset Rows Handled", value="600,000+")
        c3.metric(label="Languages", value="ID (Native), EN")

    with col2:
        # Informative box highlighting core technological capabilities
        st.info("""
        **🚀 Technical Skillsets:**
        * **Languages:** Python, SQL
        * **Data Analysis:** Microsoft Power BI, MetaBase, Excel
        * **Frameworks/Libraries:** Jupyter Lab, PYGIMLI, Streamlit
        * **GIS & Spatial:** ArcMap 10.8
        * **Operations:** Budget Management, Project Coordination, Document Control
        """)

# --- PAGE: EXPERIENCE & EDUCATION ---
elif page == "Experience & Education":
    st.title("Work & Leadership Timeline")
    
    tab1, tab2 = st.tabs(["Professional Experience", "Education History"])
    
    with tab1:
        st.markdown("#### Data Analyst and Data Scientist Intern")
        st.caption("📆 **April 2026 - June 2026** | *BLKPP DIY (Balai Latihan Kerja dan Pengembangan Produktivitas)*")
        st.markdown("""
        * Leveraged **SQL** and **Python** algorithms to drive extraction, comprehensive cleaning pipelines, and optimization structural layers over **600,000+ operational rows**.
        * Architected **4 high-fidelity interactive Business Intelligence dashboards** via Power BI and MetaBase to track operational KPIs.
        * Engineered and deployed **1 production-level recommendation engine** via Machine Learning protocols, integrating an automated **Telegram chatbot** extension to enhance accessibility.
        """)
        
        st.markdown("---")
        st.markdown("#### Undergraduate Thesis Student (Internship)")
        st.caption("📆 **August 2024 - May 2026** | *Danone AQUA*")
        st.markdown("""
        * Programmed custom **Python inversion scripts** utilizing the `PYGIMLI` module inside Jupyter Lab to model and interpret 1D Vertical Electrical Sounding data across **37 hydrogeological research targets**.
        * Processed digital elevation models (DEM) to produce **5 full-scale regional maps** (geology, hydrology matrices, and groundwater basins) using ArcMap 10.8.
        """)
        
        st.markdown("---")
        st.markdown("#### Acquisition Team Leader")
        st.caption("📆 **July 2024 - November 2024** | *Universitas Pembangunan Nasional Veteran Yogyakarta*")
        st.markdown("""
        * Directed logistical field operations and team distributions across 2 discrete geological survey zones (Secang and Paliyan).
        * Maintained full accountability for field asset data integrity covering **15 VES points** and **2 linear resistivity lines**.
        """)

        st.markdown("---")
        st.markdown("#### Head of Course and Workshop Division")
        st.caption("📆 **September 2022 - September 2023** | *Society of Exploration Geophysicists UGM Student Chapter (SEG UGM SC)*")
        st.markdown("""
        * Led an internal division of 8 team members to successfully orchestrate **4 technical workshops and national seminars**.
        * Allocated operational event funds (~IDR 700,000 per event) while controlling milestone structural schedules.
        """)

    with tab2:
        st.markdown("#### 🎓 Universitas Gadjah Mada (UGM)")
        st.caption("📆 **2020 - 2026**")
        st.write("**Bachelor of Science - Geophysics**")
        st.write("📊 *GPA: 3.75 / 4.00*")
        
        st.markdown("---")
        st.markdown("#### 🏫 SMA N 7 Yogyakarta")
        st.caption("📆 **2017 - 2020**")
        st.write("**Senior High School - Mathematics and Natural Sciences (MIPA)**")

# --- PAGE: PROJECTS GALLERY ---
elif page == "Projects Gallery":
    st.title("Interactive Work Portfolio")
    st.markdown("Filter through current machine learning models, engineering pipelines, and analytical tools.")
    
    # Dynamic Category Selector Filter
    category_filter = st.selectbox(
        "Choose Category Focus:", 
        ["All Projects", "Data Science & Machine Learning", "Data Analysis & Time Series"]
    )
    
    # Storage structure containing the specific project metrics
    projects = [
        {
            "title": "Membangun Sistem Rekomendasi: Dari Teori Association Rules hingga Implementasi Aplikasi Streamlit",
            "category": "Data Science & Machine Learning",
            "desc": "Built an interactive e-commerce product engine applying complex rule sets. Deployed out to end-users via clean modular web application environments.",
            "stack": ["Python", "Streamlit", "ML Pipelines"],
            "link": "https://github.com/dewitrilestari/Portofolio"
        },
        {
            "title": "Analyzing Public Sentiment on the Indonesian Rupiah",
            "category": "Data Science & Machine Learning",
            "desc": "Extracted and text-mined social data landscapes reflecting economic updates of IDR. Modeled target classification structures using NLP libraries.",
            "stack": ["Python", "NLP", "SQL Data Streams"],
            "link": "https://github.com/dewitrilestari/Portofolio"
        },
        {
            "title": "Dashboard Forecasting Curah Hujan Harian BMKG (LSTM)",
            "category": "Data Analysis & Time Series",
            "desc": "Constructed an experimental recurrent time-series network (LSTM) predicting continuous daily precipitation shifts, mapping outcomes directly to dynamic analytics visualizers.",
            "stack": ["Deep Learning (LSTM)", "Power BI", "Python"],
            "link": "https://github.com/dewitrilestari/Portofolio"
        }
    ]
    
    # Filtering Logic Execution
    filtered_projects = [
        p for p in projects 
        if category_filter == "All Projects" or p["category"] == category_filter
    ]
    
    # Layout rendering dynamically based on rows
    if filtered_projects:
        for idx, proj in enumerate(filtered_projects):
            with st.container():
                st.markdown(f"### {proj['title']}")
                st.caption(f"📁 **Category:** {proj['category']}")
                st.write(proj['desc'])
                
                # Render technical stack pills
                stack_badges = "".join([f'<span class="badge">{tech}</span>' for tech in proj['stack']])
                st.markdown(stack_badges, unsafe_allow_html=True)
                
                st.markdown(f"🔗 [View Project Repository]({proj['link']})")
                st.markdown("---")
    else:
        st.info("No matching projects found in this specific category selection.")

# --- PAGE: CONTACT ME ---
elif page == "Contact Me":
    st.title("Let's Connect!")
    st.write("Have a position open or interested in data system collaboration? Drop a message below.")
    
    with st.form(key="contact_form", clear_on_submit=True):
        user_name = st.text_input("Full Name", placeholder="John Doe")
        user_email = st.text_input("Email Address", placeholder="johndoe@example.com")
        message = st.text_area("Your Message", placeholder="Type your context or inquiry here...")
        
        submit_btn = st.form_submit_button("Send Message")
        
        if submit_btn:
            if user_name and user_email and message:
                st.success(f"Thank you, {user_name}! Your message has been simulated successfully.")
            else:
                st.error("Please fill out all fields before submitting.")
