-- ============================================
-- SentiBR - PostgreSQL Initialization Script
-- ============================================

-- Extensões
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- ============================================
-- Schema: predictions
-- ============================================
CREATE SCHEMA IF NOT EXISTS predictions;

-- Tabela de predições
CREATE TABLE IF NOT EXISTS predictions.predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    text TEXT NOT NULL,
    sentiment VARCHAR(20) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    aspects JSONB,
    model_version VARCHAR(50) NOT NULL,
    inference_time_ms INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_predictions_sentiment ON predictions.predictions(sentiment);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions.predictions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_model_version ON predictions.predictions(model_version);
CREATE INDEX IF NOT EXISTS idx_predictions_confidence ON predictions.predictions(confidence);
CREATE INDEX IF NOT EXISTS idx_predictions_aspects ON predictions.predictions USING GIN (aspects);

-- ============================================
-- Schema: feedback
-- ============================================
CREATE SCHEMA IF NOT EXISTS feedback;

-- Tabela de feedbacks
CREATE TABLE IF NOT EXISTS feedback.feedbacks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prediction_id UUID NOT NULL,
    original_sentiment VARCHAR(20) NOT NULL,
    corrected_sentiment VARCHAR(20),
    feedback_type VARCHAR(20) NOT NULL CHECK (feedback_type IN ('correct', 'incorrect', 'partial')),
    user_comment TEXT,
    user_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prediction_id) REFERENCES predictions.predictions(id) ON DELETE CASCADE
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_feedbacks_prediction_id ON feedback.feedbacks(prediction_id);
CREATE INDEX IF NOT EXISTS idx_feedbacks_feedback_type ON feedback.feedbacks(feedback_type);
CREATE INDEX IF NOT EXISTS idx_feedbacks_created_at ON feedback.feedbacks(created_at DESC);

-- ============================================
-- Schema: metrics
-- ============================================
CREATE SCHEMA IF NOT EXISTS metrics;

-- Tabela de métricas agregadas por hora
CREATE TABLE IF NOT EXISTS metrics.hourly_metrics (
    id SERIAL PRIMARY KEY,
    hour_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    total_predictions INTEGER NOT NULL DEFAULT 0,
    positive_count INTEGER NOT NULL DEFAULT 0,
    negative_count INTEGER NOT NULL DEFAULT 0,
    neutral_count INTEGER NOT NULL DEFAULT 0,
    avg_confidence DECIMAL(5,4),
    avg_inference_time_ms INTEGER,
    error_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(hour_timestamp)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_hourly_metrics_timestamp ON metrics.hourly_metrics(hour_timestamp DESC);

-- Tabela de drift metrics
CREATE TABLE IF NOT EXISTS metrics.drift_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,6) NOT NULL,
    threshold DECIMAL(10,6),
    is_alert BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_drift_metrics_created_at ON metrics.drift_metrics(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_drift_metrics_is_alert ON metrics.drift_metrics(is_alert);

-- ============================================
-- Schema: mlflow (para o backend do MLflow)
-- ============================================
-- O MLflow cria suas próprias tabelas automaticamente

-- ============================================
-- Views úteis
-- ============================================

-- View: Estatísticas diárias
CREATE OR REPLACE VIEW metrics.daily_stats AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_predictions,
    COUNT(*) FILTER (WHERE sentiment = 'positive') as positive_count,
    COUNT(*) FILTER (WHERE sentiment = 'negative') as negative_count,
    COUNT(*) FILTER (WHERE sentiment = 'neutral') as neutral_count,
    AVG(confidence)::DECIMAL(5,4) as avg_confidence,
    AVG(inference_time_ms)::INTEGER as avg_inference_time_ms,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY inference_time_ms) as median_inference_time_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY inference_time_ms) as p95_inference_time_ms
FROM predictions.predictions
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- View: Taxa de feedback
CREATE OR REPLACE VIEW feedback.feedback_stats AS
SELECT 
    DATE(f.created_at) as date,
    COUNT(*) as total_feedbacks,
    COUNT(*) FILTER (WHERE f.feedback_type = 'correct') as correct_count,
    COUNT(*) FILTER (WHERE f.feedback_type = 'incorrect') as incorrect_count,
    COUNT(*) FILTER (WHERE f.feedback_type = 'partial') as partial_count,
    (COUNT(*) FILTER (WHERE f.feedback_type = 'correct')::DECIMAL / COUNT(*) * 100)::DECIMAL(5,2) as accuracy_rate
FROM feedback.feedbacks f
GROUP BY DATE(f.created_at)
ORDER BY date DESC;

-- View: Distribuição de sentimentos por aspecto
CREATE OR REPLACE VIEW predictions.aspect_sentiment_distribution AS
SELECT 
    aspect->>'aspect' as aspect_name,
    aspect->>'sentiment' as sentiment,
    COUNT(*) as count,
    AVG((aspect->>'confidence')::DECIMAL)::DECIMAL(5,4) as avg_confidence
FROM predictions.predictions,
     jsonb_array_elements(aspects) as aspect
WHERE aspects IS NOT NULL
GROUP BY aspect->>'aspect', aspect->>'sentiment'
ORDER BY aspect_name, sentiment;

-- ============================================
-- Funções úteis
-- ============================================

-- Função: Calcular métricas horárias
CREATE OR REPLACE FUNCTION metrics.aggregate_hourly_metrics()
RETURNS void AS $$
BEGIN
    INSERT INTO metrics.hourly_metrics (
        hour_timestamp,
        total_predictions,
        positive_count,
        negative_count,
        neutral_count,
        avg_confidence,
        avg_inference_time_ms
    )
    SELECT 
        DATE_TRUNC('hour', created_at) as hour_timestamp,
        COUNT(*) as total_predictions,
        COUNT(*) FILTER (WHERE sentiment = 'positive') as positive_count,
        COUNT(*) FILTER (WHERE sentiment = 'negative') as negative_count,
        COUNT(*) FILTER (WHERE sentiment = 'neutral') as neutral_count,
        AVG(confidence)::DECIMAL(5,4) as avg_confidence,
        AVG(inference_time_ms)::INTEGER as avg_inference_time_ms
    FROM predictions.predictions
    WHERE created_at >= DATE_TRUNC('hour', NOW() - INTERVAL '1 hour')
      AND created_at < DATE_TRUNC('hour', NOW())
    GROUP BY DATE_TRUNC('hour', created_at)
    ON CONFLICT (hour_timestamp) DO UPDATE SET
        total_predictions = EXCLUDED.total_predictions,
        positive_count = EXCLUDED.positive_count,
        negative_count = EXCLUDED.negative_count,
        neutral_count = EXCLUDED.neutral_count,
        avg_confidence = EXCLUDED.avg_confidence,
        avg_inference_time_ms = EXCLUDED.avg_inference_time_ms;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Dados de exemplo (opcional)
-- ============================================

-- Inserir algumas predições de exemplo
-- INSERT INTO predictions.predictions (text, sentiment, confidence, model_version, inference_time_ms)
-- VALUES 
--     ('A comida estava deliciosa!', 'positive', 0.95, 'bert-v1.0', 45),
--     ('Entrega muito demorada', 'negative', 0.88, 'bert-v1.0', 42),
--     ('Normal, nada de especial', 'neutral', 0.72, 'bert-v1.0', 38);

-- ============================================
-- Permissões
-- ============================================

-- Garantir permissões para o usuário sentibr_user
GRANT ALL PRIVILEGES ON SCHEMA predictions TO sentibr_user;
GRANT ALL PRIVILEGES ON SCHEMA feedback TO sentibr_user;
GRANT ALL PRIVILEGES ON SCHEMA metrics TO sentibr_user;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA predictions TO sentibr_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA feedback TO sentibr_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA metrics TO sentibr_user;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA predictions TO sentibr_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA feedback TO sentibr_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA metrics TO sentibr_user;

-- ============================================
-- Logs
-- ============================================
\echo 'SentiBR database initialized successfully!'
\echo 'Schemas created: predictions, feedback, metrics'
\echo 'User: sentibr_user'
\echo 'Database: sentibr'
