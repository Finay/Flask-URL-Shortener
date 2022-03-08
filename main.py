from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import validators
import random
from string import ascii_lowercase, ascii_uppercase, digits

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stuff.db'
# Initialize the database
db = SQLAlchemy(app)
appip = "http://127.0.0.1:5000"
failfile = "fail.html"
allowed = ascii_lowercase + ascii_uppercase + digits + "-_!"


# Create db model
class URLS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<Entry %r>' % self.id


@app.route("/", methods=["POST", "GET"])
def addEntry():
    if request.method == "POST":
        url = "http://" + request.form["url"]
        if validators.url(url):
            pref = request.form["pref"].strip()
            if pref == "":
                randomstr = getuniquestr(4)
                testingquery = URLS.query.filter_by(url=url).first()
                if testingquery is not None:
                    return render_template("complete.html", shorturl=appip + "/" + testingquery.path)
            elif checkstringallowed(pref) and URLS.query.filter_by(path=pref).first() is None:
                randomstr = pref
            else:
                return render_template(failfile, errormsg="Your preferred shortlink was taken or includes characters "
                                                          "other than \"" + allowed + '"')
            entry = URLS(url=url, path=randomstr)
            try:
                db.session.add(entry)
                db.session.commit()
                return render_template("complete.html", shorturl=appip + "/" + randomstr)
            except:
                return render_template(failfile)
        else:
            return render_template(failfile, errormsg="Invalid URL")
    else:
        title = "Shorten URLS!"
        return render_template("home.html", title=title, appip=appip)


@app.route("/<path>")
def redir(path):
    query = URLS.query.filter_by(path=path).first()
    if query is not None:
        return redirect(query.url)
    else:
        return render_template(failfile, errormsg="That short url does not work :(")


def getuniquestr(length):
    randomstr = "".join(random.choice(ascii_lowercase) for i in range(length))
    query = URLS.query.filter_by(path=randomstr).first()
    if query is not None:
        randomstr = getuniquestr(length)
    return randomstr


def checkstringallowed(string, maxlength=20, allowedchars=allowed):
    if len(string) >= maxlength:
        return False
    for i in string:
        if i not in allowedchars:
            return False
    return True


if __name__ == "__main__":
    app.run(debug=True)
