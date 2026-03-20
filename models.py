from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Track(db.Model):
    __tablename__ = 'tracks'
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    transportType = db.Column(db.String(20), nullable=False)
    supplier = db.Column(db.String(20), nullable=False, default='Angela')
    currentStatus = db.Column(db.String(100), nullable=False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)

    points = db.relationship('Point', backref='track', cascade='all, delete-orphan')

class Point(db.Model):
    __tablename__ = 'points'
    id = db.Column(db.Integer, primary_key=True)
    track_id = db.Column(db.String(50), db.ForeignKey('tracks.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20), default='')
    comment = db.Column(db.Text, default='')
    order = db.Column(db.Integer, nullable=False)

    files = db.relationship('File', backref='point', cascade='all, delete-orphan')

class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.String(50), primary_key=True)
    point_id = db.Column(db.Integer, db.ForeignKey('points.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(500), nullable=False)

db.Index('idx_point_track_id', Point.track_id)
db.Index('idx_file_point_id', File.point_id)