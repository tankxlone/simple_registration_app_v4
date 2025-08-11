from flask import render_template, request, jsonify, current_app
from app.profile import bp
from app.models import User
from app.forms import ProfileUpdateForm
from app import db
import os
from werkzeug.utils import secure_filename
from PIL import Image
import uuid
import jwt

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_avatar(file):
    """Save avatar file with proper naming and validation"""
    if file and allowed_file(file.filename):
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Ensure upload directory exists
        upload_path = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_path, exist_ok=True)
        
        filepath = os.path.join(upload_path, filename)
        
        # Open and validate image
        try:
            with Image.open(file.stream) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if too large (max 500x500)
                if img.width > 500 or img.height > 500:
                    img.thumbnail((500, 500), Image.Resampling.LANCZOS)
                
                # Save optimized image
                img.save(filepath, 'JPEG', quality=85, optimize=True)
                
                return filename
        except Exception as e:
            current_app.logger.error(f"Error processing avatar: {e}")
            return None
    
    return None

@bp.route('/', methods=['GET'])
def profile():
    """User profile page"""
    try:
        # Get user from JWT token in cookies
        user = None
        access_token = request.cookies.get('access_token_cookie')
        
        if access_token:
            try:
                # Decode the JWT token manually
                from config import Config
                decoded = jwt.decode(access_token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
                user_id = decoded.get('sub')
                
                if user_id:
                    user = User.query.get(user_id)
                    if not user:
                        return jsonify({'error': 'User not found'}), 404
                else:
                    return jsonify({'error': 'Invalid token'}), 401
            except Exception as e:
                print(f"DEBUG: JWT decode error in profile: {e}")
                return jsonify({'error': 'Invalid token'}), 401
        else:
            return jsonify({'error': 'Authentication required'}), 401
        
        return render_template('profile/profile.html', user=user)
        
    except Exception as e:
        print(f"DEBUG: Profile error: {e}")
        return jsonify({'error': 'Failed to load profile'}), 500

@bp.route('/update', methods=['POST'])
def update_profile():
    """Update user profile information"""
    try:
        # Get user from JWT token in cookies
        user = None
        access_token = request.cookies.get('access_token_cookie')
        
        if access_token:
            try:
                # Decode the JWT token manually
                from config import Config
                decoded = jwt.decode(access_token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
                user_id = decoded.get('sub')
                
                if user_id:
                    user = User.query.get(user_id)
                    if not user:
                        return jsonify({'error': 'User not found'}), 404
                else:
                    return jsonify({'error': 'Invalid token'}), 401
            except Exception as e:
                print(f"DEBUG: JWT decode error in update_profile: {e}")
                return jsonify({'error': 'Invalid token'}), 401
        else:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Validate name
        name = request.form.get('name', '').strip()
        is_valid, name_msg = User.validate_name(name)
        if not is_valid:
            return jsonify({'error': name_msg}), 400
        
        # Handle avatar upload
        avatar_filename = None
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file.filename:  # Only process if file was selected
                avatar_filename = save_avatar(file)
                if not avatar_filename:
                    return jsonify({'error': 'Invalid avatar file'}), 400
        
        # Update user
        user.name = name
        if avatar_filename:
            # Remove old avatar if exists
            if user.avatar_filename:
                old_avatar_path = os.path.join(current_app.config['UPLOAD_FOLDER'], user.avatar_filename)
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)
            user.avatar_filename = avatar_filename
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'name': user.name,
                'avatar_filename': user.avatar_filename
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Profile update error: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500

@bp.route('/avatar/<filename>')
def get_avatar(filename):
    """Serve avatar files"""
    try:
        from flask import send_from_directory
        # Get the absolute path to the upload folder
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
        print(f"DEBUG: Serving avatar {filename} from folder {upload_folder}")
        print(f"DEBUG: Full path: {os.path.join(upload_folder, filename)}")
        print(f"DEBUG: File exists: {os.path.exists(os.path.join(upload_folder, filename))}")
        
        if not os.path.exists(os.path.join(upload_folder, filename)):
            print(f"DEBUG: File not found: {filename}")
            return jsonify({'error': 'Avatar file not found'}), 404
            
        return send_from_directory(upload_folder, filename)
    except Exception as e:
        print(f"DEBUG: Avatar serve error: {e}")
        current_app.logger.error(f"Avatar serve error: {e}")
        return jsonify({'error': 'Avatar not found'}), 404
