from application import app, db, manager
from flask_script import Server, Command
from www import *
import os
import sys
import requests
import configparser
import json
import requests
import time
import re
import glob
from pprint import pprint
from common.models.game import Game
from common.models.review import Review

# web server
manager.add_command("runserver", Server(host = "0.0.0.0", use_debugger=True, use_reloader=True))

# create tables
@Command
def create_all():
    """
    テーブルの作成
    """
    db.create_all()

@Command
def get_game():
    """
    STEAMのAPIよりゲーム情報を取得する
    """
    
    # 設定ファイルのパスを取得
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_steam_api = os.path.join(base_path, "config/steam_api.ini")
    config_file = os.path.join(base_path, "config/file.ini")
    
    # configparserの宣言とiniファイルの読み込み
    config_steam_api_ini = configparser.ConfigParser()
    config_file_ini = configparser.ConfigParser()
    config_steam_api_ini.read(config_steam_api, encoding="utf-8")
    config_file_ini.read(config_file, encoding="utf-8")

    # APIでゲーム情報の取得
    response = requests.get(config_steam_api_ini["URL"]["ISteamApps"])

    # HTTP200ではなかったらエラー終了
    if response.status_code != 200:
        print("Error: http error %d" %(response.status_code), file=sys.stderr)
        sys.exit(1)

    # 書き込むファイルのパスを宣言する
    output_file_path = os.path.join(base_path, "static/" + config_file_ini["AppList"]["FileName"])
    try:
        file = open(output_file_path, "w", encoding="utf-8")
        file.write(response.text)
    except Exception as e:
        print(e)
    finally:
        file.close()
        
@Command
def get_review():
    """
    STEAMのAPIより口コミ情報を取得する
    """
    
    # 設定ファイルのパスを取得
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_steam_api = os.path.join(base_path, "config/steam_api.ini")
    config_file = os.path.join(base_path, "config/file.ini")
    
    # configparserの宣言とiniファイルの読み込み
    config_steam_api_ini = configparser.ConfigParser()
    config_file_ini = configparser.ConfigParser()
    config_steam_api_ini.read(config_steam_api, encoding="utf-8")
    config_file_ini.read(config_file, encoding="utf-8")

    # DBからゲーム情報を取得
    games = Game.selectGame()
    for game in games:
        get_cnt = 1
        request_parameter = {
            "json": "1",
            "filter": "updated",
            "language": "japanese",
            "day_range": "all",
            "cursor": "*",
            "review_type":"all",
            "purchase_type":"all",
            "num_per_page":"100"
        }
        while True:
            # APIで口コミ情報の取得
            response = requests.get(config_steam_api_ini["URL"]["AppReviews"] + "/" + str(game.appid), params=request_parameter, allow_redirects=False)
            print(response.url)
            
            # HTTP200ではなかったらエラー終了
            if response.status_code != 200:
                print("Error: http error %d" %(response.status_code), file=sys.stderr)
                sys.exit(1)
                
            # json文字列を辞書型に変換
            json_review_dict = json.loads(response.text)
            
            # 次のセットのcursorがない場合は処理を抜ける
            if json_review_dict["query_summary"]["num_reviews"] == 0:
                break
            request_parameter["cursor"] = json_review_dict["cursor"]
            
            # 出力先のフォルダを作成
            game_name = re.sub(r'[\\|/|:|?|.|"|\'|<|>|\|*|™|®]', "-", game.name)
            output_path = os.path.join(base_path, "static/" + str(game.appid) + "_" + game_name)
            output_path = output_path[:64].strip()
            if not os.path.isdir(output_path):
                os.mkdir(output_path)
                
            # 書き込むファイルのパスを宣言する
            output_file_path = output_path + "/" + str(game.appid) + "_" + request_parameter["language"] + "_" + str(get_cnt) + "_" + \
                config_file_ini["ReviewList"]["FileName"]
            try:
                file = open(output_file_path, "w", encoding="utf-8")
                file.write(response.text)
            except Exception as e:
                print(e)
            finally:
                file.close()
                
            get_cnt += 1

@Command
def ins_game():
    """
    ゲーム情報（JSON）からDBに登録する
    """
    
    # 設定ファイルの読み込み
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(base_path, "config/file.ini")
    config_file_ini = configparser.ConfigParser()
    config_file_ini.read(config_file, encoding="utf-8")
    
    # ファイルの存在チェック
    if not os.path.exists(os.path.join(base_path, "static/" + config_file_ini["AppList"]["FileName"])) :
        print("AppListファイルが見つかりません。")
        sys.exit
        
    # json読み込み
    json_file = open(os.path.join(base_path, "static/" + config_file_ini["AppList"]["FileName"]), encoding="utf-8")
    json_game_dict = json.load(json_file)
    
    games = []
    for apps in json_game_dict["applist"]["apps"]:
        # 登録済の場合処理をスキップ
        game = Game.selectGameByAppId(apps["appid"])
        if game is not None :
            continue
        games.append(Game(
            appid = apps["appid"],
            name  = apps["name"]
        ))
    # ゲーム情報を登録する
    Game.insertGame(games)

@Command
def ins_review():
    """
    口コミ情報（JSON）からDBに登録する
    """    
    # 設定ファイルの読み込み
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(base_path, "config/file.ini")
    config_file_ini = configparser.ConfigParser()
    config_file_ini.read(config_file, encoding="utf-8")
        
    # DBからゲーム情報を取得
    games = Game.selectGame()
    for game in games:
        # ゲームフォルダを検索
        game_name = re.sub(r'[\\|/|:|?|.|"|\'|<|>|\|*|™|®]', "-", game.name)
        output_path = os.path.join(base_path, "static/" + str(game.appid) + "_" + game_name)
        output_path = output_path[:64].strip()
        
        # フォルダが存在しなければ処理をスキップ
        if not os.path.isdir(output_path):
            continue
        
        # レビューリストを検索
        files = sorted(glob.glob(output_path + "/*" + config_file_ini["ReviewList"]["FileName"]), key=natural_keys)
        
        # ファイルが存在しなければ処理をスキップ
        if not files:
            continue
        
        for i, file in enumerate(files):
            # json読み込み
            json_file = open(file, encoding="utf-8")
            json_review_dict = json.load(json_file)
            
            # 先頭ファイルからレビュー情報を取得し、ゲーム情報を更新
            if i == 0:
                Game.updateReview(game.appid, json_review_dict["query_summary"])
            
            reviews = []
            for review in json_review_dict["reviews"]:
                # キーの存在チェック
                try :
                    review["author"]["playtime_at_review"]
                except KeyError:
                    review["author"]["playtime_at_review"] = 0
                
                # レビュー情報の登録
                reviews.append(Review(
                    recommendationid            = review["recommendationid"],
                    appid                       = game.appid,
                    steamid                     = review["author"]["steamid"],
                    language                    = review["language"],
                    review                      = review["review"],
                    timestamp_created           = review["timestamp_created"],
                    timestamp_updated           = review["timestamp_updated"],
                    voted_up                    = review["voted_up"],
                    votes_up                    = review["votes_up"],
                    votes_funny                 = review["votes_funny"],
                    weighted_vote_score         = review["weighted_vote_score"],
                    comment_count               = review["comment_count"],
                    steam_purchase              = review["steam_purchase"],
                    received_for_free           = review["received_for_free"],
                    written_during_early_access = review["written_during_early_access"],
                    num_games_owned             = review["author"]["num_games_owned"],
                    num_reviews                 = review["author"]["num_reviews"],
                    playtime_forever            = review["author"]["playtime_forever"],
                    playtime_last_two_weeks     = review["author"]["playtime_last_two_weeks"],
                    playtime_at_review          = review["author"]["playtime_at_review"],
                    last_played                 = review["author"]["last_played"]
                ))
                
            # レビュー情報を登録する
            try:
                Review.insertReview(reviews)
            finally:
                pass
            print(str(game.appid) + "_" + game.name + " " + str(len(reviews)) + "件登録")


@Command
def upd_votes():
    """
    口コミ情報（JSON）からDBに登録する
    """    
    # 設定ファイルの読み込み
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(base_path, "config/file.ini")
    config_file_ini = configparser.ConfigParser()
    config_file_ini.read(config_file, encoding="utf-8")
        
    # DBからゲーム情報を取得
    games = Game.selectGame()
    for game in games:
        # ゲームフォルダを検索
        game_name = re.sub(r'[\\|/|:|?|.|"|\'|<|>|\|*|™|®]', "-", game.name)
        output_path = os.path.join(base_path, "static/" + str(game.appid) + "_" + game_name)
        output_path = output_path[:64].strip()
        
        # フォルダが存在しなければ処理をスキップ
        if not os.path.isdir(output_path):
            continue
        
        # レビューリストを検索
        files = sorted(glob.glob(output_path + "/*" + config_file_ini["ReviewList"]["FileName"]), key=natural_keys)
        
        # ファイルが存在しなければ処理をスキップ
        if not files:
            continue
        
        for i, file in enumerate(files):
            # json読み込み
            json_file = open(file, encoding="utf-8")
            json_review_dict = json.load(json_file)
            
            for review in json_review_dict["reviews"]:
                # レビュー情報を登録する
                Review.updateReview(game.appid, review) 
                print(game.name + " " + review["recommendationid"])
                     
        
manager.add_command("create_all", create_all)
manager.add_command("get_game", get_game)
manager.add_command("get_review", get_review)
manager.add_command("ins_game", ins_game)
manager.add_command("ins_review", ins_review)
manager.add_command("upd_votes", upd_votes)

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def main():
    manager.run()

if __name__ == "__main__":
    # app.run( host = "0.0.0.0" )

    try:
        import sys
        sys.exit( main() )
    except Exception as e:
        import traceback
        traceback.print_exc()