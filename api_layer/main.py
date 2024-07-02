from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import markdown
import re
from assistant.processes.free_recall.base import FreeRecallAssistant

app = FastAPI()

# Mount the static files
app.mount("/static", StaticFiles(directory="api_layer/static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="api_layer/static")

@app.get("/")
def read_root(request: Request):

    user_id = '1'
    topic = '1'
    user_topic_key = '1_1_2'
    assistant = FreeRecallAssistant(user_id=user_id, topic=topic)

    try:
        json_item = assistant._get_latest_user_topic_data(
            table_name='FreeRecallData',
            user_topic_key=user_topic_key
        )
        
        weaknesses = re.split(r"\d+\.-", json_item['json_guidelines']['weaknesses'])

        weaknesses = [
            item.strip() for item in weaknesses if item
        ]

    except Exception as e:

        print(f"Error fetching guidelines: {e}")
        json_item = {
            'json_guidelines': {
                'weaknesses': "Try to get your best!",
                'strengths': ""
            }
        }

        weaknesses = [json_item['json_guidelines']['weaknesses']]

    context = {
        "request":  request,
        "weaknesses": weaknesses,
        "strengths": json_item['json_guidelines']['strengths']
    }

    return templates.TemplateResponse(
        "free_recall_form.html",
        context
        )

@app.get("/create_topic")
def create_topic():
    return {"message": "Create a new topic"}

@app.post("/submit")
async def submit_form(title: str = Form(...), document: str = Form(...)):

    # Process the submitted data
    assistant = FreeRecallAssistant(user_id='1', topic=title)

    redefined_document, feedback_md = assistant.first_step(user_content=document)

    guidelines = assistant.third_step(redefined_document)

    print('New Guidelines:', guidelines)
    assistant.push_guidelines()

    # convert the response markdown to html
    html_content = markdown.markdown(feedback_md)
    
    return {"html_content": html_content}

@app.get("/feedback")
def thank_you(request: Request):
    # Render a thank you page template, or return a simple JSON message
    # return templates.TemplateResponse("thank_you.html", {"request": request})
    return {"message": "Thank you for your submission!"}