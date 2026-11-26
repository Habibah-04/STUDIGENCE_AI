
import streamlit as st


def apply_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

    /* =========================================
       1. GLOBAL THEME
       ========================================= */

    :root {
        --gold: #D99A35;
        --gold-light: #F4B84F;
        --gold-bright: #FFD477;
        --amber: #B96B1C;

        --dark: #100D0B;
        --dark-card: #1B1511;
        --dark-soft: #251B14;

        --text: #FFF7E9;
        --muted: #C4B5A0;
        --border: rgba(244,184,79,.24);

        --cream: #F3EBDD;
        --cream-dark: #E7D8C0;
        --ink: #29221B;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                ellipse at 10% 0%,
                rgba(185,107,28,.10),
                transparent 30%
            ),
            radial-gradient(
                ellipse at 92% 8%,
                rgba(244,184,79,.08),
                transparent 28%
            ),
            #100D0B;

        color: var(--text);
    }

    .main .block-container {
        max-width: 1480px;
        padding: 1.6rem 2.2rem 3rem;
    }

    #MainMenu,
    footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"],
    section[data-testid="stSidebar"] {
        display: none !important;
    }

    /* =========================================
       2. TYPOGRAPHY
       ========================================= */

    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif !important;
        color: #FFF8EB !important;
        letter-spacing: -.45px;
    }

    h1 {
        font-size: 2.25rem !important;
        font-weight: 800 !important;
    }

    h2 {
        font-size: 1.55rem !important;
        font-weight: 700 !important;
    }

    h3 {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
    }

    p, li, label, .stMarkdown {
        color: #E0D2BE;
    }

    .page-title,
    .main h1,
    .main h2 {
        color: #F4B84F !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 800 !important;
    }

    /* =========================================
       3. BUTTONS
       ========================================= */

    .stButton > button,
    .stFormSubmitButton > button {
        background: linear-gradient(
            135deg,
            #D99A35,
            #9D591C
        ) !important;

        color: #160F09 !important;
        border: 1px solid rgba(255,212,119,.62) !important;
        border-radius: 12px !important;
        min-height: 44px;
        font-weight: 750 !important;
        transition: all .2s ease;

        box-shadow: 0 5px 18px rgba(185,107,28,.12);
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: linear-gradient(
            135deg,
            #FFD477,
            #D99A35
        ) !important;

        border-color: #FFE1A0 !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(217,154,53,.2);
    }

    /* =========================================
       4. INPUTS - DARK PAGES
       ========================================= */

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input,
    .stDateInput input {
        background: #1B1511 !important;
        color: #FFF7E9 !important;
        border: 1px solid #57412B !important;
        border-radius: 10px !important;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: #F4B84F !important;
        box-shadow: 0 0 0 1px #F4B84F !important;
    }

    .stSelectbox div[data-baseweb="select"],
    .stMultiSelect div[data-baseweb="select"] {
        background: #1B1511 !important;
        color: #FFF7E9 !important;
        border-radius: 10px !important;
    }

    [data-baseweb="popover"] {
        background: #251B14 !important;
    }

    /* =========================================
       5. METRIC CARDS
       ========================================= */

    div[data-testid="stMetric"] {
        background: linear-gradient(
            145deg,
            rgba(255,190,83,.10),
            rgba(35,24,16,.92)
        );

        padding: 18px;
        border: 1px solid var(--border);
        border-radius: 16px;

        box-shadow: 0 8px 24px rgba(0,0,0,.18);
    }

    div[data-testid="stMetricLabel"] {
        color: #D8C3A2 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #FFD477 !important;
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
    }

    /* =========================================
       6. TABS
       ========================================= */

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid var(--border);
    }

    .stTabs [data-baseweb="tab"] {
        color: #D8C3A2 !important;
        border-radius: 9px 9px 0 0;
        padding: 10px 16px;
    }

    .stTabs [aria-selected="true"] {
        color: #FFD477 !important;
        border-bottom: 3px solid #D99A35 !important;
    }

    /* =========================================
       7. EXPANDERS, ALERTS, TABLES
       ========================================= */

    [data-testid="stExpander"] {
        background: #1B1511;
        border: 1px solid var(--border);
        border-radius: 12px;
    }

    [data-testid="stAlert"] {
        background: #211811;
        border: 1px solid var(--border);
        border-radius: 12px;
    }

    [data-testid="stChatMessage"] {
        background: #1B1511;
        border: 1px solid var(--border);
        border-radius: 14px;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }

    .stProgress > div > div > div {
        background: linear-gradient(
            90deg,
            #9D591C,
            #FFD477
        );
    }

    hr {
        border-color: rgba(244,184,79,.22) !important;
    }

    /* =========================================
       8. DASHBOARD WELCOME CARD
       ========================================= */

    .top-welcome {
        background: linear-gradient(
            110deg,
            rgba(255,190,83,.12),
            rgba(37,25,17,.82)
        );

        border: 1px solid rgba(244,184,79,.25);
        border-radius: 18px;

        padding: 1.1rem 1.35rem;
        margin: .2rem 0 1.2rem;
    }

    .top-welcome .eyebrow {
        color: #F4B84F;
        font-size: .7rem;
        letter-spacing: 2px;
        font-weight: 800;
    }

    .top-welcome h2 {
        margin: .25rem 0 .15rem;
    }

    .top-welcome p {
        margin: 0;
        color: #CDB99D;
        font-size: .9rem;
    }

    /* =========================================
       9. DASHBOARD NAVIGATION PANELS
       ========================================= */

    .nav-panel {
        background: linear-gradient(
            145deg,
            rgba(217,154,53,.14),
            rgba(27,21,17,.96)
        );

        border: 1px solid rgba(244,184,79,.30);
        border-radius: 18px;
        padding: 16px;
        min-height: 100%;

        box-shadow: 0 8px 25px rgba(0,0,0,.20);
    }

    .nav-panel-title {
        color: #FFD477;
        font-family: 'Outfit', sans-serif;
        font-size: 1.12rem;
        font-weight: 800;
        letter-spacing: 1.5px;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(244,184,79,.25);
    }

    .st-key-dashboard_nav button {
        min-height: 105px !important;
        height: auto !important;
        white-space: pre-wrap !important;
        text-align: left !important;
        line-height: 1.45 !important;
        padding: 12px !important;

        background: linear-gradient(
            145deg,
            rgba(244,184,79,.19),
            rgba(34,24,17,.98)
        ) !important;

        border: 1px solid rgba(244,184,79,.30) !important;
        border-radius: 13px !important;
        color: #FFF0D4 !important;
    }

    .st-key-dashboard_nav button:hover {
        background: linear-gradient(
            145deg,
            rgba(255,212,119,.35),
            rgba(72,43,18,.98)
        ) !important;

        border-color: #FFD477 !important;
        transform: translateY(-2px);
    }

    /* =========================================
       10. AUTHENTICATION HERO CARD
       ========================================= */

    .st-key-auth_hero {
        background:
            radial-gradient(
                circle at 82% 20%,
                rgba(255,183,66,.15),
                transparent 34%
            ),
            linear-gradient(
                120deg,
                #251A11,
                #100D0B
            ) !important;

        border: 1px solid rgba(244,184,79,.38) !important;
        border-radius: 24px !important;

        padding: 28px 32px !important;
        margin: 1.5rem 0 2rem !important;

        box-shadow:
            0 18px 45px rgba(0,0,0,.30),
            inset 0 1px rgba(255,255,255,.04);
    }

    .auth-hero-copy {
        padding: 16px 12px;
    }

    .auth-kicker {
        color: #F4B84F !important;
        font-size: .76rem;
        font-weight: 800;
        letter-spacing: 3px;
        margin-bottom: 15px;
        text-transform: uppercase;
    }

    .auth-brand-title {
        color: #FFD477 !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: clamp(2.1rem, 4vw, 3.6rem);
        font-weight: 800;
        line-height: 1.08;
        letter-spacing: -1.5px;
    }

    .auth-brand-subtitle {
        color: #F5EBDD !important;
        font-size: 1.08rem;
        font-weight: 600;
        line-height: 1.6;
        margin-top: 15px;
    }

    .auth-hero-description {
        color: #CFC1AE !important;
        font-size: .91rem;
        line-height: 1.8;
        max-width: 490px;
        margin-top: 16px;
    }

    /* Hero mascot */
    .st-key-auth_hero img {
        width: 100%;
        max-height: 350px;
        object-fit: contain;
        border-radius: 18px;
    }

    /* =========================================
       11. AUTHENTICATION FORM CARDS
       ========================================= */

    .st-key-auth_login_card,
    .st-key-auth_signup_card {
        background: #F3EBDD !important;
        border: 1px solid #E1D2B9 !important;
        border-radius: 19px !important;

        padding: 24px 25px !important;
        min-height: 100%;

        box-shadow: 0 12px 30px rgba(0,0,0,.20);
    }

    /* Headings inside cream cards */
    .st-key-auth_login_card h1,
    .st-key-auth_login_card h2,
    .st-key-auth_login_card h3,
    .st-key-auth_signup_card h1,
    .st-key-auth_signup_card h2,
    .st-key-auth_signup_card h3 {
        color: #29221B !important;
    }

    /* Labels and descriptions */
    .st-key-auth_login_card p,
    .st-key-auth_signup_card p,
    .st-key-auth_login_card label,
    .st-key-auth_signup_card label,
    .st-key-auth_login_card [data-testid="stMarkdownContainer"],
    .st-key-auth_signup_card [data-testid="stMarkdownContainer"] {
        color: #30271F !important;
    }

    .auth-form-heading {
        color: #7C4B19 !important;
        font-family: 'Outfit', sans-serif;
        font-size: 1.2rem;
        font-weight: 800;
        letter-spacing: 1.5px;
        margin-bottom: 7px;
    }

    .auth-form-description {
        color: #776A5B !important;
        font-size: .86rem;
        margin-bottom: 18px;
    }

    /* Light card input fields */
    .st-key-auth_login_card input,
    .st-key-auth_signup_card input {
        background: #FFFFFF !important;
        color: #241E18 !important;
        border: 1px solid #D4C5AE !important;
        border-radius: 10px !important;
    }

    .st-key-auth_login_card input::placeholder,
    .st-key-auth_signup_card input::placeholder {
        color: #8B8175 !important;
    }

    /* Light card select boxes */
    .st-key-auth_login_card [data-baseweb="select"],
    .st-key-auth_signup_card [data-baseweb="select"] {
        background: #FFFFFF !important;
        color: #241E18 !important;
        border-radius: 10px !important;
    }

    .st-key-auth_login_card [data-baseweb="select"] *,
    .st-key-auth_signup_card [data-baseweb="select"] * {
        color: #241E18 !important;
    }

    /* Authentication buttons */
    .st-key-auth_login_card .stFormSubmitButton button,
    .st-key-auth_signup_card .stFormSubmitButton button {
        background: linear-gradient(
            135deg,
            #D99A35,
            #A96520
        ) !important;

        color: #1D160F !important;
        border: 1px solid #C58A32 !important;
        border-radius: 11px !important;
        font-weight: 800 !important;
        min-height: 46px;
    }

    .st-key-auth_login_card .stFormSubmitButton button:hover,
    .st-key-auth_signup_card .stFormSubmitButton button:hover {
        background: linear-gradient(
            135deg,
            #FFD477,
            #D99A35
        ) !important;
    }

    /* Authentication footer */
    .auth-footer {
        text-align: center;
        color: #BBA98F !important;
        font-size: .78rem;
        letter-spacing: 1px;
        margin-top: 28px;
    }

    /* =========================================
       12. RESPONSIVE DESIGN
       ========================================= */

    @media(max-width: 1000px) {
        .st-key-auth_hero {
            padding: 20px !important;
        }

        .auth-brand-title {
            font-size: 2.4rem;
        }
    }

    @media(max-width: 800px) {
        .main .block-container {
            padding: 1rem .8rem 2rem;
        }

        .st-key-auth_hero {
            padding: 16px !important;
            margin: 1rem 0 !important;
        }

        .auth-brand-title {
            font-size: 2rem;
        }

        .auth-hero-copy {
            padding: 8px;
        }

        .auth-hero-description {
            font-size: .85rem;
        }

        .st-key-auth_login_card,
        .st-key-auth_signup_card {
            padding: 17px !important;
        }
    }

/* =========================================
   BROWN TEXT FOR INFORMATIONAL MESSAGES
   ========================================= */

/* Streamlit informational and empty-state messages */
.stAlert,
[data-testid="stAlert"] {
    color: #70451F !important;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] div,
[data-testid="stAlert"] span {
    color: #70451F !important;
}

/* Empty-state messages and captions */
.stCaption,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
    color: #80552F !important;
}

/* General informational text */
.stMarkdown p,
.stMarkdown li {
    color: #80552F;
}

/* Empty task and empty chart messages */
[data-testid="stEmpty"],
[data-testid="stNotificationContent"] {
    color: #70451F !important;
}

/* Streamlit placeholder text */
[data-testid="stAlert"] {
    background: #F3EBDD !important;
    border: 1px solid #E1D2B9 !important;
    border-radius: 12px !important;
}


/* =========================================
   AI GENERATED STUDY NOTES - WARM ACADEMIA
   ========================================= */

.st-key-ai_generated_notes {
    background: #FFFCF6 !important;
    border: 1px solid #DCCDBB !important;
    border-radius: 16px !important;
    padding: 28px 32px !important;
    margin: 18px 0 !important;
    color: #493629 !important;
}

/* Main headings */
.st-key-ai_generated_notes h1,
.st-key-ai_generated_notes h2,
.st-key-ai_generated_notes h3,
.st-key-ai_generated_notes h4 {
    color: #493629 !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 750 !important;
}

/* Paragraphs and list items */
.st-key-ai_generated_notes p,
.st-key-ai_generated_notes li,
.st-key-ai_generated_notes span {
    color: #493629 !important;
    line-height: 1.8 !important;
}

/* Important text */
.st-key-ai_generated_notes strong {
    color: #65452F !important;
    font-weight: 750 !important;
}

/* Ordered and unordered lists */
.st-key-ai_generated_notes ol,
.st-key-ai_generated_notes ul {
    padding-left: 25px !important;
}

/* Inline code */
.st-key-ai_generated_notes code {
    background: #F1E7D9 !important;
    color: #754B30 !important;
    border-radius: 4px;
}

/* Code blocks */
.st-key-ai_generated_notes pre {
    background: #F4EDE2 !important;
    border: 1px solid #DCCDBB !important;
    border-radius: 10px !important;
    padding: 14px !important;
}

/* Horizontal separators */
.st-key-ai_generated_notes hr {
    border-color: #DCCDBB !important;
}

/* Links */
.st-key-ai_generated_notes a {
    color: #86583F !important;
}


    </style>
    """, unsafe_allow_html=True)


def sidebar_user(user):
    st.caption(f"Signed in as **{user['name']}**")
    st.caption(user.get("education_level", "Student"))
