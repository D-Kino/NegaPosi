from application import db
from sqlalchemy.dialects.mysql import TINYINT as Tinyint
from sqlalchemy.dialects.mysql import BIGINT as BigInt
from sqlalchemy.dialects.mysql import FLOAT as float
from sqlalchemy.dialects.mysql import TEXT as Text
from sqlalchemy.dialects.mysql import DATETIME as DateTime
from sqlalchemy.dialects.mysql import BOOLEAN as Boolean

class Review(db.Model):
    __tablename__ = 'review'

    recommendationid            = db.Column(BigInt, primary_key=True)
    appid                       = db.Column(db.Integer, primary_key=True)
    steamid                     = db.Column(BigInt, nullable=False)
    language                    = db.Column(db.String(64), nullable=False)
    review                      = db.Column(Text, nullable=False)
    timestamp_created           = db.Column(DateTime, nullable=False)
    timestamp_updated           = db.Column(DateTime, nullable=False)
    voted_up                    = db.Column(Boolean, nullable=False)
    votes_up                    = db.Column(db.Integer, nullable=False)
    votes_funny                 = db.Column(db.Integer, nullable=False)
    weighted_vote_score         = db.Column(float, nullable=False)
    comment_count               = db.Column(db.Integer, nullable=False)
    steam_purchase              = db.Column(Tinyint, nullable=False)
    received_for_free           = db.Column(Tinyint, nullable=False)
    written_during_early_access = db.Column(Tinyint, nullable=False)
    num_games_owned             = db.Column(db.Integer, nullable=False)
    num_reviews                 = db.Column(db.Integer, nullable=False)
    playtime_forever            = db.Column(db.Integer, nullable=False)
    playtime_last_two_weeks     = db.Column(db.Integer, nullable=False)
    playtime_at_review          = db.Column(db.Integer, nullable=False)
    last_played                 = db.Column(DateTime, nullable=False)
    
    def selectReviewById (id) :
        review = db.session.query(Review).filter_by(appid=id).first()
        return review
    
    def insertReview (reviews) :
        """
        口コミ情報の登録
        """
        db.session.add_all(reviews)
        db.session.commit()
        
    def updateReview (appid, re):
        """
        レビュー情報の更新
        """
        review = Review.selectReviewById(appid)
        review.voted_up = re["voted_up"]
        review.votes_up = re["votes_up"]
        db.session.commit()        