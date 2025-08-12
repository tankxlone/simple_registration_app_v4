from flask import render_template, request, jsonify, current_app, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.feedback import bp
from app.models import User, Feedback
from app.forms import FeedbackForm
from app.services.sentiment_service import get_sentiment_service
from app import db
from datetime import datetime


@bp.route('/welcome', methods=['GET', 'POST'])
@jwt_required()
def welcome_feedback():
    """Welcome feedback form for new users (one-time only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return redirect(url_for('auth.login'))
        
        # Check if user has already submitted feedback
        if user.has_submitted_feedback:
            return redirect(url_for('main.dashboard'))
        
        if request.method == 'POST':
            data = request.get_json()
            text = data.get('text', '').strip()
            rating = data.get('rating', 5)
            
            # Validate input
            if not text or len(text) < 10:
                return jsonify({'error': 'Please provide feedback text (at least 10 characters)'}), 400
            
            # Convert rating to int and validate
            try:
                rating_int = int(rating)
                if not (1 <= rating_int <= 5):
                    return jsonify({'error': 'Rating must be between 1 and 5'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'Rating must be a valid number between 1 and 5'}), 400
            
            # Get sentiment analysis
            sentiment_service = get_sentiment_service()
            sentiment_label, sentiment_score, sentiment_analysis = sentiment_service.analyze_sentiment(text)
            
            # Create feedback
            feedback = Feedback(
                user_id=user.id,
                text=text,
                rating=rating_int,
                sentiment_label=sentiment_label,
                sentiment_score=sentiment_score
            )
            
            # Mark user as having submitted feedback
            user.has_submitted_feedback = True
            
            # Create notification for feedback submission
            from app.models import Notification
            Notification.create_notification(
                event_type='feedback_submission',
                title='New Feedback Submission',
                message=f'User {user.name} has submitted new feedback with {rating_int}/5 rating.',
                user_id=user.id,
                event_data={'rating': rating_int, 'sentiment': sentiment_label, 'sentiment_score': sentiment_score}
            )
            
            db.session.add(feedback)
            db.session.commit()
            
            return jsonify({
                'message': 'Thank you for your feedback! Welcome to our platform!',
                'redirect': '/dashboard'
            }), 201
        
        return render_template('feedback/welcome.html', user=user)
        
    except Exception as e:
        print(f"DEBUG: Welcome feedback error: {e}")
        return jsonify({'error': 'An error occurred. Please try again.'}), 500

@bp.route('/submit', methods=['GET', 'POST'])
@jwt_required()
def submit_feedback():
    """Submit feedback form"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user has already submitted feedback
        if user.has_submitted_feedback:
            return jsonify({'error': 'You have already submitted feedback. This is a one-time form.'}), 403
        
        if request.method == 'POST':
            data = request.get_json()
            
            # Validate input
            text = data.get('text', '').strip()
            rating = data.get('rating')
            
            errors = {}
            
            # Text validation
            is_valid, text_msg = Feedback.validate_text(text)
            if not is_valid:
                errors['text'] = text_msg
            
            # Rating validation
            is_valid, rating_msg = Feedback.validate_rating(rating)
            if not is_valid:
                errors['rating'] = rating_msg
            
            if errors:
                return jsonify({'errors': errors}), 400
            
            # Check for banned words
            sentiment_service = get_sentiment_service()
            if sentiment_service._contains_banned_words(text):
                return jsonify({'error': 'Feedback contains inappropriate content'}), 400
            
            # Analyze sentiment
            sentiment_label, sentiment_score, analysis = sentiment_service.analyze_sentiment(text)
            
            # Create feedback
            feedback = Feedback(
                user_id=current_user_id,
                text=text,
                rating=int(rating),
                sentiment_label=sentiment_label,
                sentiment_score=sentiment_score
            )
            
            # Mark user as having submitted feedback
            user.has_submitted_feedback = True
            
            # Create notification for feedback submission
            from app.models import Notification
            Notification.create_notification(
                event_type='feedback_submission',
                title='New Feedback Submission',
                message=f'User {user.name} has submitted new feedback with {rating}/5 rating.',
                user_id=current_user_id,
                event_data={'rating': rating, 'sentiment': sentiment_label, 'sentiment_score': sentiment_score}
            )
            
            db.session.add(feedback)
            db.session.commit()
            
            return jsonify({
                'message': 'Feedback submitted successfully',
                'feedback': {
                    'id': feedback.id,
                    'sentiment': sentiment_label,
                    'confidence': sentiment_score
                }
            }), 201
        
        return render_template('feedback/submit.html', user=user)
        
    except Exception as e:
        current_app.logger.error(f"Feedback submission error: {e}")
        return jsonify({'error': 'Failed to submit feedback'}), 500

@bp.route('/my-feedback')
@jwt_required()
def my_feedback():
    """View user's feedback history"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's feedback with pagination
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        feedback_pagination = Feedback.query.filter_by(user_id=current_user_id)\
            .order_by(Feedback.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        feedback_list = []
        for feedback in feedback_pagination.items:
            try:
                sentiment_label, sentiment_score = feedback.get_final_sentiment()
                # Handle None values safely
                sentiment_label = sentiment_label or 'neutral'
                sentiment_score = sentiment_score or 0.0
                
                feedback_list.append({
                    'id': feedback.id,
                    'text': feedback.text,
                    'rating': feedback.rating,
                    'sentiment': sentiment_label,
                    'confidence': sentiment_score,
                    'created_at': feedback.created_at.strftime('%Y-%m-%d %H:%M'),
                    'is_corrected': feedback.is_corrected
                })
            except Exception as e:
                print(f"DEBUG: Error processing feedback {feedback.id}: {e}")
                continue
        
        return render_template('feedback/my_feedback.html',
                             user=user,
                             feedback_list=feedback_list,
                             pagination=feedback_pagination)
        
    except Exception as e:
        current_app.logger.error(f"Feedback history error: {e}")
        return jsonify({'error': 'Failed to load feedback history'}), 500

@bp.route('/feedback/<int:feedback_id>')
@jwt_required()
def view_feedback(feedback_id):
    """View specific feedback detail"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        feedback = Feedback.query.get_or_404(feedback_id)
        
        # Check if user owns this feedback or is admin
        if feedback.user_id != current_user_id and not user.is_admin():
            return jsonify({'error': 'Access denied'}), 403
        
        feedback_data = {
            'id': feedback.id,
            'text': feedback.text,
            'rating': feedback.rating,
            'sentiment': feedback.get_final_sentiment()[0],
            'confidence': feedback.get_final_sentiment()[1],
            'created_at': feedback.created_at.strftime('%Y-%m-%d %H:%M'),
            'is_corrected': feedback.is_corrected,
            'admin_corrected_label': feedback.admin_corrected_label,
            'admin_corrected_score': feedback.admin_corrected_score
        }
        
        return render_template('feedback/view_feedback.html',
                             user=user,
                             feedback=feedback_data)
        
    except Exception as e:
        current_app.logger.error(f"Feedback view error: {e}")
        return jsonify({'error': 'Failed to load feedback'}), 500
