# backend/training/training_worker.py
from celery import Celery

celery_app = Celery('reverse_turing_trainer')

@celery_app.task
def retrain_judge_model(misclassified_batch_id):
    # Load misclassified examples from database
    batch = get_training_batch(misclassified_batch_id)
    
    # Prepare training data
    trainer = JudgeTrainer()
    training_data = trainer.prepare_training_data(batch['examples'])
    
    # Fine-tune with LoRA
    new_model_version = trainer.fine_tune_judge(training_data)
    
    # Update model registry
    update_model_version(new_model_version)
    
    # Notify system of new model availability
    socketio.emit('model_updated', {'version': new_model_version}, broadcast=True)