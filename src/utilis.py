from flask import request, session
import random
import pandas as pd
import hashlib
import json
import os


PHOTO_SETS_FILENAME = "data/photo_sets.json"


# Utilities
def get_client_ip():
    return request.remote_addr


def get_user_agent():
    return request.headers.get("User-Agent")


def get_comparison_data():
    df = pd.read_excel("data/FounderImageURL60.xlsx")
    return [
        {"id": row["founder_identifier_uuid"], "url": row["download_url"]}
        for _, row in df.iterrows()
    ]


def generate_unique_codes(batch_number, version):
    batch_code = f"{batch_number:02x}"
    unique_input = f"{batch_number}{version}{random.random()}"
    completion_code = hashlib.sha1(unique_input.encode()).hexdigest()[:10]
    return batch_code, batch_code, completion_code


def generate_photo_sets():
    comparison_data = get_comparison_data()

    fixed_photos = comparison_data[:10]
    varying_photos = comparison_data[10:]

    batch_size = 50
    num_batches = (len(varying_photos) + batch_size - 1) // batch_size
    version_count = 4

    photo_sets = []

    for version in range(1, version_count + 1):
        for batch_number in range(1, num_batches + 1):
            start_index = (batch_number - 1) * batch_size
            end_index = min(start_index + batch_size, len(varying_photos))
            current_batch = varying_photos[start_index:end_index]

            if current_batch:
                if version > 1:
                    random.shuffle(current_batch)

                hex_code, ten_digit_code, completion_code = generate_unique_codes(
                    batch_number, version
                )

                photo_sets.append(
                    {
                        "fixed_photos": fixed_photos,  # Store full photo data
                        "current_batch": current_batch,  # Store full photo data
                        "batch_code": hex_code,
                        "unique_code": ten_digit_code,
                        "completion_code": completion_code,
                        "version": version,
                        "batch_number": batch_number,
                        "used": False,
                    }
                )

    with open(PHOTO_SETS_FILENAME, "w") as file:
        json.dump(photo_sets, file, indent=2)

    return photo_sets


def load_or_create_photo_sets():
    if os.path.exists(PHOTO_SETS_FILENAME):
        with open(PHOTO_SETS_FILENAME, "r") as file:
            photo_sets = json.load(file)
    else:
        photo_sets = generate_photo_sets()
        with open(PHOTO_SETS_FILENAME, "w") as file:
            json.dump(photo_sets, file)
    return photo_sets
