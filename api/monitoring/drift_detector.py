"""
Data Drift Detector para SentiBR
Detecta mudanças na distribuição dos dados usando testes estatísticos
"""
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path


class DriftDetector:
    """
    Detector de drift de dados usando testes estatísticos
    """
    
    def __init__(
        self,
        baseline_path: Optional[Path] = None,
        warning_threshold: float = 0.15,
        critical_threshold: float = 0.25
    ):
        """
        Inicializa o detector de drift
        
        Args:
            baseline_path: Caminho para arquivo com distribuição baseline
            warning_threshold: Threshold para alerta de warning
            critical_threshold: Threshold para alerta crítico
        """
        self.baseline_path = baseline_path
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        
        # Baseline statistics
        self.baseline_stats = {}
        self.baseline_distribution = {}
        
        if baseline_path and baseline_path.exists():
            self.load_baseline()
    
    def load_baseline(self):
        """Carrega distribuição baseline do arquivo"""
        try:
            with open(self.baseline_path, 'r') as f:
                data = json.load(f)
                self.baseline_stats = data.get('stats', {})
                self.baseline_distribution = data.get('distribution', {})
            print(f"✅ Baseline carregado de {self.baseline_path}")
        except Exception as e:
            print(f"⚠️ Erro ao carregar baseline: {e}")
    
    def save_baseline(self, data: pd.DataFrame, save_path: Path):
        """
        Salva distribuição atual como baseline
        
        Args:
            data: DataFrame com os dados
            save_path: Caminho para salvar o baseline
        """
        stats = self._compute_statistics(data)
        distribution = self._compute_distribution(data)
        
        baseline = {
            'timestamp': datetime.now().isoformat(),
            'n_samples': len(data),
            'stats': stats,
            'distribution': distribution
        }
        
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w') as f:
            json.dump(baseline, f, indent=2)
        
        self.baseline_stats = stats
        self.baseline_distribution = distribution
        self.baseline_path = save_path
        
        print(f"✅ Baseline salvo em {save_path}")
    
    def detect_drift(
        self,
        current_data: pd.DataFrame,
        features: Optional[List[str]] = None
    ) -> Dict:
        """
        Detecta drift comparando dados atuais com baseline
        
        Args:
            current_data: DataFrame com dados atuais
            features: Lista de features para checar drift (None = todas)
        
        Returns:
            Dict com resultados do drift
        """
        if not self.baseline_stats:
            return {
                'error': 'Baseline não carregado. Execute save_baseline() primeiro.'
            }
        
        # Features a checar
        if features is None:
            features = list(self.baseline_stats.keys())
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'n_samples': len(current_data),
            'features': {},
            'overall_drift_score': 0.0,
            'drift_detected': False,
            'severity': 'normal'
        }
        
        drift_scores = []
        
        for feature in features:
            if feature not in current_data.columns:
                continue
            
            # Executar testes estatísticos
            feature_result = self._test_feature_drift(
                current_data[feature].values,
                feature
            )
            
            results['features'][feature] = feature_result
            drift_scores.append(feature_result['drift_score'])
        
        # Calcular drift score geral (média dos scores)
        if drift_scores:
            results['overall_drift_score'] = np.mean(drift_scores)
        
        # Determinar severity
        if results['overall_drift_score'] >= self.critical_threshold:
            results['drift_detected'] = True
            results['severity'] = 'critical'
        elif results['overall_drift_score'] >= self.warning_threshold:
            results['drift_detected'] = True
            results['severity'] = 'warning'
        else:
            results['severity'] = 'normal'
        
        return results
    
    def _test_feature_drift(
        self,
        current_values: np.ndarray,
        feature: str
    ) -> Dict:
        """
        Testa drift de uma feature específica
        
        Args:
            current_values: Valores atuais da feature
            feature: Nome da feature
        
        Returns:
            Dict com resultados do teste
        """
        baseline_values = self.baseline_distribution.get(feature, [])
        
        if not baseline_values:
            return {
                'drift_score': 0.0,
                'test': 'none',
                'p_value': 1.0,
                'statistic': 0.0
            }
        
        # Determinar tipo da feature
        if self._is_numeric(current_values):
            result = self._test_numeric_drift(current_values, baseline_values)
        else:
            result = self._test_categorical_drift(current_values, baseline_values)
        
        return result
    
    def _test_numeric_drift(
        self,
        current: np.ndarray,
        baseline: List[float]
    ) -> Dict:
        """
        Testa drift de feature numérica usando Kolmogorov-Smirnov test
        
        Args:
            current: Valores atuais
            baseline: Valores baseline
        
        Returns:
            Dict com resultados do KS test
        """
        # Kolmogorov-Smirnov test
        ks_stat, p_value = stats.ks_2samp(current, baseline)
        
        # Drift score baseado na KS statistic
        # KS stat varia de 0 (idêntico) a 1 (completamente diferente)
        drift_score = ks_stat
        
        return {
            'test': 'kolmogorov_smirnov',
            'drift_score': float(drift_score),
            'ks_statistic': float(ks_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'mean_shift': float(np.mean(current) - np.mean(baseline)),
            'std_shift': float(np.std(current) - np.std(baseline))
        }
    
    def _test_categorical_drift(
        self,
        current: np.ndarray,
        baseline: List
    ) -> Dict:
        """
        Testa drift de feature categórica usando Chi-Square test
        
        Args:
            current: Valores atuais
            baseline: Valores baseline
        
        Returns:
            Dict com resultados do Chi-Square test
        """
        # Contar frequências
        current_counts = pd.Series(current).value_counts()
        baseline_counts = pd.Series(baseline).value_counts()
        
        # Alinhar índices
        all_categories = set(current_counts.index) | set(baseline_counts.index)
        current_freq = [current_counts.get(cat, 0) for cat in all_categories]
        baseline_freq = [baseline_counts.get(cat, 0) for cat in all_categories]
        
        # Chi-square test
        chi2_stat, p_value = stats.chisquare(current_freq, baseline_freq)
        
        # Drift score normalizado
        total = sum(current_freq) + sum(baseline_freq)
        drift_score = min(chi2_stat / total, 1.0)
        
        return {
            'test': 'chi_square',
            'drift_score': float(drift_score),
            'chi2_statistic': float(chi2_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'categories': len(all_categories)
        }
    
    def _is_numeric(self, values: np.ndarray) -> bool:
        """Verifica se valores são numéricos"""
        try:
            values.astype(float)
            return True
        except (ValueError, TypeError):
            return False
    
    def _compute_statistics(self, data: pd.DataFrame) -> Dict:
        """
        Computa estatísticas dos dados
        
        Args:
            data: DataFrame com os dados
        
        Returns:
            Dict com estatísticas por feature
        """
        stats_dict = {}
        
        for col in data.columns:
            if pd.api.types.is_numeric_dtype(data[col]):
                stats_dict[col] = {
                    'type': 'numeric',
                    'mean': float(data[col].mean()),
                    'std': float(data[col].std()),
                    'min': float(data[col].min()),
                    'max': float(data[col].max()),
                    'median': float(data[col].median()),
                    'q25': float(data[col].quantile(0.25)),
                    'q75': float(data[col].quantile(0.75))
                }
            else:
                value_counts = data[col].value_counts()
                stats_dict[col] = {
                    'type': 'categorical',
                    'n_unique': int(data[col].nunique()),
                    'top_values': value_counts.head(10).to_dict()
                }
        
        return stats_dict
    
    def _compute_distribution(self, data: pd.DataFrame) -> Dict:
        """
        Computa distribuição dos dados para cada feature
        
        Args:
            data: DataFrame com os dados
        
        Returns:
            Dict com distribuições
        """
        distribution_dict = {}
        
        for col in data.columns:
            if pd.api.types.is_numeric_dtype(data[col]):
                # Para numérico, salvar todos os valores (ou amostra)
                values = data[col].dropna().values
                if len(values) > 10000:
                    # Amostrar se muito grande
                    values = np.random.choice(values, 10000, replace=False)
                distribution_dict[col] = values.tolist()
            else:
                # Para categórico, salvar valores
                distribution_dict[col] = data[col].dropna().tolist()
        
        return distribution_dict
    
    def get_drift_report(self, drift_results: Dict) -> str:
        """
        Gera relatório textual do drift
        
        Args:
            drift_results: Resultados do detect_drift()
        
        Returns:
            String com relatório formatado
        """
        report = []
        report.append("=" * 60)
        report.append("RELATÓRIO DE DRIFT DE DADOS")
        report.append("=" * 60)
        report.append(f"Timestamp: {drift_results['timestamp']}")
        report.append(f"Amostras: {drift_results['n_samples']}")
        report.append(f"Drift Score Geral: {drift_results['overall_drift_score']:.2%}")
        report.append(f"Severity: {drift_results['severity'].upper()}")
        report.append(f"Drift Detectado: {'SIM' if drift_results['drift_detected'] else 'NÃO'}")
        report.append("")
        
        report.append("FEATURES:")
        report.append("-" * 60)
        
        for feature, result in drift_results.get('features', {}).items():
            report.append(f"\n{feature}:")
            report.append(f"  Drift Score: {result['drift_score']:.2%}")
            report.append(f"  Teste: {result['test']}")
            report.append(f"  P-value: {result.get('p_value', 0):.4f}")
            report.append(f"  Significativo: {'SIM' if result.get('significant', False) else 'NÃO'}")
            
            if 'mean_shift' in result:
                report.append(f"  Mean Shift: {result['mean_shift']:.4f}")
                report.append(f"  Std Shift: {result['std_shift']:.4f}")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


# ============================================
# Funções Helper
# ============================================

def create_mock_baseline(save_path: Path, n_samples: int = 10000):
    """
    Cria um baseline mockado para testes
    
    Args:
        save_path: Caminho para salvar
        n_samples: Número de amostras
    """
    # Gerar dados mockados
    data = pd.DataFrame({
        'text_length': np.random.normal(100, 20, n_samples),
        'word_count': np.random.poisson(20, n_samples),
        'sentiment_positive_prob': np.random.beta(2, 5, n_samples),
        'sentiment_negative_prob': np.random.beta(5, 2, n_samples),
        'has_emoji': np.random.choice([True, False], n_samples, p=[0.3, 0.7]),
        'language': np.random.choice(['pt', 'en', 'es'], n_samples, p=[0.8, 0.15, 0.05])
    })
    
    # Criar detector e salvar baseline
    detector = DriftDetector()
    detector.save_baseline(data, save_path)
    
    print(f"✅ Mock baseline criado: {save_path}")
    return detector


if __name__ == "__main__":
    # Exemplo de uso
    baseline_path = Path("data/baseline_distribution.json")
    
    # Criar baseline mockado
    detector = create_mock_baseline(baseline_path)
    
    # Simular dados com drift
    current_data = pd.DataFrame({
        'text_length': np.random.normal(120, 25, 1000),  # Drift: média maior
        'word_count': np.random.poisson(22, 1000),       # Drift: leve
        'sentiment_positive_prob': np.random.beta(3, 4, 1000),  # Drift médio
        'sentiment_negative_prob': np.random.beta(4, 3, 1000),  # Drift médio
        'has_emoji': np.random.choice([True, False], 1000, p=[0.5, 0.5]),  # Drift alto
        'language': np.random.choice(['pt', 'en', 'es'], 1000, p=[0.6, 0.3, 0.1])  # Drift médio
    })
    
    # Detectar drift
    results = detector.detect_drift(current_data)
    
    # Mostrar relatório
    print(detector.get_drift_report(results))
