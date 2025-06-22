from flask import Blueprint, jsonify, render_template, current_app
from lib_version.version_awareness import VersionUtil
from app import current_users_gauge, get_version
from app.routes.metrics_route import extract_major_version


main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    """
    Render the main page of the application.
    ---
    tags:
      - Main
    summary: Renders the main page.
    responses:
      200:
        description: The main HTML page.
        content:
          text/html:
            schema:
              type: string
    """
    # Inc active user number
    version = extract_major_version(get_version())
    current_users_gauge.labels(version=version).inc()
    version_util = VersionUtil()
    lib_version = version_util.get_version()
    return render_template('index.html', version=current_app.config["VERSION"], lib_version=lib_version)
    
@main_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    ---
    tags:
      - Main
    summary: Checks the health of the application.
    responses:
      200:
        description: Application is alive.
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: alive!
    """
    return jsonify({"status": "alive!"})
