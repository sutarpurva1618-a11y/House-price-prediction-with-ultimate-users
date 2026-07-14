import numpy as np
import pickle

# Load models
with open("rent_model.pkl", "rb") as f:
    rent_model = pickle.load(f)

with open("price_model.pkl", "rb") as f:
    price_model = pickle.load(f)

with open("columns.pkl", "rb") as f:
    columns = pickle.load(f)

def prepare_input(location, area, bedrooms, bathrooms, balconies):
    x = np.zeros(len(columns))

    x[columns.get_loc("area")] = area
    x[columns.get_loc("bedrooms")] = bedrooms
    x[columns.get_loc("bathrooms")] = bathrooms
    x[columns.get_loc("balconies")] = balconies

    loc_col = "location_" + location.lower()

    if loc_col in columns:
        x[columns.get_loc(loc_col)] = 1
    else:
        if "location_other" in columns:
            x[columns.get_loc("location_other")] = 1

    return x.reshape(1, -1)

# User input
location = input("Enter location: ")
area = float(input("Enter area (sqft): "))
bedrooms = int(input("Enter bedrooms: "))
bathrooms = int(input("Enter bathrooms: "))
balconies = int(input("Enter balconies: "))

input_data = prepare_input(location, area, bedrooms, bathrooms, balconies)

rent = rent_model.predict(input_data)[0]
price = price_model.predict(input_data)[0]

print("\n🏠 Predicted Results:")
print(f"Rent: ₹ {round(rent, 2)}")
print(f"Price: ₹ {round(price, 2)}")