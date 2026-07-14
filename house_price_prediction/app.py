import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="House AI", layout="wide")

# -------------------------------
# UI STYLE
# -------------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(to right, #e3f2fd, white);
}
.stButton>button {
    background-color: #1976d2;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_csv("data.csv")
df["id"] = df.index
df.columns = df.columns.str.strip().str.lower()
df = df.rename(columns={"locality": "location", "beds": "bedrooms"})
df["location"] = df["location"].astype(str).str.lower()

# Add Buy Price
buy_multiplier = 120
df["buy_price"] = df["rent"] * buy_multiplier

# -------------------------------
# SESSION STATE
# -------------------------------
defaults = {
    "page": "home",
    "history": [],
    "selected_houses": [],
    "advisor_choice": "",
    "logged_advisor": None,
    "recommended": pd.DataFrame(),
    "index": 0,
    "customer_choice": "",
    "interests": {},
    "house_trends": {}
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -------------------------------
# NAVIGATION
# -------------------------------
def go_back():
    if st.session_state.history:
        st.session_state.page = st.session_state.history.pop()

def go_to(page):
    st.session_state.history.append(st.session_state.page)
    st.session_state.page = page

# -------------------------------
# HOME PAGE
# -------------------------------
if st.session_state.page == "home":
    st.title("🏠 AI House Finder")

    col1, col2 = st.columns(2)

    if col1.button("👤 Customer"):
        go_to("form")
        st.rerun()

    if col2.button("🧑‍💼 Advisor"):
        go_to("advisor_login")
        st.rerun()

# -------------------------------
# CUSTOMER FORM
# -------------------------------
elif st.session_state.page == "form":
    if st.button("⬅ Back"):
        go_back()
        st.rerun()

    st.title("Enter Details")

    locations = df["location"].dropna().unique()
    location = st.multiselect("Location", locations)
    budget = st.number_input("Budget ₹", min_value=1000)
    area = st.number_input("Area (sqft)", min_value=100.0, step=50.0)
    bedrooms = st.number_input("Bedrooms", min_value=1)
    bathrooms = st.number_input("Bathrooms", min_value=1)
    rent_or_buy = st.radio("Rent or Buy?", ["Rent", "Buy"])

    if st.button("Submit"):
        filtered = df.copy()

        if location:
            filtered = filtered[filtered["location"].isin(location)]

        filtered["area_diff"] = abs(filtered["area"] - area)

        if rent_or_buy == "Rent":
            filtered = filtered[filtered["rent"] <= budget * 1.5]
            recommended = filtered.sort_values(by=["area_diff", "rent"]).head(10)
        else:
            filtered = filtered[filtered["buy_price"] <= budget * 1.5]
            recommended = filtered.sort_values(by=["area_diff", "buy_price"]).head(10)

        recommended = recommended.reset_index(drop=True)

        if len(recommended) > 0 and recommended["area_diff"].iloc[0] > 1000:
            st.warning("⚠ Exact area not available. Showing closest matches.")

        st.session_state.recommended = recommended
        st.session_state.index = 0
        st.session_state.customer_choice = rent_or_buy

        go_to("recommend")
        st.rerun()

# -------------------------------
# RECOMMEND PAGE
# -------------------------------
elif st.session_state.page == "recommend":
    if st.button("⬅ Back"):
        go_back()
        st.rerun()

    st.title("🏠 Browse Houses")

    data = st.session_state.recommended

    if len(data) == 0:
        st.error("No houses found. Try different inputs.")
        st.stop()

    i = st.session_state.index

    if i >= len(data):
        st.session_state.index = 0
        i = 0

    row = data.iloc[i]

    # IMAGE SECTION
    images = [
        "https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6",
        "https://images.unsplash.com/photo-1523217582562-09d0def993a6",
        "https://images.unsplash.com/photo-1507089947368-19c1da9775ae",
        "https://images.unsplash.com/photo-1494526585095-c41746248156",
        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750"
    ]

    image_url = images[i % len(images)]

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.image(image_url, width=200)
        st.write(f"📍 {row['location']}")
        st.write(f"🏠 {row['area']} sqft")
        st.write(f"🛏 {row['bedrooms']} BHK")

        if st.session_state.customer_choice == "Rent":
            st.write(f"💰 Rent: ₹ {row['rent']}")
        else:
            st.write(f"💰 Buy Price: ₹ {row['buy_price']}")

    if st.checkbox("Select this house", key=f"select_{i}"):
        if i not in st.session_state.selected_houses:
            st.session_state.selected_houses.append(i)

    col1, col2 = st.columns(2)

    if col1.button("⬅ Previous") and i > 0:
        st.session_state.index -= 1
        st.rerun()

    if col2.button("Next ➡") and i < len(data) - 1:
        st.session_state.index += 1
        st.rerun()

    if st.button("Submit Selection"):
        go_to("advisor_select")
        st.rerun()

# -------------------------------
# ADVISOR SELECT
# -------------------------------
elif st.session_state.page == "advisor_select":
    if st.button("⬅ Back"):
        go_back()
        st.rerun()

    st.title("Nearby Advisors")

    advisors = [
        {"name": "ADVISOR1", "location": "pune"},
        {"name": "ADVISOR2", "location": "mumbai"},
        {"name": "ADVISOR3", "location": "delhi"}
    ]

    for adv in advisors:
        st.write(f"👤 {adv['name']} ({adv['location']})")

        if st.button(f"Select {adv['name']}"):
            st.session_state.advisor_choice = adv["name"]
            go_to("final")
            st.rerun()

# -------------------------------
# FINAL PAGE
# -------------------------------
elif st.session_state.page == "final":
    st.title("✅ Success")
    st.success("✔ Interest recorded")

    advisor = st.session_state.advisor_choice

    if advisor not in st.session_state.interests:
        st.session_state.interests[advisor] = []

    for i in st.session_state.selected_houses:
        if i < len(st.session_state.recommended):
            row = st.session_state.recommended.iloc[i]

            house_info = {
                "location": row['location'],
                "price": row['rent'] if st.session_state.customer_choice == "Rent" else row['buy_price'],
                "type": st.session_state.customer_choice
            }

            if house_info not in st.session_state.interests[advisor]:
                st.session_state.interests[advisor].append(house_info)

            # PRICE TREND GRAPH
            if row['id'] not in st.session_state.house_trends:
                base_price = house_info["price"]
                st.session_state.house_trends[row['id']] = base_price * np.random.uniform(0.95, 1.05, 6)

            trend = st.session_state.house_trends[row['id']]
            months = ["Nov", "Dec", "Jan", "Feb", "Mar", "Apr"]

            fig, ax = plt.subplots(figsize=(4, 2))
            ax.plot(months, trend, marker='o')
            ax.set_title("Past Price Trend")
            st.pyplot(fig)

    st.session_state.selected_houses = []

    if st.button("⬅ Home"):
        st.session_state.page = "home"
        st.session_state.history = []
        st.rerun()

# -------------------------------
# ADVISOR LOGIN
# -------------------------------
elif st.session_state.page == "advisor_login":
    st.title("Advisor Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in ["ADVISOR1", "ADVISOR2", "ADVISOR3"] and password == "1234":
            st.session_state.logged_advisor = username
            go_to("advisor_dashboard")
            st.rerun()
        else:
            st.error("Invalid login")

    if st.button("⬅ Back"):
        go_back()
        st.rerun()

# -------------------------------
# ADVISOR DASHBOARD
# -------------------------------
elif st.session_state.page == "advisor_dashboard":
    st.title(f"Dashboard ({st.session_state.logged_advisor})")

    advisor = st.session_state.logged_advisor

    if advisor in st.session_state.interests and st.session_state.interests[advisor]:
        for house in st.session_state.interests[advisor]:
            st.write(f"📍 {house['location']} - ₹ {house['price']} ({house['type']})")
    else:
        st.write("No interests yet")

    if st.button("Logout"):
        st.session_state.logged_advisor = None
        st.session_state.interests = {}
        go_to("home")
        st.rerun()