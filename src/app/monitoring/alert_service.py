"""Alert service for Slack notifications."""
import json
from typing import Dict, Any
from slack_sdk.webhook import WebhookClient
from slack_sdk import WebClient
from sqlalchemy.orm import Session

from ..models.database import DriftAlert, ModelMetadata
from ..core.config import get_settings


class AlertService:
    """Service for sending alerts via Slack."""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.settings = get_settings()
        
        # Initialize Slack clients
        if self.settings.SLACK_WEBHOOK_URL:
            self.webhook_client = WebhookClient(self.settings.SLACK_WEBHOOK_URL)
        else:
            self.webhook_client = None
        
        if self.settings.SLACK_BOT_TOKEN:
            self.slack_client = WebClient(token=self.settings.SLACK_BOT_TOKEN)
        else:
            self.slack_client = None
    
    async def send_drift_alert(self, drift_alert: DriftAlert) -> bool:
        """Send drift detection alert to Slack."""
        if not self.webhook_client and not self.slack_client:
            print("Warning: Slack not configured, skipping alert")
            return False
        
        # Get model info
        model = self.db.query(ModelMetadata).filter(
            ModelMetadata.id == drift_alert.model_id
        ).first()
        
        # Parse drifted features
        features_drifted = []
        if drift_alert.features_drifted:
            try:
                features_drifted = json.loads(drift_alert.features_drifted)
            except:
                pass
        
        # Create message
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 Data Drift Detected"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Tenant:*\n{self.tenant_id}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Model:*\n{model.model_name if model else 'Unknown'}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Drift Score:*\n{drift_alert.drift_score}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Alert ID:*\n{drift_alert.id}"
                        }
                    ]
                }
            ]
        }
        
        if features_drifted:
            message["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Drifted Features:*\n{', '.join(features_drifted)}"
                }
            })
        
        message["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "🔄 Auto-retraining pipeline will be triggered..."
            }
        })
        
        try:
            if self.webhook_client:
                self.webhook_client.send(
                    text="Data Drift Detected",
                    blocks=message["blocks"]
                )
            return True
        except Exception as e:
            print(f"Error sending Slack alert: {str(e)}")
            return False
    
    async def send_retraining_success_alert(
        self,
        drift_alert: DriftAlert,
        new_model: ModelMetadata,
        metrics: Dict[str, float]
    ) -> bool:
        """Send retraining success alert to Slack."""
        if not self.webhook_client and not self.slack_client:
            print("Warning: Slack not configured, skipping alert")
            return False
        
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "✅ Model Retraining Successful"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Tenant:*\n{self.tenant_id}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Model:*\n{new_model.model_name}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Version:*\n{new_model.model_version}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Deployed:*\n{'Yes' if new_model.is_deployed else 'No'}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Performance Metrics:*\n• Accuracy: {metrics.get('accuracy', 0):.4f}\n• Precision: {metrics.get('precision', 0):.4f}\n• Recall: {metrics.get('recall', 0):.4f}\n• F1 Score: {metrics.get('f1_score', 0):.4f}"
                    }
                }
            ]
        }
        
        try:
            if self.webhook_client:
                self.webhook_client.send(
                    text="Model Retraining Successful",
                    blocks=message["blocks"]
                )
            return True
        except Exception as e:
            print(f"Error sending Slack alert: {str(e)}")
            return False
