  import streamlit as st
  from openai import OpenAI
  import requests
  from bs4 import BeautifulSoup

  st.set_page_config(page_title="Content Idea Generator", page_icon="💡")

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

  st.title("💡 Content Idea Generator")

  client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

  def scrape_website(url):
      try:
          if not url.startswith("http"):
              url = "https://" + url
          headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
          response = requests.get(url, headers=headers, timeout=10)
          soup = BeautifulSoup(response.text, "html.parser")

          for tag in soup(["script", "style", "nav", "footer", "header"]):
              tag.decompose()

          text = soup.get_text(separator=" ", strip=True)
          return text[:8000]
      except Exception as e:
          return f"Error scraping website: {str(e)}"

  with st.form("client_form"):
      st.subheader("Client Information")
      website_url = st.text_input("Client's Website URL", placeholder="example.com")

      st.subheader("Content Types Needed")
      do_socials = st.checkbox("Social Media Posts", value=True)
      do_blogs = st.checkbox("Blog Articles")
      do_emails = st.checkbox("Email Campaigns")

      submitted = st.form_submit_button("Generate Ideas")

  if submitted:
      if not website_url:
          st.warning("Please enter a website URL.")
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
              with st.spinner("Scanning website..."):
                  website_content = scrape_website(website_url)

              if website_content.startswith("Error"):
                  st.error(website_content)
              else:
                  with st.spinner("Analyzing business and generating ideas..."):
                      system_prompt = """You are a creative content strategist. You will be given the text content from a client's website.

  Your job is to:
  1. Analyze the website to understand: business name, industry, location, what makes them unique, their services/products, target audience, and whether
  they are a legal/law firm
  2. For legal clients, identify their practice areas and consider state-specific laws that could be content topics
  3. Search your knowledge for recent news or trends in their industry and location that could be leveraged
  4. Generate specific, actionable content ideas

  Always format your response with:
  - A brief summary of the business (2-3 sentences)
  - Clear sections for each content type requested
  - For each idea: a headline/hook, why it's relevant, and a brief description"""

                      user_prompt = f"""Here is the website content for a client:

  ---
  {website_content}
  ---

  Based on this website, generate content ideas for: {", ".join(content_types)}

  Please provide 3-5 ideas for each content type. Make the ideas specific to this business, not generic. If this is a legal client, include ideas around
  relevant laws in their state/jurisdiction."""

                      try:
                          response = client.chat.completions.create(
                              model="gpt-4o",
                              messages=[
                                  {"role": "system", "content": system_prompt},
                                  {"role": "user", "content": user_prompt}
                              ],
                              max_tokens=2500
                          )

                          ideas = response.choices[0].message.content

                          st.subheader("📋 Content Ideas")
                          st.markdown(ideas)

                          st.download_button(
                              label="Download Ideas",
                              data=ideas,
                              file_name="content_ideas.txt",
                              mime="text/plain"
                          )

                      except Exception as e:
                          st.error(f"Error generating ideas: {str(e)}")
