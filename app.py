# project/__init__.py

from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from werkzeug import secure_filename
from flask.ext.mysql import MySQL
import time
from passlib.apps import custom_app_context as pwd_context




# config

app = Flask(__name__)
mysql = MySQL()
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = "apple"
app.config["MYSQL_DATABASE_DB"] = "vigu"
app.config["MYSQL_DATABASE_HOST"] = "localhost"
app.config["MYSQL_DATABASE_POST"] = "3306"
mysql.init_app(app)

UPLOAD_FOLDER = '/static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
posttype = {}
posttype = {'blocks':'0','hoods':'1','allfriends':'2','private':'3','neighbours':'4'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/import', methods= ['POST']) 
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        print file;
        if file and allowed_file(file.name):

            filename = secure_filename(file.name)
            request.files['file'].save('static/img/f.jpg')
            return redirect(url_for('uploaded_file',
                                    filename=filename))
	return jsonify(result={"status": 200})


def getuserid(uname):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select userid from users where username = '"+uname+"'")
    row = cursor.fetchone()
    print row[0]
    return row[0]
# routes

@app.route("/")
def load():
    return render_template("index.html")

@app.route('/api/login', methods=['POST'])
def login():
    req = request.json
    print req
    _uname = req['username']
    _pass = req['password']
    status = False
    try:
        if _uname and _pass :
            conn = mysql.connect()
            cursor = conn.cursor()
            query = ("select password from users where username = '"+_uname+"'")
            cursor.execute(query)
            row = cursor.fetchone()
            if row:
	            epass = row[0]
	            ok = pwd_context.verify(_pass, epass) 
	            if ok:
	                status = True
	                return jsonify({'message':'Login Successfull','code':'200','result': status, 'user': req})
	            else:
	                status = True
	                return jsonify({'message':'Enter Valid Username/Password','code':'201','result': status})
	    else:
	    	status = True
	     	return jsonify({'message':'User not registered or Invalid Username/Password','code':'201','result': status})

    except MySQL.Error,e:
        print "ERROR %d IN CONNECTION: %s" % (e.args[0], e.args[1])
        return False

@app.route("/api/logout")
def logout():
    return jsonify({"result": "success"})


@app.route("/api/blockreq/<uname>")
def post(uname):
	userid = getuserid(uname)
	print userid
	status = False
	result = {}
	visibility = 0
	output = {}
	if userid :
		conn = mysql.connect()
		cursor = conn.cursor()
		query = ("Select p.postid, p.subject , p.content , p.datetime  from post p, userdetails u where p.author = u.userid and p.visibility = %s and u.blockid = (select blockid from userdetails where userid = %s) order by p.datetime desc")
		cursor.execute(query,(visibility,userid))
		posts= {}
		posts['items'] = [dict(postid=row[0], subject=row[1], content =row[2], datetime =row[3]) for row in cursor.fetchall()]
		v = posts.get('items')
		if v is None:
			posts['status'] = "Fail"
			posts['message'] = "Content not available"
		else:
			posts['status'] = "Success"
			posts['message'] = "Coontent available"
		conn.close()
		return jsonify(posts)



@app.route("/api/profile/<uname>")
def profile(uname):
	_username = uname
	status = False
	print _username
	conn = mysql.connect()
	cursor = conn.cursor()
	query = ("Select interest from userdetails where userid = (select userid from Users where username = %s)")
	cursor.execute(query,(_username))
	return jsonify({"message":"need to update","code":"201","result": True})

@app.route('/api/search/<uname>/<text>',methods=['GET'])
def search(uname,text):
	userid = getuserid(uname)
	conn = mysql.connect()
	cursor = conn.cursor()
	v_block = 0
	v_hood = 1
	v_all_f = 2
	v_pvt = 3
	v_neigh = 4
	search = '%'+text+'%'
	status = 1
	queryt = "Select p.postid, p.subject, p.content, p.datetime from post p, userdetails u, comments c where p.author = u.userid and c.postid = p.postid and p.visibility = %s and u.userid = %s and (p.subject like %s or p.content like %s or c.comment like %s )"+"union select p.postid, P.subject, p.content, p.datetime from userdetails u,post p, comments c where p.author= u.userid and c.postid = p.postid and p.visibility = %s and u.blockid in (select blockid from blocks where hoodid = (select b.hoodid from blocks b, userdetails u where b.blockid = u.blockid and u.userid = %s)) and ( p.subject like %s or p.content like %s or c.comment like %s )"+"union select p.postid, p.subject, p.content, p.datetime from post p, comments c where  p.visibility = %s and c.postid = p.postid and p.author in (Select userone from frndrequest where (usertwo = %s) and status = %s union  Select usertwo from frndrequest where (userone = %s) and status = %s ) and ( p.subject like %s or p.content like %s or c.comment like %s )"+"union select p.postid, p.subject, p.content, p.datetime from post p, comments c where p.author = %s and  c.postid = p.postid and p.visibility= %s and (p.subject like %s or p.content like %s or c.comment like %s)"
	query = (queryt)
	cursor.execute(query,(v_block,userid,search,search,search,v_hood,userid,search,search,search,v_all_f,userid,status,userid,status,search,search,search,userid,v_all_f,search,search,search))
	posts={}
	posts['items'] = [dict(postid=row[0], subject=row[1], content =row[2], datetime =row[3]) for row in cursor.fetchall()]
	v = posts.get('items')
	print v
	if v is None:
		posts['status'] = "Fail"
		posts['message'] = "Content not available"
	else:
		posts['status'] = "Success"
		posts['message'] = "Coontent available"
	conn.close()
	return jsonify(posts)

@app.route("/api/hoodreq/<uname>")
def hoodpost(uname):
	userid = getuserid(uname)
	status = False
	result = {}
	visibility = 1
	output = {}
	if userid :
		conn = mysql.connect()
		cursor = conn.cursor()
		query = ("Select p.postid, p.subject , p.content , p.datetime  from post p, userdetails u where p.author = u.userid and p.visibility = %s and u.blockid = (select blockid from userdetails where userid = %s) order by p.datetime desc")
		cursor.execute(query,(visibility,userid))
		posts= {}
		posts['items'] = [dict(postid=row[0], subject=row[1], content =row[2], datetime =row[3]) for row in cursor.fetchall()]
		v = posts.get('items')
		if bool(v):
			posts['status'] = "Success"
			posts['message'] = "Coontent available"
		else:
			posts['status'] = "Fail"
			posts['message'] = "Content not available"
		conn.close()
		return jsonify(posts)

@app.route("/api/neigbhorreq/<uname>")
def neigbhorpost(uname):
	userid = getuserid(uname)
	status = False
	result = {}
	visibility = 4
	output = {}
	if userid :
		conn = mysql.connect()
		cursor = conn.cursor()
		query = ("select * from (Select p.postid, p.subject , p.content , p.datetime  from post p where p.author in (Select fromid from neighbours where toid = %s) and p.visibility = %s union select p.postid, p.subject , p.content , p.datetime from post p where p.author = %s and p.visibility = %s)a order By a.datetime desc")
		cursor.execute(query,(userid,visibility,userid,visibility))
		posts= {}
		posts['items'] = [dict(postid=row[0], subject=row[1], content =row[2], datetime =row[3]) for row in cursor.fetchall()]
		v = posts.get('items')
		if bool(v):
			posts['status'] = "Success"
			posts['message'] = "Coontent available"
		else:
			posts['status'] = "Fail"
			posts['message'] = "Content not available"
		conn.close()
		return jsonify(posts)

@app.route("/api/friendreq/<uname>")
def allfriendpost(uname):
	userid = getuserid(uname)
	status = False
	result = {}
	visibility = 2
	status = 1
	output = {}
	if userid :
		conn = mysql.connect()
		cursor = conn.cursor()
		query = ("select * from (Select p.postid, p.subject , p.content , p.datetime  from post p where p.author in (Select userone from frndrequest where (usertwo = %s) and status = %s union select usertwo from frndrequest where (userone = %s)and status = %s) and p.visibility = %s union select p.postid, p.subject , p.content , p.datetime from post p where p.author = %s and p.visibility = %s)a order By a.datetime desc")
		print query
		cursor.execute(query,(userid, status,userid, status, visibility,userid,visibility))
		posts= {}
		posts['items'] = [dict(postid=row[0], subject=row[1], content =row[2], datetime =row[3]) for row in cursor.fetchall()]
		print posts
		v = posts.get('items')
		if bool(v):
			posts['status'] = "Success"
			posts['message'] = "Coontent available"
		else:
			posts['status'] = "Fail"
			posts['message'] = "Content not available"
		conn.close()
		return jsonify(posts)

@app.route("/api/private/<uname>")
def pvtmsg(uname):
	userid = getuserid(uname)
	status = False
	visibility = 3
	if userid :
		conn = mysql.connect()
		cursor = conn.cursor()
		query = ("select * from (select p.postid,p.subject,p.content,p.datetime,concat (u.first_name,' ',u.last_name) from post p,privatemsg m,users u where p.postid = m.postid and m.userid = %s and p.author = u.userid  union select p.postid,p.subject,p.content,p.datetime,concat(u.first_name,' ',u.last_name) from post p, users u where p.author = %s  and p.visibility = %s and u.userid = %s)a order By a.datetime desc")
		cursor.execute(query,(userid,userid, visibility,userid))
		posts= {}
		posts['items'] = [dict(postid=row[0], subject=row[1], content =row[2], datetime =row[3], uname = row[4]) for row in cursor.fetchall()]
		print posts
		v = posts.get('items')
		if bool(v):
			posts['status'] = "Success"
			posts['message'] = "Coontent available"
		else:
			posts['status'] = "Fail"
			posts['message'] = "Content not available"
		conn.close()
		return jsonify(posts)

@app.route('/api/pvtmembers/<username>/<pid>/',methods=['GET'])
def getpvtmembers(pid,username):
    conn = mysql.connect()
    cursor = conn.cursor()
    posts = {}
    uid = getuserid(username)
    query = ("select userid , concat(first_name,' ',last_name) from users where userid in (select userid from privatemsg where postid = %s and userid != %s)")
    cursor.execute(query,(pid,uid))
    posts={}
    posts['items'] = [dict(userid=row[0], name=row[1] ) for row in cursor.fetchall()]
    v = posts.get('items')
    if bool(v):
        posts['status'] = "Success"
        posts['message'] = "Content available"
    else:
        posts['status'] = "Fail"
        posts['message'] = "Content not available"
    conn.close()
    return jsonify(posts)

@app.route('/api/comments/<pid>/',methods=['GET'])
def getcomments(pid):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select c.comment,c.datetime,c.author, concat(u.first_name,' ',u.last_name)  from comments c, users u where u.userid = c.author and c.postid = '"+pid+"'")
    posts={}
    posts['items'] = [dict(comment=row[0], datetime=row[1], author =row[2],username = row[3]) for row in cursor.fetchall()]
    cursor.execute("select p.subject, p.content, p.datetime, concat(u.first_name,' ',u.last_name) from post p, Users u where postid = '"+pid+"' and userid = author")
    posts['post'] = [dict(subject=row[0], content=row[1], datetime =row[2], uname =row[3]) for row in cursor.fetchall()]
    v = posts.get('items')
    if bool(v):
        posts['status'] = "Success"
        posts['message'] = "Content available"
    else:
        posts['status'] = "Fail"
        posts['message'] = "Content not available"
    conn.close()
    return jsonify(posts)


@app.route('/api/pending/<username>',methods = ['GET'])
def pending(username):
	conn = mysql.connect()
	cursor = conn.cursor()
	uid = getuserid(username)
	print uid
	posts ={}
	status = 0
	print "testsssss"
	query1 = ("select userid , concat (first_name,' ',last_name) from users where userid in (select userone  from frndrequest where usertwo = %s and status = %s and fromid != %s union select usertwo from FrndRequest where userone = %s and status = %s and fromid != %s) ") 
	cursor.execute(query1,(uid,status,uid,uid,status,uid))
	posts['pending'] = [dict(userid=row[0], name=row[1]) for row in cursor.fetchall()]
	query2 = ("select userid , concat (first_name,' ',last_name) from users where userid in (select userone  from frndrequest where usertwo = %s and status = %s and fromid = %s union select usertwo from FrndRequest where userone = %s and status = %s and fromid = %s)") 
	cursor.execute(query2,(uid,status,uid,uid,status,uid))
	posts['requested'] = [dict(userid=row[0], name=row[1]) for row in cursor.fetchall()]
	query3 = ("select userid,concat(first_name ,last_name) from users where userid NOT IN (select userone from frndrequest where usertwo = %s union select usertwo from frndrequest where userone = %s) and userid!= %s")
	cursor.execute(query3,(uid,uid,uid))
	posts['tobesent'] = [dict(userid=row[0], name=row[1]) for row in cursor.fetchall()]
	b = posts.get('tobesent')
	s = posts.get('pending') 
	v = posts.get('requested')
	if bool(s) or bool(v) or bool(b):
		posts['status'] = "Success"
		posts['message'] = "Content available"
	else:
		posts['status'] = "Fail"
		posts['message'] = "Content not available or no requests pending"
	conn.close()
	return jsonify(posts)

@app.route('/api/friendrequest/',methods = ['POST'])
def frndrequest():
	req = request.json
	_uname = req["username"]
	toid = req["toid"]
	fromid = getuserid(_uname)
	conn = mysql.connect()
	cursor = conn.cursor()
	status = 0
	posts ={}
	t = time.strftime('%Y-%m-%d %H:%M:%S')
	print t
	query = ("Insert into FrndRequest (userone, usertwo, status, fromid,datetime) values (%s,%s,%s,%s,%s)")
	print "query"
	if (fromid > toid):
		print "if"
		cursor.execute(query,(toid,fromid,status,fromid,t))
		conn.commit()
	else:
		print "else"
		cursor.execute(query,(fromid,toid,status,fromid,t))
		conn.commit()
	fid = cursor.lastrowid
	print fid
	if fid:
		print "success query"
		posts['status'] = "Success"
		posts['message'] = "Content available"
	else:
		print "failed query"
		posts['status'] = "Fail"
		posts['message'] = "Content not available"
	conn.close()
	return jsonify(posts)


@app.route('/api/oldfriends/<username>',methods = ['GET'])
def getnewfriends(username):
    conn = mysql.connect()
    cursor = conn.cursor()
    uid = getuserid(username)
    status = 1
    posts = {}
    query = ("select a.userone, concat(u.first_name, ' ',u.last_name) from(select userone from frndrequest where (usertwo = %s) and status = %s union \
    	select usertwo from frndrequest where (userone = %s) and status = %s )a,users u where u.userid = a.userone")
    cursor.execute(query,(uid,status,uid,status))
    posts['items'] = [dict(id= row[0],name=row[1]) for row in cursor.fetchall()]
    conn.close()
    return jsonify(posts)

@app.route('/api/viewprofile/<pid>/',methods=['GET'])
def vprofile(pid):
    conn = mysql.connect()
    cursor = conn.cursor()
    posts={}
    cursor.execute("select concat(u.first_name, ' ', u.last_name), ud.description, ud.interest, ud.dob from userdetails ud, users u where ud.userid = '"+pid+"' and u.userid = '"+pid+"'")
    posts['post'] = [dict(subject=row[0], content=row[1], datetime =row[2], uname =row[3]) for row in cursor.fetchall()]
    v = posts.get('post')
    if bool(v):
        posts['status'] = "Success"
        posts['message'] = "Content available"
    else:
        posts['status'] = "Fail"
        posts['message'] = "Content not available"
    conn.close()
    return jsonify(posts)

@app.route('/api/post/',methods = ['POST'])
def setposts():
    conn = mysql.connect()
    cursor = conn.cursor()
    req = request.json
    username = req['username']
    print username
    content = req['content']
    subject = req['subject']
    ptype = req['type'].lower()
    posts = {}
    vis = posttype[ptype]
    t = time.strftime('%Y-%m-%d %H:%M:%S')
    uid = getuserid(username)
    print vis
    query=("insert into post(subject,content,datetime,author,visibility) values (%s,%s,%s,%s,%s)")
    cursor.execute(query,(subject,content,t,uid,vis))
    conn.commit()
    fid = cursor.lastrowid
    print fid
    if fid:
        posts['status'] = "Success"
        posts['message'] = "Content available"
    else:
        posts['status'] = "Fail"
        posts['message'] = "Content not available"
    conn.close()
    return jsonify(posts)

@app.route('/api/approvefriend/<username>/<toid>',methods = ['GET'])
def approvefrequest(username,toid):
    conn = mysql.connect()
    cursor = conn.cursor()
    posts = {}
    status = "1"
    t = time.strftime('%Y-%m-%d %H:%M:%S')
    uid = getuserid(username)
    query=("update frndrequest set fromid = %s, status= %s, datetime=%s where userone = %s and usertwo = %s")
    if uid > toid:
        cursor.execute(query,(uid,status,t,toid,uid))
        conn.commit()
    else:
        cursor.execute(query,(uid,status,t,uid,toid))
        conn.commit()
    fid = cursor.lastrowid
    if not fid:
        posts['status'] = "Success"
        posts['message'] = "Content available"
    else:
        posts['status'] = "Fail"
        posts['message'] = "Content not available"
    conn.close()
    return jsonify(posts)

@app.route('/api/rejectfriend/<username>/<toid>',methods = ['GET'])
def rejectfrequest(username,toid):
    conn = mysql.connect()
    cursor = conn.cursor()
    posts = {}
    status = '2'
    t = time.strftime('%Y-%m-%d %H:%M:%S')
    uid = getuserid(username)
    query=("update frndrequest set fromid = %s, status= %s, datetime=%s where userone = %s and usertwo = %s")
    if uid > toid:
        cursor.execute(query,(uid,status,t,toid,uid))
        conn.commit()
    else:
        cursor.execute(query,(uid,status,t,uid,toid))
        conn.commit()
    fid = cursor.lastrowid
    if not fid:
        posts['status'] = "Success"
        posts['message'] = "Content available"
    else:
        posts['status'] = "Fail"
        posts['message'] = "Content not available"
    conn.close()
    return jsonify(posts)


@app.route('/api/addcomment/',methods = ['POST'])
def addcmt():
    conn = mysql.connect()
    cursor = conn.cursor()
    req = request.json
    username = req['username']
    content = req['content']
    pid = req['pid']
    posts = {}
    t = time.strftime('%Y-%m-%d %H:%M:%S')
    uid = getuserid(username)
    query=("insert into comments(postid,comment,datetime,author) values (%s,%s,%s,%s)")
    cursor.execute(query,(pid,content,t,uid))
    conn.commit()
    fid = cursor.lastrowid
    print fid
    if fid:
        posts['status'] = "Success"
        posts['message'] = "Content available"
    else:
        posts['status'] = "Fail"
        posts['message'] = "Content not available"
    conn.close()
    return jsonify(posts)

@app.route('/api/registeraddress/',methods = ['POST'])
def registeraddress():
    conn = mysql.connect()
    cursor = conn.cursor()
    req = request.json
    print "address block"
    print req
    username = req['username']
    uid = getuserid(username)
    print uid
    posts = {}
    doorno = req['doorno']
    aptno = req['aptno']
    street = req['street']
    city = req['city']
    state = req['state']
    uzip = req['zip']
    print "query to start"
    args =(uid,doorno,aptno,street,city,state,uzip,0)
    print args
    result_args = cursor.callproc('newaddressupdates', args)
    if result_args[7] == 0:
    	posts['status'] = "201"
    	posts['message'] = "Inserted"
    else:
    	posts['status'] = "Failed"
    	posts['message'] = "Zip Out of Bound"
	conn.close()
    return jsonify(posts)

@app.route('/api/register/',methods = ['POST'])
def registernewuser():
    print "query to start register"
    conn = mysql.connect()
    cursor = conn.cursor()
    req = request.json
    username = req['username']
    posts = {}
    email = req['email']
    password = req['password']
    lastname = req['lastname']
    firstname = req['firstname']
    out = 0
    hash = pwd_context.encrypt(password)
    print "query to start register"
    createdate = time.strftime('%Y-%m-%d %H:%M:%S')
    print createdate
    args =[out,username,firstname,lastname,email,hash]
    print args
    result_args = cursor.callproc('checkusername', args)
    cursor.execute('select @_checkusername_0')
    row = cursor.fetchone()
    val = row[0]
    print val
    conn.commit()
    if val == 201:
    	posts['status'] = "Success"
    	posts['message'] = "Inserted"
    else:
    	posts['status'] = "Failed"
    	posts['message'] = "User Name already taken"
	conn.close()
    return jsonify(posts)

@app.route('/api/blockchange/',methods = ['POST'])
def blockchng():
    conn = mysql.connect()
    cursor = conn.cursor()
    req = request.json
    username = req['username']
    doorno = req['doorno']
    aptno = req['aptno']
    street = req['street']
    city = req['city']
    state = req['state']
    uzip = req['zip']
    posts = {}
    uid = getuserid(username)
    args = [uid,doorno,aptno,street,city,state,uzip,0]
    print args
    result_args = cursor.callproc('Blockrequest', args)
    print result_args
    print "test"
    posts['status'] = "Success"
    posts['message'] = "Content available"
    conn.close()
    return jsonify(posts)

@app.route('/api/pendingbrequest/<username>/',methods = ['GET'])
def pendingbreq(username):
    conn = mysql.connect()
    print "inside block"
    cursor = conn.cursor()
    posts = {}
    uid = getuserid(username)
    print uid
    status = 0
    query = ("select u.userid,concat(u.first_name,' ',u.last_name),b.breqid from blockrequest b,users u,Userdetails ud where b.userid = ud.userid and u.userid = ud.userid and b.breqid in (select breqid from ApprRequest where userid = %s and status = %s)")
    print query
    cursor.execute(query,(uid,status))
    print "after execute"
    posts['items'] = [dict(uid=row[0], name=row[1],breqid = row[2]) for row in cursor.fetchall()]
    fid = cursor.lastrowid
    v = posts.get('items')
    if bool(v):
        posts['status'] = "Success"
        posts['message'] = "Content available"
    else:
        posts['status'] = "Fail"
        posts['message'] = "Content not available"
    conn.close()
    return jsonify(posts)

@app.route('/api/listofneighbors/<username>/',methods = ['GET'])
def listneighbors(username):
    conn = mysql.connect()
    print "inside block"
    cursor = conn.cursor()
    posts = {}
    uid = getuserid(username)
    print uid
    query = ("select u.userid as uids,  concat(u.first_name,' ',u.last_name) from userdetails ud, users u where ud.blockid = (select s.blockid from userdetails s where userid = %s) and u.userid = ud.userid and ud.userid not in (select toid from Neighbours where fromid = %s)")
    print query
    cursor.execute(query,(uid,uid))
    print "after execute"
    posts['items'] = [dict(uid=row[0], name=row[1]) for row in cursor.fetchall()]
    fid = cursor.lastrowid
    v = posts.get('items')
    if bool(v):
        posts['status'] = "Success"
        posts['message'] = "Content available"
    else:
        posts['status'] = "Fail"
        posts['message'] = "Content not available"
    conn.close()
    return jsonify(posts)

@app.route('/api/addednb/<username>/',methods = ['GET'])
def availneighbors(username):
    conn = mysql.connect()
    print "inside block"
    cursor = conn.cursor()
    posts = {}
    uid = getuserid(username)
    print uid
    query = ("select userid, concat(first_name,' ',last_name) from Users where userid in (select toid from neighbours where fromid = %s and fromid = %s) ")
    print query
    cursor.execute(query,(uid,uid))
    print "after execute"
    posts['items'] = [dict(uid=row[0], name=row[1]) for row in cursor.fetchall()]
    fid = cursor.lastrowid
    v = posts.get('items')
    if bool(v):
        posts['status'] = "Success"
        posts['message'] = "Content available"
    else:
        posts['status'] = "Fail"
        posts['message'] = "Content not available"
    conn.close()
    return jsonify(posts)

@app.route('/api/acceptbrequest/<username>/<brid>',methods = ['GET'])
def aceptrequest(username,brid):
    conn = mysql.connect()
    cursor = conn.cursor()
    posts = {}
    print "inside"
    uid = getuserid(username)
    print brid
    print uid
    args = [uid,brid,0]
    print args
    result_args = cursor.callproc('approverequest',args)
    result = result_args[0]
    if result == 1:
        posts['status'] = "Success"
        posts['message'] = "user approved and added to block "
    else :
        posts['status'] = "Success"
        posts['message'] = "user approval Success"
    conn.close()
    return jsonify(posts)

@app.route('/api/displayprofile/<username>/',methods=['GET'])
def displayprofile(username):
	conn = mysql.connect()
	cursor = conn.cursor()
	posts={}
	userid = getuserid(username)
	print userid
	query = ("select description,interest,dob from userdetails where userid=%s and userid = %s") 
	cursor.execute(query,(userid,userid))
	posts['items'] = [dict( description=row[0],interest=row[1],dob = str(row[2])) for row in cursor.fetchall()]
	conn.close()
	print posts
	return jsonify(posts)

@app.route('/api/addnewnb/',methods = ['POST'])
def addnewnb():
    conn = mysql.connect()
    cursor = conn.cursor()
    req = request.json
    username = req['username']
    nid = req['nid']
    posts = {}
    print nid,username
    uid = getuserid(username)
    t = time.strftime('%Y-%m-%d %H:%M:%S')
    print "query portion"
    query=("insert into neighbours (fromid, toid, datetime) values (%s,%s,%s)")
    cursor.execute(query,(uid,nid,t))
    conn.commit()
    fid = cursor.lastrowid
    print fid
    print "test"
    posts['status'] = "Success"
    posts['message'] = "Content available"
    conn.close()
    return jsonify(posts)

if __name__ == "__main__":
   app.run()