from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models, auth
from ..database import get_db

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/", response_model=schemas.Message)
def send_message(msg: schemas.MessageCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    trip = db.query(models.Trip).filter(models.Trip.id == msg.trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    is_participant = db.query(models.TripApplication).filter(
        models.TripApplication.trip_id == msg.trip_id,
        models.TripApplication.user_id == current_user.id,
        models.TripApplication.status == "accepted"
    ).first()
    if not is_participant and trip.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You are not a participant of this trip")
    receiver_participant = db.query(models.TripApplication).filter(
        models.TripApplication.trip_id == msg.trip_id,
        models.TripApplication.user_id == msg.receiver_id,
        models.TripApplication.status == "accepted"
    ).first()
    if not receiver_participant and trip.created_by != msg.receiver_id:
        raise HTTPException(status_code=400, detail="Receiver is not a participant")
    db_msg = models.Message(
        trip_id=msg.trip_id,
        sender_id=current_user.id,
        receiver_id=msg.receiver_id,
        content=msg.content
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return db_msg

@router.get("/trip/{trip_id}", response_model=List[schemas.Message])
def get_messages_for_trip(trip_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    is_participant = db.query(models.TripApplication).filter(
        models.TripApplication.trip_id == trip_id,
        models.TripApplication.user_id == current_user.id,
        models.TripApplication.status == "accepted"
    ).first()
    if not is_participant and trip.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not a participant")
    messages = db.query(models.Message).filter(models.Message.trip_id == trip_id).all()
    return messages