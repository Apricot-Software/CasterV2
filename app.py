# Caster V2
# Developed by Collin Davis
import time
from castersecrets import sql_host, sql_dbname, sql_user, sql_password, nr_user, nr_pass
from flask import Flask, jsonify, render_template, redirect, request, url_for, make_response, session, send_file
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
app.config['SECRET_KEY'] = nr_pass

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
        <div style="background-image: url('https://castersocial.com/static/img/casterlogo.png'); width: 40px; height: 40px; background-size: cover;"></div>
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
    return render_template('caster.html')

@app.route('/robots.txt')
def robots():
    return send_file("static/other/robots.txt")

@app.route('/favicon.ico')
def favicon():
    return send_file("static/img/castersmall.png")

@app.route('/search')
def search():
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

        return redirect(f"/{profile_user}")
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

        try:
            profile_user = c.fetchone()[0]
        except TypeError:
            return redirect(url_for("login"))

        return redirect(f"/{profile_user}")

@app.route('/<profile_user>')
def smol_profile(profile_user):
    if profile_user == "@":
        return "YOU"
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
    

    try:
        displayName = result[0]
    except TypeError:
        return redirect(url_for("login"))
    pfp = result[1]
    bio = result[2]


    return render_template('settings.html', displayName=displayName, pfp=pfp, bio=remove_html_tags(bio))

@app.route('/post')
def post():
    post_id = request.args.get("id")

    token = request.cookies.get("token")

    conn = psycopg2.connect(
        host=sql_host,
        dbname=sql_dbname,
        user=sql_user,
        password=sql_password,
        port=5432
    )
    c = conn.cursor()

    c.execute("SELECT username, postcontent, messageid, timestamp, (SELECT COUNT(*) FROM casterposts WHERE refpostid = %s) AS refpost_count FROM casterposts WHERE messageid = %s", [post_id, post_id])
    fetchedPost = c.fetchone()

    c.execute("SELECT pfp, displayname, isveri FROM usercred WHERE username = %s", [fetchedPost[0]])
    userinfo = c.fetchone()
    
    unixtime = round(float(fetchedPost[3]))
    timestamp = datetime.datetime.utcfromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')
    if userinfo[2] == "YES":
        isveri = "unset"
    else:
        isveri = "none"
    if userinfo:
        pfp = f"{userinfo[0]}"
        handle = f"{fetchedPost[0]}".replace("@", "")
        displayName = f"{userinfo[1]}"
        postContent = f"{fetchedPost[1]}"
        postId = f"{fetchedPost[2]}"
        replys = f"{str(fetchedPost[4])}"
        

    c.execute("SELECT pfp FROM usercred WHERE token = %s", [token])

    try:
        user_pfp = c.fetchone()[0]
    except TypeError:
        user_pfp = "static/img/userdefault.png"

    return render_template("viewpost.html", pfp=pfp, handle=handle, displayName=displayName, isveri=isveri, postContent=postContent, post_id=postId, timestamp=timestamp, replys=replys, user_pfp=user_pfp)



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
    resp.set_cookie('token', '', expires=0)
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

    c.execute("""
            SELECT
            p.username,
            p.postcontent,
            p.messageid,
            p.timestamp,
            (SELECT COUNT(*) FROM casterposts WHERE refpostid = p.messageid) AS refpost_count
        FROM
            casterposts p
        ORDER BY 
            timestamp 
            DESC 
            LIMIT 15 OFFSET %s
            """, [page])

    fetchedPosts = c.fetchall()

    posts = []

    for post in fetchedPosts:
        c.execute("SELECT pfp, displayname, isveri FROM usercred WHERE username = %s", [post[0]])

        userinfo = c.fetchone()
        
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
                "timestamp": f"{timestamp}",
                "replys": f"{post[4]}"
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
    # page = int(request.args.get("page"))
    # page = page * 15
    conn = psycopg2.connect(
        host=sql_host,
        dbname=sql_dbname,
        user=sql_user,
        password=sql_password,
        port=5432
    )
    c = conn.cursor()
    c.execute("""
        SELECT
            p.username,
            p.postcontent,
            p.messageid,
            p.timestamp,
            (SELECT COUNT(*) FROM casterposts WHERE refpostid = p.messageid) AS refpost_count
        FROM
            casterposts p
        WHERE
            to_tsvector('english', p.postcontent) @@ to_tsquery(%s)
        ORDER BY 
            timestamp 
            DESC 
            LIMIT 15
            """, [query])

    fetchedPosts = c.fetchall()

    posts = []

    for post in fetchedPosts:
        c.execute("SELECT pfp, displayname, isveri FROM usercred WHERE username = %s", [post[0]])

        userinfo = c.fetchone()
        
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
                "timestamp": f"{timestamp}",
                "replys": f"{post[4]}"
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
        SELECT
            p.username,
            p.postcontent,
            p.messageid,
            p.timestamp,
            (SELECT COUNT(*) FROM casterposts WHERE refpostid = p.messageid) AS refpost_count
        FROM
            casterposts p
        WHERE
            refpostid=%s
        ORDER BY 
            timestamp 
            DESC 
            LIMIT 15
            OFFSET %s
            """, [refid, page])

    fetchedPosts = c.fetchall()

    posts = []

    for post in fetchedPosts:
        c.execute("SELECT pfp, displayname, isveri FROM usercred WHERE username = %s", [post[0]])

        userinfo = c.fetchone()
        
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
                "timestamp": f"{timestamp}",
                "replys": f"{post[4]}"
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

        

        posts = []

        for post in fetchedPosts:
            
            c.execute("SELECT pfp, displayname, isveri FROM usercred WHERE username = %s", [post[0]])
            userinfo = c.fetchone()
            
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

@app.route('/api/replychain')
def reply_chain_api():
    id = request.args.get("id")
    conn = psycopg2.connect(
        host=sql_host,
        dbname=sql_dbname,
        user=sql_user,
        password=sql_password,
        port=5432
    )
    c = conn.cursor()

    global buildLoop
    buildLoop = True

    posts = []

    while buildLoop:
        c.execute("SELECT username, postcontent, messageid, timestamp, refpostid FROM casterposts WHERE messageid = %s", [id])

        post = c.fetchone()

        



        c.execute("SELECT pfp, displayname, isveri FROM usercred WHERE username = %s", [post[0]])
        userinfo = c.fetchone()
        
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
            posts.insert(0, post_data)
            if post[4] is not None:
                buildLoop = True
                id = post[4]
            else:
                buildLoop = False
                

    return jsonify(posts)

@app.route('/api/replychain/users')
def reply_chain_users_api():
    id = request.args.get("id")
    conn = psycopg2.connect(
        host=sql_host,
        dbname=sql_dbname,
        user=sql_user,
        password=sql_password,
        port=5432
    )
    c = conn.cursor()

    buildLoop = True
    users = []
    seen_usernames = set()

    while buildLoop:
        c.execute("SELECT username, refpostid FROM casterposts WHERE messageid = %s", [id])
        post = c.fetchone()

        if post:
            username = post[0]
            if username not in seen_usernames:
                c.execute("SELECT pfp, bio, displayname, isveri FROM usercred WHERE username = %s", [username])
                userinfo = c.fetchone()
                if userinfo[3] == "YES":
                    isveri = True
                else:
                    isveri = False
                if userinfo:
                    user_info = {
                        "displayName": userinfo[2],
                        "handle": f"@{username}",
                        "isveri": isveri,
                        "pfp": userinfo[0],
                        "bio": userinfo[1]
                    }
                    users.insert(0 ,user_info)
                    seen_usernames.add(username)
            if post[1] is not None:
                id = post[1]
            else:
                buildLoop = False
        else:
            buildLoop = False

    return jsonify(users)

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
    session.permanent = True
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
    app.run()
