#!/bin/bash
# 🧠 ML Model Training Script

echo "🤖 Training ML Models for Match Prediction..."
echo "=============================================="

echo "📊 Checking available training data..."
curl -s http://localhost:8001/api/stats | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Matches: {data.get(\"matches\", 0)}')
print(f'Team Stats: {data.get(\"team_stats\", 0)}')
print(f'Player Stats: {data.get(\"player_stats\", 0)}')
"

echo ""
echo "⚠️  Warning: Training may take several minutes depending on data size."
read -p "Do you want to continue? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting ML model training..."
    echo "Please wait..."
    
    # Train models and capture response
    response=$(curl -s -X POST http://localhost:8001/api/train-ml-models)
    
    # Check if training was successful
    if echo "$response" | grep -q "success.*true"; then
        echo "✅ ML models trained successfully!"
        echo ""
        echo "📈 Training Results:"
        echo "$response" | python3 -m json.tool
        
        echo ""
        echo "🎯 Models are now ready for predictions!"
        echo "Access the Match Prediction tab at http://localhost:3000"
    else
        echo "❌ Training failed. Response:"
        echo "$response" | python3 -m json.tool
        echo ""
        echo "🔍 Check backend logs for details:"
        echo "tail -f /var/log/supervisor/backend.*.log"
    fi
else
    echo "Training cancelled."
fi

echo ""
echo "🔄 To check model status anytime:"
echo "curl -X GET http://localhost:8001/api/ml-models/status"