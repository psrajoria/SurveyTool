# from flask import Flask, render_template, request, redirect, url_for, session
# from flask_sqlalchemy import SQLAlchemy
# import pandas as pd

# app = Flask(__name__)
# app.secret_key = "supersecretkey"

# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///responses.db"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# db = SQLAlchemy(app)


# class Response(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     age = db.Column(db.Integer, nullable=False)
#     email = db.Column(db.String(100), nullable=False)
#     image_index = db.Column(db.Integer, nullable=False)
#     similarity_score = db.Column(db.Float, nullable=False)

#     def __repr__(self):
#         return f"<Response {self.name}>"


# # Load URLs and founder names from Excel
# def get_comparison_data():
#     df = pd.read_excel("FounderImageURL60.xlsx")
#     return [
#         {"name": row["founder_identifier_uuid"], "url": row["download_url"]}
#         for _, row in df.iterrows()
#     ]


# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         session["name"] = request.form.get("name")
#         session["age"] = request.form.get("age")
#         session["email"] = request.form.get("email")
#         session["current_image"] = 0  # Start with the first image
#         return redirect(url_for("survey"))

#     return render_template("index.html")


# @app.route("/survey", methods=["GET", "POST"])
# def survey():
#     main_image = "https://upload.wikimedia.org/wikipedia/commons/d/da/Elizabeth_Holmes_2014_cropped.jpg"  # Replace with the actual main image URL
#     comparison_data = get_comparison_data()

#     if request.method == "POST":
#         similarity_score = request.form.get("similarity_score")
#         current_image = session.get("current_image", 0)
#         response = Response(
#             name=session["name"],
#             age=int(session["age"]),
#             email=session["email"],
#             image_index=current_image,
#             similarity_score=float(similarity_score),
#         )
#         db.session.add(response)
#         db.session.commit()

#         if current_image + 1 < len(comparison_data):
#             session["current_image"] = current_image + 1
#             return redirect(url_for("survey"))
#         else:
#             return redirect(url_for("results"))

#     current_image = session.get("current_image", 0)
#     return render_template(
#         "survey.html",
#         main_image=main_image,
#         compare_image=comparison_data[current_image]["url"],
#         current_image=current_image + 1,
#         total_images=len(comparison_data),
#     )


# @app.route("/results")
# def results():
#     responses = Response.query.all()
#     comparison_data = get_comparison_data()

#     # Map image index to founder name
#     for response in responses:
#         response.founder_name = comparison_data[response.image_index]["name"]

#     total_responses = len(responses)
#     average_age = (
#         sum(r.age for r in responses) / total_responses if total_responses else 0
#     )
#     average_similarity = (
#         sum(r.similarity_score for r in responses) / total_responses
#         if total_responses
#         else 0
#     )
#     unique_names = len(set(r.name for r in responses))

#     return render_template(
#         "results.html",
#         responses=responses,
#         total_responses=total_responses,
#         average_age=round(average_age, 2),
#         unique_names=unique_names,
#         average_similarity=round(average_similarity, 2),
#     )


# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)


# from flask import Flask, render_template, request, redirect, url_for, session, flash
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
import io


app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///responses.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Define Response model
class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    image_index = db.Column(db.Integer, nullable=False)
    similarity_score = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Response {self.name}>"


# Load comparison data
def get_comparison_data():
    df = pd.read_excel("data/FounderImageURL60.xlsx")
    return [
        {"name": row["founder_identifier_uuid"], "url": row["download_url"]}
        for _, row in df.iterrows()
    ]


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session["name"] = request.form.get("name")
        session["age"] = request.form.get("age")
        session["email"] = request.form.get("email")
        session["current_image"] = 0  # Start with the first image
        return redirect(url_for("survey"))
    return render_template("index.html")


@app.route("/survey", methods=["GET", "POST"])
def survey():
    main_image = "https://upload.wikimedia.org/wikipedia/commons/d/da/Elizabeth_Holmes_2014_cropped.jpg"
    comparison_data = get_comparison_data()

    if request.method == "POST":
        similarity_score = request.form.get("similarity_score")
        current_image = session.get("current_image", 0)
        response = Response(
            name=session["name"],
            age=int(session["age"]),
            email=session["email"],
            image_index=current_image,
            similarity_score=float(similarity_score),
        )
        db.session.add(response)
        db.session.commit()

        if current_image + 1 < len(comparison_data):
            session["current_image"] = current_image + 1
            return redirect(url_for("survey"))
        else:
            return redirect(url_for("thankyou"))

    current_image = session.get("current_image", 0)
    return render_template(
        "survey.html",
        main_image=main_image,
        compare_image=comparison_data[current_image]["url"],
        current_image=current_image + 1,
        total_images=len(comparison_data),
    )


@app.route("/thankyou", methods=["GET", "POST"])
def thankyou():
    if request.method == "POST":
        code = request.form.get("code")
        if code == "123":  # Replace with your actual code validation logic
            return render_template("thankyou_complete.html")
        else:
            flash("Invalid code. Please try again.")
    return render_template("thankyou.html")


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

    responses = Response.query.all()
    comparison_data = get_comparison_data()

    # Map image index to founder name
    for response in responses:
        response.founder_name = comparison_data[response.image_index]["name"]

    total_responses = len(responses)
    average_age = (
        sum(r.age for r in responses) / total_responses if total_responses else 0
    )
    average_similarity = (
        sum(r.similarity_score for r in responses) / total_responses
        if total_responses
        else 0
    )
    unique_names = len(set(r.name for r in responses))

    return render_template(
        "results.html",
        responses=responses,
        total_responses=total_responses,
        average_age=round(average_age, 2),
        unique_names=unique_names,
        average_similarity=round(average_similarity, 2),
    )


@app.route("/download_results")
def download_results():
    responses = Response.query.all()
    comparison_data = get_comparison_data()

    # Map image index to founder name
    data = []
    for response in responses:
        founder_name = comparison_data[response.image_index]["name"]
        data.append(
            {
                "Name": response.name,
                "Age": response.age,
                "Email": response.email,
                "Founder Name": founder_name,
                "Similarity Score": response.similarity_score,
            }
        )

    # Create a DataFrame and write to Excel
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Results")

    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name="survey_results.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
