import logging

from flask import Flask
from flask import render_template, flash, redirect
from reportform import ReportForm
from config import Config
from fflogs import FFlogs

app = Flask(__name__)

# Load config from env variables
app.config.from_object(Config)

# Allow logging in devmode
if app.env == 'development':
    logging.basicConfig(level=logging.DEBUG)

# User is expected to enter report id there
@app.route('/', methods=['GET', 'POST'])
def index():
    form = ReportForm()
    app.logger.error('testerrorr env {}'.format(app.env))
    app.env
    app.logger.info('testinfo')
    if form.validate_on_submit():
        return redirect("/{}".format(form.report_id.data))
    return render_template('index.html', form=form)


# List all fights contained in an fflog report
@app.route('/<report_id>', methods=['GET', 'POST'])
def report(report_id):
    fflogs = FFlogs(app.config['API_KEY'])
    return render_template('report.html', report_id=report_id)


# Display specific fight details against dummy threshold values
@app.route('/<report_id>/<fight_id>', methods=['GET', 'POST'])
def fight(report_id, fight_id):
    return render_template('fight.html', report_id=report_id, fight_id=fight_id)


# Web server loop
if __name__ == '__main__':
    app.run()
