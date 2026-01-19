import os
import datetime
import time
import re
import json
from mobilerun import Mobilerun 

os.environ["MOBILERUN_API_KEY"] = "<YOUR_API_KEY>"

client = Mobilerun(
    api_key=os.environ.get("MOBILERUN_API_KEY") 
)

SOURCE_PATH = "/storage/0000-0000/DCIM/Camera"
DEST_STUDY = "/storage/0000-0000/Documents/StudyNotes" 

def open_image_on_screen(filepath):
    print(f"   Opening image...")
    cmd = f"adb shell am start -a android.intent.action.VIEW -d \"file://{filepath}\" -t \"image/*\""
    os.system(cmd)
    time.sleep(5) 

def close_image_on_screen():
    os.system("adb shell input keyevent 4")
    time.sleep(3)

def ask_mobilerun_classifier(client):
    prompt = """
    Analyze the center of the image. 
    IGNORE the black system bars, buttons (Share/Lens), and status icons at the top/bottom.
    
    Classify the MAIN CONTENT as 'STUDY' or 'OTHER'.

    RULE 1: IT IS 'STUDY' IF:
    - You see handwritten notes.
    - You see text written on whiteboard, blackboard, or a textbook page.

    RULE 2: IT IS 'OTHER' IF:
    - if it's main subject is a person's photo.
    - It is a photo of a crowd,

    and finally return only one word 'STUDY' or 'OTHER'
    """

    try:
        response = client.tasks.run(
            llm_model="google/gemini-3-flash", 
            task=prompt,
            vision=True,
            device_id = "93f0faca-cc95-4087-ac9b-4d0679eef0a9"
        )
        task_id = response.id
        
        for _ in range(20): 
            time.sleep(2)
            task_wrapper = client.tasks.retrieve(task_id)
            current_task = task_wrapper.task
            status = getattr(current_task, 'status', 'UNKNOWN').upper()
            if status == 'COMPLETED':
                print(f"   API Status: {status}")
                trajectory = getattr(current_task, 'trajectory', [])
                for event in reversed(trajectory):
                    event_name = event.get('event', '')
                    event_data = event.get('data', {})
                    if event_name in ['ResultEvent', 'FinalizeEvent']:
                        reason = event_data.get('reason', '')
                        print(f"   Found Result: {reason}")
                        if "STUDY" in str(reason).upper():
                            return "STUDY"
                        if "OTHER" in str(reason).upper():
                            return "OTHER"
                print("Could not find any result")
                return "OTHER"
        print("   Timed out waiting for API.")
        return "OTHER"

    except Exception as e:
        print(f"   API Error: {e}")
        return "ERROR"

def get_recent_photos():
    print(f"Scanning {SOURCE_PATH}...")
    today = datetime.datetime.now()
    cutoff_date = today - datetime.timedelta(days=30)
    try:
        output = os.popen(f"adb shell ls \"{SOURCE_PATH}\"").read()
    except Exception: return []
    files_to_process = []
    pattern = re.compile(r"IMG[-_](\d{8})") 
    for filename in output.split('\n'):
        filename = filename.strip()
        match = pattern.search(filename)
        if match:
            try:
                file_date = datetime.datetime.strptime(match.group(1), "%Y%m%d")
                if file_date > cutoff_date:
                    files_to_process.append(f"{SOURCE_PATH}/{filename}")
            except ValueError: continue
    
    return files_to_process

if __name__ == "__main__":
    print("STARTING AGENT (GEMINI 3 FLASH)")
    photos = get_recent_photos()
    if not photos:
        print("   No recent photos found.")
    else:
        print(f"   Found {len(photos)} photos. Processing first {len(photos)}...")
        os.system(f"adb shell mkdir -p {DEST_STUDY}")

        for full_path in photos[:len(photos)]:
            filename = os.path.basename(full_path)
            print(f"Processing: {filename}")
            
            try:
                open_image_on_screen(full_path)
                category = ask_mobilerun_classifier(client)
                category = str(category).strip().upper()
                
                close_image_on_screen()
                
                if category == "ERROR":
                    print("   Skipping due to API Error.")
                elif "STUDY" in category:
                    print(f"   Result: STUDY -> Moving file.")
                    os.system(f'adb shell mv "{full_path}" "{DEST_STUDY}/"')
                else:
                    print(f"   Result: OTHER -> Skipping.")
                
                time.sleep(1.5)

            except Exception as loop_error:
                print(f"   Unexpected Script Error: {loop_error}")
                continue 

        print("\n✅ Done.")