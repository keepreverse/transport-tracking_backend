import os
import shutil
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from models import db, Track, Point, File
from utils import generate_uuid, delete_file_from_disk

tracks_bp = Blueprint('tracks', __name__)

@tracks_bp.route('/', methods=['GET'])
def get_tracks():
    transport_filter = request.args.get('transport', 'all')
    supplier_filter = request.args.get('supplier', 'all')
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'newest')

    query = Track.query

    if transport_filter != 'all':
        query = query.filter_by(transportType=transport_filter)
    if supplier_filter != 'all':
        query = query.filter_by(supplier=supplier_filter)
    if search:
        query = query.filter(Track.name.ilike(f'%{search}%'))

    if sort == 'newest':
        query = query.order_by(Track.createdAt.desc())
    elif sort == 'oldest':
        query = query.order_by(Track.createdAt.asc())
    elif sort == 'name_asc':
        query = query.order_by(Track.name.asc())
    elif sort == 'name_desc':
        query = query.order_by(Track.name.desc())

    tracks = query.all()
    result = []
    for t in tracks:
        points = [{
            'id': p.id,
            'name': p.name,
            'icon': p.icon,
            'date': p.date,
            'comment': p.comment,
            'files': [{'id': f.id, 'name': f.name, 'size': f.size, 'type': f.type} for f in p.files]
        } for p in sorted(t.points, key=lambda p: p.order)]
        result.append({
            'id': t.id,
            'name': t.name,
            'transportType': t.transportType,
            'supplier': t.supplier,
            'currentStatus': t.currentStatus,
            'intervalProgress': t.intervalProgress,
            'points': points
        })
    return jsonify(result)

@tracks_bp.route('/', methods=['POST'])
def create_track():
    data = request.json
    track_id = str(int(datetime.utcnow().timestamp() * 1000))
    new_track = Track(
        id=track_id,
        name=data['name'],
        transportType=data['transportType'],
        supplier=data.get('supplier', 'Angela'),
        currentStatus=data.get('currentStatus', 'Отгрузка'),
        intervalProgress=data.get('intervalProgress', 50)
    )
    db.session.add(new_track)
    db.session.flush()

    points_data = data.get('points', [])
    for point_data in points_data:
        point = Point(
            track_id=new_track.id,
            name=point_data['name'],
            icon=point_data['icon'],
            date=point_data.get('date', ''),
            comment=point_data.get('comment', ''),
            order=point_data['order']
        )
        db.session.add(point)

    db.session.commit()
    return jsonify({'id': track_id}), 201

@tracks_bp.route('/<track_id>', methods=['GET'])
def get_track(track_id):
    track = Track.query.get_or_404(track_id)
    points = [{
        'id': p.id,
        'name': p.name,
        'icon': p.icon,
        'date': p.date,
        'comment': p.comment,
        'files': [{'id': f.id, 'name': f.name, 'size': f.size, 'type': f.type} for f in p.files]
    } for p in sorted(track.points, key=lambda p: p.order)]
    return jsonify({
        'id': track.id,
        'name': track.name,
        'transportType': track.transportType,
        'supplier': track.supplier,
        'currentStatus': track.currentStatus,
        'intervalProgress': track.intervalProgress,
        'points': points
    })

@tracks_bp.route('/<track_id>', methods=['PUT'])
def update_track(track_id):
    track = Track.query.get_or_404(track_id)
    data = request.json

    if 'name' in data:
        track.name = data['name']
    if 'currentStatus' in data:
        track.currentStatus = data['currentStatus']
    if 'intervalProgress' in data:
        track.intervalProgress = data['intervalProgress']

    if 'points' in data:
        # Ожидается массив объектов с полями order, date, comment
        for point_update in data['points']:
            order = point_update.get('order')
            point = Point.query.filter_by(track_id=track.id, order=order).first()
            if point:
                if 'date' in point_update:
                    point.date = point_update['date']
                if 'comment' in point_update:
                    point.comment = point_update['comment']

    db.session.commit()
    return jsonify({'status': 'ok'})

@tracks_bp.route('/<track_id>', methods=['DELETE'])
def delete_track(track_id):
    track = Track.query.get_or_404(track_id)
    for point in track.points:
        for file in point.files:
            delete_file_from_disk(file.path)
    db.session.delete(track)
    db.session.commit()
    return jsonify({'status': 'ok'})

@tracks_bp.route('/<track_id>/copy', methods=['POST'])
def copy_track(track_id):
    data = request.json
    with_files = data.get('withFiles', False)
    original = Track.query.get_or_404(track_id)

    new_id = str(int(datetime.utcnow().timestamp() * 1000))
    new_track = Track(
        id=new_id,
        name=f"{original.name} (копия)",
        transportType=original.transportType,
        supplier=original.supplier,
        currentStatus=original.currentStatus,
        intervalProgress=original.intervalProgress
    )
    db.session.add(new_track)
    db.session.flush()

    for point in sorted(original.points, key=lambda p: p.order):
        new_point = Point(
            track_id=new_track.id,
            name=point.name,
            icon=point.icon,
            date=point.date,
            comment=point.comment,
            order=point.order
        )
        db.session.add(new_point)
        db.session.flush()

        if with_files:
            for f in point.files:
                old_path = f.path
                ext = os.path.splitext(f.name)[1]
                new_filename = generate_uuid() + ext
                new_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
                shutil.copy2(old_path, new_path)
                new_file = File(
                    id=generate_uuid(),
                    point_id=new_point.id,
                    name=f.name,
                    size=f.size,
                    type=f.type,
                    path=new_path
                )
                db.session.add(new_file)
    db.session.commit()
    return jsonify({'id': new_id}), 201