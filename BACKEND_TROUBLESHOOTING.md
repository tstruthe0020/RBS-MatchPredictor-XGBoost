# Backend Connection Troubleshooting

## 🔍 **Let's Diagnose the Issue Step by Step**

The backend might be crashing silently after startup. Let's find out what's happening.

## Step 1: Check if Python Process is Still Running

After starting the backend with `python server.py`, check if the process is still running:

### Windows (PowerShell):
```powershell
# Check if Python is running on port 8001
netstat -ano | findstr :8001

# Check all Python processes
tasklist | findstr python
```

### What to Look For:
- **If you see a line with `:8001` and `LISTENING`** = Good, server is running
- **If you see nothing** = Server crashed or isn't binding to port

## Step 2: Add More Detailed Logging

Let's modify the server startup to see exactly where it fails. Please replace the bottom of your `server.py` file with this:

```python
if __name__ == "__main__":
    import uvicorn
    print("Starting Football Analytics API Server...")
    print("Checking imports...")
    
    try:
        print("Testing app initialization...")
        print(f"App routes: {len(app.routes)} routes loaded")
        print("Starting Uvicorn server...")
        uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
    except Exception as e:
        print(f"ERROR starting server: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")  # Keep window open to see error
```

## Step 3: Alternative Startup Method

If the above doesn't work, try starting the server using uvicorn directly:

```bash
cd C:\Users\theos\RBS-MatchPredictor-XGBoost\backend
uvicorn server:app --host 0.0.0.0 --port 8001
```

## Step 4: Check for Port Conflicts

Maybe something else is using port 8001:

```powershell
# Check what's using port 8001
netstat -ano | findstr :8001

# Try a different port (8000):
# In server.py, change port to 8000, then test http://localhost:8000/docs
```

## Step 5: Test with Minimal Server

Create a test file `test_server.py` in the backend directory:

```python
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    print("Starting minimal test server...")
    uvicorn.run(app, host="0.0.0.0", port=8002)
```

Then run:
```bash
python test_server.py
```

And test: http://localhost:8002

## 🎯 **Next Steps:**

1. **First**: Try Step 1 to see if the process is running
2. **If not running**: Use Step 2 to add better error logging
3. **If still issues**: Try Step 3 (uvicorn command)
4. **If still failing**: Try Step 5 (minimal server test)

**Please run Step 1 first and let me know what you find!**