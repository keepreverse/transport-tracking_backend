import os
from flask import Blueprint, request, send_file, jsonify, current_app
from models import db, File, Point
from utils import generate_uuid, delete_file_from_disk

files_bp = Blueprint('files', __name__)

@files_bp.route('/upload', methods=['POST'])
def upload_file():
    point_id = request.form.get('pointId')
    if not point_id:
        return jsonify({'error': 'pointId required'}), 400
    point = Point.query.get(point_id)
    if not point:
        return jsonify({'error': 'Point not found'}), 404

    uploaded_files = request.files.getlist('files')
    saved = []
    for f in uploaded_files:

        original_name = f.filename

        _, ext = os.path.splitext(original_name)
        new_filename = generate_uuid() + ext
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
        f.save(save_path)

        file_id = generate_uuid()
        file_record = File(
            id=file_id,
            point_id=point.id,
            name=original_name,
            size=os.path.getsize(save_path),
            type=f.content_type,
            path=save_path
        )
        db.session.add(file_record)
        saved.append({
            'id': file_id,
            'name': original_name,
            'size': file_record.size,
            'type': file_record.type
        })
    db.session.commit()
    return jsonify(saved), 201

@files_bp.route('/<file_id>', methods=['GET'])
def get_file(file_id):
    file_record = File.query.get_or_404(file_id)
    return send_file(file_record.path, as_attachment=False, download_name=file_record.name)

@files_bp.route('/<file_id>/download', methods=['GET'])
def download_file(file_id):
    file_record = File.query.get_or_404(file_id)
    return send_file(file_record.path, as_attachment=True, download_name=file_record.name)

@files_bp.route('/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    file_record = File.query.get_or_404(file_id)
    delete_file_from_disk(file_record.path)
    db.session.delete(file_record)
    db.session.commit()
    return jsonify({'status': 'ok'})