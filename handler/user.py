import hashlib, time, random
import pymongo
from flask import Blueprint, request, session, jsonify
import smtplib
from email.mime.text import MIMEText
from email.header import Header


bp = Blueprint('user', __name__)
client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
db = client['bilidb']
coll = db['user']

def md5(require, salt):
    md = hashlib.md5()
    md.update(str(require).encode('utf-8'))
    md.update(str(salt).encode('utf-8'))
    return md.hexdigest()



@bp.route('/api/user/signin', methods=['POST'])
def signin():
    request_json = request.get_json()
    if coll.find_one({'email':request_json['email']}) is not None:
        if md5(str(request_json['password']), coll.find_one({'email':request_json['email']})['time']) == coll.find_one({'email':request_json['email']})['password']:
            session['user'] = {
                'id':coll.find_one({'email':request_json['email']})['id'],
                'email':coll.find_one({'email':request_json['email']})['email'],
                'name':coll.find_one({'email':request_json['email']})['name'],
                'status': coll.find_one({'email':request_json['email']})['status'],
                'signin': True,
                }
            return jsonify({'state': 'succeed'})
        else:
            return jsonify({'state': 'password_error'})
    else:
        return jsonify({'state': 'user_none'})
    

@bp.route('/api/user/signup', methods=['POST'])
def signup():
    request_json = request.get_json()
    if str(request_json['auth']) == db['user_auth'].find_one({'email': request_json['email']})['auth']:
        if time.time() - db['user_auth'].find_one({'email': request_json['email']})['time'] <= 300:
            if coll.find_one({'email': request_json['email']}) is None:
                time_then = time.time()
                if coll.find_one() is None:
                    user_id = 1
                else:
                    user_id = coll.find_one(sort=[( '_id', -1)])['id']+1
                document = {
                    'id': user_id,
                    'email': request_json['email'],
                    'name': request_json['name'],
                    'password': md5(str(request_json['password']), time_then),
                    'status': 1,
                    'count': {
                        'visit_all': 0,
                        'visit_index': 0,
                    },
                    'time': time_then,
                    }
                coll.insert_one(document)
                return jsonify({'state': 'succeed'})
            else:
                return jsonify({'state': 'repetition'})
        else:
            return jsonify({'state': 'auth_past'})
    else:
        return jsonify({'state': 'auth_error'})


@bp.route('/api/user/signup/auth', methods=['POST'])
def signup_auth():
    auth = ''
    request_json = request.get_json()
    for i in range(6):
        auth += str(random.randint(0, 9))
    smtp = smtplib.SMTP_SSL('smtp.exmail.qq.com', 465)
    smtp.connect('smtp.exmail.qq.com', port=465)
    smtp.login(user='renzhenmao@bilidb.com', password='R/enzhenmao123')
    mail_msg = f'''
    <div style="text-align: center;">
        <span style='text-align: center; font-size:2px color: #666;'>BiliDataBase BiliDB 2023 ©All Rights Reserves</span>
    </div>
    <div style="border:3px solid #25ACE3; border-radius: 7px; margin: 10px; padding: 20px;">
    <div style="text-align: center;">
        <span style="font-size: 24px; font-weight: bold; background: -webkit-linear-gradient(315deg,#00AEEC 20%, #FF6060); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">新的数据客，你好！</span>
    </div>
    <br><br>
    <span style="color: #555;">您正在注册<a href="www.bilidb.com" style="color: #555;">BILIDB</a>新账号，验证代码是：<span style="font-weight: bold; color: #666">{auth}</span>，有效期为<span style="font-weight: bold; color: #666">5分钟</span>，请妥善保管。</span>
    <br>
    <span style="color: #555;">如果这不是您的行为，可直接删除这封邮件。</span>
    <br><br>
    <span style='font-size:5px color: #666;'>谢谢！</span>
    <br>
    <span style='font-size:5px color: #666;'>@认真猫</span>
    </div>
    
    '''
    message = MIMEText(mail_msg, 'html', 'utf-8')
    message['From'] = Header('renzhenmao@bilidb.com', 'utf-8')  # 发件人的昵称
    message['To'] = Header(request_json['email'], 'utf-8')  # 收件人的昵称
    message['Subject'] = Header(f'BiliDB - 点击查看验证码', 'utf-8')  # 定义主题内容
    smtp.sendmail(from_addr='renzhenmao@bilidb.com', to_addrs=request_json['email'],msg=message.as_string())
    document = {
        'email': request_json['email'],
        'auth': auth,
        'time': time.time(),
        }
    if db['user_auth'].find_one({'email':request_json['email']}) is None:
        db['user_auth'].insert_one(document)
    else:
        db['user_auth'].delete_one({'email':request_json['email']})
        db['user_auth'].insert_one(document)
    return ''


@bp.route('/api/user/session/get', methods=['GET'])
def getSession():
    if 'user' in session:
        return jsonify(session['user'])
    else:
        return jsonify({'signin': False})
    

@bp.route('/api/user/signout', methods=['POST','GET'])
def signout():
    session.clear()
    return session
