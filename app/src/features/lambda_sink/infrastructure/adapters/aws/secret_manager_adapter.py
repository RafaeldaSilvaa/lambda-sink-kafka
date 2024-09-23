from typing import Dict, Any

import boto3
import json
from botocore.exceptions import ClientError

from src.features.lambda_sink.domain.interfaces.secret_manager_interface import ISecretManager


class SecretManagerAdapter(ISecretManager):
    def __init__(self, secret_name: str):
        self.secret_name: str = secret_name
        self.client = boto3.client('secretsmanager', endpoint_url='http://localhost:4566')

    def get_secret(self):
        try:
            get_secret_value_response: Dict[str, Any] = self.client.get_secret_value(SecretId=self.secret_name)
            secret: str = get_secret_value_response['SecretString']
            return json.loads(secret)
        except ClientError as e:
            print(f"Error retrieving secret: {e}")
            raise
