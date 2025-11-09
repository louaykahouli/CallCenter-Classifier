import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
import mlflow
import mlflow.transformers
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding
)
from datasets import Dataset
import torch
from typing import Dict, List, Tuple
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransformerTrainer:
    """Classe pour gérer l'entraînement du modèle Transformer"""
    
    def __init__(self, 
                 model_name: str = "distilbert-base-multilingual-cased",
                 max_length: int = 128,
                 batch_size: int = 4,  # Réduit la taille du batch à 4
                 learning_rate: float = 2e-5,
                 num_epochs: int = 3):
        """
        Initialisation du trainer
        
        Args:
            model_name: Nom du modèle pré-entraîné Hugging Face
            max_length: Longueur maximale des séquences
            batch_size: Taille des batchs
            learning_rate: Taux d'apprentissage
            num_epochs: Nombre d'époques
        """
        self.model_name = model_name
        self.max_length = max_length
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        
        self.tokenizer = None
        self.model = None
        self.label2id = None
        self.id2label = None
        
    def load_data(self, data_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Charge et prépare les données
        
        Args:
            data_path: Chemin vers le fichier CSV
            
        Returns:
            Train et test DataFrames
        """
        logger.info(f"Chargement des données depuis {data_path}")
        
        # Charger le dataset
        df = pd.read_csv(data_path)
        
        # Nettoyage basique
        df = df.dropna(subset=['Document', 'Topic_group'])
        df['Document'] = df['Document'].astype(str)
        df['Topic_group'] = df['Topic_group'].astype(str)
        
        logger.info(f"Dataset chargé: {len(df)} exemples")
        logger.info(f"Catégories: {df['Topic_group'].unique()}")
        
        # Créer les mappings label <-> id
        unique_labels = sorted(df['Topic_group'].unique())
        self.label2id = {label: idx for idx, label in enumerate(unique_labels)}
        self.id2label = {idx: label for label, idx in self.label2id.items()}
        
        # Convertir les labels en IDs
        df['label'] = df['Topic_group'].map(self.label2id)
        
        # Split train/test
        train_df, test_df = train_test_split(
            df, 
            test_size=0.2, 
            random_state=42,
            stratify=df['label']
        )
        
        logger.info(f"Train: {len(train_df)}, Test: {len(test_df)}")
        
        return train_df, test_df
    
    def prepare_datasets(self, train_df: pd.DataFrame, test_df: pd.DataFrame):
        """
        Prépare les datasets pour l'entraînement
        
        Args:
            train_df: DataFrame d'entraînement
            test_df: DataFrame de test
            
        Returns:
            Datasets tokenizés
        """
        logger.info("Tokenization des données...")
        
        # Initialiser le tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Créer les datasets Hugging Face
        train_dataset = Dataset.from_pandas(train_df[['Document', 'label']])
        test_dataset = Dataset.from_pandas(test_df[['Document', 'label']])
        
        # Fonction de tokenization
        def tokenize_function(examples):
            return self.tokenizer(
                examples['Document'],
                padding='max_length',
                truncation=True,
                max_length=self.max_length
            )
        
        # Tokenizer les datasets
        train_tokenized = train_dataset.map(tokenize_function, batched=True)
        test_tokenized = test_dataset.map(tokenize_function, batched=True)
        
        # Définir le format pour PyTorch
        train_tokenized.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
        test_tokenized.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
        
        return train_tokenized, test_tokenized
    
    def compute_metrics(self, eval_pred):
        """
        Calcule les métriques d'évaluation
        
        Args:
            eval_pred: Prédictions et labels
            
        Returns:
            Dictionnaire des métriques
        """
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        accuracy = accuracy_score(labels, predictions)
        f1_macro = f1_score(labels, predictions, average='macro')
        f1_weighted = f1_score(labels, predictions, average='weighted')
        
        return {
            'accuracy': accuracy,
            'f1_macro': f1_macro,
            'f1_weighted': f1_weighted
        }
    
    def train(self, train_dataset, test_dataset, output_dir: str = "./models/transformer"):
        """
        Entraîne le modèle Transformer
        
        Args:
            train_dataset: Dataset d'entraînement tokenizé
            test_dataset: Dataset de test tokenizé
            output_dir: Répertoire de sauvegarde du modèle
        """
        logger.info("Initialisation du modèle...")
        
        # Charger le modèle pré-entraîné
        # Charger le modèle pré-entraîné
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=len(self.label2id),
            ignore_mismatched_sizes=True
        )
        # Enable gradient checkpointing
        self.model.gradient_checkpointing_enable()
        
        # Configuration de l'entraînement
        training_args = TrainingArguments(
            output_dir=output_dir,
            learning_rate=self.learning_rate,
            per_device_train_batch_size=self.batch_size,
            per_device_eval_batch_size=self.batch_size,
            gradient_accumulation_steps=4,  # Augmenté à 4 pour compenser le batch size plus petit
            gradient_checkpointing=True,  # Activer le gradient checkpointing
            num_train_epochs=self.num_epochs,
            weight_decay=0.01,
            logging_dir=f"{output_dir}/logs",
            logging_steps=100,
            fp16=True  # Use mixed precision training
        )
        
        # Data collator pour le padding dynamique
        data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)
        
        # Initialiser le Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=test_dataset,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
            compute_metrics=self.compute_metrics
        )
        
        logger.info("Début de l'entraînement...")
        
        # Entraîner le modèle
        trainer.train()
        
        # Évaluation finale
        logger.info("Évaluation finale...")
        eval_results = trainer.evaluate()
        
        logger.info(f"Résultats: {eval_results}")
        
        return trainer, eval_results
    
    def save_model(self, trainer: Trainer, output_dir: str):
        """
        Sauvegarde le modèle et les métadonnées
        
        Args:
            trainer: Trainer Hugging Face
            output_dir: Répertoire de sauvegarde
        """
        logger.info(f"Sauvegarde du modèle dans {output_dir}")
        
        # Sauvegarder le modèle et le tokenizer
        trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        # Sauvegarder les mappings
        import json
        with open(f"{output_dir}/label_mappings.json", "w") as f:
            json.dump({
                "label2id": self.label2id,
                "id2label": self.id2label
            }, f, indent=2)
        
        logger.info("Modèle sauvegardé avec succès")


def main():
    """Fonction principale d'entraînement avec MLflow tracking"""
    
    # Configuration
    DATA_PATH = "data/processed/tickets_clean.csv"
    OUTPUT_DIR = "models/transformer"
    MLFLOW_TRACKING_URI = "http://localhost:5000"
    EXPERIMENT_NAME = "CallCenterAI-Transformer"
    
    # Configurer MLflow
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)
    
    # Hyperparamètres
    hyperparams = {
        "model_name": "distilbert-base-multilingual-cased",
        "max_length": 128,
        "batch_size": 16,
        "learning_rate": 2e-5,
        "num_epochs": 3
    }
    
    # Démarrer un run MLflow avec un nom descriptif
    import datetime
    run_name = f"transformer-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    with mlflow.start_run(run_name=run_name):
        
        # Logger les hyperparamètres
        mlflow.log_params(hyperparams)
        
        # Logger des métadonnées système
        mlflow.log_param("data_path", DATA_PATH)
        mlflow.log_param("output_dir", OUTPUT_DIR)
        mlflow.log_param("pytorch_version", torch.__version__)
        mlflow.log_param("device", "cuda" if torch.cuda.is_available() else "cpu")
        
        # Tags pour faciliter la recherche
        mlflow.set_tag("model_type", "transformer")
        mlflow.set_tag("framework", "huggingface")
        mlflow.set_tag("task", "text_classification")
        mlflow.set_tag("language", "multilingual")
        
        # Initialiser le trainer
        transformer_trainer = TransformerTrainer(**hyperparams)
        
        # Charger les données
        train_df, test_df = transformer_trainer.load_data(DATA_PATH)
        
        # Logger des infos sur les données
        mlflow.log_param("train_size", len(train_df))
        mlflow.log_param("test_size", len(test_df))
        mlflow.log_param("num_classes", len(transformer_trainer.label2id))
        
        # Logger la distribution des classes
        class_distribution = train_df['Topic_group'].value_counts().to_dict()
        for class_name, count in class_distribution.items():
            mlflow.log_metric(f"train_class_{class_name}_count", count)
        
        # Préparer les datasets
        train_dataset, test_dataset = transformer_trainer.prepare_datasets(train_df, test_df)
        
        # Entraîner le modèle
        import time
        start_time = time.time()
        trainer, eval_results = transformer_trainer.train(train_dataset, test_dataset, OUTPUT_DIR)
        training_time = time.time() - start_time
        
        # Logger les métriques
        mlflow.log_metrics({
            "eval_accuracy": eval_results['eval_accuracy'],
            "eval_f1_macro": eval_results['eval_f1_macro'],
            "eval_f1_weighted": eval_results['eval_f1_weighted'],
            "eval_loss": eval_results['eval_loss'],
            "training_time_seconds": training_time
        })
        
        # Obtenir les prédictions pour un rapport détaillé
        predictions = trainer.predict(test_dataset)
        pred_labels = np.argmax(predictions.predictions, axis=1)
        true_labels = predictions.label_ids
        
        # Logger le rapport de classification
        from sklearn.metrics import classification_report
        report = classification_report(
            true_labels, 
            pred_labels, 
            target_names=list(transformer_trainer.label2id.keys()),
            output_dict=True
        )
        
        # Logger les métriques par classe
        for class_name, metrics in report.items():
            if isinstance(metrics, dict):
                for metric_name, value in metrics.items():
                    mlflow.log_metric(f"{class_name}_{metric_name}", value)
        
        # Sauvegarder le modèle
        transformer_trainer.save_model(trainer, OUTPUT_DIR)
        
        # Logger la matrice de confusion comme artifact
        from sklearn.metrics import confusion_matrix
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        cm = confusion_matrix(true_labels, pred_labels)
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=list(transformer_trainer.label2id.keys()),
                    yticklabels=list(transformer_trainer.label2id.keys()))
        plt.title('Matrice de Confusion')
        plt.ylabel('Vraie Classe')
        plt.xlabel('Classe Prédite')
        plt.tight_layout()
        
        # Sauvegarder et logger la figure
        confusion_matrix_path = f"{OUTPUT_DIR}/confusion_matrix.png"
        plt.savefig(confusion_matrix_path)
        mlflow.log_artifact(confusion_matrix_path)
        plt.close()
        
        # Logger le rapport de classification en texte
        report_text = classification_report(
            true_labels, 
            pred_labels, 
            target_names=list(transformer_trainer.label2id.keys())
        )
        report_path = f"{OUTPUT_DIR}/classification_report.txt"
        with open(report_path, 'w') as f:
            f.write(report_text)
        mlflow.log_artifact(report_path)
        
        # Logger le modèle dans MLflow
        mlflow.transformers.log_model(
            transformers_model={
                "model": transformer_trainer.model,
                "tokenizer": transformer_trainer.tokenizer
            },
            artifact_path="model",
            registered_model_name="CallCenterAI-Transformer"
        )
        
        logger.info("✅ Entraînement terminé avec succès!")
        logger.info(f"Run ID: {mlflow.active_run().info.run_id}")


if __name__ == "__main__":
    main()