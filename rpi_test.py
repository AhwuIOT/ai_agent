import requests
import time

# Send prompt to model
def send_prompt(prompt: str):
    url = "http://192.168.1.188:5000/ask"
    response = requests.post(url, json={"prompt": prompt})
    if response.status_code == 200:
        job_id = response.json()["job_id"]
        print(f"Task submitted. Job ID: {job_id}")
        return job_id
    else:
        raise Exception(f"Request failed: {response.text}")

# Poll result from model
def fetch_result(job_id: str, max_wait: int = 30):
    url = f"http://192.168.1.188:5000/result/{job_id}"
    for i in range(max_wait):
        res = requests.get(url)
        data = res.json()
        if data["status"] == "done":
            print(f"Answer received: {data['result']}")
            return
        elif data["status"] == "failed":
            print("Task failed.")
            return
        else:
            print(f"Waiting... ({i + 1} sec)")
            time.sleep(1)
    print("Timeout. Please try again later.")

# Test flow
if __name__ == "__main__":
    prompt = "可以跑中文嗎?"
    job_id = send_prompt(prompt)
    fetch_result(job_id)
