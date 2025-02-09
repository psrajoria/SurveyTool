from flask import request, session, flash, redirect, url_for
import random
import pandas as pd
import hashlib
import json
import os
from functools import wraps


PHOTO_SETS_FILENAME = "data/photo_sets.json"


# Utilities
def get_client_ip():
    return request.remote_addr


def get_user_agent():
    return request.headers.get("User-Agent")


def generate_unique_participant_id():
    ip = get_client_ip()
    user_agent = get_user_agent()
    unique_string = f"{ip}-{user_agent}"
    return hashlib.sha256(unique_string.encode()).hexdigest()


def get_comparison_data():
    df = pd.read_excel("data/FounderImageURL60.xlsx")
    return [
        {"id": row["founder_identifier_uuid"], "url": row["download_url"]}
        for _, row in df.iterrows()
    ]


def generate_unique_codes(batch_number, version):
    batch_code = f"{batch_number:02x}"
    unique_input = f"{batch_number}{version}{random.random()}"
    completion_code = hashlib.sha1(unique_input.encode()).hexdigest()[:10].upper()
    return batch_code, batch_code, completion_code


def generate_photo_sets():
    comparison_data = get_comparison_data()

    fixed_photos = comparison_data[:10]
    varying_photos = comparison_data[10:]

    batch_size = 50
    num_batches = (len(varying_photos) + batch_size - 1) // batch_size
    version_count = 10

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


def ensure_step_access(step_name):
    """
    Decorator to ensure access to certain routes is only allowed
    if the user has completed prior steps.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Define a sequential requirement. After each step is completed,
            # a flag is set in the session.
            required_steps = {
                "question": "consent_given",  # Can access 'question' if 'consent_given' in session
                "sample": "question_answered",  # Can access 'sample' if 'question_answered' in session
                "survey": "sample_read",  # Can access 'survey' if 'question_answered' in session
                "feedback": "survey_completed",  # Can access 'feedback' if 'survey_completed' in session
                "thankyou": "feedback_given",  # Can access 'thankyou' if 'feedback_given' in session
                "thankyou_complete": "completion_code_entered",  # Can access 'thankyou_complete' if 'completion_code_entered' in session
            }

            required_step = required_steps.get(step_name)
            if required_step and not session.get(required_step):
                flash("Please complete the previous steps first.")
                return redirect(url_for("consent"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator
