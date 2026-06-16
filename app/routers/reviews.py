from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models, auth
from ..database import get_db

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/", response_model=schemas.Review)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    trip = db.query(models.Trip).filter(models.Trip.id == review.trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if current_user.id == review.to_user_id:
        raise HTTPException(status_code=400, detail="Cannot review yourself")
    current_participant = db.query(models.TripApplication).filter(
        models.TripApplication.trip_id == review.trip_id,
        models.TripApplication.user_id == current_user.id,
        models.TripApplication.status == "accepted"
    ).first()
    to_participant = db.query(models.TripApplication).filter(
        models.TripApplication.trip_id == review.trip_id,
        models.TripApplication.user_id == review.to_user_id,
        models.TripApplication.status == "accepted"
    ).first()
    if (not current_participant and trip.created_by != current_user.id) or (not to_participant and trip.created_by != review.to_user_id):
        raise HTTPException(status_code=403, detail="Both users must be participants of the trip")
    existing = db.query(models.Review).filter(
        models.Review.from_user_id == current_user.id,
        models.Review.to_user_id == review.to_user_id,
        models.Review.trip_id == review.trip_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Review already given")
    db_review = models.Review(
        from_user_id=current_user.id,
        to_user_id=review.to_user_id,
        trip_id=review.trip_id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@router.get("/user/{user_id}", response_model=List[schemas.Review])
def get_reviews_for_user(user_id: int, db: Session = Depends(get_db)):
    reviews = db.query(models.Review).filter(models.Review.to_user_id == user_id).all()
    return reviews