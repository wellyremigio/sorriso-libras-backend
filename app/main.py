from fastapi import FastAPI

app = FastAPI(
    title="Sorriso Libras API",
    description="API do aplicativo Sorriso Libras",
    version= "1.0.0",
)

@app.get("/")
def read_root():
    return {
        "message": "API Sorriso libras funcionando!"
    }
    
    
@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }