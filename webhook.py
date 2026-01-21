from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhook")
async def mercado_pago(request: Request):
    data = await request.json()
    print("Webhook recebido:", data)
    return {"status": "ok"}
