# Run once to add dummy data
from app import db, Policy

db.create_all()
db.session.add_all([
    Policy(name="Life Shield", type="Life", premium=12000),
    Policy(name="Health Plus", type="Health", premium=8000),
    Policy(name="Auto Secure", type="Vehicle", premium=5000)
])
db.session.commit()
print("Sample policies added!")
