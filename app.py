
import streamlit as st
import pandas as pd
from datetime import datetime

from mongodb.mongodb_connection import connect_mongodb
from mongodb.account_operations import (
    get_accounts,
    get_analysis,
    add_account,
    delete_account,
    save_analysis,
    clear_analysis,
)

from qdrant.qdrant_connection import connect_qdrant
from qdrant.qdrant_operations import (
    save_account_vector,
    search_similar_accounts,
    delete_account_vector,
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AccountGuard | Fake Account Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# PROFESSIONAL THEME
# --------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #f5f7fb;
    }

    [data-testid="stSidebar"] {
        background: #111827;
    }

    [data-testid="stSidebar"] * {
        color: #f9fafb;
    }

    .main-title {
        font-size: 30px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 2px;
    }

    .subtitle {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 24px;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e5eaf2;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }

    div[data-testid="stMetricLabel"] {
        color: #64748b;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #111827;
        font-weight: 800;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        min-height: 42px;
    }

    div[data-testid="stForm"] {
        background: white;
        padding: 20px;
        border: 1px solid #e5eaf2;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# DATABASE CONNECTIONS
# --------------------------------------------------

if "database_loaded" not in st.session_state:

    try:
        # Establish MongoDB connection first
        db = connect_mongodb()

        # Load existing data
        st.session_state.accounts = get_accounts()
        st.session_state.analysis_history = get_analysis()

        st.session_state.database_loaded = True

    except Exception as error:
        st.error(f"MongoDB connection failed: {error}")
        st.stop()


if "qdrant_ready" not in st.session_state:

    try:
        connect_qdrant()
        st.session_state.qdrant_ready = True

    except Exception as error:
        st.session_state.qdrant_ready = False
        st.warning(f"Qdrant connection failed: {error}")


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def refresh_data():
    """Reload account and analysis records from MongoDB."""

    st.session_state.accounts = get_accounts()
    st.session_state.analysis_history = get_analysis()


def calculate_risk(account):

    score = 0
    reasons = []

    followers = int(account.get("followers", 0))
    following = int(account.get("following", 0))
    posts = int(account.get("posts_count", 0))
    age = int(account.get("account_age_days", 0))

    if followers < 100:
        score += 30
        reasons.append("Very low follower count")

    if following > 1000:
        score += 25
        reasons.append("Following an unusually large number of accounts")

    if posts < 5:
        score += 20
        reasons.append("Very low number of posts")

    if age < 30:
        score += 25
        reasons.append("Newly created account")

    score = min(score, 100)

    if score >= 70:
        level = "HIGH"
        status = "SUSPICIOUS"

    elif score >= 40:
        level = "MEDIUM"
        status = "REVIEW REQUIRED"

    else:
        level = "LOW"
        status = "NORMAL"

    if not reasons:
        reasons.append("No major risk indicators found")

    return score, level, status, reasons


def show_page_header(title, description):

    st.markdown(
        f'<div class="main-title">{title}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="subtitle">{description}</div>',
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("## 🛡️ AccountGuard")
    st.caption("Social Media Security Intelligence")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "Add Account",
            "Manage Accounts",
            "Analyze Account",
            "Detection History",
        ],
    )

    st.divider()
    st.caption("AccountGuard | Prototype")


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if page == "Dashboard":

    refresh_data()

    show_page_header(
        "Security Dashboard",
        "Monitor social media accounts and review suspicious activity.",
    )

    accounts = st.session_state.accounts
    history = st.session_state.analysis_history

    total_accounts = len(accounts)
    total_analyses = len(history)

    suspicious_count = sum(
        1 for item in history
        if item.get("status") == "SUSPICIOUS"
    )

    normal_count = sum(
        1 for item in history
        if item.get("status") == "NORMAL"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Accounts", total_accounts)
    col2.metric("Total Analyses", total_analyses)
    col3.metric("Suspicious Results", suspicious_count)
    col4.metric("Normal Results", normal_count)

    st.markdown("### Recent Detection Results")

    if history:

        display_data = []

        for item in history[:10]:

            display_data.append({
                "Username": item.get("username", "Unknown"),
                "Risk Score": item.get("risk_score", 0),
                "Risk Level": item.get("risk_level", "Unknown"),
                "Status": item.get("status", "Unknown"),
                "Date": item.get("date", ""),
            })

        st.dataframe(
            pd.DataFrame(display_data),
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("No analysis results yet. Go to Analyze Account to start.")

    st.markdown("### Database Connections")

    db_col1, db_col2 = st.columns(2)

    with db_col1:
        st.markdown("**MongoDB Atlas**")
        st.success("Connected")

    with db_col2:
        st.markdown("**Qdrant Cloud**")

        if st.session_state.qdrant_ready:
            st.success("Connected")
        else:
            st.warning("Unavailable")


# --------------------------------------------------
# ADD ACCOUNT
# --------------------------------------------------

elif page == "Add Account":

    show_page_header(
        "Add Social Media Account",
        "Enter account information to store it and prepare it for risk analysis.",
    )

    with st.form("add_account_form"):

        username = st.text_input(
            "Username",
            placeholder="example_user",
        )

        col1, col2 = st.columns(2)

        with col1:

            followers = st.number_input(
                "Followers",
                min_value=0,
                step=1,
            )

            following = st.number_input(
                "Following",
                min_value=0,
                step=1,
            )

        with col2:

            posts_count = st.number_input(
                "Number of Posts",
                min_value=0,
                step=1,
            )

            account_age_days = st.number_input(
                "Account Age (Days)",
                min_value=0,
                step=1,
            )

        verified = st.checkbox("Verified Account")

        submitted = st.form_submit_button(
            "Save Account",
            type="primary",
            use_container_width=True,
        )

    if submitted:

        if not username.strip():

            st.error("Please enter a username.")

        else:

            user_id = f"U{int(datetime.now().timestamp() * 1000)}"

            account = {
                "user_id": user_id,
                "username": username.strip(),
                "followers": int(followers),
                "following": int(following),
                "posts_count": int(posts_count),
                "account_age_days": int(account_age_days),
                "verified": verified,
                "created_at": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }

            try:

                saved = add_account(account)

                if not saved:

                    st.error("This username already exists.")

                else:

                    if st.session_state.qdrant_ready:

                        try:

                            save_account_vector(account)

                            st.success(
                                "Account saved in MongoDB and Qdrant."
                            )

                        except Exception as error:

                            st.warning(
                                "Account saved in MongoDB, but Qdrant "
                                f"could not save its vector: {error}"
                            )

                    else:

                        st.success("Account saved in MongoDB.")

                    refresh_data()

            except Exception as error:

                st.error(f"Could not save account: {error}")


# --------------------------------------------------
# MANAGE ACCOUNTS
# --------------------------------------------------

elif page == "Manage Accounts":

    refresh_data()

    show_page_header(
        "Manage Accounts",
        "View stored accounts and remove records when required.",
    )

    accounts = st.session_state.accounts

    if not accounts:

        st.info("No accounts are available.")

    else:

        display_accounts = []

        for account in accounts:

            display_accounts.append({
                "User ID": account.get("user_id", ""),
                "Username": account.get("username", ""),
                "Followers": account.get("followers", 0),
                "Following": account.get("following", 0),
                "Posts": account.get("posts_count", 0),
                "Account Age (Days)": account.get("account_age_days", 0),
                "Verified": account.get("verified", False),
            })

        st.dataframe(
            pd.DataFrame(display_accounts),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### Delete Account")

        account_options = {
            f"{a.get('username', 'Unknown')} ({a.get('user_id', '')})":
            a.get("user_id")
            for a in accounts
        }

        selected = st.selectbox(
            "Select an account",
            list(account_options.keys()),
        )

        if st.button("Delete Account", type="primary"):

            selected_id = account_options[selected]

            try:

                if st.session_state.qdrant_ready:
                    delete_account_vector(selected_id)

                delete_account(selected_id)

                refresh_data()

                st.success("Account deleted successfully.")
                st.rerun()

            except Exception as error:

                st.error(f"Account deletion failed: {error}")


# --------------------------------------------------
# ANALYZE ACCOUNT
# --------------------------------------------------

elif page == "Analyze Account":

    refresh_data()

    show_page_header(
        "Account Risk Analysis",
        "Evaluate an account using basic profile indicators and similarity search.",
    )

    accounts = st.session_state.accounts

    if not accounts:

        st.info("Add an account before starting an analysis.")

    else:

        account_options = {
            f"{a.get('username', 'Unknown')} ({a.get('user_id', '')})": a
            for a in accounts
        }

        selected_label = st.selectbox(
            "Select account to analyze",
            list(account_options.keys()),
        )

        selected_account = account_options[selected_label]

        st.markdown("### Account Information")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Followers", selected_account.get("followers", 0))
        c2.metric("Following", selected_account.get("following", 0))
        c3.metric("Posts", selected_account.get("posts_count", 0))
        c4.metric(
            "Age (Days)",
            selected_account.get("account_age_days", 0),
        )

        if st.button("Run Risk Analysis", type="primary"):

            score, level, status, reasons = calculate_risk(
                selected_account
            )

            result = {
                "user_id": selected_account.get("user_id"),
                "username": selected_account.get("username"),
                "risk_score": score,
                "risk_level": level,
                "status": status,
                "reasons": reasons,
                "date": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }

            try:

                save_analysis(result)
                refresh_data()

                st.markdown("### Analysis Result")

                result_col1, result_col2, result_col3 = st.columns(3)

                result_col1.metric("Risk Score", f"{score}/100")
                result_col2.metric("Risk Level", level)
                result_col3.metric("Detection Status", status)

                if status == "SUSPICIOUS":

                    st.error("Suspicious account indicators detected.")

                elif status == "REVIEW REQUIRED":

                    st.warning("This account requires further review.")

                else:

                    st.success("No major risk indicators detected.")

                st.markdown("### Risk Indicators")

                for reason in reasons:
                    st.write(f"• {reason}")

                st.caption(
                    "This is a rule-based prototype, not a definitive "
                    "determination that an account is fake."
                )

                # Qdrant similarity search
                if st.session_state.qdrant_ready:

                    try:

                        similar_accounts = search_similar_accounts(
                            selected_account,
                            limit=5,
                        )

                        st.markdown("### Similar Accounts")

                        similar_rows = []

                        for point in similar_accounts:

                            payload = point.payload or {}

                            if payload.get("user_id") == selected_account.get(
                                "user_id"
                            ):
                                continue

                            similar_rows.append({
                                "Username": payload.get(
                                    "username", "Unknown"
                                ),
                                "Followers": payload.get("followers", 0),
                                "Following": payload.get("following", 0),
                                "Posts": payload.get("posts_count", 0),
                                "Similarity Score": round(
                                    point.score, 4
                                ),
                            })

                        if similar_rows:

                            st.dataframe(
                                pd.DataFrame(similar_rows),
                                use_container_width=True,
                                hide_index=True,
                            )

                        else:

                            st.info("No other similar accounts found.")

                    except Exception as error:

                        st.warning(
                            f"Similarity search failed: {error}"
                        )

                else:

                    st.info(
                        "Qdrant is unavailable. Similarity search was skipped."
                    )

            except Exception as error:

                st.error(f"Analysis could not be saved: {error}")


# --------------------------------------------------
# DETECTION HISTORY
# --------------------------------------------------

elif page == "Detection History":

    refresh_data()

    show_page_header(
        "Detection History",
        "Review previously completed account risk analyses.",
    )

    history = st.session_state.analysis_history

    if not history:

        st.info("No detection history available.")

    else:

        history_rows = []

        for item in history:

            reasons = item.get("reasons", [])

            history_rows.append({
                "Username": item.get("username", "Unknown"),
                "Risk Score": item.get("risk_score", 0),
                "Risk Level": item.get("risk_level", "Unknown"),
                "Status": item.get("status", "Unknown"),
                "Reasons": ", ".join(reasons)
                if isinstance(reasons, list)
                else str(reasons),
                "Date": item.get("date", ""),
            })

        history_df = pd.DataFrame(history_rows)

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True,
        )

        csv_data = history_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download History as CSV",
            data=csv_data,
            file_name="account_detection_history.csv",
            mime="text/csv",
        )

        st.divider()

        if st.button("Clear Detection History"):

            try:

                clear_analysis()
                refresh_data()

                st.success("Detection history cleared.")
                st.rerun()

            except Exception as error:

                st.error(
                    f"Could not clear history: {error}"
                )
