#!/bin/bash
# 🚀 Soccer ML Prediction Platform - Quick Start Script

echo "⚽ Starting Soccer ML Prediction Platform..."
echo "======================================================"

# Check if services are running
echo "📋 Checking service status..."
sudo supervisorctl status

echo ""
echo "🔧 System Information:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8001"
echo "- API Docs: http://localhost:8001/docs"

echo ""
echo "🤖 ML Model Status Check..."
curl -s http://localhost:8001/api/ml-models/status | python3 -m json.tool

echo ""
echo "📚 Next Steps:"
echo "1. Access the platform at http://localhost:3000"
echo "2. Upload your match data (if not done already)"
echo "3. Train ML models in the Match Prediction tab"
echo "4. Start making predictions!"

echo ""
echo "🆘 If you encounter issues:"
echo "- Check logs: tail -f /var/log/supervisor/backend.*.log"
echo "- Restart services: sudo supervisorctl restart all"
echo "- Review startup guide: cat /app/STARTUP_GUIDE.md"

echo ""
echo "✅ Platform ready! Happy predicting! ⚽🤖"