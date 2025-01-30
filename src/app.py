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
    assign_photos,
)

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///responses.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class UserConsent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consent_id = db.Column(db.String(100), unique=True, nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    user_agent = db.Column(db.String(200), nullable=False)
    consent_given = db.Column(db.Boolean, default=False, nullable=False)


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.String(100), nullable=False)
    consent_id = db.Column(db.String(100), nullable=False)  # New field
    version = db.Column(db.Integer, nullable=False)
    image_index = db.Column(db.Integer, nullable=False)
    similarity_score = db.Column(db.Float, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)


# # Routes for consent
# @app.route("/", methods=["GET"])
# def consent():
#     ip = get_client_ip()
#     user_agent = get_user_agent()
#     consent_record = UserConsent.query.filter_by(
#         ip_address=ip, user_agent=user_agent
#     ).first()

#     if consent_record and consent_record.consent_given:
#         return redirect(url_for("index"))
#     return render_template("consent.html")


@app.route("/", methods=["GET"])
def consent():
    ip = get_client_ip()
    user_agent = get_user_agent()
    # Ensure proper database querying
    consent_record = UserConsent.query.filter_by(
        ip_address=ip, user_agent=user_agent
    ).first()

    if consent_record and consent_record.consent_given:
        return redirect(url_for("index"))
    return render_template("consent.html")


# # Routes for consent
@app.route("/give_consent", methods=["POST"])
def give_consent():
    consent_status = request.form.get("consent")
    if consent_status == "accepted":
        ip = get_client_ip()
        user_agent = get_user_agent()
        consent_id = str(uuid.uuid4())  # Generate a unique consent ID
        consent_record = UserConsent(
            consent_id=consent_id,
            ip_address=ip,
            user_agent=user_agent,
            consent_given=True,
        )
        db.session.add(consent_record)
        db.session.commit()
        session["consent_id"] = consent_id  # Store the consent_id in session
        return redirect(url_for("index"))
    elif consent_status == "denied":
        return redirect(url_for("exit"))
    else:
        flash("Please select an option to proceed.")
        return redirect(url_for("consent"))


# @app.route("/index", methods=["GET", "POST"])
# def index():
#     error = None
#     ip = get_client_ip()
#     user_agent = get_user_agent()
#     consent_record = UserConsent.query.filter_by(
#         ip_address=ip, user_agent=user_agent
#     ).first()

#     if not consent_record or not consent_record.consent_given:
#         return redirect(url_for("consent"))

#     # Check if this user has already completed the survey
#     if consent_record:
#         existing_responses = Response.query.filter_by(
#             consent_id=consent_record.consent_id, completed=True
#         ).all()
#         if existing_responses:
#             error = "You have already completed this survey."

#     if request.method == "POST" and not error:
#         answer = request.form.get("answer")
#         if answer != "correct":
#             error = "Incorrect answer. Please select the correct option to proceed."
#         else:
#             participant_id = str(uuid.uuid4())
#             session["participant_id"] = participant_id

#             version = random.choice([1, 2, 3, 4])
#             session["version"] = version
#             session["current_image"] = 0
#             session["start_time"] = datetime.now()

#             comparison_data = get_comparison_data()
#             session["photos"] = assign_photos(version, comparison_data)

#             return redirect(url_for("survey"))

#     return render_template("index.html", error=error)


# @app.route("/index", methods=["GET", "POST"])
# def index():
#     error = None
#     ip = request.remote_addr  # Replace with your method to get client IP
#     user_agent = request.headers.get(
#         "User-Agent"
#     )  # Replace with your method to get user agent

#     consent_record = None  # Replace with your database query logic

#     if consent_record is None or not consent_record.consent_given:
#         return redirect(url_for("consent"))

#     if request.method == "POST" and not error:
#         answer = request.form.get("answer")
#         if answer != "correct":
#             error = "Incorrect answer. Please select the correct option to proceed."
#         else:
#             participant_id = str(uuid.uuid4())
#             session["participant_id"] = participant_id

#             version = random.choice(range(1, 11))  # Randomize from 1 to 10
#             session["version"] = version
#             session["current_image"] = 0
#             session["start_time"] = datetime.now()

#             comparison_data = get_comparison_data()
#             try:
#                 session["photos"] = assign_photos(version, comparison_data)
#                 return redirect(url_for("survey"))
#             except ValueError as e:
#                 error = str(e)  # Capture error if the combination is exhausted
#                 return render_template("index.html", error=error)

#     return render_template("index.html", error=error)


@app.route("/index", methods=["GET", "POST"])
def index():
    error = None
    ip = get_client_ip()
    user_agent = get_user_agent()
    # Query database for consent check
    consent_record = UserConsent.query.filter_by(
        ip_address=ip, user_agent=user_agent
    ).first()

    if not consent_record or not consent_record.consent_given:
        return redirect(url_for("consent"))

    if request.method == "POST" and not error:
        answer = request.form.get("answer")
        if answer != "correct":
            error = "Incorrect answer. Please select the correct option to proceed."
        else:
            participant_id = str(uuid.uuid4())
            session["participant_id"] = participant_id

            version = random.choice(range(1, 11))  # Randomize from 1 to 10
            session["version"] = version
            session["current_image"] = 0
            session["start_time"] = datetime.now()

            comparison_data = get_comparison_data()
            try:
                session["photos"] = assign_photos(version, comparison_data)
                return redirect(url_for("survey"))
            except ValueError as e:
                error = str(e)  # Capture error if the combination is exhausted

    return render_template("index.html", error=error)


# showing consent id on top of survey for transparency
@app.route("/survey", methods=["GET", "POST"])
def survey():
    photos = session.get("photos", [])
    current_image = session.get("current_image", 0)
    consent_id = session.get("consent_id")  # Retrieve the consent_id

    if request.method == "POST":
        similarity_score = request.form.get("similarity_score")

        # Save the response
        participant_id = session.get("participant_id")
        version = session.get("version")

        response = Response(
            participant_id=participant_id,
            consent_id=consent_id,
            version=version,
            image_index=current_image,
            similarity_score=float(similarity_score),
        )

        db.session.add(response)
        db.session.commit()

        # Increment current image index
        current_image += 1
        session["current_image"] = current_image

        if current_image >= len(photos):
            return redirect(url_for("thankyou"))
        else:
            return redirect(url_for("survey"))

    # Render the current image
    try:
        compare_image = photos[current_image]["url"]
    except IndexError:
        return redirect(url_for("thankyou"))

    main_image = url_for("static", filename="images/main.png")

    return render_template(
        "survey.html",
        main_image=main_image,
        compare_image=compare_image,
        current_image=current_image + 1,
        total_images=len(photos),
        consent_id=consent_id,  # Pass the consent_id to the template
    )


# @app.route("/thankyou", methods=["GET", "POST"])
# def thankyou():
#     if request.method == "POST":
#         completion_code = request.form.get("completion_code")
#         if completion_code == "VALID_CODE":
#             responses = Response.query.filter_by(
#                 participant_id=session.get("participant_id"), completed=False
#             ).all()
#             for response in responses:
#                 response.completed = True
#                 db.session.commit()
#             return redirect(url_for("thankyou_complete"))
#         else:
#             flash("Incorrect completion code.")
#             return redirect(url_for("index"))

#     return render_template("thankyou.html")


@app.route("/thankyou", methods=["GET", "POST"])
def thankyou():
    completion_code = session.get(
        "completion_code"
    )  # Retrieve the completion code from the session

    if request.method == "POST":
        entered_code = request.form.get("completion_code")

        # Validate the completion code against the session stored code
        if entered_code == completion_code:
            participant_id = session.get("participant_id")
            responses = []  # Replace with actual response retrieval logic
            for response in responses:
                response.completed = True
                # Uncomment and replace with your DB commit logic
                # db.session.commit()
            return redirect(url_for("thankyou_complete"))
        else:
            flash("Incorrect completion code.")
            return redirect(url_for("index"))

    # Render the page with the completion code
    return render_template("thankyou.html", completion_code=completion_code)


@app.route("/thankyou_complete")
def thankyou_complete():
    start_time = session.get("start_time")
    end_time = datetime.now()

    # Ensure both datetimes are naive
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
            if password == "admin123":  # Replace with your actual password
                session["authenticated"] = True
            else:
                flash("Incorrect password. Please try again.")
                return render_template("login.html")
        else:
            return render_template("login.html")

    responses = Response.query.filter_by(completed=True).all()
    participants = set(response.participant_id for response in responses)
    total_responses = len(responses)
    total_participants = len(participants)

    version_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    total_similarity_score = 0
    version_similarity_sums = {1: 0, 2: 0, 3: 0, 4: 0}

    all_similarity_scores = []

    for response in responses:
        version_counts[response.version] += 1
        total_similarity_score += response.similarity_score
        version_similarity_sums[response.version] += response.similarity_score
        all_similarity_scores.append(response.similarity_score)

    average_similarity = (
        total_similarity_score / total_responses if total_responses else 0
    )

    # Calculate median similarity score
    median_similarity = calculate_median_similarity()

    # Calculate average similarity per version
    version_average_similarity = {
        version: (
            version_similarity_sums[version] / version_counts[version]
            if version_counts[version] > 0
            else 0
        )
        for version in version_counts
    }

    participant_data = []
    for participant in participants:
        participant_responses = [
            response for response in responses if response.participant_id == participant
        ]
        participant_scores = [r.similarity_score for r in participant_responses]
        participant_avg = sum(participant_scores) / len(participant_scores)
        participant_data.append(
            {
                "id": participant,
                "version": (
                    participant_responses[0].version if participant_responses else None
                ),
                "average_score": round(participant_avg, 2),
            }
        )

    return render_template(
        "results.html",
        total_responses=total_responses,
        total_participants=total_participants,
        average_similarity=round(average_similarity, 2),
        median_similarity=median_similarity,
        version_counts=version_counts,
        version_average_similarity=version_average_similarity,
        participant_data=participant_data,
    )


@app.route("/download_results")
def download_results():
    responses = Response.query.filter_by(completed=True).all()

    data = {
        "Participant ID": [response.participant_id for response in responses],
        "Version": [response.version for response in responses],
        "Image Index": [response.image_index for response in responses],
        "Similarity Score": [response.similarity_score for response in responses],
    }

    df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Survey Results")

    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name="survey_results.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False)
