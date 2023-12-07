from product import app,db
from flask import *
from product.models import *
from flask_login import login_user,logout_user,login_required,current_user
from product import login_manager
from flask_bcrypt import Bcrypt
from product.email import *

bcrypt=Bcrypt(app)

email_productin=0
user=0
otp_productin=0
email_count=0
dash=["div1","product"]

@login_manager.user_loader
def user_loader(user_id):
	return User.query.filter_by(id=user_id).first()

@app.route('/')
@app.route("/home")
def home():
	return render_template("home.html",products=product.query.all())


@app.route("/signup",methods=["POST","GET"])
def signup():
	if request.method=="POST":
		message=""
		check=User.query.filter_by(username=request.form["username"]).first()
		check1=User.query.filter_by(email=request.form["email"]).first()

		if(request.form["password"]!=request.form["password1"]):
			message+="Passowrd didn't match.  "
		if(check is not None):
			message+="Username is already exist.  "
		if(check1 is not None):
			message+="Email is already exist."
		if(message!=""):
			flash(message,"danger")
			return redirect(url_for("signup"))
		else:
			hashed_pass=bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")
			user1=User(u=request.form["username"],e=request.form["email"],p=hashed_pass,isa=False)
			global email_productin,user,otp_productin
			email_productin=request.form["email"]
			user=user1
			otp_productin=sendemail(email_productin)
			if(otp_productin!=-1):
				return redirect(url_for("verification"))
			else:
				flash("Please check your network","danger")
				user=email_productin=otp_productin=email_count=0
				return redirect(url_for("signup"))

	return render_template("signup.html")

@app.route("/verification",methods=["POST","GET"])
def verification():
	global user,email_productin,otp_productin,email_count
	if(user==0 or email_productin==0 or otp_productin==0):
		flash("Please enter your credentials. Then you will get the otp for email verification. ","danger")
		return redirect(url_for("signup"))
	else:
		if(request.method=="POST"):
			if(email_count>=5):
				user=email_productin=otp_productin=email_count=0
				flash("5 attempts for email verification is completed. Please try to signup again","danger")
				return redirect(url_for("signup"))
			if(request.form["otp"]==str(otp_productin)):
				db.session.add(user)
				db.session.commit()
				user=email_productin=otp_productin=email_count=0
				flash("You have successfully create account. You can login now. ","success")
				return redirect(url_for("home"))
			else:
				email_count+=1
				flash("OTP is incorrect. Please try again","danger")
				return redirect(url_for("verification"))
		return render_template("email_verification.html",email=email_productin)

@app.route("/signin",methods=["POST","GET"])
def signin():
	if request.method=="POST":
		if(request.form["userormail"]=="username"):
			check=User.query.filter_by(username=request.form["username"]).first()
		else:
			check=User.query.filter_by(email=request.form["username"]).first()
		if(check is None):
			flash("Login credentials are wrong. Please check once","danger")
			return redirect(url_for("signin"))
		else:
			pass_check=bcrypt.check_password_hash(check.password,request.form["password"])
			if(pass_check):
				if(check.isadmin==0):
					login_user(check)
					return redirect(url_for("userpage"))
				else:
					login_user(check)
					return redirect(url_for("adminpage"))
			else:
				flash("Login credentials are wrong. Please check once","danger")
				return redirect(url_for("signin"))

	return render_template("signin.html")

@app.route("/userpage",methods=["POST","GET"])
@login_required
def userpage():
	if(current_user.isadmin==True):
		return redirect(url_for("adminpage"))
	if(request.method=="POST" and request.form["submit"]=="buy_item"):
		id=request.form["id"]
		name=request.form["pname"]
		price=request.form["price"]
		check=booking.query.filter_by(cid=current_user.id,pid=id).first()
		if(check is not None):
			flash("It is already booked","danger")
			return redirect(url_for("home"))
		prod=product.query.filter_by(id=id).first()
		if(prod is None):
			flash("Item is not found.","danger")
			return redirect(url_for("home"))
		if(prod.name!=name or prod.price!=float(price)):
			flash("Item is manipulated. Please try again. ","danger")
			return redirect(url_for("home"))
		bookings=booking(c=current_user.id,p=id)
		db.session.add(bookings)
		db.session.commit()
		return redirect(url_for("userpage"))
	if(request.method=="POST" and request.form["submit"]=="sell_item"):
		pid=request.form["pid"]
		bookings=booking.query.filter_by(cid=current_user.id,pid=pid).first()
		if(bookings is None):
			flash("There is no such booking.Please try again","danger")
			return redirect(url_for("userpage"))
		db.session.delete(bookings)
		db.session.commit()
		return redirect(url_for("userpage"))
	return render_template("userpage.html",bookings=booking.query.filter_by(cid=current_user.id).all(),products=product.query.all())

@app.route("/adminpage",methods=["POST","GET"])
@login_required
def adminpage():
	if(current_user.isadmin==False):
		return redirect(url_for("userpage"))
	global dash
	#if we use request.form.get("submit",None) the it will never send keyerror and also if value is not found then None will be set as default
	if(request.method=="POST" and request.form.get("submit",None)=="remove"):
		account=User.query.filter_by(id=request.form["userid"]).first()
		userid=request.form["userid"]
		username=request.form["username"]
		email=request.form["email"]
		password=request.form["password"]
		admin=request.form["admin"]
		if admin=="False":
			admin=False
		else:
			admin=True
		if(account is None):
			flash("Account is already removed","danger")
			return redirect(url_for("adminpage"))
		if(account.id==int(userid) and account.username==username and account.email==email and account.password==password and account.isadmin==admin):
			db.session.delete(account)
			db.session.commit()
			bookings=booking.query.filter_by(cid=userid).all()
			for i in bookings:
				db.session.delete(i)
				db.session.commit()
			dash=["div2","accounts"]
			return redirect(url_for("adminpage"))
		else:
			dash=["div2","accounts"]
			flash("User credentials are manipulated. Please check. ","danger")
			return redirect(url_for("adminpage"))
	elif(request.method=="POST" and request.form.get("submit",None)=="add"):
		username=request.form["username"]
		email=request.form["email"]
		password=request.form["password"]
		admin=request.form["admin"]
		if(int(admin)!=0):
			admin=True
		else:
			admin=False
		message=""
		check=User.query.filter_by(email=email).first()
		check1=User.query.filter_by(username=username).first()
		if(check is not None):
			message+="Email is already exist. "
		if(check1 is not None):
			message+="Username is already exist. "
		if(message!=""):
			dash=["div2","accounts"]
			flash(message+" To add the current account delete the existed account. ","danger")
			return redirect(url_for("adminpage"))
		else:
			hashed_pass=bcrypt.generate_password_hash(password).decode("utf-8")
			account=User(u=username,e=email,p=hashed_pass,isa=admin)
			db.session.add(account)
			db.session.commit()
			dash=["div2","accounts"]
			return redirect(url_for("adminpage"))
	elif(request.method=="POST" and request.form.get("submit",None)=="add_item"):
		item_name=request.form["item_name"]
		price=request.form["price"]
		desc=request.form["desc"]
		message=""
		check1=product.query.filter_by(name=item_name).first()
		check2=product.query.filter_by(description=desc).first()
		if(check1 is not None):message+="Item name is already exist. "
		if(check2 is not None):message+="Description is already exist. "
		if(message!=""):
			dash=["div1","product"]
			flash(message,"danger")
			return redirect(url_for("adminpage"))
		products=product(n=item_name,p=price,d=desc)
		db.session.add(products)
		db.session.commit()
		dash=["div1","product"]
		return redirect(url_for("adminpage"))
	elif(request.method=="POST" and request.form["submit"]=="remove_item"):
		id=int(request.form["id"])
		name=request.form["item_name"]
		price=float(request.form["price"])
		desc=request.form["desc"]
		products=product.query.filter_by(id=id).first()
		dash=["div1","product"]
		if(products is None):
			flash("Item is already removed","danger")
			return redirect(url_for("adminpage"))
		if(products.id!=id or products.name!=name or products.price!=price or products.description!=desc):
			flash("Item details are manipulated. Refresh the page and try again. ","danger")
			return redirect(url_for("adminpage"))
		db.session.delete(products)
		db.session.commit()
		bookings=booking.query.filter_by(pid=id).all()
		for i in bookings:
			db.session.delete(i)
			db.session.commit()
		redirect(url_for("adminpage"))
	elif(request.method=="POST" and request.form["submit"]=="remove_booking"):
		cid=request.form["cid"]
		pid=request.form["pid"]
		bookg=booking.query.filter_by(cid=cid,pid=pid).first()
		dash=["div3","bookings"]
		if(bookg is None):
			flash("Item is not found.","danger")
			return redirect(url_for("adminpage"))
		db.session.delete(bookg)
		db.session.commit()
		return redirect(url_for("adminpage"))
	elif(request.method=="POST" and request.form["submit"]=="update_item"):
		pid=request.form["pid"]
		pname=request.form["pname"]
		price=request.form["price"]
		desc=request.form["desc"]
		check=product.query.filter_by(id=pid).first()
		if(check is None):
				flash("item is not found","danger")
				return redirect(url_for("adminpage"))
		check.name=pname
		check.price=price
		check.description=desc
		db.session.commit()
		return redirect(url_for("adminpage"))
	return render_template("adminpage.html",users=User.query.all(),products=product.query.all(),bookings=booking.query.all(),dash=dash)


@app.route("/logout")
@login_required
def logout():
	global dash
	dash=["div1","product"]
	logout_user()
	flash("Logout successfully.","success")
	return redirect(url_for("home"))
