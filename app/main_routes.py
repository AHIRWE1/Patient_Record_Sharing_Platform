from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/help')
def help():
    return render_template('help.html')

