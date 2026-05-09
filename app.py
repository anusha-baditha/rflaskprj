from flask import Flask,jsonify,request,flash,redirect,url_for
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from mysql.connector import connection
from werkzeug.utils import secure_filename
from otp import genotp
import os
app=Flask(__name__)
app.secret_key='code'
CORS(app)
BASE_DIR=os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER=os.path.join(BASE_DIR,'static','uploads')
ALLOWED_EXTENSIONS={"png",'jpg','gif','webp','jpeg'}
MAX_CONTENT_LENGTH=6 *1024*1024 #6MB
os.makedirs(UPLOAD_FOLDER,exist_ok=True)
bcrypt=Bcrypt(app)
app.config['SESSION_TYPE']='filesystem'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH']=MAX_CONTENT_LENGTH

mydb=connection.MySQLConnection(
    host='localhost',
    user='root',
    password='admin',
    database='rflaskdb'
)

@app.route('/api/register',methods=['POST'])
def register():

    try:

        # get json data from frontend/postman
        data=request.get_json()

        username=data['username'].strip()
        email=data['email'].strip()
        password=data['password'].strip()
        address=data['address'].strip()

        # database cursor
        cursor=mydb.cursor(buffered=True)

        # check email exists or not
        cursor.execute(
            'select count(*) from userdata where email=%s',
            [email]
        )

        email_count=cursor.fetchone()[0]

        # duplicate email
        if email_count>0:

            return jsonify({
                'status':'failed',
                'message':'Email already already exists'
            }),400

        # password hashing
        hashed_password=bcrypt.generate_password_hash(
            password
        ).decode('utf-8')

        # insert user
        cursor.execute(
            '''
            insert into userdata(
                username,
                email,
                password,
                address
            )
            values(%s,%s,%s,%s)
            ''',
            [
                username,
                email,
                hashed_password,
                address
            ]
        )

        mydb.commit()

        return jsonify({
            'status':'success',
            'message':'User Registered Successfully'
        }),201

    except Exception as e:

        return jsonify({
            'status':'failed',
            'message':str(e)
        }),500
def allowed_file(filename:str)->bool:
    return "." in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/api/upload',methods=['POST'])
def upload():
    itemname=request.form['itemname']
    price=request.form['price']
    item_filedata=request.files['image']

    filename=item_filedata.filename
    if item_filedata and filename:
        if not allowed_file(filename):
            flash('File type is not Allowed.pls give png,jpg,jpng,webp,gif')
            return redirect(url_for('upload'))
        orig_secure=secure_filename(filename)
        ext=os.path.splitext(orig_secure)[1] #anusha.txt
        filename=genotp()+ext
        save_path=os.path.join(app.config['UPLOAD_FOLDER'],filename)
        try:
            item_filedata.save(save_path)
        except Exception  as e:
            flash('colud not store file data')
            return redirect(url_for('upload'))
    cursor=mydb.cursor(buffered=True)
    cursor.execute(
    '''
    insert into items(
        itemname,
        price,
        itemimage
    )
    values(%s,%s,%s)
    ''',
    [
        itemname,
        price,
        filename
    ]
)
    mydb.commit()
    return jsonify({
        'message':'File Uploaded'
    })
@app.route('/api/items')
def get_items():

    cursor=mydb.cursor(buffered=True)

    cursor.execute(
        '''
        select
        itemid,
        itemname,
        price,
        itemimage
        from items
        '''
    )

    data=cursor.fetchall()

    items=[]

    for item in data:

        image_url=f'http://127.0.0.1:5000/static/uploads/{item[3]}'

        items.append({

            'itemid':item[0],
            'itemname':item[1],
            'price':item[2],
            'image':image_url
        })

    return jsonify(items)
if __name__=='__main__':

    app.run(debug=True)