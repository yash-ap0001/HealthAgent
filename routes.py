from datetime import datetime, timedelta
from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

from app import app, db
from models import User, HealthData, Insight

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    # Get health data statistics
    stats = {}
    
    # Steps data
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    
    steps_data = HealthData.query.filter(
        HealthData.user_id == current_user.id,
        HealthData.data_type == 'steps',
        HealthData.date >= thirty_days_ago
    ).order_by(HealthData.date).all()
    
    steps_avg = db.session.query(func.avg(HealthData.value)).filter(
        HealthData.user_id == current_user.id,
        HealthData.data_type == 'steps',
        HealthData.date >= thirty_days_ago
    ).scalar() or 0
    
    stats['steps'] = {
        'average': round(steps_avg),
        'data': [(str(data.date), data.value) for data in steps_data],
        'goal': 10000  # Default step goal
    }
    
    # Sleep data
    sleep_data = HealthData.query.filter(
        HealthData.user_id == current_user.id,
        HealthData.data_type == 'sleep',
        HealthData.date >= thirty_days_ago
    ).order_by(HealthData.date).all()
    
    sleep_avg = db.session.query(func.avg(HealthData.value)).filter(
        HealthData.user_id == current_user.id,
        HealthData.data_type == 'sleep',
        HealthData.date >= thirty_days_ago
    ).scalar() or 0
    
    stats['sleep'] = {
        'average': round(sleep_avg, 1),
        'data': [(str(data.date), data.value) for data in sleep_data],
        'goal': 8.0  # Default sleep goal in hours
    }
    
    # Heart rate data
    hr_data = HealthData.query.filter(
        HealthData.user_id == current_user.id,
        HealthData.data_type == 'heart_rate',
        HealthData.date >= thirty_days_ago
    ).order_by(HealthData.date).all()
    
    hr_avg = db.session.query(func.avg(HealthData.value)).filter(
        HealthData.user_id == current_user.id,
        HealthData.data_type == 'heart_rate',
        HealthData.date >= thirty_days_ago
    ).scalar() or 0
    
    stats['heart_rate'] = {
        'average': round(hr_avg),
        'data': [(str(data.date), data.value) for data in hr_data],
        'threshold': 70  # Default resting heart rate threshold
    }
    
    # Get recent insights
    insights = Insight.query.filter(
        Insight.user_id == current_user.id
    ).order_by(Insight.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                          user=current_user, 
                          stats=stats, 
                          insights=insights)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return render_template('register.html')
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# API routes
@app.route('/api/health-data', methods=['GET', 'POST'])
def api_health_data():
    if request.method == 'GET':
        # Get health data based on type and date range
        user_id = request.args.get('user_id')
        data_type = request.args.get('data_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = HealthData.query
        
        if user_id:
            query = query.filter(HealthData.user_id == user_id)
        
        if data_type:
            query = query.filter(HealthData.data_type == data_type)
        
        if start_date:
            query = query.filter(HealthData.date >= start_date)
        
        if end_date:
            query = query.filter(HealthData.date <= end_date)
        
        health_data = query.order_by(HealthData.date).all()
        
        return jsonify([{
            'id': data.id,
            'user_id': data.user_id,
            'data_type': data.data_type,
            'date': str(data.date),
            'value': data.value,
            'unit': data.unit,
            'metadata': data.metadata,
            'source': data.source,
            'created_at': str(data.created_at),
            'updated_at': str(data.updated_at)
        } for data in health_data])
    
    elif request.method == 'POST':
        # Add new health data
        data = request.json
        
        new_data = HealthData(
            user_id=data.get('user_id'),
            data_type=data.get('data_type'),
            date=datetime.strptime(data.get('date'), '%Y-%m-%d').date(),
            value=data.get('value'),
            unit=data.get('unit'),
            metadata=data.get('metadata'),
            source=data.get('source')
        )
        
        db.session.add(new_data)
        db.session.commit()
        
        return jsonify({
            'id': new_data.id,
            'message': 'Health data added successfully'
        }), 201

@app.route('/api/insights', methods=['GET', 'POST'])
def api_insights():
    if request.method == 'GET':
        # Get insights based on category
        user_id = request.args.get('user_id')
        category = request.args.get('category')
        
        query = Insight.query
        
        if user_id:
            query = query.filter(Insight.user_id == user_id)
        
        if category:
            query = query.filter(Insight.category == category)
        
        insights = query.order_by(Insight.created_at.desc()).all()
        
        return jsonify([{
            'id': insight.id,
            'user_id': insight.user_id,
            'category': insight.category,
            'title': insight.title,
            'description': insight.description,
            'severity': insight.severity,
            'is_actionable': insight.is_actionable,
            'recommendation': insight.recommendation,
            'created_at': str(insight.created_at),
            'updated_at': str(insight.updated_at)
        } for insight in insights])
    
    elif request.method == 'POST':
        # Create new insight
        data = request.json
        
        new_insight = Insight(
            user_id=data.get('user_id'),
            category=data.get('category'),
            title=data.get('title'),
            description=data.get('description'),
            severity=data.get('severity'),
            is_actionable=data.get('is_actionable', True),
            recommendation=data.get('recommendation')
        )
        
        db.session.add(new_insight)
        db.session.commit()
        
        return jsonify({
            'id': new_insight.id,
            'message': 'Insight created successfully'
        }), 201

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500