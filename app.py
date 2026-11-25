from pathlib import Path
from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
from src.db import init_db, authenticate, create_user
from src.focus_tracker import start_session, heartbeat, end_session, new_session_id, start_sweeper
from src.ui import apply_styles
from src.creative_studio import creative_studio
from src.advanced import (
    ensure_extra_tables, dashboard, tutor, pdf_lab, exam, planner,
    learning_dna, mistake_dna, revision, career, resume, video_finder,
    notes_studio, analytics, settings
)

BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "assets"

st.set_page_config(
    page_title="STUDIGENCE AI",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="collapsed"
)
init_db()
ensure_extra_tables()
apply_styles()

# Fix dashboard navigation text wrapping
st.markdown("""
<style>
/* Target only dashboard navigation cards */
.st-key-dashboard_nav div[data-testid="stButton"] button {
    height: auto !important;
    min-height: 96px !important;
    max-height: none !important;
    width: 100% !important;
    padding: 14px 10px !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
}

/* Remove ellipsis and allow multiple lines */
.st-key-dashboard_nav div[data-testid="stButton"] button p {
    display: block !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    -webkit-line-clamp: unset !important;
    max-height: none !important;
    overflow-wrap: break-word !important;
    word-break: normal !important;
    line-height: 1.5 !important;
    text-align: center !important;
    width: 100% !important;
}
</style>
""", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"




def auth_screen():
    st.markdown("<div style='height:2vh'></div>", unsafe_allow_html=True)

    with st.container(key="auth_hero"):
        left, right = st.columns(
            [1.15, 0.85],
            gap="large",
            vertical_alignment="center"
        )

        with left:
            st.markdown("""
                <div class="auth-hero-copy">
                    <div class="auth-kicker">
                        YOUR PERSONAL LEARNING STUDIO
                    </div>
                    <div class="auth-brand-title">
                        STUDIGENCE AI
                    </div>
                    <div class="auth-brand-subtitle">
                        Learn smarter & practise better with this Study Assistant.
                    </div>
                    <div class="auth-hero-description">
                        Your learning companion for understanding concepts,
                        practising questions, creating notes and building
                        your future with AI.
                    </div>
                </div>
                
            """, unsafe_allow_html=True)

        with right:
            mascot = ASSET_DIR / "studigence_mascot.gif"

            if mascot.exists():
                st.image(
                    str(mascot),
                    use_container_width=True
                )
            else:
                st.warning(
                    "RoboTutor GIF not found. "
                    "Please check assets/studigence_mascot.gif"
                )

    login_col, signup_col = st.columns(2, gap="large")

    with login_col:
        with st.container(key="auth_login_card"):
            st.markdown(
                '<div class="auth-form-heading">SIGN IN</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="auth-form-description">'
                'Welcome back! Continue your learning journey.'
                '</div>',
                unsafe_allow_html=True
            )

            with st.form("login_form"):
                email = st.text_input(
                    "Email address",
                    key="login_email"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password"
                )

                submit = st.form_submit_button(
                    "Sign In",
                    use_container_width=True
                )

            if submit:
                user = authenticate(email, password)

                if user:
                    st.session_state.user = user
                    st.session_state.page = "Dashboard"
                    st.rerun()
                else:
                    st.error("Email or password is incorrect.")

    with signup_col:
        with st.container(key="auth_signup_card"):
            st.markdown(
                '<div class="auth-form-heading">CREATE ACCOUNT</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="auth-form-description">'
                'Create your account and start learning smarter.'
                '</div>',
                unsafe_allow_html=True
            )

            with st.form("signup_form"):
                name = st.text_input("Full name")

                email = st.text_input(
                    "Email address",
                    key="signup_email"
                )

                password = st.text_input(
                    "Password (minimum 8 characters)",
                    type="password",
                    key="signup_password"
                )

                level = st.selectbox(
                    "Education level",
                    [
                        "School",
                        "College",
                        "University",
                        "Competitive exam",
                        "Lifelong learner"
                    ]
                )

                goal = st.text_input("Learning goal")

                submit = st.form_submit_button(
                    "Create Account",
                    use_container_width=True
                )

            if submit:
                try:
                    create_user(
                        name,
                        email,
                        password,
                        level,
                        goal
                    )
                    st.success("Account created. Please sign in.")

                except ValueError as error:
                    st.error(str(error))

    st.markdown(
        """
        <p class="auth-footer">
            STUDIGENCE AI · Learn · Practise · Progress
        </p>
        """,
        unsafe_allow_html=True
    )

NAV_GROUPS = {
    "LEARN": [
        ("AI Tutor", "Learn and understand topics"),
        ("PDF Lab", "Study your documents"),
        ("Creative Studio", "Create diagrams and files"),
        ("Exam Center", "Practise with AI exams"),
    ],

    "POWER UP": [
        ("Notes Studio", "Create and manage notes"),
        ("YouTube Finder", "Find learning videos"),
        ("Learning DNA", "Track your learning"),
        ("Mistake DNA", "Understand your mistakes"),
        ("Memory Revision", "Revise saved concepts"),
        ("Study Planner", "Organise study tasks"),
    ],

    "CAREER": [
        ("Career Intelligence", "Explore career paths"),
        ("Resume Studio", "Build your resume"),
        ("Analytics & Reports", "View your progress"),
    ],
}

PAGES = {
    "Dashboard": lambda uid, user, profile: dashboard(uid, user),
    "AI Tutor": lambda uid, user, profile: tutor(uid),
    "PDF Lab": lambda uid, user, profile: pdf_lab(uid),
    "Creative Studio": lambda uid, user, profile: creative_studio(uid),
    "Exam Center": lambda uid, user, profile: exam(uid),
    "Study Planner": lambda uid, user, profile: planner(uid),
    "Learning DNA": lambda uid, user, profile: learning_dna(uid),
    "Mistake DNA": lambda uid, user, profile: mistake_dna(uid),
    "Memory Revision": lambda uid, user, profile: revision(uid),
    "Career Intelligence": lambda uid, user, profile: career(uid, profile),
    "Resume Studio": lambda uid, user, profile: resume(uid),
    "YouTube Finder": lambda uid, user, profile: video_finder(uid),
    "Notes Studio": lambda uid, user, profile: notes_studio(uid),
    "Analytics & Reports": lambda uid, user, profile: analytics(uid),
    "Settings": lambda uid, user, profile: settings(uid, profile),
}



def render_module_cards():
    st.markdown("### Explore Your Learning Space")
    st.caption("Choose a module to get started.")

    with st.container(key="dashboard_nav"):
        panel_cols = st.columns(3, gap="medium")

        for panel_col, (group, items) in zip(
            panel_cols, NAV_GROUPS.items()
        ):
            with panel_col:
                with st.container(border=True):
                    st.markdown(
                        f'<div class="nav-panel-title">{group}</div>',
                        unsafe_allow_html=True
                    )

                    for start in range(0, len(items), 2):
                        pair = items[start:start + 2]
                        cols = st.columns(2, gap="small")

                        for col, (page, description) in zip(cols, pair):
                            with col:
                                if st.button(
                                    f"{page}\n\n{description}",
                                    key=f"nav_{page}",
                                    use_container_width=True
                                ):
                                    st.session_state.page = page
                                    st.rerun()

def render_topbar(user):
    first = (user.get("name") or "Learner").split()[0]
    if st.session_state.page == "Dashboard":
        left, profile_col, signout_col = st.columns([7, 1.7, 1.1], vertical_alignment="center")
        with left:
            st.markdown(
                f"<div class='top-welcome'><div class='eyebrow'>WELCOME BACK</div>"
                f"<h2>Hello, {first}.</h2><p>Ready to make today's learning count?</p></div>",
                unsafe_allow_html=True
            )
        with profile_col:
            if st.button("Profile settings", key="top_profile", use_container_width=True):
                st.session_state.page = "Settings"
                st.rerun()
        with signout_col:
            if st.button("Sign out", key="top_signout", use_container_width=True):
                if st.session_state.get("focus_session_id"):
                    end_session(st.session_state.user["id"], st.session_state.focus_session_id)
                    st.session_state.pop("focus_session_id", None)
                st.session_state.user = None
                st.session_state.page = "Dashboard"
                st.rerun()
    else:
        left, dash_col, profile_col, signout_col = st.columns([5.8, 1.1, 1.7, 1.1], vertical_alignment="center")
        with left:
            st.markdown(
                f"<div style='padding:.45rem 0'><div style='color:#F4B84F;font-size:.72rem;letter-spacing:2px;font-weight:800'>STUDIGENCE AI</div>"
                f"<div style='color:#FFF4E2;font-family:Outfit,sans-serif;font-size:1.35rem;font-weight:750'>{st.session_state.page}</div></div>",
                unsafe_allow_html=True
            )
        with dash_col:
            if st.button("Dashboard", key="top_dashboard", use_container_width=True):
                st.session_state.page = "Dashboard"
                st.rerun()
        with profile_col:
            if st.button("Profile settings", key="top_profile_inner", use_container_width=True):
                st.session_state.page = "Settings"
                st.rerun()
        with signout_col:
            if st.button("Sign out", key="top_signout_inner", use_container_width=True):
                if st.session_state.get("focus_session_id"):
                    end_session(st.session_state.user["id"], st.session_state.focus_session_id)
                    st.session_state.pop("focus_session_id", None)
                st.session_state.user = None
                st.session_state.page = "Dashboard"
                st.rerun()


if not st.session_state.user:
    auth_screen()
    st.stop()

user = st.session_state.user
uid = user["id"]
from src.db import get_profile
from src.focus_tracker import start_session, heartbeat, new_session_id, start_sweeper

if not st.session_state.get("focus_session_id"):
    st.session_state.focus_session_id = new_session_id()
    start_session(uid, st.session_state.focus_session_id)
start_sweeper()

@st.fragment(run_every="5s")
def _focus_heartbeat():
    heartbeat(uid, st.session_state.focus_session_id)

_focus_heartbeat()
profile = get_profile(uid)

render_topbar(user)
if st.session_state.page == "Dashboard":
    render_module_cards()
    st.divider()

PAGES.get(st.session_state.page, PAGES["Dashboard"])(uid, user, profile)
