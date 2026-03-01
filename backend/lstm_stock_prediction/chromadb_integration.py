"""
ChromaDB Integration for LSTM Stock Predictions
Store and query prediction results with metadata
"""

import chromadb
from chromadb.config import Settings
from datetime import datetime
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import os


class LSTMPredictionStore:
    """
    Store and retrieve LSTM stock prediction results using ChromaDB
    """
    
    def __init__(self, host: str = "localhost", port: int = 8000, use_local: bool = False):
        """
        Initialize ChromaDB connection
        
        Args:
            host: ChromaDB server host (use 'chromadb' if inside Docker)
            port: ChromaDB server port
            use_local: Use local client instead of server (for testing)
        """
        self.use_local = use_local
        
        if use_local:
            self.client = chromadb.Client()
            print("✓ Using local ChromaDB client")
        else:
            try:
                # Use environment variables if available
                host = os.getenv('CHROMADB_HOST', host)
                port = int(os.getenv('CHROMADB_PORT', port))
                
                self.client = chromadb.HttpClient(host=host, port=port)
                self.client.heartbeat()
                print(f"✓ Connected to ChromaDB at {host}:{port}")
            except Exception as e:
                print(f"⚠ Could not connect to ChromaDB server: {e}")
                print("  Falling back to local client")
                self.client = chromadb.Client()
                self.use_local = True
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="lstm_stock_predictions",
            metadata={"description": "LSTM model predictions for stock prices"}
        )
        
        print(f"✓ Collection ready with {self.collection.count()} items")
    
    
    def store_prediction(self, result: Dict, model_version: str = "v1.0") -> Optional[str]:
        """
        Store prediction result in ChromaDB
        
        Args:
            result: Dictionary from train_company_lstm() with keys:
                    - status, company, data_points, r2_score, mae, rmse, etc.
            model_version: Model version identifier
            
        Returns:
            Document ID if successful, None otherwise
        """
        if result.get('status') != 'success':
            print(f"⚠ Skipping {result.get('company', 'unknown')} - {result.get('status')}")
            return None
        
        # Create unique ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        company_safe = result['company'].replace(' ', '_').replace('/', '_')[:50]
        doc_id = f"{company_safe}_{timestamp}"
        
        # Create embedding from predictions
        prediction_vector = self._create_embedding(result)
        
        # Prepare metadata
        metadata = {
            "company": result['company'][:100],  # ChromaDB has size limits
            "timestamp": timestamp,
            "data_points": int(result['data_points']),
            "train_samples": int(result['train_samples']),
            "test_samples": int(result['test_samples']),
            "r2_score": float(result['r2_score']),
            "mse": float(result['mse']),
            "rmse": float(result['rmse']),
            "mae": float(result['mae']),
            "final_train_loss": float(result['final_train_loss']),
            "final_val_loss": float(result['final_val_loss']),
            "model_version": model_version,
            "performance": self._categorize_performance(result['r2_score'])
        }
        
        # Create document text
        document = self._create_document_text(result, metadata)
        
        # Store in ChromaDB
        try:
            self.collection.add(
                ids=[doc_id],
                embeddings=[prediction_vector],
                documents=[document],
                metadatas=[metadata]
            )
            print(f"✓ Stored: {result['company'][:40]} | R²={result['r2_score']:.4f}")
            return doc_id
        
        except Exception as e:
            print(f"✗ Error storing {result['company']}: {e}")
            return None
    
    
    def store_batch(self, results: List[Dict], model_version: str = "v1.0") -> List[str]:
        """Store multiple prediction results"""
        stored_ids = []
        
        print(f"\nStoring {len(results)} predictions in ChromaDB...")
        print("="*70)
        
        for result in results:
            doc_id = self.store_prediction(result, model_version)
            if doc_id:
                stored_ids.append(doc_id)
        
        print("="*70)
        print(f"✓ Stored {len(stored_ids)}/{len(results)} predictions")
        print(f"  Total in collection: {self.collection.count()}")
        
        return stored_ids
    
    
    def query_by_company(self, company_name: str, limit: int = 5) -> Dict:
        """Query predictions for a specific company"""
        results = self.collection.get(
            where={"company": {"$contains": company_name}},
            limit=limit
        )
        return results
    
    
    def query_by_r2_threshold(self, min_r2: float = 0.7, limit: int = 10) -> Dict:
        """Get predictions with R² score above threshold"""
        results = self.collection.get(
            where={"r2_score": {"$gte": min_r2}},
            limit=limit
        )
        return results
    
    
    def query_by_performance(self, performance: str = "excellent", limit: int = 10) -> Dict:
        """
        Query by performance category
        Categories: excellent (R²≥0.7), good (0.5≤R²<0.7), fair (0.3≤R²<0.5), poor (<0.3)
        """
        results = self.collection.get(
            where={"performance": performance},
            limit=limit
        )
        return results
    
    
    def get_all_as_dataframe(self) -> pd.DataFrame:
        """Get all predictions as pandas DataFrame"""
        results = self.collection.get()
        
        if len(results['ids']) == 0:
            return pd.DataFrame()
        
        df = pd.DataFrame(results['metadatas'])
        df['id'] = results['ids']
        df = df.sort_values('r2_score', ascending=False)
        
        return df
    
    
    def get_statistics(self) -> Dict:
        """Get collection statistics"""
        df = self.get_all_as_dataframe()
        
        if df.empty:
            return {"error": "No predictions in collection"}
        
        stats = {
            "total_predictions": len(df),
            "companies": df['company'].nunique(),
            "avg_r2_score": df['r2_score'].mean(),
            "median_r2_score": df['r2_score'].median(),
            "best_r2_score": df['r2_score'].max(),
            "worst_r2_score": df['r2_score'].min(),
            "avg_mae": df['mae'].mean(),
            "performance_distribution": df['performance'].value_counts().to_dict()
        }
        
        return stats
    
    
    def delete_by_company(self, company_name: str) -> int:
        """Delete all predictions for a company"""
        results = self.collection.get(
            where={"company": {"$contains": company_name}}
        )
        
        if len(results['ids']) == 0:
            return 0
        
        self.collection.delete(ids=results['ids'])
        return len(results['ids'])
    
    
    def clear_collection(self):
        """Delete all predictions from collection"""
        count = self.collection.count()
        self.client.delete_collection("lstm_stock_predictions")
        self.collection = self.client.get_or_create_collection(
            name="lstm_stock_predictions",
            metadata={"description": "LSTM model predictions for stock prices"}
        )
        print(f"✓ Deleted {count} predictions")
    
    
    def _create_embedding(self, result: Dict, embedding_size: int = 384) -> List[float]:
        """
        Create embedding vector from prediction results
        
        For now, uses predictions + metrics. In production, could use:
        - Time series features (FFT, wavelets)
        - Statistical features (mean, std, skew, kurtosis)
        - Model-based embeddings (autoencoder)
        """
        # Get predictions
        y_pred = result['y_pred'].flatten()
        
        # Create feature vector with predictions + metrics
        features = []
        
        # Add prediction statistics
        features.extend([
            np.mean(y_pred),
            np.std(y_pred),
            np.min(y_pred),
            np.max(y_pred),
        ])
        
        # Add metrics
        features.extend([
            result['r2_score'],
            result['mae'],
            result['rmse'],
            result['mse']
        ])
        
        # Add first N predictions
        n_pred = min(len(y_pred), embedding_size - len(features))
        features.extend(y_pred[:n_pred].tolist())
        
        # Pad or truncate to embedding_size
        if len(features) < embedding_size:
            features.extend([0.0] * (embedding_size - len(features)))
        else:
            features = features[:embedding_size]
        
        return features
    
    
    def _categorize_performance(self, r2_score: float) -> str:
        """Categorize model performance based on R² score"""
        if r2_score >= 0.7:
            return "excellent"
        elif r2_score >= 0.5:
            return "good"
        elif r2_score >= 0.3:
            return "fair"
        else:
            return "poor"
    
    
    def _create_document_text(self, result: Dict, metadata: Dict) -> str:
        """Create searchable text document"""
        return f"""Stock Price Prediction for {result['company']}
Date: {metadata['timestamp']}
Model Version: {metadata['model_version']}

Performance Metrics:
- R² Score: {result['r2_score']:.4f}
- Mean Absolute Error: {result['mae']:.6f}
- Root Mean Squared Error: {result['rmse']:.6f}
- Mean Squared Error: {result['mse']:.6f}

Training Information:
- Total Data Points: {result['data_points']}
- Training Samples: {result['train_samples']}
- Test Samples: {result['test_samples']}
- Final Training Loss: {result['final_train_loss']:.6f}
- Final Validation Loss: {result['final_val_loss']:.6f}

Performance Category: {metadata['performance']}
"""


# Example usage
if __name__ == "__main__":
    # Initialize store
    store = LSTMPredictionStore(host="localhost", port=8000)
    
    # Get statistics
    stats = store.get_statistics()
    print("\nCollection Statistics:")
    print(stats)
    
    # Get all predictions as DataFrame
    df = store.get_all_as_dataframe()
    if not df.empty:
        print("\nTop predictions:")
        print(df[['company', 'r2_score', 'mae', 'performance']].head())
    
    # Query by performance
    excellent = store.query_by_performance("excellent")
    print(f"\n{len(excellent['ids'])} excellent predictions found")
