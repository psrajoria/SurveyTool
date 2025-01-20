# from flask import Flask, render_template, request
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)

# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///responses.db"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# db = SQLAlchemy(app)


# class Response(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     age = db.Column(db.Integer, nullable=False)
#     feedback = db.Column(db.Text, nullable=False)

#     def __repr__(self):
#         return f"<Response {self.name}>"


# # db.create_all()


# @app.route("/")
# def index():
#     return render_template("index.html")


# @app.route("/submit", methods=["POST"])
# def submit():
#     name = request.form.get("name")
#     age = request.form.get("age")
#     feedback = request.form.get("feedback")

#     response = Response(name=name, age=age, feedback=feedback)
#     db.session.add(response)
#     db.session.commit()

#     return "Thank you for your feedback!"


# @app.route("/results")
# def results():
#     responses = Response.query.all()
#     total_responses = len(responses)
#     average_age = round(
#         sum([response.age for response in responses]) / total_responses, 1
#     )
#     unique_names = len(set([response.name for response in responses]))
#     return render_template(
#         "results.html",
#         responses=responses,
#         total_responses=total_responses,
#         average_age=average_age,
#         unique_names=unique_names,
#     )


# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)


# from flask import Flask, render_template, request
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)

# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///responses.db"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# db = SQLAlchemy(app)


# class Response(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     age = db.Column(db.Integer, nullable=False)
#     similarity_score = db.Column(db.Float, nullable=False)

#     def __repr__(self):
#         return f"<Response {self.name}>"


# @app.route("/")
# def index():
#     return render_template("index.html")


# @app.route("/submit", methods=["POST"])
# def submit():
#     name = request.form.get("name")
#     age = request.form.get("age")
#     similarity_score = request.form.get("similarity_score")

#     response = Response(
#         name=name, age=int(age), similarity_score=float(similarity_score)
#     )
#     db.session.add(response)
#     db.session.commit()

#     return "Thank you for your feedback!"


# @app.route("/results")
# def results():
#     responses = Response.query.all()
#     total_responses = len(responses)
#     average_age = (
#         round(sum([response.age for response in responses]) / total_responses, 1)
#         if total_responses > 0
#         else 0
#     )
#     average_similarity = (
#         round(
#             sum([response.similarity_score for response in responses])
#             / total_responses,
#             2,
#         )
#         if total_responses > 0
#         else 0
#     )
#     unique_names = len(set([response.name for response in responses]))
#     return render_template(
#         "results.html",
#         responses=responses,
#         total_responses=total_responses,
#         average_age=average_age,
#         average_similarity=average_similarity,
#         unique_names=unique_names,
#     )


# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)


# from flask import Flask, render_template, request, redirect, url_for, session
# from flask_sqlalchemy import SQLAlchemy

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
#     images = [
#         "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT0dMzIMHGDfk0q1jLF2NJaYX7-lJTmHxxkaoTf2nR54FMm0O22zdpA68n2DAefKB80gnXbfmU3xlsoffRHgMvyCg",
#         "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Elon_Musk_Royal_Society_crop.jpg/330px-Elon_Musk_Royal_Society_crop.jpg",
#         "https://avatars.githubusercontent.com/u/52934110?v=4",
#         # Add more image URLs as needed
#     ]

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

#         if current_image + 1 < len(images):
#             session["current_image"] = current_image + 1
#             return redirect(url_for("survey"))
#         else:
#             return redirect(url_for("results"))

#     current_image = session.get("current_image", 0)
#     return render_template(
#         "survey.html",
#         main_image=images[0],  # Main image for comparison
#         compare_image=images[current_image],
#         current_image=current_image + 1,
#         total_images=len(images),
#     )


# @app.route("/results")
# def results():
#     responses = Response.query.all()
#     return render_template("results.html", responses=responses)


# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///responses.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    image_index = db.Column(db.Integer, nullable=False)
    similarity_score = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Response {self.name}>"


# Load URLs and founder names from Excel
def get_comparison_data():
    df = pd.read_excel("FounderImageURL60.xlsx")
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
    main_image = "https://upload.wikimedia.org/wikipedia/commons/d/da/Elizabeth_Holmes_2014_cropped.jpg"  # Replace with the actual main image URL
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
            return redirect(url_for("results"))

    current_image = session.get("current_image", 0)
    return render_template(
        "survey.html",
        main_image=main_image,
        compare_image=comparison_data[current_image]["url"],
        current_image=current_image + 1,
        total_images=len(comparison_data),
    )


@app.route("/results")
def results():
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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
