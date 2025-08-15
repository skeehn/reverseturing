# backend/analytics.py
class ModelAnalytics:
    def track_prediction(self, prediction, actual, confidence):
        # Store prediction accuracy
        # Update running statistics
        # Trigger retraining if accuracy drops below threshold
        
    def generate_insights(self):
        return {
            'accuracy_by_room_type': self.get_room_accuracy(),
            'common_mistakes': self.get_mistake_patterns(),
            'human_tells': self.get_human_indicators(),
            'ai_tells': self.get_ai_indicators()
        }