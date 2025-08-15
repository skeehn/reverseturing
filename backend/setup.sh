# Create requirements.txt
cat > backend/requirements.txt << EOF
flask==2.3.3
flask-socketio==5.3.6
transformers==4.35.0
torch==2.1.0
datasets==2.14.0
peft==0.6.0
bitsandbytes==0.41.0
psycopg2-binary==2.9.7
redis==4.6.0
celery==5.3.0
python-dotenv==1.0.0
accelerate==0.24.0
EOF

pip install -r requirements.txt