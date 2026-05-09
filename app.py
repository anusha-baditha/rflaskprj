from flask import Flask,jsonify,request
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from mysql.connector import connection

app=Flask(__name__)

CORS(app)

bcrypt=Bcrypt(app)

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


if __name__=='__main__':

    app.run(debug=True)