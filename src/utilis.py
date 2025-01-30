from flask import request, session
import random
import pandas as pd
import hashlib

# # Load comparison data
# def get_comparison_data():
#     df = pd.read_excel("data/FounderImageURL60.xlsx")
#     return [
#         {"id": row["founder_identifier_uuid"], "url": row["download_url"]}
#         for _, row in df.iterrows()
#     ]


# def assign_photos(version, comparison_data):
#     fixed_photos = comparison_data[:10]
#     varying_photos = comparison_data[10:]

#     if version in [2, 3, 4]:
#         seed = 42 if version == 2 else 101 if version == 3 else 202
#         random.seed(seed)
#         random.shuffle(varying_photos)

#     all_photos = fixed_photos + varying_photos[:50]
#     return all_photos


# Utilities
def get_client_ip():
    return request.remote_addr


def get_user_agent():
    return request.headers.get("User-Agent")


# Maintain a dictionary to track usage count for (batch, version) combinations
usage_tracker = {}


# Load comparison data from Excel file
def get_comparison_data():
    df = pd.read_excel("data/FounderImageURL60.xlsx")
    return [
        {"id": row["founder_identifier_uuid"], "url": row["download_url"]}
        for _, row in df.iterrows()
    ]


# Function to generate unique codes
def generate_unique_codes(batch_number):
    # Generate a unique 6-digit hexadecimal code for the batch
    hex_code = hex(batch_number)[2:].zfill(6)  # Ensure it's 6 digits

    # Generate a unique 10-digit code using a hash
    unique_input = f"{batch_number}{random.random()}"
    ten_digit_code = hashlib.sha1(unique_input.encode()).hexdigest()[
        :10
    ]  # First 10 digits of a SHA-1 hash

    return hex_code, ten_digit_code


# Function to assign photos to a session
def assign_photos(version, comparison_data):
    fixed_photos = comparison_data[:10]  # First 10 photos remain fixed
    varying_photos = comparison_data[10:]  # Remainder for randomization

    # Define batch number and unique identifiers for the batch
    batch_number = random.randint(1, 1000)
    hex_code, ten_digit_code = generate_unique_codes(batch_number)

    # Build the unique key for tracking usage
    usage_key = f"{batch_number}-{version}"

    # Check and update usage count
    if usage_key not in usage_tracker:
        usage_tracker[usage_key] = 0

    if usage_tracker[usage_key] >= 10:
        raise ValueError(
            "This batch and version combination has been used 10 times and is no longer available."
        )

    # Update the usage count
    usage_tracker[usage_key] += 1

    # Create the photos combination
    all_photos = fixed_photos.copy()  # Start with the fixed photos

    # Shuffle the varying photos based on version
    if version in range(2, 11):  # Adjusting versions to allow 2-10
        seed = version * 101  # Unique seed based on version
        random.seed(seed)
        random.shuffle(varying_photos)  # Shuffle only the varying photos

    # Choose 10 random photos from the varying set
    random_photos = varying_photos[:10]

    # Assign batch and unique codes to photos
    for photo in fixed_photos + random_photos:
        photo["batch_code"] = hex_code  # Assign the batch hex code
        photo["unique_code"] = ten_digit_code  # Assign the unique 10-digit code

    all_photos.extend(random_photos)  # Combine fixed and random photos

    # Store the unique code in the session for later validation
    session["completion_code"] = ten_digit_code

    return all_photos
