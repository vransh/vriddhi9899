from flask import  Flask,render_template, redirect,request,flash,url_for,session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,BooleanField,PasswordField,ValidationError
from wtforms.validators import DataRequired,EqualTo,length
import json
from datetime import datetime
from flask_login import LoginManager,current_user,login_user, login_required,logout_user
from flask_login import UserMixin
import winsound
import random
from werkzeug.security import check_password_hash,generate_password_hash

with open(r'C:\Users\Dell\ansh\innovate_app\templates\configure.json', 'r') as c:
    params = json.load(c)["params"]


app = Flask(__name__)




app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
app.config['SECRET_KEY']='superfeifj43uhf&^Uhajhwefi43y7rf43iday898&98'

    


db = SQLAlchemy(app)

mail = Mail(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('notfound.html'),404

class Comments(db.Model,UserMixin):
    sno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    description=db.Column(db.String(500),default="You can easily fill this.")
    mine=db.relationship('Posts',backref="user")
    password = db.Column( nullable=False)
    email = db.Column(db.String(50), nullable=False,unique=True)
    img_file = db.Column(db.String(500), nullable=True)
    id=db.Column(db.String(8),nullable=False)
    date = db.Column(db.String(12), nullable=True)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)
#class Reviews(db.Model):
    #sno = db.Column(db.Integer, primary_key=True)
    
    #post_id = db.Column(db.Integer, db.ForeignKey('posts.sno', ondelete='CASCADE'), nullable=False)
   
    #reviews = db.Column(db.String(500), nullable=False)
    #date = db.Column(db.String(12), nullable=False)


class Posts(db.Model,UserMixin):
    __searchable__ = ['title', 'content']
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(120), nullable=False)
   # post = db.relationship('Reviews', backref=db.backref('posts_rev'))
    user_id = db.Column(db.Integer, db.ForeignKey('comments.sno', ondelete='CASCADE'))
    date = db.Column(db.String(12), nullable=True)
    


@app.route("/")
def create():
    return render_template('index.html',params=params)

@app.route("/home",methods=['GET','POST'])

def home():
 
 if session['email']:
    index=1
    if(request.method=='POST'):
        slug =Posts.query.filter_by(slug=request.form.get('q')).first()
        id=Comments.query.filter_by(sno=request.form.get('q')).first()
       
        if slug:
           slug=request.form.get('q')
           return redirect('/individual_post/'+slug)
        else:
            id=request.form.get('q')
            return redirect('/user_account/'+id)  
    posts= Posts.query.all()

    return render_template('home.html', params=params,posts=posts,index=index)
 else:
  return redirect('/signin')
     
#@app.route("/comments", methods=['GET', 'POST'])
#def comments():
  #if request.method=='POST':
     # name=request.form.get('name')
      #email=request.form.get('email')
      #comment=request.form.get('comment')
      
 # return render_template('comment_mine.html')
@app.route("/new_account",methods=['GET','POST'])
def craccount():

 if request.method=='POST':
    user = Comments.query.filter_by(email=request.form.get('email')).first()
    if user:
      flash('Individual, this email is already registered !')
      return redirect('/new_account')
    else:
      username=request.form.get('username')
      email=request.form.get('email')
      password=request.form.get('password')
      c_pass=request.form.get('cpass')
      for i in range(1,10):
        id=random.randint(1000,10000)
        if not Comments.query.filter_by(id=id).first():
           uid=id
           break
        
           
      if c_pass==password:
          hash_pass=generate_password_hash(c_pass,"sha256")
          user = Comments(username=username, email=email,password=hash_pass,id=uid,date=datetime.now())
          db.session.add(user)
          db.session.commit()
          session['email']=email
          return redirect('/home')
      else:
          flash('Both password fields must match')
          return redirect('/new_account')
 return render_template("new_account.html",params=params)

@app.route("/signin",methods=['GET','POST'])
def dash_route():
         passed=None
         passw=None
         myemail=None
         
        #if form.validate_on_submit()
         if request.method=='POST':
           myemail=Comments.query.filter_by(email=request.form.get('email')).first()
           
           
           passw=request.form.get('password')
           if  myemail: 
              if check_password_hash(myemail.password,passw):
                session['email']=request.form.get('email')
                return redirect('/home')
                
              else:
                  flash('Wrong password .')
                  return redirect('/signin')
           else:
                  flash('Individual, Please enter the correct details !')
                  return redirect('/signin')
         
         return render_template("signin.html",params=params,myemail=myemail)
 
@app.route("/add_post" ,methods = ['GET', 'POST'])

def add_post():
    user_id_of_user=Comments.query.filter_by(email=session['email']).first()
    if request.method == 'POST':
            #user=current_user.sno
            box_title = request.form.get('title')
            #tline = request.form.get('tline')
            category = request.form.get('category')
            content = request.form.get('content')
            user = user_id_of_user.sno
           
           
          
            post = Posts(title=box_title, slug=category.replace(' ','-'),date=datetime.now(), content=content,user_id=user)
            
            db.session.add(post)
            db.session.commit()
            return redirect('/profile')
    return render_template('add_post.html', params=params)

@app.route("/individual_post/edit/<int:sno>" ,methods = ['GET', 'POST'])

def edit_post(sno):
    post=Posts.query.filter_by(sno=sno).first()
    if request.method == 'POST':
            #user=current_user.sno
            box_title = request.form.get('title')
            #tline = request.form.get('tline')
            category = request.form.get('category')
            content = request.form.get('content')
       
            post.title = box_title
            post.slug = category
            post.content = content
       
            db.session.commit()
            return redirect('/profile')
    return render_template('edit.html', params=params,post=post)


#@app.route('/individual_post/delete/<int:id>')  
#def delete(id):
    
      # Post_to_delete=Posts.query.filter_by(id=id).first()
       #db.session.delete(Post_to_delete)
       #db.session.commit()
       #return redirect('/profile',parmas=params)
   
@app.route('/individual_post/<string:post_slug>', methods=['GET'])
def post_route(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
        
    return render_template('individual_post.html', params=params, post=post)


@app.route("/profile",methods=['GET','POST'])
def profile():
    user=Comments.query.filter_by(email=session['email']).first()
    posts_of_user=Posts.query.filter_by(user_id=user.sno).all()
    #user_des=user.description
    if request.method == 'POST':
                
              
                user.description = request.form.get('descrip')
               
                db.session.commit()
                return redirect('/profile')
    return render_template("profile.html",params=params,user=user,posts_of_user=posts_of_user)


@app.route('/user_account/<string:id>', methods=['GET','POST'])

def Account_route(id):
    posts_of_user=None
    user = Comments.query.filter_by(id=id).first()
    user_id_for_posts=user.sno
    
    posts_of_user=Posts.query.filter_by(user_id= user_id_for_posts).all()
    if request.method == 'POST':
                
                
                user.description = request.form.get('descrip')
            
        
    return render_template('user_account.html', params=params,id=id,user=user,posts_of_user=posts_of_user)
@app.route('/searched', methods=['POSt'])
def search():
    index=1
    posts=None
    searched=request.form.get('q')
    user_search=request.form.get('q')
    if request.method=='POST':
       if Comments.query.filter_by(id=searched).first():
           return redirect('/user_account/'+searched)
       else:
        posts=Posts.query.filter(Posts.content.like('%'+ searched +'%'))
        posts=posts.order_by(Posts.title).all()
    
       #return redirect('/searched')
       return render_template('search.html',posts=posts,index=index,params=params,searched=searched)

# community
@app.route('/community')
def community():
    index=1
    users=Comments.query.filter_by().all()
    return render_template('community.html' ,parmas=params,users=users,index=index)
@app.route('/about_me')
def poste():
     
      return render_template('purpose.html')

@app.route('/logout',methods=['GET','POST'])
def logout():
    session.pop('email',None)
    return redirect('/signin')
if __name__=='__main__':
  app.run(debug=True)

