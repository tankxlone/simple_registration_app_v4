from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import bp
from app.models import User, Feedback, Notification
from app.services.sentiment_service import get_sentiment_service
from app.services.notification_service import get_notification_count_for_role, get_notifications_for_role, mark_notification_read
from app import db, limiter
from sqlalchemy import text
from datetime import datetime

@bp.route('/feedback/preview', methods=['POST'])
@limiter.limit("10 per minute")
def feedback_preview():
    """Real-time sentiment preview without storing data"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Validate text length
        if len(text) < 10 or len(text) > 500:
            return jsonify({'error': 'Text must be between 10 and 500 characters'}), 400
        
        # Get sentiment service
        sentiment_service = get_sentiment_service()
        
        # Check for banned words
        if sentiment_service._contains_banned_words(text):
            return jsonify({
                'sentiment': 'negative',
                'confidence': 1.0,
                'banned_words_detected': True,
                'message': 'Text contains inappropriate content'
            }), 200
        
        # Analyze sentiment
        sentiment_label, confidence_score, analysis = sentiment_service.analyze_sentiment(text)
        
        return jsonify({
            'sentiment': sentiment_label,
            'confidence': confidence_score,
            'banned_words_detected': False,
            'analysis': analysis
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Sentiment preview error: {e}")
        return jsonify({'error': 'Failed to analyze sentiment'}), 500

@bp.route('/feedback/stats', methods=['GET'])
@jwt_required()
def feedback_stats():
    """Get feedback statistics for current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's feedback statistics
        total_feedback = Feedback.query.filter_by(user_id=current_user_id).count()
        
        # Sentiment distribution
        sentiment_counts = db.session.query(
            Feedback.sentiment_label,
            db.func.count(Feedback.id)
        ).filter_by(user_id=current_user_id).group_by(Feedback.sentiment_label).all()
        
        sentiment_stats = {}
        for label, count in sentiment_counts:
            sentiment_stats[label] = count
        
        # Rating distribution
        rating_counts = db.session.query(
            Feedback.rating,
            db.func.count(Feedback.id)
        ).filter_by(user_id=current_user_id).group_by(Feedback.rating).all()
        
        rating_stats = {}
        for rating, count in rating_counts:
            rating_stats[str(rating)] = count
        
        # Average rating
        avg_rating = db.session.query(db.func.avg(Feedback.rating))\
            .filter_by(user_id=current_user_id).scalar() or 0
        
        return jsonify({
            'total_feedback': total_feedback,
            'sentiment_distribution': sentiment_stats,
            'rating_distribution': rating_stats,
            'average_rating': round(float(avg_rating), 2)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Feedback stats error: {e}")
        return jsonify({'error': 'Failed to get feedback statistics'}), 500

@bp.route('/admin/stats', methods=['GET'])
@jwt_required()
def admin_stats():
    """Get admin statistics (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        # Overall statistics
        total_users = User.query.count()
        total_feedback = Feedback.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        
        # Sentiment distribution across all feedback
        sentiment_counts = db.session.query(
            Feedback.sentiment_label,
            db.func.count(Feedback.id)
        ).group_by(Feedback.sentiment_label).all()
        
        sentiment_stats = {}
        for label, count in sentiment_counts:
            sentiment_stats[label] = count
        
        # Rating distribution
        rating_counts = db.session.query(
            Feedback.rating,
            db.func.count(Feedback.id)
        ).group_by(Feedback.rating).all()
        
        rating_stats = {}
        for rating, count in rating_counts:
            rating_stats[str(rating)] = count
        
        # Average rating
        avg_rating = db.session.query(db.func.avg(Feedback.rating)).scalar() or 0
        
        # Recent activity (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        recent_users = User.query.filter(User.created_at >= week_ago).count()
        recent_feedback = Feedback.query.filter(Feedback.created_at >= week_ago).count()
        
        return jsonify({
            'total_users': total_users,
            'total_feedback': total_feedback,
            'active_users': active_users,
            'sentiment_distribution': sentiment_stats,
            'rating_distribution': rating_stats,
            'average_rating': round(float(avg_rating), 2),
            'recent_users': recent_users,
            'recent_feedback': recent_feedback
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Admin stats error: {e}")
        return jsonify({'error': 'Failed to get admin statistics'}), 500

@bp.route('/notifications/count', methods=['GET'])
@jwt_required()
def get_notification_count():
    """Get unread notification count for current user's role"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get notification count for user's role
        unread_count = get_notification_count_for_role(user.role)
        
        return jsonify({
            'is_admin': user.is_admin(),
            'unread_count': unread_count
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting notification count: {e}")
        return jsonify({'error': 'Failed to get notification count'}), 500

@bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get recent notifications for current user's role"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get limit from query params
        limit = request.args.get('limit', 50, type=int)
        if limit > 100:  # Cap at 100
            limit = 100
        
        # Get notifications for user's role
        notifications = get_notifications_for_role(user.role, limit)
        
        # Format notifications
        notification_list = []
        for notification in notifications:
            notification_list.append({
                'id': notification.id,
                'message': notification.message,
                'type': notification.type,
                'timestamp': notification.timestamp.isoformat(),
                'read': notification.read,
                'user_id': notification.user_id,
                'event_data': notification.event_data
            })
        
        return jsonify({
            'notifications': notification_list,
            'total': len(notification_list)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting notifications: {e}")
        return jsonify({'error': 'Failed to get notifications'}), 500

@bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read_api(notification_id):
    """Mark a notification as read"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Mark notification as read
        success = mark_notification_read(notification_id)
        
        if success:
            return jsonify({'message': 'Notification marked as read'}), 200
        else:
            return jsonify({'error': 'Notification not found'}), 404
        
    except Exception as e:
        current_app.logger.error(f"Error marking notification as read: {e}")
        return jsonify({'error': 'Failed to mark notification as read'}), 500

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Basic database connectivity check
        db.session.execute(text('SELECT 1'))
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'disconnected',
            'error': str(e)
        }), 500
