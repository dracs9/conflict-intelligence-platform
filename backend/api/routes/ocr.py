"""
OCR API Routes
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import ConflictSession, DialogueTurn
from services.ocr_service import OCRService
import main

router = APIRouter()

ocr_service = OCRService()

@router.post("/upload-screenshot")
async def upload_screenshot(
    user_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload chat screenshot and extract dialogue
    Creates a new session with extracted turns
    """
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read image bytes
    image_bytes = await file.read()
    
    # Process with OCR
    try:
        extracted_turns = ocr_service.process_chat_screenshot(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
    
    if not extracted_turns:
        raise HTTPException(status_code=400, detail="No text found in image")
    
    # Create session
    session = ConflictSession(
        user_id=user_id,
        session_name=f"Screenshot Upload {file.filename}"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Process and save turns
    processed_turns = []
    for turn_data in extracted_turns:
        # Analyze turn
        analysis = main.conflict_analyzer.analyze_turn(turn_data["text"], turn_data["speaker"])
        
        # Save turn
        turn = DialogueTurn(
            session_id=session.id,
            turn_id=turn_data["turn_id"],
            speaker=turn_data["speaker"],
            text=turn_data["text"],
            sentiment=analysis["sentiment"]["label"],
            sentiment_score=analysis["sentiment"]["score"],
            aggression_score=analysis["aggression_score"],
            passive_aggression_score=analysis["passive_aggression_score"],
            conflict_score=analysis["conflict_score"],
            bias_tags=analysis["bias_tags"]
        )
        db.add(turn)
        
        processed_turns.append({
            "turn_id": turn.turn_id,
            "speaker": turn.speaker,
            "text": turn.text,
            "analysis": analysis
        })
    
    db.commit()
    
    return {
        "session_id": session.id,
        "session_name": session.session_name,
        "extracted_turns": len(extracted_turns),
        "turns": processed_turns
    }

@router.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    """Simple text extraction from image"""
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    image_bytes = await file.read()
    
    try:
        text = ocr_service.extract_text_simple(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")
    
    return {
        "extracted_text": text,
        "character_count": len(text)
    }
