from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models, auth
from ..database import get_db

router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("/", response_model=schemas.TripApplication)
def create_application(app: schemas.TripApplicationCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    trip = db.query(models.Trip).filter(models.Trip.id == app.trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if trip.created_by == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot apply to your own trip")
    existing = db.query(models.TripApplication).filter(
        models.TripApplication.user_id == current_user.id,
        models.TripApplication.trip_id == app.trip_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Application already exists")
    db_app = models.TripApplication(user_id=current_user.id, trip_id=app.trip_id, comment=app.comment)
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

@router.get("/my", response_model=List[schemas.TripApplication])
def my_applications(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    apps = db.query(models.TripApplication).filter(models.TripApplication.user_id == current_user.id).all()
    return apps

@router.get("/for-trip/{trip_id}", response_model=List[schemas.TripApplication])
def applications_for_trip(trip_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if trip.created_by != current_user.id and current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only trip creator can view applications")
    apps = db.query(models.TripApplication).filter(models.TripApplication.trip_id == trip_id).all()
    return apps

@router.put("/{app_id}", response_model=schemas.TripApplication)
def update_application_status(app_id: int, status_update: schemas.TripApplicationUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    app = db.query(models.TripApplication).filter(models.TripApplication.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    trip = db.query(models.Trip).filter(models.Trip.id == app.trip_id).first()
    if not trip or (trip.created_by != current_user.id and current_user.role != models.UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Not allowed")
    app.status = status_update.status
    db.commit()
    db.refresh(app)
    return app