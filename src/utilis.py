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


# Load comparison data from Excel file
def get_comparison_data():
    df = pd.read_excel("data/FounderImageURL60.xlsx")
    return [
        {"id": row["founder_identifier_uuid"], "url": row["download_url"]}
        for _, row in df.iterrows()
    ]


# # Function to generate unique codes
# def generate_unique_codes(batch_number):
#     # Generate a unique 6-digit hexadecimal code for the batch
#     hex_code = hex(batch_number)[2:].zfill(6)  # Ensure it's 6 digits

#     # Generate a unique 10-digit code using a hash
#     unique_input = f"{batch_number}{random.random()}"
#     ten_digit_code = hashlib.sha1(unique_input.encode()).hexdigest()[
#         :10
#     ]  # First 10 digits of a SHA-1 hash

#     return hex_code, ten_digit_code


# # Function to assign photos to a session
# def assign_photos(version, comparison_data):
#     fixed_photos = comparison_data[:10]  # First 10 photos remain fixed
#     varying_photos = comparison_data[10:]  # Remainder for randomization

#     # Define batch number and unique identifiers for the batch
#     batch_number = random.randint(1, 1000)
#     hex_code, ten_digit_code = generate_unique_codes(batch_number)

#     # Build the unique key for tracking usage
#     usage_key = f"{batch_number}-{version}"

#     # Check and update usage count
#     if usage_key not in usage_tracker:
#         usage_tracker[usage_key] = 0

#     if usage_tracker[usage_key] >= 10:
#         raise ValueError(
#             "This batch and version combination has been used 10 times and is no longer available."
#         )

#     # Update the usage count
#     usage_tracker[usage_key] += 1

#     # Create the photos combination
#     all_photos = fixed_photos.copy()  # Start with the fixed photos

#     # Shuffle the varying photos based on version
#     if version in range(2, 11):  # Adjusting versions to allow 2-10
#         seed = version * 101  # Unique seed based on version
#         random.seed(seed)
#         random.shuffle(varying_photos)  # Shuffle only the varying photos

#     # Choose 10 random photos from the varying set
#     random_photos = varying_photos[:10]

#     # Assign batch and unique codes to photos
#     for photo in fixed_photos + random_photos:
#         photo["batch_code"] = hex_code  # Assign the batch hex code
#         photo["unique_code"] = ten_digit_code  # Assign the unique 10-digit code

#     all_photos.extend(random_photos)  # Combine fixed and random photos

#     # Store the unique code in the session for later validation
#     session["completion_code"] = ten_digit_code

#     return all_photos


# # Usage tracker
# usage_tracker = {}


# def generate_unique_codes(batch_number):
#     hex_code = hex(batch_number)[2:].zfill(6)  # Generate a 6-digit hex code
#     unique_input = f"{batch_number}{random.random()}"
#     ten_digit_code = hashlib.sha1(unique_input.encode()).hexdigest()[:10]
#     return hex_code, ten_digit_code


# def assign_photos(version, comparison_data):
#     fixed_photos = comparison_data[:10]  # First 10 photos are fixed
#     varying_photos = comparison_data[10:]  # Photos available for batch

#     # Assign a batch number based on the version (or another identifier)
#     batch_number = version  # Using version for indicating batch number
#     hex_code, ten_digit_code = generate_unique_codes(batch_number)

#     # Create a unique usage key for tracking
#     usage_key = f"{batch_number}-{version}"

#     # Check and update usage count
#     if usage_key not in usage_tracker:
#         usage_tracker[usage_key] = 0
#     if usage_tracker[usage_key] >= 10:
#         raise ValueError(
#             "This batch and version combination has been used 10 times and is no longer available."
#         )

#     # Increment usage count
#     usage_tracker[usage_key] += 1

#     # Shuffle the varying photos based on version
#     if version in range(2, 11):  # For versions 2 to 10
#         seed = version * 101  # Unique seed per version
#         random.seed(seed)
#         random.shuffle(varying_photos)  # Shuffle the varying photos

#     # Forming rotating batches of 10 from varying photos
#     start_index = (batch_number - 1) * 10 % len(varying_photos)
#     end_index = start_index + 10
#     batch_photos = varying_photos[start_index:end_index]

#     # Handle wrap-around if we run out of photos
#     if end_index > len(varying_photos):
#         remaining = end_index - len(varying_photos)
#         batch_photos += varying_photos[:remaining]

#     # Combine fixed photos with the selected varying set
#     combined_photos = fixed_photos + batch_photos

#     # For v1, do not shuffle combined_photos, keep the original order beyond the fixed photos
#     if version == 1:
#         final_selection = combined_photos
#     else:
#         # For other versions, shuffle and keep the first 20
#         random.seed(seed)  # Re-seed to ensure consistency
#         random.shuffle(combined_photos)
#         final_selection = combined_photos[:20]

#     # Assign codes to the selected photos
#     for photo in final_selection:
#         photo["batch_code"] = hex_code
#         photo["unique_code"] = ten_digit_code

#     # Store the completion code in a session
#     session["completion_code"] = ten_digit_code

#     return final_selection


# Usage tracker dictionary to ensure usage limits on certain combinations
usage_tracker = {}


def generate_unique_codes(batch_number):
    """Generate a unique 6-digit hexadecimal code and a 10-digit unique hash."""
    hex_code = hex(batch_number)[2:].zfill(6)
    unique_input = f"{batch_number}{random.random()}"
    ten_digit_code = hashlib.sha1(unique_input.encode()).hexdigest()[:10]
    return hex_code, ten_digit_code


# def assign_photos(version, comparison_data):
#     """Assign photos to a survey session based on version number."""
#     fixed_photos = comparison_data[:10]  # The first 10 photos are fixed
#     varying_photos = comparison_data[10:]  # Remaining photos to be batched

#     # Discard any photos that don't fit into a full batch of 10
#     varying_photos = varying_photos[: len(varying_photos) - len(varying_photos) % 10]

#     # Assign a batch number based on the version
#     batch_number = version
#     hex_code, ten_digit_code = generate_unique_codes(batch_number)

#     # Track the usage of batch-version combinations
#     usage_key = f"{batch_number}-{version}"
#     if usage_key not in usage_tracker:
#         usage_tracker[usage_key] = 0
#     if usage_tracker[usage_key] >= 10:
#         raise ValueError(
#             "This batch and version combination has been used 10 times and is no longer available."
#         )

#     # Increment usage count
#     usage_tracker[usage_key] += 1

#     # Shuffle the varying photos based on version, except for version 1
#     if version in range(2, 11):
#         seed = version * 101
#         random.seed(seed)
#         random.shuffle(varying_photos)

#     # Determine the batch indices
#     start_index = (version - 1) * 10
#     end_index = start_index + 10

#     # Ensure the selected batch is available
#     if end_index > len(varying_photos):
#         raise ValueError(
#             f"Not enough photos to create a full batch for version {version}"
#         )

#     batch_photos = varying_photos[start_index:end_index]

#     # Combine the fixed photos with the selected batch of 10 varying photos
#     final_selection = fixed_photos + batch_photos

#     # Assign codes to the final set of photos
#     for photo in final_selection:
#         photo["batch_code"] = hex_code
#         photo["unique_code"] = ten_digit_code

#     # Store the completion code for session use
#     session["completion_code"] = ten_digit_code

#     return final_selection


# def assign_photos(version, comparison_data):
#     """Assign photos to a survey session, ensuring unique batches per version."""

#     # First 10 photos are fixed
#     fixed_photos = comparison_data[:10]
#     varying_photos = comparison_data[10:]  # Remaining photos to be batched

#     # Ensure only full batches of 10 are used
#     num_batches = len(varying_photos) // 10
#     varying_photos = varying_photos[: num_batches * 10]

#     # Create batches
#     batch_list = [varying_photos[i : i + 10] for i in range(0, len(varying_photos), 10)]

#     # Assign a batch number and codes
#     batch_number = version
#     hex_code, ten_digit_code = generate_unique_codes(batch_number)

#     # Tracker for usage count
#     usage_key = f"{batch_number}-{version}"
#     if usage_key not in usage_tracker:
#         usage_tracker[usage_key] = 0
#     if usage_tracker[usage_key] >= 10:
#         raise ValueError(
#             "This batch and version combination has been used 10 times and is no longer available."
#         )

#     # Increment usage count for this combination
#     usage_tracker[usage_key] += 1

#     # Shuffle the batches based on version (maintain order for version 1)
#     if version in range(2, 11):
#         seed = version * 101
#         random.seed(seed)
#         random.shuffle(batch_list)

#     # Select the appropriate batch (ensure no overlap and sequential)
#     current_batch = batch_list[version - 1]

#     # Combine fixed photos with the selected batch of 10 varying photos
#     final_selection = fixed_photos + current_batch

#     # Assign codes to the final set of photos
#     for photo in final_selection:
#         photo["batch_code"] = hex_code
#         photo["unique_code"] = ten_digit_code

#     # Store the completion code for session use
#     session["completion_code"] = ten_digit_code

#     return final_selection


def assign_photos(version, comparison_data):
    """Assign photos to a survey session, ensuring a random batch is selected."""

    # First 10 photos are fixed
    fixed_photos = comparison_data[:10]
    varying_photos = comparison_data[10:]  # Remaining photos to be batched

    # Ensure only full batches of 10 are used
    num_batches = len(varying_photos) // 10
    varying_photos = varying_photos[: num_batches * 10]

    # Create batches
    batch_list = [varying_photos[i : i + 10] for i in range(0, len(varying_photos), 10)]

    # Assign a batch number and codes
    batch_number = version
    hex_code, ten_digit_code = generate_unique_codes(batch_number)

    # Tracker for usage count
    usage_key = f"{batch_number}-{version}"
    if usage_key not in usage_tracker:
        usage_tracker[usage_key] = 0
    if usage_tracker[usage_key] >= 10:
        raise ValueError(
            "This batch and version combination has been used 10 times and is no longer available."
        )

    # Increment usage count for this combination
    usage_tracker[usage_key] += 1

    # Shuffle the batches based on version, ensuring v1 selects sequentially
    if version == 1:
        current_batch = batch_list[0]  # Maintain order for version 1
    else:
        seed = version * 101
        random.seed(seed)
        random.shuffle(batch_list)
        current_batch = random.choice(batch_list)  # Select a random batch

    # Combine fixed photos with the selected random batch of 10 photos
    final_selection = fixed_photos + current_batch

    # Assign codes to the final set of photos
    for photo in final_selection:
        photo["batch_code"] = hex_code
        photo["unique_code"] = ten_digit_code

    # Store the completion code for session use
    session["completion_code"] = ten_digit_code

    return final_selection
