import functools
from flask import (
    Blueprint, request, jsonify, session, g
)
from werkzeug.security import check_password_hash, generate_password_hash
from api.services.db_service import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        data = request.get_json()

        name = data.get('name')
        password = data.get('password')
        personal_email = data.get('personal_email')
        contact_email = data.get('contact_email')
        is_admin = data.get('is_admin')
        
        if name is None or password is None or personal_email is None or contact_email is None or is_admin is None:
            return jsonify({"error": "Missing required information."}), 400

        db = get_db()
        cursor = db.cursor(dictionary=True)

        try: 
            cursor.execute(
                'INSERT INTO user (name, password, personal_email, contact_email, is_admin) VALUES (%s, %s, %s, %s, %s)',
                (name, generate_password_hash(password), personal_email, contact_email, is_admin)
            )
            db.commit()
            cursor.execute('SELECT id, name, personal_email, contact_email, is_admin FROM user WHERE name = %s', (name,))
            new_user = cursor.fetchone()

            return jsonify({"user": new_user}), 201

        except Exception as e:
            if "Duplicate entry" in str(e):
                return jsonify({"error": "Account already exists."}), 400
            
            return jsonify({"error": "An unexpected error occurred."}), 400
        
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        password = data.get('password')

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            'SELECT * FROM user WHERE name = %s', (name,)
        )
        user = cursor.fetchone()

        if user is None:
            return jsonify({"error": "Invalid name."}), 400
        
        if not check_password_hash(user['password'], password):
            return jsonify({"error": "Invalid password."}), 400
        
        session.clear()
        session['user_id'] = user['id']
        return jsonify({"user": user}), 200

@bp.route('/logout', methods=('GET', 'POST'))
def logout():
    session.clear()
    return jsonify({"message": "Successfully logged out."}), 200

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            'SELECT * FROM user WHERE id = %s', (user_id,)
        )
        g.user = cursor.fetchone()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return jsonify({"error": "Unauthorized"}), 401
        return view(**kwargs)

    return wrapped_view
