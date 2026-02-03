from fastapi import FastAPI, Request, Response
import asyncio

app = FastAPI()
relay_conn = {"writer": None}

@app.get("/")
async def yemot_api(request: Request):
    params = request.query_params
    duration_minutes = params.get("time") # משך הזמן בדקות
    
    # בדיקה אם הממסר מחובר לשרת
    if relay_conn["writer"] is None:
        # הודעה למתקשר במידה והמכשיר לא מחובר לאינטרנט
        return Response(content="id_list_message=t-תקלה. הממסר אינו מחובר לשרת.", media_type="text/plain")

    if not duration_minutes:
        return Response(content="id_list_message=t-שגיאה. לא התקבל משך זמן.", media_type="text/plain")

    try:
        # המרה לשניות עבור הממסר
        minutes_int = int(duration_minutes)
        seconds = minutes_int * 60
        
        # פקודה להדלקת ממסר 1 לזמן קצוב (לפי ה-VB שמצאנו: 11:שניות)
        command = f"11:{seconds}"
        
        relay_conn["writer"].write(command.encode())
        await relay_conn["writer"].drain()
        
        # יצירת הטקסט שהמרכזייה תקריא למתקשר
        text_to_say = f"התאורה הופעלה בהצלחה ל {minutes_int} דקות"
        if minutes_int == 1:
            text_to_say = "התאורה הופעלה לדקה אחת"
            
        # החזרת הפקודה לימות המשיח (השמעת הודעה וסיום שיחה)
        return Response(content=f"id_list_message=t-{text_to_say}&say_bye=yes", media_type="text/plain")

    except ValueError:
        return Response(content="id_list_message=t-נתון לא תקין.", media_type="text/plain")

# ניהול החיבור מהממסר (TCP)
async def handle_relay(reader, writer):
    relay_conn["writer"] = writer
    print("הממסר (SR-201) מחובר כעת.")
    try:
        while True:
            data = await reader.read(100)
            if not data: break
    finally:
        relay_conn["writer"] = None
        print("הממסר התנתק.")

@app.on_event("startup")
async def startup():
    # פתיחת הפורט לממסר (6722)
    server = await asyncio.start_server(handle_relay, '0.0.0.0', 6722)
    asyncio.create_task(server.serve_forever())