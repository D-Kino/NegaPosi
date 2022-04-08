from application import db
from sqlalchemy.dialects.mysql import INTEGER as Integer
from sqlalchemy.dialects.mysql import TINYINT as Tinyint

class Game(db.Model):
    __tablename__ = 'game'

    appid             = db.Column(Integer(unsigned=True), primary_key=True)
    name              = db.Column(db.String(256), nullable=False)
    review_score      = db.Column(Tinyint(unsigned=True), nullable=True)
    review_score_desc = db.Column(db.String(128), nullable=True)
    total_positive    = db.Column(Integer(unsigned=True), nullable=True)
    total_negative    = db.Column(Integer(unsigned=True), nullable=True)
    total_reviews     = db.Column(Integer(unsigned=True), nullable=True)
    
    def selectGame () :
        games = db.session.query(Game).filter(Game.appid > 648580).order_by(Game.appid.asc()).all()
        return games
    
    def selectGameByAppId (id) :
        game = db.session.query(Game).filter_by(appid=id).first()
        return game
    
    def insertGame (games) :
        """
        ゲーム情報の登録
        """
        db.session.add_all(games)
        db.session.commit()
    
    def updateReview (id, review):
        """
        レビュー情報の更新
        """
        game = Game.selectGameByAppId(id)
        game.review_score = review["review_score"]
        game.review_score_desc = review["review_score_desc"]
        game.total_positive = review["total_positive"]
        game.total_negative = review["total_negative"]
        game.total_reviews = review["total_reviews"]
        db.session.commit()