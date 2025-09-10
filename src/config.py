import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.config = self.load_config()
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure required directories exist"""
        (self.root_dir / 'static' / 'css').mkdir(parents=True, exist_ok=True)

    def load_config(self):
        try:
            with open(self.root_dir / 'config.yaml', 'r') as file:
                config = yaml.safe_load(file)
            return config
        except Exception as e:
            logger.warning(f"Error loading config file: {e}. Using default configuration.")
            return self.get_default_config()

    def get_default_config(self):
        return {
            'data': {
                'filename': 'customer_churn.csv',
                'categorical_columns': [
                    'ContractType', 'InternetService', 'PaymentMethod',
                    'StreamingTV', 'StreamingMovies', 'PhoneService', 'Gender'
                ],
                'numerical_columns': [
                    'Tenure', 'MonthlyCharges', 'TotalCharges', 'SatisfactionScore'
                ]
            },
            'model': {
                'target': 'Churn',
                'test_size': 0.2,
                'random_state': 42,
                'n_estimators': 100,
                'max_depth': 10,
                'class_weight': 'balanced'
            },
            'visualization': {
                'color_scheme': ["#2ecc71", "#e74c3c", "#3498db"],
                'chart_theme': "plotly_white",
                'categorical_palette': "Set3",
                'correlation_colorscale': "RdBu"
            }
        }

    @property
    def data_path(self):
        return self.root_dir / 'data' / self.config['data']['filename']

    @property
    def style_path(self):
        return self.root_dir / 'static' / 'css' / 'style.css'

config = Config()
