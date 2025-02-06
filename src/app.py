from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file,
)
import json
from flask_migrate import Migrate

from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import random
import uuid
import io
from datetime import datetime
from utilis import (
    get_client_ip,
    get_user_agent,
    get_comparison_data,
    load_or_create_photo_sets,
)
import hashlib


def generate_unique_participant_id():
    ip = get_client_ip()
    user_agent = get_user_agent()
    unique_string = f"{ip}-{user_agent}"
    return hashlib.sha256(unique_string.encode()).hexdigest()


from functools import wraps


app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///responses.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)

PHOTO_SETS_FILENAME = "data/photo_sets.json"

# from models import Response

# Global to track photo sets
photo_sets = load_or_create_photo_sets()


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


def assign_photos():
    # Ensure availability of un-used photo sets
    available_photo_sets = [s for s in photo_sets if not s["used"]]

    if not available_photo_sets:
        raise ValueError("No more sets available.")

    selected_set = random.choice(available_photo_sets)

    # Load all comparison data, print for troubleshooting
    complete_photo_data = get_comparison_data()
    print(f"Loaded comparison data with {len(complete_photo_data)} entries.")

    fixed_photo_details = [
        photo
        for photo in complete_photo_data
        if any(fp["id"] == photo["id"] for fp in selected_set["fixed_photos"])
    ]

    current_batch_details = [
        photo
        for photo in complete_photo_data
        if any(cp["id"] == photo["id"] for cp in selected_set["current_batch"])
    ]

    session["completion_code"] = selected_set["completion_code"]
    session["batch_code"] = selected_set["batch_code"]
    session["version"] = selected_set["version"]
    session["photos"] = fixed_photo_details + current_batch_details
    session["current_image"] = 0

    # Debug output to verify assignment
    print(f"Assigned batch: {session['batch_code']}, Version: {session['version']}")
    print(f"Fixed photos assigned: {len(fixed_photo_details)}")
    print(f"Current batch photos assigned: {len(current_batch_details)}")
    print(f"Total photos assigned: {len(session['photos'])}")


def check_survey_completion():
    """
    Check if the survey has already been completed using the consent_id.
    If completed, redirect with a flash message indicating completion.
    """
    consent_id = session.get("consent_id")

    if consent_id:
        # Check if there are any completed responses associated with this consent_id
        completed_responses = Response.query.filter_by(
            consent_id=consent_id, completed=True
        ).all()

        if completed_responses:
            flash("You have already completed this survey.")
            return redirect(url_for("thankyou_complete"))

    # Return None if the survey has not been completed
    return None


class UserConsent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consent_id = db.Column(db.String(100), unique=True, nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    user_agent = db.Column(db.String(200), nullable=False)
    consent_given = db.Column(db.Boolean, default=False, nullable=False)


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.String(100), nullable=False)
    consent_id = db.Column(db.String(100), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    image_index = db.Column(db.Integer, nullable=False)
    similarity_score = db.Column(db.Float, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    batch_code = db.Column(db.String(6), nullable=False)  # Assumes you store this info
    photo_id = db.Column(db.String(100), nullable=False)  # New column for photo ID
    completion_code = db.Column(
        db.String(10), nullable=True
    )  # New column for completion code
    mturk_id = db.Column(
        db.String(100), nullable=True
    )  # New column for Worker MTurk ID
    image_displayed = db.Column(db.Boolean, default=False, nullable=False)  # New column


class FeedbackResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.String(100), nullable=False)
    consent_id = db.Column(db.String(100), nullable=False)
    features_considered = db.Column(db.Text, nullable=False)
    improvement_suggestions = db.Column(db.Text, nullable=True)


@app.route("/", methods=["GET"])
def consent():
    ip = get_client_ip()
    user_agent = get_user_agent()
    consent_record = UserConsent.query.filter_by(
        ip_address=ip, user_agent=user_agent
    ).first()

    if consent_record and consent_record.consent_given:
        return redirect(url_for("index"))
    return render_template("consent.html")


@app.route("/give_consent", methods=["POST"])
def give_consent():
    consent_status = request.form.get("consent")
    if consent_status == "accepted":
        ip = get_client_ip()
        user_agent = get_user_agent()
        consent_id = str(uuid.uuid4())
        consent_record = UserConsent(
            consent_id=consent_id,
            ip_address=ip,
            user_agent=user_agent,
            consent_given=True,
        )
        db.session.add(consent_record)
        db.session.commit()
        session["consent_id"] = consent_id
        return redirect(url_for("index"))
    elif consent_status == "denied":
        return redirect(url_for("exit"))
    else:
        flash("Please select an option to proceed.")
        return redirect(url_for("consent"))


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/index", methods=["GET", "POST"])
@ensure_step_access("index")
def index():
    error = None
    ip = get_client_ip()
    user_agent = get_user_agent()
    consent_record = UserConsent.query.filter_by(
        ip_address=ip, user_agent=user_agent
    ).first()

    if not consent_record or not consent_record.consent_given:
        return redirect(url_for("consent"))
        # Check if this user has already completed the survey
    if consent_record:
        existing_responses = Response.query.filter_by(
            consent_id=consent_record.consent_id, completed=True
        ).all()
        if existing_responses:
            error = "You have already completed this survey."

    if request.method == "POST" and not error:
        answer = request.form.get("answer")
        if answer != "correct":
            error = "Incorrect answer. Please select the correct option to proceed."
        else:
            # participant_id = str(uuid.uuid4())
            participant_id = generate_unique_participant_id()
            session["participant_id"] = participant_id
            session["start_time"] = datetime.now()
            session["question_answered"] = True

            try:
                assign_photos()
                # print(f"The current photos assigned are", assign_photos())
                return redirect(url_for("sample"))
            except ValueError as e:
                error = str(e)

    return render_template("index.html", error=error)


@app.route("/sample", methods=["GET", "POST"])
@ensure_step_access("sample")
def sample():
    if "question_answered" not in session:
        return redirect(url_for("consent"))

    # Handle the POST request to move to the survey
    if request.method == "POST":
        session["sample_read"] = True
        # Redirect to the first photo in the survey
        if "photos" in session and len(session["photos"]) > 0:
            first_photo_id = session["photos"][0][
                "id"
            ]  # Get the hex ID of the first photo
            return redirect(url_for("survey", photo_id=first_photo_id))
    main_image = url_for("static", filename="images/main.png")
    sample_image = "https://images.crunchbase.com/image/upload/itjrb3ayy0rgopgi53st.png"

    return render_template(
        "sample.html", main_image=main_image, sample_image=sample_image
    )


# @app.route("/survey", methods=["GET", "POST"])
# @ensure_step_access("survey")
# def survey():
#     if "sample_read" not in session:
#         return redirect(url_for("consent"))

#     photos = session.get("photos", [])
#     current_image = session.get("current_image", 0)
#     consent_id = session.get("consent_id")

#     if request.method == "POST":

#         similarity_score = request.form.get("similarity_score")
#         image_not_displayed = request.form.get("imageNotDisplayed") == "1"
#         image_displayed = (
#             not image_not_displayed
#         )  # True by default, False if checkbox is checked

#         # Save the response
#         participant_id = session.get("participant_id")
#         version = session.get("version")
#         # batch_code = photos[0]["batch_code"]  # Assuming first photo has batch code
#         batch_code = session.get("batch_code")
#         photo_id = photos[current_image][
#             "id"
#         ]  # Retrieve photo ID for the current image

#         response = Response(
#             participant_id=participant_id,
#             consent_id=consent_id,
#             version=version,
#             image_index=current_image,
#             photo_id=photo_id,
#             similarity_score=float(similarity_score),
#             batch_code=batch_code,
#             completed=False,  # Initial state is not completed
#             image_displayed=image_displayed,  # Set based on checkbox
#         )

#         db.session.add(response)
#         db.session.commit()

#         current_image += 1
#         session["current_image"] = current_image

#         if current_image >= len(photos):
#             print(f"Current image index: {current_image}, Total images: {len(photos)}")
#             print("Survey completed.")
#             session["survey_completed"] = True
#             print(session["survey_completed"])
#             session.modified = True
#             return redirect(url_for("feedback"))
#         else:
#             return redirect(url_for("survey"))

#     try:
#         compare_image = photos[current_image]["url"]
#     except IndexError:
#         return redirect(url_for("thankyou"))

#     main_image = url_for("static", filename="images/main.png")

#     return render_template(
#         "survey.html",
#         main_image=main_image,
#         compare_image=compare_image,
#         current_image=current_image + 1,
#         total_images=len(photos),
#         consent_id=consent_id,
#     )


@app.route("/survey/<photo_id>", methods=["GET", "POST"])
@ensure_step_access("survey")
def survey(photo_id):
    if "sample_read" not in session:
        return redirect(url_for("consent"))

    photos = session.get("photos", [])

    # Try to find the index of the current photo in the photos list
    current_image_index = next(
        (index for index, photo in enumerate(photos) if photo["id"] == photo_id), None
    )

    # Check if the current_image_index is valid
    if current_image_index is None:
        print(
            f"Error: No photo found with ID {photo_id}. Redirecting to thank you page."
        )
        return redirect(url_for("thankyou"))  # If the photo_id is invalid

    consent_id = session.get("consent_id")

    # Safely retrieve the current photo since current_image_index is valid
    current_photo = photos[current_image_index]

    if request.method == "POST":
        similarity_score = request.form.get("similarity_score")
        image_not_displayed = request.form.get("imageNotDisplayed") == "1"
        image_displayed = not image_not_displayed

        # Save response logic here
        participant_id = session.get("participant_id")
        version = session.get("version")
        batch_code = session.get("batch_code")

        response = Response(
            participant_id=participant_id,
            consent_id=consent_id,
            version=version,
            image_index=current_image_index,
            photo_id=current_photo["id"],
            similarity_score=float(similarity_score),
            batch_code=batch_code,
            completed=False,
            image_displayed=image_displayed,
        )

        db.session.add(response)
        db.session.commit()

        # Move to the next photo
        next_image_index = current_image_index + 1

        if next_image_index >= len(photos):
            session["survey_completed"] = True
            return redirect(url_for("feedback"))
        else:
            next_photo_id = photos[next_image_index]["id"]
            print(f"Redirecting to next photo with ID: {next_photo_id}")  # Debug print
            return redirect(url_for("survey", photo_id=next_photo_id))

    # Render the survey for the current photo
    compare_image = current_photo["url"]
    main_image = url_for("static", filename="images/main.png")

    return render_template(
        "survey.html",
        main_image=main_image,
        compare_image=compare_image,
        current_image=current_image_index + 1,
        total_images=len(photos),
        consent_id=consent_id,
        current_photo=current_photo,  # Pass the current photo as well
    )


@app.route("/feedback", methods=["GET", "POST"])
@ensure_step_access("feedback")
def feedback():
    if request.method == "POST":
        features_considered = request.form.getlist("features_considered")
        improvement_suggestions = request.form.get("improvement_suggestions")

        feedback = FeedbackResponse(
            participant_id=session.get("participant_id"),
            consent_id=session.get("consent_id"),
            features_considered=",".join(features_considered),
            improvement_suggestions=improvement_suggestions,
        )

        db.session.add(feedback)
        db.session.commit()

        # Mark feedback as given
        session["feedback_given"] = True

        return redirect(url_for("thankyou"))

    return render_template("feedback.html")


@app.route("/thankyou", methods=["GET", "POST"])
def thankyou():
    # if "survey_completed" not in session:
    # if "survey_completed" not in session or "feedback_given" not in session:
    if not session.get("survey_completed") or not session.get("feedback_given"):
        flash("Please complete the survey and feedback to proceed.")

        return redirect(url_for("consent"))
    completion_check = check_survey_completion()
    if completion_check:
        return completion_check

    completion_code = session.get("completion_code")

    if request.method == "POST":
        entered_code = request.form.get("completion_code")
        mturk_id = request.form.get("mturk_id")

        if entered_code == completion_code:
            participant_id = session.get("participant_id")

            # Store the entered completion code in session (or DB if required)
            session["entered_completion_code"] = entered_code
            session["mturk_id"] = mturk_id

            # Mark survey responses as completed
            responses = Response.query.filter_by(
                participant_id=participant_id, completed=False
            ).all()
            for response in responses:
                response.completed = True
                response.completion_code = entered_code
                response.mturk_id = mturk_id
            db.session.commit()

            # Mark the photo set as used
            for photo_set in photo_sets:
                if photo_set["completion_code"] == completion_code:
                    photo_set["used"] = True
                    break
            # Save updated photo sets to JSON
            with open(PHOTO_SETS_FILENAME, "w") as file:
                json.dump(photo_sets, file, indent=2)

            return redirect(url_for("thankyou_complete"))
        else:
            flash("Incorrect completion code.")
            return redirect(url_for("thankyou"))

    return render_template("thankyou.html", completion_code=completion_code)


@app.route("/thankyou_complete")
def thankyou_complete():
    start_time = session.get("start_time")
    end_time = datetime.now()

    if start_time.tzinfo is not None:
        start_time = start_time.replace(tzinfo=None)

    if end_time.tzinfo is not None:
        end_time = end_time.replace(tzinfo=None)

    elapsed_time = end_time - start_time
    return render_template("thankyou_complete.html", elapsed_time=elapsed_time)


@app.route("/results", methods=["GET", "POST"])
def results():
    if "authenticated" not in session:
        if request.method == "POST":
            password = request.form.get("password")
            if password == "admin123":
                session["authenticated"] = True
            else:
                flash("Incorrect password. Please try again.")
                return render_template("login.html")
        else:
            return render_template("login.html")

    responses = Response.query.filter_by(completed=True).all()
    participants = set(response.participant_id for response in responses)

    # Compute additional information
    total_responses = len(responses)
    unique_participants = len(participants)
    similarity_scores = [response.similarity_score for response in responses]
    average_similarity = sum(similarity_scores) / len(similarity_scores)

    from statistics import median

    median_similarity = median(similarity_scores)

    # Version and participant-specific data
    version_counts = {i: 0 for i in range(1, 11)}  # Defaults to 0 for 1-10
    version_average_similarity = {i: [] for i in range(1, 11)}

    for response in responses:
        version_counts[response.version] += 1
        version_average_similarity[response.version].append(response.similarity_score)

    for version in version_average_similarity:
        scores = version_average_similarity[version]
        version_average_similarity[version] = sum(scores) / len(scores) if scores else 0

    # Participant data for table
    participant_data = []
    for participant in participants:
        participant_responses = [
            r for r in responses if r.participant_id == participant
        ]
        avg_score = sum(r.similarity_score for r in participant_responses) / len(
            participant_responses
        )
        participant_data.append(
            {
                "id": participant,
                "version": (
                    participant_responses[0].version if participant_responses else None
                ),
                "average_score": avg_score,
                "responses": participant_responses,  # Include all responses from this participant
            }
        )

    return render_template(
        "results.html",
        total_responses=total_responses,
        total_participants=unique_participants,
        average_similarity=average_similarity,
        median_similarity=median_similarity,
        version_counts=version_counts,
        version_average_similarity=version_average_similarity,
        participant_data=participant_data,
    )


# def export_to_excel(filename):
#     responses = Response.query.all()
#     data = []
#     for response in responses:
#         data.append(
#             {
#                 "Participant ID": response.participant_id,
#                 "Consent ID": response.consent_id,
#                 "Batch Code": response.batch_code,
#                 "Version": response.version,
#                 "Image ID": response.photo_id,
#                 "Image Index": response.image_index,
#                 "Similarity Score": response.similarity_score,
#                 "Completed": response.completed,
#                 # "Completion Code": session.get(
#                 #     "entered_completion_code", "N/A"
#                 # ),  # Store completion code\
#                 "Completion Code": response.completion_code,
#                 "MTurk ID": response.mturk_id,
#             }
#         )

#     df = pd.DataFrame(data)
#     df.to_excel(filename, index=False)


def export_to_excel(filename):
    responses = Response.query.all()
    feedbacks = FeedbackResponse.query.all()

    # Create a dictionary to map feedback to participant and consent IDs
    feedback_map = {}
    for feedback in feedbacks:
        key = (feedback.participant_id, feedback.consent_id)
        feedback_map[key] = {
            "Features Considered": feedback.features_considered,
            "Improvement Suggestions": feedback.improvement_suggestions,
        }

    data = []
    for response in responses:
        participant_id = response.participant_id
        consent_id = response.consent_id

        feedback_info = feedback_map.get(
            (participant_id, consent_id),
            {"Features Considered": "N/A", "Improvement Suggestions": "N/A"},
        )

        data.append(
            {
                "Participant ID": participant_id,
                "Consent ID": consent_id,
                "Batch Code": response.batch_code,
                "Version": response.version,
                "Image ID": response.photo_id,
                "Image Index": response.image_index,
                "Similarity Score": response.similarity_score,
                "Image Displayed": response.image_displayed,
                "Completed": response.completed,
                "Completion Code": response.completion_code,
                "MTurk ID": response.mturk_id,
                "Features Considered": feedback_info["Features Considered"],
                "Improvement Suggestions": feedback_info["Improvement Suggestions"],
            }
        )

    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)


@app.route("/download_results", methods=["GET"])
def download_results():
    filename = "survey_results.xlsx"
    export_to_excel(filename)
    return send_file(filename, as_attachment=True)


@app.route("/exit")
def exit():
    return render_template("exit.html")


def calculate_median_similarity():
    similarities = [
        response.similarity_score
        for response in Response.query.filter_by(completed=True).all()
    ]
    if similarities:
        sorted_scores = sorted(similarities)
        mid = len(sorted_scores) // 2
        if len(sorted_scores) % 2 == 0:
            return (sorted_scores[mid - 1] + sorted_scores[mid]) / 2.0
        else:
            return sorted_scores[mid]
    return 0


# if __name__ == "__main__":
# with app.app_context():
#     db.create_all()
# app.run(debug=False)
#    app.run(host="0.0.0.0", port=5000, debug=True)
