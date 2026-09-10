from app.services.model_worker_client import ModelWorkerClient

client = ModelWorkerClient(
    ip_address="10.151.15.9",
    port=11434,
    protocol="http",
    is_ollama=True
)

health = client.check_health()
print(f"Health: {health}")

response = client.generate(
    model="llama3.2:1b",
    messages=[{"role": "user", "content": "Explain in one sentence what a refinery is."}]
)
print(f"Response: {response}")
