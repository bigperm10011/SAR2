from app import app, db
from app.models import Leaver, Srep, Suspect

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Leaver': Leaver, 'Srep': Srep, 'Suspect': Suspect}
