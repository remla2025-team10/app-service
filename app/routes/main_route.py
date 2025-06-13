from flask import Blueprint, jsonify, render_template, current_app
from lib_version.version_awareness import VersionUtil
from app import current_users_gauge
from app.routes.metrics_route import get_version_number 


main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    # Inc active user number
    version = get_version_number()
    current_users_gauge.labels(version=version).inc()
    version_util = VersionUtil()
    lib_version = version_util.get_version()
    return render_template('index.html', version=current_app.config["VERSION"], lib_version=lib_version)
    
@main_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "alive!"})
