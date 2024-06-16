from product import app
from flask_mail import Mail,Message
from random import *
from flask import render_template

app.config["MAIL_SERVER"]="smtp.gmail.com"
app.config["MAIL_USERNAME"]="nkumarteja123@gmail.com"
app.config["MAIL_PASSWORD"]="yrgf hzhl eopm"
app.config["MAIL_USE_TLS"]=False
app.config["MAIL_USE_SSL"]=True
app.config["MAIL_PORT"]=465

mail=Mail(app)

def sendemail(useremail):
    try:
        otp=randint(100000,999999)
        body1=render_template("email_temp.html",otp=otp)
        msg=Message(sender="nkumarteja123@gmail.com",recipients=[useremail],subject="OTP verification for ProductIn",html=body1)
        mail.send(msg)
        return otp
    except:
        return -1
