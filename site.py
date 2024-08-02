# Caster V2
# Developed by Collin Davis
import time
from realsecrets import sql_host, sql_dbname, sql_user, sql_password, nr_user, nr_pass
from flask import Flask, jsonify, render_template, redirect, request, url_for, make_response
import asyncio
import psycopg2
import os
import re
import hashlib
import string
import bleach
import random
import smtplib
from email.message import EmailMessage
from bs4 import BeautifulSoup
import datetime
import base64

app = Flask(__name__)

valid_chars = "".join([string.digits, string.ascii_letters, "_"])
valid_pass_chars = "".join([string.digits, string.ascii_letters, string.punctuation])
def store_post_content(user_id, content):
    sanitized_content = bleach.clean(content, tags=[], attributes={}, protocols=[], strip=True)
def token_generator(size=36, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def message_id_generator(size=12, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def remove_html_tags(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()




def email_alert(subject, body, to):
    try:
        msg = EmailMessage()
        msg.set_content(body, subtype='html')
        msg['subject'] = subject
        msg['to'] = to
        msg['from'] = nr_user

        server = smtplib.SMTP("smtp.forwardemail.net", 587)
        server.starttls()
        server.login(nr_user, nr_pass)
        server.send_message(msg)

        server.quit()
    except Exception as e:
        print(e)



def convert_mentions_to_links(text, postid, sender_username):
    conn = psycopg2.connect(
        host=sql_host,
        dbname=sql_dbname,
        user=sql_user,
        password=sql_password,
        port=5432
    )
    c = conn.cursor()

    # Regular expression to find mentions in the text
    mention_pattern = r'@(\w+)'

    # Function to replace each mention with a link
    def replace_mention_with_link(match):
        username = match.group(1)
        c.execute("SELECT email FROM usercred WHERE username = %s", [username])
        email = c.fetchone()[0]

        with open('static/img/castersmall.png', 'rb') as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            print(img_base64)

        body = f"""
        <html>
        <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:ital,wght@0,100..700;1,100..700&display=swap" rel="stylesheet">
        <style>
        .title {{
            font-family: "Roboto Mono", monospace;
            font-size: 30px;
            color: white;
        }}
        body {{
            background-color: black;
        }}
        </style>
        </head>
        
        <body style="background-color:#000000; padding: 15px;">
        <img alt="" src="data:image/png;base64,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">
        <h1 class='title'>@{sender_username} mentioned you in a post</h1>
        <a href="https://castersocial.com/post?id={postid}">Click to view post</a>
        </body>
        </html>
        """

        email_alert(f"@{sender_username} mentioned you in a post", body, email)
        return f'<a href="/profile?user={username}">@{username}</a>'


    # Use re.sub to replace all mentions with links
    result = re.sub(mention_pattern, replace_mention_with_link, text)

    return result


@app.route('/')
def home():
    token = request.cookies.get('token')
    print(token)
    if token is not None:
        conn = psycopg2.connect(
            host=sql_host,
            dbname=sql_dbname,
            user=sql_user,
            password=sql_password,
            port=5432
        )
        c = conn.cursor()

        c.execute('SELECT pfp FROM usercred WHERE token = %s', [token])

        try:
            pfp = c.fetchone()[0]
        except TypeError:
            return redirect(url_for('login'))

        return render_template('caster.html', pfp=pfp)
    else:
        return redirect(url_for('login'))

@app.route('/search')
def search():
    token = request.cookies.get('token')
    print(token)
    if token is not None:
        conn = psycopg2.connect(
            host=sql_host,
            dbname=sql_dbname,
            user=sql_user,
            password=sql_password,
            port=5432
        )
        c = conn.cursor()

        c.execute('SELECT pfp FROM usercred WHERE token = %s', [token])

        try:
            pfp = c.fetchone()[0]
        except TypeError:
            return redirect(url_for('login'))

        return render_template('search.html', pfp=pfp)
    else:
        return redirect(url_for('login'))

@app.route('/profile')
def profile():
    profile_user = request.args.get('user')
    if profile_user is not None:
        conn = psycopg2.connect(
            host=sql_host,
            dbname=sql_dbname,
            user=sql_user,
            password=sql_password,
            port=5432
        )

        c = conn.cursor()

        c.execute("SELECT pfp, displayname, bio, isveri FROM usercred WHERE username = %s", [profile_user])

        user_data = c.fetchone()

        pfp = user_data[0]
        displayname = user_data[1]
        bio = user_data[2]
        if user_data[3] == "YES":
            isveri = "unset"
        else:
            isveri = "none"

        return render_template('profile.html', profile_user=profile_user, pfp=pfp, displayname=displayname, bio=bio, isveri=isveri)
    else:
        token = request.cookies.get('token')

        conn = psycopg2.connect(
            host=sql_host,
            dbname=sql_dbname,
            user=sql_user,
            password=sql_password,
            port=5432
        )

        c = conn.cursor()

        c.execute("SELECT username FROM usercred WHERE token = %s", [token])

        profile_user = c.fetchone()[0]

        c.execute("SELECT pfp, displayname, bio, isveri FROM usercred WHERE username = %s", [profile_user])

        user_data = c.fetchone()

        pfp = user_data[0]
        displayname = user_data[1]
        bio = user_data[2]
        if user_data[3] == "YES":
            isveri = "unset"
        else:
            isveri = "none"

        return render_template('profile.html', profile_user=profile_user, pfp=pfp, displayname=displayname, bio=bio, isveri=isveri)

@app.route('/create')
def create():
    token = request.cookies.get('token')
    print(token)
    if token is not None:
        conn = psycopg2.connect(
            host=sql_host,
            dbname=sql_dbname,
            user=sql_user,
            password=sql_password,
            port=5432
        )
        c = conn.cursor()

        c.execute('SELECT pfp FROM usercred WHERE token = %s', [token])

        pfp = c.fetchone()[0]
        print(pfp)
        if pfp is None:
            return redirect(url_for('login'))

        return render_template('post.html', pfp=pfp)
    else:
        return redirect(url_for('login'))

@app.route('/settings')
def settings():
    conn = psycopg2.connect(
        host=sql_host,
        dbname=sql_dbname,
        user=sql_user,
        password=sql_password,
        port=5432
    )
    c = conn.cursor()

    token = request.cookies.get('token')

    c.execute("SELECT displayname, pfp, bio FROM public.usercred WHERE token = %s", [token])
    result = c.fetchone()
    print(result)

    displayName = result[0]
    pfp = result[1]
    bio = result[2]


    return render_template('settings.html', displayName=displayName, pfp=pfp, bio=remove_html_tags(bio))

@app.route('/post')
def post():
    post_id = request.args.get("id")

    token = request.cookies.get("token")
    if token is None:
        return redirect(url_for("login"))

    conn = psycopg2.connect(
        host=sql_host,
        dbname=sql_dbname,
        user=sql_user,
        password=sql_password,
        port=5432
    )
    c = conn.cursor()

    c.execute("SELECT username, postcontent, messageid, timestamp FROM casterposts WHERE messageid = %s", [post_id])
    fetchedPost = c.fetchone()

    c.execute("SELECT pfp, displayname FROM usercred WHERE username = %s", [fetchedPost[0]])
    userinfo = c.fetchone()
    print(userinfo)
    unixtime = round(float(fetchedPost[3]))
    timestamp = datetime.datetime.utcfromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')
    if userinfo:
        pfp = f"{userinfo[0]}"
        handle = f"{fetchedPost[0]}".replace("@", "")
        displayName = f"{userinfo[1]}"
        postContent = f"{fetchedPost[1]}"
        postId = f"{fetchedPost[2]}"
        timestamp = f"{timestamp}"
        print()

    c.execute("SELECT pfp FROM usercred WHERE token = %s", [token])
    user_pfp = c.fetchone()[0]

    return render_template("viewpost.html", pfp=pfp, handle=handle, displayName=displayName, postContent=postContent, post_id=postId, timestamp=timestamp, user_pfp=user_pfp)

@app.route('/login')
def login():
    if request.args.get('message') is not None:
        message = request.args.get('message')
        return render_template('login.html', message=message)
    return render_template('login.html')

@app.route('/signup')
def signup():
    if request.args.get('message') is not None:
        message = request.args.get('message')
        return render_template('signup.html', message=message)
    return render_template('signup.html')

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for("login")))
    resp.delete_cookie("login")
    return resp

@app.route('/api/posts')
async def post_api():
    page = int(request.args.get("page"))
    page = page * 15
    conn = psycopg2.connect(
        host=sql_host,
        dbname=sql_dbname,
        user=sql_user,
        password=sql_password,
        port=5432
    )
    c = conn.cursor()

    c.execute("SELECT username, postcontent, messageid, timestamp FROM casterposts ORDER BY timestamp DESC LIMIT 15 OFFSET %s", [page])

    fetchedPosts = c.fetchall()

    posts = []

    for post in fetchedPosts:
        c.execute("SELECT pfp, displayname, isveri FROM usercred WHERE username = %s", [post[0]])

        userinfo = c.fetchone()
        print(userinfo)
        unixtime = round(float(post[3]))
        timestamp = datetime.datetime.utcfromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')
        if userinfo:
            if userinfo[2] == "YES":
                isveri = True
            else:
                isveri = False

            post_data = {
                "pfp": f"{userinfo[0]}",
                "handle": f"@{post[0]}",
                "displayName": f"{userinfo[1]}",
                "isveri": isveri,
                "postContent": f"{post[1]}",
                "postId": f"{post[2]}",
                "timestamp": f"{timestamp}"
            }
            posts.append(post_data)

    # posts = [
        # {
            # "pfp": "static/img/limeade.png",
            # "handle": "@lime",
            # "displayName": "limeade",
            # "postContent": "This is a test"
        # },
        # {
            # "pfp": "static/img/limeade.png",
            # "handle": "@lime",
            # "displayName": "limeade",
            # "postContent": "comedy is now illegal"
    #         # }
    #     # ]
    return jsonify(posts)

@app.route('/api/searchposts')
async def post_search_api():
    query = request.args.get("query")
    page = int(request.args.get("page"))
    page = page * 15
    conn = psycopg2.connect(
        host=sql_host,
        dbname=sql_dbname,
        user=sql_user,
        password=sql_password,
        port=5432
    )
    c = conn.cursor()

    c.execute("""
            SELECT username, postcontent, messageid, timestamp
            FROM casterposts
            WHERE to_tsvector('english', postcontent) @@ to_tsquery(%s)
            ORDER BY timestamp DESC
            LIMIT 15;
            """, [query])

    fetchedPosts = c.fetchall()

    posts = []

    for post in fetchedPosts:
        c.execute("SELECT pfp, displayname, isveri FROM usercred WHERE username = %s", [post[0]])

        userinfo = c.fetchone()
        print(userinfo)
        unixtime = round(float(post[3]))
        timestamp = datetime.datetime.utcfromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')
        if userinfo:
            if userinfo[2] == "YES":
                isveri = True
            else:
                isveri = False

            post_data = {
                "pfp": f"{userinfo[0]}",
                "handle": f"@{post[0]}",
                "displayName": f"{userinfo[1]}",
                "isveri": isveri,
                "postContent": f"{post[1]}",
                "postId": f"{post[2]}",
                "timestamp": f"{timestamp}"
            }
            posts.append(post_data)

    # posts = [
        # {
            # "pfp": "static/img/limeade.png",
            # "handle": "@lime",
            # "displayName": "limeade",
            # "postContent": "This is a test"
        # },
        # {
            # "pfp": "static/img/limeade.png",
            # "handle": "@lime",
            # "displayName": "limeade",
            # "postContent": "comedy is now illegal"
    #         # }
    #     # ]
    return jsonify(posts)

@app.route('/api/replyposts')
async def reply_posts_api():
    refid = request.args.get("refid")
    page = int(request.args.get("page"))
    page = page * 15
    conn = psycopg2.connect(
        host=sql_host,
        dbname=sql_dbname,
        user=sql_user,
        password=sql_password,
        port=5432
    )
    c = conn.cursor()

    c.execute("""
            SELECT username, postcontent, messageid, timestamp
            FROM casterposts
            WHERE refpostid=%s
            ORDER BY timestamp DESC
            LIMIT 15
            OFFSET %s;
            """, [refid, page])

    fetchedPosts = c.fetchall()

    posts = []

    for post in fetchedPosts:
        c.execute("SELECT pfp, displayname, isveri FROM usercred WHERE username = %s", [post[0]])

        userinfo = c.fetchone()
        print(userinfo)
        unixtime = round(float(post[3]))
        timestamp = datetime.datetime.utcfromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')
        if userinfo:
            if userinfo[2] == "YES":
                isveri = True
            else:
                isveri = False

            post_data = {
                "pfp": f"{userinfo[0]}",
                "handle": f"@{post[0]}",
                "displayName": f"{userinfo[1]}",
                "isveri": isveri,
                "postContent": f"{post[1]}",
                "postId": f"{post[2]}",
                "timestamp": f"{timestamp}"
            }
            posts.append(post_data)

    # posts = [
        # {
            # "pfp": "static/img/limeade.png",
            # "handle": "@lime",
            # "displayName": "limeade",
            # "postContent": "This is a test"
        # },
        # {
            # "pfp": "static/img/limeade.png",
            # "handle": "@lime",
            # "displayName": "limeade",
            # "postContent": "comedy is now illegal"
    #         # }
    #     # ]
    return jsonify(posts)

@app.route('/api/searchusers')

@app.route('/api/userposts')
def user_post_api():
    user = request.args.get("user")
    page = int(request.args.get("page"))
    page = page * 15
    if user is not None:
        conn = psycopg2.connect(
            host=sql_host,
            dbname=sql_dbname,
            user=sql_user,
            password=sql_password,
            port=5432
        )
        c = conn.cursor()

        c.execute("SELECT username, postcontent, messageid, timestamp FROM casterposts WHERE username = %s ORDER BY timestamp DESC LIMIT 15 OFFSET %s", [user, page])

        fetchedPosts = c.fetchall()

        print(fetchedPosts)

        posts = []

        for post in fetchedPosts:
            print(post)
            c.execute("SELECT pfp, displayname, isveri FROM usercred WHERE username = %s", [post[0]])
            userinfo = c.fetchone()
            print(userinfo)
            unixtime = round(float(post[3]))
            timestamp = datetime.datetime.utcfromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')
            if userinfo:
                if userinfo[2] == "YES":
                    isveri = True
                else:
                    isveri = False

                post_data = {
                    "pfp": f"{userinfo[0]}",
                    "handle": f"@{post[0]}",
                    "displayName": f"{userinfo[1]}",
                    "isveri": isveri,
                    "postContent": f"{post[1]}",
                    "postId": f"{post[2]}",
                    "timestamp": f"{timestamp}"
                }
                posts.append(post_data)

        return jsonify(posts)

@app.route('/api/sendpost', methods=['POST', 'GET'])
def send_post_api():
    token = request.cookies.get('token')
    if token is not None:
        conn = psycopg2.connect(
            host=sql_host,
            dbname=sql_dbname,
            user=sql_user,
            password=sql_password,
            port=5432
        )

        c = conn.cursor()

        c.execute('SELECT username FROM usercred WHERE token = %s', [token])

        username = c.fetchone()[0]
        messageid = token_generator(20)
        postContent = request.get_json()['content']
        timestamp = time.time()

        c.execute('INSERT INTO casterposts (messageid, username, postcontent, timestamp) VALUES (%s, %s, %s, %s)', [messageid, username, convert_mentions_to_links(bleach.linkify(bleach.clean(postContent)), messageid, username), timestamp])
        conn.commit()
        conn.close()
        return jsonify({"message": "Post successfully created", "postId": f"{messageid}"}), 200
    else:
        return jsonify({"error": "Unauthorized"}), 401

@app.route('/api/sendreplypost', methods=['POST', 'GET'])
def send_reply_post_api():
    token = request.cookies.get('token')
    refid = request.args.get('refid')
    if token is not None:
        conn = psycopg2.connect(
            host=sql_host,
            dbname=sql_dbname,
            user=sql_user,
            password=sql_password,
            port=5432
        )

        c = conn.cursor()

        c.execute('SELECT username FROM usercred WHERE token = %s', [token])

        username = c.fetchone()[0]
        messageid = token_generator(20)
        postContent = request.get_json()['content']
        timestamp = time.time()

        c.execute('INSERT INTO casterposts (messageid, username, postcontent, timestamp, refpostid) VALUES (%s, %s, %s, %s, %s)', [messageid, username, convert_mentions_to_links(bleach.linkify(bleach.clean(postContent)), messageid, username), timestamp, refid])
        conn.commit()
        conn.close()
        return jsonify({"message": "Post successfully created", "postId": f"{messageid}"}), 200
    else:
        return jsonify({"error": "Unauthorized"}), 401



ALLOWED_EXTENSIONS = {'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/api/uploadpfp", methods=['POST', 'GET'])
def uploadpfp():
    token = request.cookies.get("token")

    conn = psycopg2.connect(
        host=sql_host,
        dbname=sql_dbname,
        user=sql_user,
        password=sql_password,
        port=5432
    )

    c = conn.cursor()

    c.execute('SELECT username FROM usercred WHERE token = %s', [token])

    username = c.fetchone()

    if username is not None:
        file_str = token_generator(25)
        if 'file' not in request.files:
            return jsonify({"message": "No file. Keeping past pfp"}), 200
        file = request.files['file']
        if file.filename == '':
            return jsonify({"message": "No file. Keeping past pfp"}), 200
        if file and allowed_file(file.filename):
            pfp_file_path = os.path.join("static/usrpfp", f"{file_str}.png")
            file.save(pfp_file_path)
            c.execute('UPDATE usercred SET pfp = %s WHERE token = %s', [pfp_file_path, token])
            conn.commit()
            conn.close()
            return jsonify({"message": "File successfully uploaded"}), 200
        else:
            return jsonify({"error": "Invalid file type"}), 400
    else:
        return jsonify({"error": "Unauthorized, invalid token"}), 401

@app.route("/api/updatedisplayname", methods=['POST', 'GET'])
def updatedisplayname():
    displayName = request.get_json()['content']

    if len(displayName) > 26:
        return jsonify({"error": "Display name too big"}), 400
    if len(displayName) < 2:
        return jsonify({"error": "Display name too small"}), 400

    token = request.cookies.get("token")

    conn = psycopg2.connect(
        host=sql_host,
        dbname=sql_dbname,
        user=sql_user,
        password=sql_password,
        port=5432
    )

    c = conn.cursor()

    c.execute('SELECT username FROM usercred WHERE token = %s', [token])

    username = c.fetchone()

    if username is not None:
        c.execute('UPDATE usercred SET displayname = %s WHERE token = %s', [bleach.clean(displayName), token])
        conn.commit()
        conn.close()
        return jsonify({"message": "Display name successfully updated"}), 200
    else:
        return jsonify({"error": "Unauthorized, invalid token"}), 401

@app.route("/api/updatebio", methods=['POST', 'GET'])
def updatebio():
    bio = request.get_json()['content']

    if len(bio) > 160:
        return jsonify({"error": "Bio too big"}), 400

    token = request.cookies.get("token")

    conn = psycopg2.connect(
        host=sql_host,
        dbname=sql_dbname,
        user=sql_user,
        password=sql_password,
        port=5432
    )

    c = conn.cursor()

    c.execute('SELECT username FROM usercred WHERE token = %s', [token])

    username = c.fetchone()

    if username is not None:
        if len(bio) == 0:
            bio = "We don't know much about this person ):"
        c.execute('UPDATE usercred SET bio = %s WHERE token = %s', [bleach.linkify(bleach.clean(bio)), token])
        conn.commit()
        conn.close()
        return jsonify({"message": "Bio successfully updated"}), 200
    else:
        return jsonify({"error": "Unauthorized, invalid token"}), 401

@app.route('/api/validatesignup', methods=['POST', 'GET'])
async def validatesignup():
    username = request.form['username'].lower()
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']


    if password == confirm_password:
        try:
            conn = psycopg2.connect(
                host=sql_host,
                dbname=sql_dbname,
                user=sql_user,
                password=sql_password,
                port=5432
            )
        except:
            await asyncio.sleep(4)
            return redirect(request.url)
        c = conn.cursor()
        c.execute("SELECT * FROM usercred WHERE username = %s", [str(username.lower())])
        result = c.fetchone()
        if result is None:
            for char in username:
                if char not in valid_chars:
                    conn.close()
                    return redirect(url_for('signup', message="Invalid character(s) in username (Only letters, numbers and underscores)"))

            c.execute("SELECT * FROM usercred WHERE email = %s", [str(email)])
            result = c.fetchone()
            if result is None:
                for char in password:
                    if char not in valid_pass_chars:
                        conn.close()
                        return redirect(url_for('signup', message="Invalid character(s) in password (Only letters, numbers and punctuation)"))

                if len(username) < 2 or len(username) > 22:
                    conn.close()
                    return redirect(url_for('signup', message="Username needs to be between 2 - 22 characters"))

                if len(password) < 8 or len(password) > 52:
                    conn.close()
                    return redirect(url_for('signup', message="Password need to be between 8 - 52 characters"))


                sign_up_token = token_generator()
                h = hashlib.new("SHA256")
                h.update(bytes(password, encoding="utf-8"))
                hashed_password = h.hexdigest()
                c.execute("INSERT INTO usercred (username, password, token, email, displayname, bio, pfp) VALUES (%s, %s, %s, %s, %s, %s, %s)", [username.lower(), hashed_password, sign_up_token, email, username.lower(), f"Hello, world. I'm {username.lower()}.", "static/img/userdefault.png"])
                email_token = token_generator()
                c.execute("INSERT INTO emailtokens (token, email) VALUES (%s, %s)", [email_token, email])
                conn.commit()
                conn.close()
                print(email)
                email_alert("Welcome to Caster",
                                        f"To get started on Caster, click this link to verify your email: https://castersocial.com/verifyemail?token={email_token}",
                                        f"{email}")
                # system_message(f"{username.lower()} signed up with a invalid email", "error")
                return redirect(url_for('login', message="Check your email for a verification message"))

            elif result is not None:
                conn.close()
                return redirect(url_for('signup', message="Email is taken"))

        elif result is not None:
            conn.close()
            return redirect(url_for('signup', message="Username is taken"))

    elif not password == confirm_password:
        return redirect(url_for('signup', message="Passwords do not match"))

@app.route('/api/validatelogin', methods=['POST', 'GET'])
async def validatelogin():
    username = request.form['username'].lower()
    password = request.form['password']
    h = hashlib.new("SHA256")
    h.update(bytes(password, encoding="utf-8"))
    hashed_password = h.hexdigest()
    try:
        conn = psycopg2.connect(
            host=sql_host,
            dbname=sql_dbname,
            user=sql_user,
            password=sql_password,
            port=5432
            )
    except:
        await asyncio.sleep(4)
        return redirect(request.url)
    c = conn.cursor()
    c.execute("SELECT * FROM usercred WHERE (username = %s OR email = %s) AND password = %s", [str(username), str(username), str(hashed_password)])
    result = c.fetchone()
    if result is None:
        conn.close()
        return redirect(url_for('login', message="Incorrect Username or Password"))

    settoken = result[2]
    c.execute("SELECT veriemail FROM usercred WHERE (username = %s OR email = %s)", [str(username), str(username)])
    result = c.fetchone()
    if result[0] is None:
        conn.close()
        return redirect(url_for('login', message="Please verify your email"))

    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('token', settoken)
    conn.close()
    return resp

@app.route('/verifyemail')
def verifyemail():
    try:
        conn = psycopg2.connect(host=sql_host, dbname=sql_dbname, user=sql_user,
                                password=sql_password, port=5432)
    except:
        time.sleep(4)
        return redirect(request.url)

    c = conn.cursor()
    if request.args.get('token') is None:
        conn.close()
        return redirect(url_for('login'))
    else:
        email_token = request.args.get('token')
        c.execute("SELECT * FROM emailtokens WHERE token = %s ", [email_token])
        result = c.fetchone()
        if result is None:
            conn.close()
            return redirect(url_for('login'))
        else:
            c.execute("DELETE FROM emailtokens WHERE token = %s", [email_token])
            c.execute("UPDATE usercred SET veriemail = 'YES' WHERE email = %s", [result[1]])
            conn.commit()
            conn.close()
            return redirect(url_for('login', message="Your email has been verified. You can now log in."))


if __name__ == '__main__':
    app.run(debug=True)