from fastapi import FastAPI, BackgroundTasks 
import time
import uuid
app = FastAPI()
# Simple in‐memory storage for job status
jobs = {}
def process_video(job_id, video_name):
    jobs[job_id] = "processing" 
    print(f"Processing video: {video_name}")
    time.sleep(10) # simulate long task jobs[job_id] = "finished"
    print(f"Finished processing: {video_name}") 
@app.get("/start")
async def start_job(video_name: str, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4()) # Generate a unique ID for the job 
    jobs[job_id] = "queued"
    background_tasks.add_task(process_video, job_id, video_name)
    return {
        "message": "Job started",
        "job_id": job_id,
        "check_status": f"/status/{job_id}"
    } 
@app.get("/status/{job_id}")
async def check_status(job_id: str):
    status = jobs.get(job_id, "job not found")
    return {
        "job_id": job_id, "status": status
    }