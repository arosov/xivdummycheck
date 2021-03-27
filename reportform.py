from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired


class ReportForm(FlaskForm):
    report_id = StringField('Enter fflogs report id or URL', validators=[InputRequired()])
    submit = SubmitField('Submit')
