from flask import Blueprint
account_api = Blueprint('account_api', __name__)
@account_api.route("/")
def accountList():
    return "list of accounts"