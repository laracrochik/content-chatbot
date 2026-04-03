import streamlit as st
import anthropic

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Content Idea Generator", page_icon="💡", layout="centered")

# ── Password gate ──────────────────────────────────────────────────────────────
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("💡 Content Idea Generator")
        pwd = st.text_input("Enter password to continue", type="password")
        if st.button("Login"):
            if pwd == st.secrets["APP_PASSWORD"]:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        st.stop()

check_password()

# ── Anthropic client ───────────────────────────────────────────────────────────
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# ── UI ─────────────────────────────────────────────────────────────────────────
st.title("💡 Content Idea Generator")
st.caption("Fill in your client's details and get tailored content ideas in seconds.")

with st.form("client_form"):
    st.subheader("Client Details")

    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client / Business Name")
        industry = st.text_input("Industry", placeholder="e.g. Personal Injury Law, Family Dentistry, Yoga Studio")
        location = st.text_input("City & State", placeholder="e.g. Austin, TX")
    with col2:
        is_legal = st.checkbox("This is a legal client")
        if is_legal:
            practice_areas = st.text_input("Practice Area(s)", placeholder="e.g. Family Law, Criminal Defense")
        else:
            practice_areas = ""
        state_only = st.text_input("State abbreviation (for legal)", placeholder="e.g. TX") if is_legal else ""

    background = st.text_area(
        "What makes this client unique?",
        placeholder="e.g. Founded by a former NFL player, bilingual staff, 20+ years in the community, award-winning, niche specialty...",
        height=120
    )

    st.subheader("Content Types")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        want_socials = st.checkbox("📱 Social Media", value=True)
    with col_b:
        want_blogs = st.checkbox("📝 Blog Posts", value=True)
    with col_c:
        want_emails = st.checkbox("📧 Email Campaigns", value=True)

    submitted = st.form_submit_button("✨ Generate Ideas", use_container_width=True)

# ── Generation ─────────────────────────────────────────────────────────────────
if submitted:
    if not client_name or not industry or not location:
        st.warning("Please fill in at least the client name, industry, and location.")
        st.stop()

    if not any([want_socials, want_blogs, want_emails]):
        st.warning("Please select at least one content type.")
        st.stop()

    selected_types = []
    if want_socials: selected_types.append("Social Media Posts")
    if want_blogs:   selected_types.append("Blog Posts")
    if want_emails:  selected_types.append("Email Campaigns")
    content_types_str = ", ".join(selected_types)

    legal_section = ""
    if is_legal and practice_areas:
        legal_section = f"""
LEGAL CLIENT INSTRUCTIONS:
- This client is a law firm. Practice areas: {practice_areas}
- State: {state_only or location}
- Use your knowledge to identify any notable or unique laws, recent legislation, or legal trends in {state_only or location} that are relevant to {practice_areas}.
- Incorporate these into content ideas where appropriate (e.g. a blog explaining a new law, a social post about a common legal misconception in that state).
"""

    prompt = f"""You are a creative content strategist for a marketing agency. Your job is to generate fresh, specific, and actionable content ideas for a client.

CLIENT PROFILE:
- Business Name: {client_name}
- Industry: {industry}
- Location: {location}
- What makes them unique: {background or "Not provided"}

CONTENT TYPES REQUESTED: {content_types_str}

{legal_section}

INSTRUCTIONS:
1. First, briefly note 2-3 things that make this client stand out based on their background and industry.
2. Search the web for recent local news in {location} or statewide news relevant to the {industry} industry. Identify 2-3 stories or trends that could inspire timely content.
3. For each requested content type, generate 4-5 specific content ideas. Each idea should:
   - Have a working title or hook
   - Be 1-2 sentences explaining the angle
   - Feel tailored to THIS client, not generic
4. Where relevant, tie ideas to the local news/trends you found, labeling them as "🔥 Trending" ideas.
5. For legal clients, add a "⚖️ Legal Angle" section with 2-3 ideas based on state-specific laws or legal trends.

Format your response cleanly with clear headers for each section. Be creative, specific, and practical."""

    with st.spinner("Researching your client and generating ideas..."):
        try:
            response = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=2000,
                tools=[{"type": "web_search_20250305", "name": "web_search"}],
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract text from response (may include tool use blocks)
            output = ""
            for block in response.content:
                if hasattr(block, "text"):
                    output += block.text

            st.success("Here are your content ideas!")
            st.markdown(output)

            # Download button
            st.download_button(
                label="📥 Download Ideas as .txt",
                data=output,
                file_name=f"{client_name.replace(' ', '_')}_content_ideas.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Something went wrong: {e}")
