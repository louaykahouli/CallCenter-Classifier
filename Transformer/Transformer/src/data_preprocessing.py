
import pandas as pd
import re
from typing import List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Classe pour nettoyer et préparer les données"""
    
    def __init__(self, min_text_length: int = 10):
        """
        Initialisation du préprocesseur
        
        Args:
            min_text_length: Longueur minimale acceptable pour un texte
        """
        self.min_text_length = min_text_length
    
    def clean_text(self, text: str) -> str:
        """
        Nettoie un texte brut
        
        Args:
            text: Texte à nettoyer
            
        Returns:
            Texte nettoyé
        """
        if not isinstance(text, str):
            return ""
        
        # Supprimer les URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Supprimer les emails
        text = re.sub(r'\S+@\S+', '', text)
        
        # Supprimer les numéros de téléphone (formats basiques)
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '', text)
        
        # Supprimer les caractères spéciaux excessifs
        text = re.sub(r'[^\w\s\.,!?;:\'\"-]', ' ', text)
        
        # Réduire les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        # Supprimer les espaces en début et fin
        text = text.strip()
        
        return text
    
    def scrub_pii(self, text: str) -> str:
        """
        Masque les informations personnelles identifiables (PII)
        
        Args:
            text: Texte contenant potentiellement des PII
            
        Returns:
            Texte avec PII masqués
        """
        # Masquer les numéros de carte de crédit
        text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]', text)
        
        # Masquer les numéros de sécurité sociale (format US)
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
        
        # Masquer les emails
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
        # Masquer les numéros de téléphone
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        
        # Masquer les adresses IP
        text = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP]', text)
        
        return text
    
    def remove_short_texts(self, df: pd.DataFrame, text_column: str = 'Document') -> pd.DataFrame:
        """
        Supprime les textes trop courts
        
        Args:
            df: DataFrame contenant les textes
            text_column: Nom de la colonne contenant les textes
            
        Returns:
            DataFrame filtré
        """
        initial_count = len(df)
        df = df[df[text_column].str.len() >= self.min_text_length].copy()
        removed_count = initial_count - len(df)
        
        if removed_count > 0:
            logger.info(f"Supprimé {removed_count} textes trop courts (< {self.min_text_length} caractères)")
        
        return df
    
    def balance_classes(self, df: pd.DataFrame, label_column: str = 'Topic_group', 
                       method: str = 'undersample', max_samples: int = None) -> pd.DataFrame:
        """
        Équilibre les classes (optionnel)
        
        Args:
            df: DataFrame à équilibrer
            label_column: Nom de la colonne des labels
            method: 'undersample' ou 'oversample'
            max_samples: Nombre maximum d'échantillons par classe (pour undersample)
            
        Returns:
            DataFrame équilibré
        """
        if method == 'undersample':
            # Trouver la classe minoritaire
            if max_samples is None:
                max_samples = df[label_column].value_counts().min()
            
            # Échantillonner chaque classe
            balanced_dfs = []
            for label in df[label_column].unique():
                label_df = df[df[label_column] == label]
                sampled = label_df.sample(n=min(len(label_df), max_samples), random_state=42)
                balanced_dfs.append(sampled)
            
            df = pd.concat(balanced_dfs, ignore_index=True)
            logger.info(f"Classes équilibrées avec {max_samples} échantillons max par classe")
        
        return df
    
    def preprocess_dataset(self, df: pd.DataFrame, 
                          text_column: str = 'Document',
                          label_column: str = 'Topic_group',
                          apply_pii_scrubbing: bool = True,
                          balance: bool = False) -> pd.DataFrame:
        """
        Pipeline complet de prétraitement
        
        Args:
            df: DataFrame brut
            text_column: Nom de la colonne texte
            label_column: Nom de la colonne label
            apply_pii_scrubbing: Appliquer le masquage PII
            balance: Équilibrer les classes
            
        Returns:
            DataFrame prétraité
        """
        logger.info(f"Début du prétraitement - {len(df)} exemples")
        
        # Copie pour éviter les modifications inattendues
        df = df.copy()
        
        # Supprimer les NaN
        df = df.dropna(subset=[text_column, label_column])
        logger.info(f"Après suppression des NaN: {len(df)} exemples")
        
        # Nettoyer les textes
        logger.info("Nettoyage des textes...")
        df[text_column] = df[text_column].apply(self.clean_text)
        
        # Masquer les PII si demandé
        if apply_pii_scrubbing:
            logger.info("Masquage des PII...")
            df[text_column] = df[text_column].apply(self.scrub_pii)
        
        # Supprimer les textes trop courts
        df = self.remove_short_texts(df, text_column)
        
        # Équilibrer les classes si demandé
        if balance:
            df = self.balance_classes(df, label_column)
        
        # Afficher la distribution des classes
        logger.info("\nDistribution des classes:")
        for label, count in df[label_column].value_counts().items():
            logger.info(f"  {label}: {count} ({count/len(df)*100:.1f}%)")
        
        logger.info(f"\nPrétraitement terminé - {len(df)} exemples finaux")
        
        return df


def main():
    """Fonction exemple d'utilisation"""
    
    # Charger les données brutes
    df = pd.read_csv("data/raw/all_tickets_processed_improved_v3.csv")
    
    # Initialiser le préprocesseur
    preprocessor = DataPreprocessor(min_text_length=10)
    
    # Prétraiter
    df_clean = preprocessor.preprocess_dataset(
        df,
        text_column='Document',
        label_column='Topic_group',
        apply_pii_scrubbing=True,
        balance=False
    )
    
    # Sauvegarder
    df_clean.to_csv("data/processed/tickets_clean.csv", index=False)
    logger.info("Données prétraitées sauvegardées dans data/processed/tickets_clean.csv")


if __name__ == "__main__":
    main()