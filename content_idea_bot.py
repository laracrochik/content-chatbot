import streamlit as st
from openai import OpenAI

  # --- Config ---
  st.set_page_config(page_title="Content Idea Generator", page_icon="💡")

  # --- Password Gate ---
  if "authenticated" not in st.session_state:
      st.session_state.authenticated = False

  if not st.session_state.authenticated:
      st.title("🔐 Content Idea Generator")
      password = st.text_input("Enter password:", type="password")
      if st.button("Login"):
          if password == st.secrets.get("APP_PASSWORD"):
              st.session_state.authenticated = True
              st.rerun()
          else:
              st.error("Incorrect password.")
      st.stop()

  # --- Main App ---
  st.title("💡 Content Idea Generator")

  client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

  # --- Client Intake Form ---
  with st.form("client_form"):
      st.subheader("Client Information")
      client_name = st.text_input("Client/Business Name")
      industry = st.text_input("Industry (e.g., legal, fitness, restaurant, tech)")
      location = st.text_input("Location (City, State)")
      background = st.text_area("What makes this client unique? (background, story, specialties)")

      is_legal = st.checkbox("This is a legal client")
      practice_area = ""
      if is_legal:
          practice_area = st.text_input("Practice area(s) (e.g., personal injury, family law, immigration)")

      st.subheader("Content Types Needed")
      do_socials = st.checkbox("Social Media Posts", value=True)
      do_blogs = st.checkbox("Blog Articles")
      do_emails = st.checkbox("Email Campaigns")

      submitted = st.form_submit_button("Generate Ideas")

  if submitted:
      if not client_name or not industry or not location:
          st.warning("Please fill in at least the client name, industry, and location.")
      else:
          content_types = []
          if do_socials:
              content_types.append("social media posts")
          if do_blogs:
              content_types.append("blog articles")
          if do_emails:
              content_types.append("email campaigns")

          if not content_types:
              st.warning("Please select at least one content type.")
          else:
              with st.spinner("Generating ideas..."):
                  # Build the prompt
                  legal_section = ""
                  if is_legal and practice_area:
                      legal_section = f"""
  This is a LEGAL client. Their practice area(s): {practice_area}
  IMPORTANT: Research and mention any notable state-specific laws in {location} that relate to their practice area(s).
  This could include recent legislation, unique state statutes, or legal trends that could be turned into educational
  content.
  """

                  system_prompt = f"""You are a creative content strategist helping a marketing team generate content
  ideas for their clients.

  For each request, you should:
  1. Consider what makes the client unique and how to highlight that
  2. Search for recent local news in their area ({location}) that relates to their industry ({industry})
  3. Suggest timely, relevant content ideas that connect their business to current events or trends
  4. Make ideas specific and actionable, not generic

  {legal_section}

  Always format your response with clear sections for each content type requested. Include specific hooks, angles, and
  why each idea would resonate with the target audience."""

                  user_prompt = f"""Generate content ideas for the following client:

  **Client Name:** {client_name}
  **Industry:** {industry}
  **Location:** {location}
  **Unique Background:** {background}
  {"**Practice Area:** " + practice_area if is_legal else ""}

  **Content types needed:** {", ".join(content_types)}

  Please provide 3-5 ideas for each content type selected. For each idea, include:
  - A specific headline or hook
  - Why it's relevant (local news tie-in, unique angle, trending topic, etc.)
  - A brief description of the content

  Search for any recent news in {location} related to {industry} that could be leveraged for timely content."""

                  try:
                      response = client.chat.completions.create(
                          model="gpt-4o",
                          messages=[
                              {"role": "system", "content": system_prompt},
                              {"role": "user", "content": user_prompt}
                          ],
                          max_tokens=2000
                      )

                      ideas = response.choices[0].message.content

                      st.subheader("📋 Content Ideas")
                      st.markdown(ideas)

                      # Download button
                      st.download_button(
                          label="Download Ideas",
                          data=ideas,
                          file_name=f"{client_name.replace(' ', '_')}_content_ideas.txt",
                          mime="text/plain"
                      )

                  except Exception as e:
                      st.error(f"Error generating ideas: {str(e)}")
