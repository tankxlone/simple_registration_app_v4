from flask import render_template, request, jsonify, current_app, send_file
from app.admin import bp
from app.models import User, Feedback, Notification
from app import db
from datetime import datetime
import csv
import io
from functools import wraps


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get user from JWT token in cookies
        user = None
        access_token = request.cookies.get('access_token_cookie')
        
        print(f"DEBUG: admin_required - access_token: {access_token[:20] if access_token else 'None'}...")
        
        if access_token:
            try:
                # Use Flask-JWT-Extended to verify token
                from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                
                print(f"DEBUG: admin_required - decoded user_id: {user_id}")
                
                if user_id:
                    user = User.query.get(user_id)
                    print(f"DEBUG: admin_required - user found: {user.name if user else 'None'}")
                    print(f"DEBUG: admin_required - user role: {user.role if user else 'None'}")
                    print(f"DEBUG: admin_required - is_admin: {user.is_admin() if user else 'None'}")
                    
                    if not user or not user.is_admin():
                        print(f"DEBUG: admin_required - Access denied: user={user is not None}, is_admin={user.is_admin() if user else False}")
                        return jsonify({'error': 'Admin access required'}), 403
                else:
                    print(f"DEBUG: admin_required - No user_id in token")
                    return jsonify({'error': 'Invalid token'}), 401
            except Exception as e:
                print(f"DEBUG: JWT verification error in admin_required: {e}")
                return jsonify({'error': 'Invalid token'}), 401
        else:
            print(f"DEBUG: admin_required - No access token found")
            return jsonify({'error': 'Authentication required'}), 401
        
        print(f"DEBUG: admin_required - Access granted for user: {user.name}")
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    try:
        # Get statistics
        total_users = User.query.count()
        total_feedback = Feedback.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        feedback_submitted = User.query.filter_by(has_submitted_feedback=True).count()
        pending_feedback = total_users - feedback_submitted
        feedback_rate = (feedback_submitted / total_users * 100) if total_users > 0 else 0
        
        # Get average rating
        avg_rating = db.session.query(db.func.avg(Feedback.rating)).scalar() or 0
        
        # Get sentiment distribution
        sentiment_stats = db.session.query(
            Feedback.sentiment_label,
            db.func.count(Feedback.id)
        ).group_by(Feedback.sentiment_label).all()
        
        # Get recent feedback
        recent_feedback = Feedback.query.order_by(Feedback.created_at.desc()).limit(10).all()
        
        feedback_data = []
        for feedback in recent_feedback:
            user = User.query.get(feedback.user_id)
            feedback_data.append({
                'id': feedback.id,
                'user_name': user.name if user else 'Unknown',
                'user_email': user.email if user else 'Unknown',
                'text': feedback.text[:100] + '...' if len(feedback.text) > 100 else feedback.text,
                'rating': feedback.rating,
                'sentiment': feedback.get_final_sentiment()[0],
                'created_at': feedback.created_at.strftime('%Y-%m-%d %H:%M'),
                'is_corrected': feedback.is_corrected
            })
        
        return render_template('admin/dashboard.html',
                             total_users=total_users,
                             total_feedback=total_feedback,
                             active_users=active_users,
                             feedback_submitted=feedback_submitted,
                             pending_feedback=pending_feedback,
                             feedback_rate=feedback_rate,
                             avg_rating=avg_rating,
                             sentiment_distribution=dict(sentiment_stats),
                             recent_feedback=feedback_data)
        
    except Exception as e:
        current_app.logger.error(f"Admin dashboard error: {e}")
        return jsonify({'error': 'Failed to load admin dashboard'}), 500

@bp.route('/users')
@admin_required
def manage_users_page():
    """Manage users page - HTML view"""
    return render_template('admin/users.html')

@bp.route('/api/users')
@admin_required
def manage_users():
    """Manage users page"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        
        # Build query with search
        query = User.query
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    User.name.ilike(search_filter),
                    User.email.ilike(search_filter)
                )
            )
        
        users_pagination = query.order_by(User.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        users_list = []
        for user in users_pagination.items:
            users_list.append({
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role,
                'is_active': user.is_active,
                'created_at': user.created_at.strftime('%Y-%m-%d'),
                'feedback_count': user.feedback.count()
            })
        
        return jsonify({
            'users': users_list,
            'total': users_pagination.total,
            'pages': users_pagination.pages,
            'current_page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        current_app.logger.error(f"User management error: {e}")
        return jsonify({'error': 'Failed to load users'}), 500

@bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    try:
        print(f"DEBUG: toggle_user_status called with user_id: {user_id}")
        user = User.query.get_or_404(user_id)
        print(f"DEBUG: Found user: {user.name}, current is_active: {user.is_active}")
        
        # Get current user ID using Flask-JWT-Extended
        current_user_id = get_jwt_identity()
        
        print(f"DEBUG: current_user_id from token: {current_user_id}")
        
        # Prevent admin from deactivating themselves
        if user.id == current_user_id:
            return jsonify({'error': 'Cannot deactivate your own account'}), 400
        
        print(f"DEBUG: Toggling user status from {user.is_active} to {not user.is_active}")
        user.is_active = not user.is_active
        db.session.commit()
        print(f"DEBUG: Status updated successfully")
        
        return jsonify({
            'message': f"User {'activated' if user.is_active else 'deactivated'} successfully",
            'is_active': user.is_active
        }), 200
        
    except Exception as e:
        print(f"DEBUG: Exception in toggle_user_status: {e}")
        db.session.rollback()
        current_app.logger.error(f"User status toggle error: {e}")
        return jsonify({'error': 'Failed to update user status'}), 500

@bp.route('/users/<int:user_id>/change-role', methods=['POST'])
@admin_required
def change_user_role(user_id):
    """Change user role"""
    try:
        user = User.query.get_or_404(user_id)
        new_role = request.json.get('role')
        
        if new_role not in ['user', 'admin']:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Get current user ID using Flask-JWT-Extended
        current_user_id = get_jwt_identity()
        

        
        # Prevent admin from changing their own role
        if user.id == current_user_id:
            return jsonify({'error': 'Cannot change your own role'}), 400
        
        user.role = new_role
        db.session.commit()
        
        return jsonify({
            'message': f"User role changed to {new_role}",
            'role': new_role
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"User role change error: {e}")
        return jsonify({'error': 'Failed to change user role'}), 500

@bp.route('/feedback')
@admin_required
def manage_feedback_page():
    """Manage feedback page - HTML view"""
    return render_template('admin/feedback.html')

@bp.route('/api/feedback')
@admin_required
def manage_feedback():
    """Manage feedback page"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sentiment_filter = request.args.get('sentiment', '').strip()
        search = request.args.get('search', '').strip()
        
        # Build query with filters
        query = Feedback.query
        
        # Apply sentiment filter
        if sentiment_filter:
            # Check both original and corrected sentiment
            query = query.filter(
                db.or_(
                    Feedback.sentiment_label == sentiment_filter,
                    Feedback.admin_corrected_label == sentiment_filter
                )
            )
        
        # Apply search filter
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    Feedback.text.ilike(search_filter),
                    User.name.ilike(search_filter),
                    User.email.ilike(search_filter)
                )
            ).join(User)  # Join with User table for name/email search
        
        feedback_pagination = query.order_by(Feedback.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        feedback_list = []
        for feedback in feedback_pagination.items:
            user = User.query.get(feedback.user_id)
            feedback_list.append({
                'id': feedback.id,
                'user_name': user.name if user else 'Unknown',
                'user_email': user.email if user else 'Unknown',
                'text': feedback.text,
                'rating': feedback.rating,
                'sentiment': feedback.get_final_sentiment()[0],
                'confidence': feedback.get_final_sentiment()[1],
                'created_at': feedback.created_at.strftime('%Y-%m-%d %H:%M'),
                'is_corrected': feedback.is_corrected,
                'admin_corrected_label': feedback.admin_corrected_label
            })
        
        return jsonify({
            'feedback': feedback_list,
            'total': feedback_pagination.total,
            'pages': feedback_pagination.pages,
            'current_page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        current_app.logger.error(f"Feedback management error: {e}")
        return jsonify({'error': 'Failed to load feedback'}), 500

@bp.route('/feedback/<int:feedback_id>/correct', methods=['POST'])
@admin_required
def correct_feedback_sentiment(feedback_id):
    """Correct feedback sentiment analysis"""
    try:
        feedback = Feedback.query.get_or_404(feedback_id)
        
        data = request.get_json()
        new_label = data.get('sentiment_label')
        new_score = data.get('sentiment_score')
        
        if new_label not in ['positive', 'negative', 'neutral']:
            return jsonify({'error': 'Invalid sentiment label'}), 400
        
        try:
            new_score = float(new_score)
            if not (0.0 <= new_score <= 1.0):
                return jsonify({'error': 'Sentiment score must be between 0 and 1'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid sentiment score'}), 400
        
        # Update feedback
        feedback.admin_corrected_label = new_label
        feedback.admin_corrected_score = new_score
        feedback.is_corrected = True
        feedback.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Sentiment corrected successfully',
            'feedback': {
                'id': feedback.id,
                'corrected_label': new_label,
                'corrected_score': new_score
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Sentiment correction error: {e}")
        return jsonify({'error': 'Failed to correct sentiment'}), 500

@bp.route('/export/feedback.csv')
@admin_required
def export_feedback_csv():
    """Export feedback data to CSV"""
    try:
        # Get all feedback
        feedback_list = Feedback.query.order_by(Feedback.created_at.desc()).all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'User Email', 'User Name', 'Text', 'Rating', 
            'Original Sentiment', 'Original Score', 'Corrected Sentiment', 
            'Corrected Score', 'Is Corrected', 'Created At'
        ])
        
        # Write data
        for feedback in feedback_list:
            user = User.query.get(feedback.user_id)
            writer.writerow([
                feedback.id,
                user.email if user else 'Unknown',
                user.name if user else 'Unknown',
                feedback.text,
                feedback.rating,
                feedback.sentiment_label,
                feedback.sentiment_score,
                feedback.admin_corrected_label or '',
                feedback.admin_corrected_score or '',
                feedback.is_corrected,
                feedback.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        # Prepare response
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'feedback_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
    except Exception as e:
        current_app.logger.error(f"CSV export error: {e}")
        return jsonify({'error': 'Failed to export CSV'}), 500

@bp.route('/notifications')
@admin_required
def manage_notifications_page():
    """Manage notifications page - HTML view"""
    return render_template('admin/notifications.html')

@bp.route('/api/notifications')
@admin_required
def manage_notifications():
    """Get notifications with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        query = Notification.query
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        notifications_pagination = query.order_by(Notification.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        notifications_list = []
        for notification in notifications_pagination.items:
            user = User.query.get(notification.user_id) if notification.user_id else None
            notifications_list.append({
                'id': notification.id,
                'event_type': notification.event_type,
                'title': notification.title,
                'message': notification.message,
                'user_name': user.name if user else 'System',
                'user_email': user.email if user else 'N/A',
                'event_data': notification.event_data,
                'is_read': notification.is_read,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M'),
                'created_at_relative': _get_relative_time(notification.created_at)
            })
        
        return jsonify({
            'notifications': notifications_list,
            'total': notifications_pagination.total,
            'pages': notifications_pagination.pages,
            'current_page': page,
            'per_page': per_page,
            'unread_count': Notification.get_unread_count()
        })
        
    except Exception as e:
        current_app.logger.error(f"Notification management error: {e}")
        return jsonify({'error': 'Failed to load notifications'}), 500

@bp.route('/api/notifications/<int:notification_id>/mark-read', methods=['POST'])
@admin_required
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        notification = Notification.query.get_or_404(notification_id)
        notification.is_read = True
        db.session.commit()
        
        return jsonify({
            'message': 'Notification marked as read',
            'unread_count': Notification.get_unread_count()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Mark notification read error: {e}")
        return jsonify({'error': 'Failed to mark notification as read'}), 500

@bp.route('/api/notifications/mark-all-read', methods=['POST'])
@admin_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        Notification.query.filter_by(is_read=False).update({'is_read': True})
        db.session.commit()
        
        return jsonify({
            'message': 'All notifications marked as read',
            'unread_count': 0
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Mark all notifications read error: {e}")
        return jsonify({'error': 'Failed to mark notifications as read'}), 500

@bp.route('/api/notifications/stats')
@admin_required
def notification_stats():
    """Get notification statistics"""
    try:
        total_notifications = Notification.query.count()
        unread_count = Notification.get_unread_count()
        
        # Get event type distribution
        event_stats = db.session.query(
            Notification.event_type,
            db.func.count(Notification.id)
        ).group_by(Notification.event_type).all()
        
        # Get recent activity (last 24 hours)
        from datetime import timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_count = Notification.query.filter(Notification.created_at >= yesterday).count()
        
        return jsonify({
            'total_notifications': total_notifications,
            'unread_count': unread_count,
            'recent_count': recent_count,
            'event_distribution': dict(event_stats)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Notification stats error: {e}")
        return jsonify({'error': 'Failed to load notification statistics'}), 500

def _get_relative_time(dt):
    """Get relative time string (e.g., '2 hours ago')"""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"
