from scripts.helpful_scripts import get_account, get_contract
from brownie import BivenToken, BivenFarm, network, config
from web3 import Web3
import yaml
import json
import os
import shutil

# probably gonna safe 80%
KEPT_BALANCE = Web3.toWei(40000000000, "ether")

# probably will need to split biven_farm and biven_token
def deploy_biven_farm_and_biven_token(front_end_update=False):
    account = get_account()
    biven_token = (BivenToken.deploy({"from": account}),)
    tx = biven_token.transfer(
        biven_farm.address, biven_token.totalSupply() - KEPT_BALANCE, {"from": account}
    )
    tx.wait(1)

    # split
    biven_farm = BivenFarm.deploy(
        biven_token.address,
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    tx = biven_token.transfer(
        biven_farm.address, biven_token.totalSupply() - KEPT_BALANCE, {"from": account}
    )
    tx.wait(1)

    # biven_token, weth_token/(wbnb_token), fau_token/(any other)
    # weth_token = get_contract("weth_token")
    # dai_token = get_contract("dai_token")
    wbnb_token = get_contract("wbnb_token")
    doge_token = get_contract("doge_token")
    dict_of_allowed_tokens = {
        biven_token: get_contract("bnb_usd_price_feed"),
        # dai_token: get_contract("dai_usd_price_feed"),
        # weth_token: get_contract("eth_usd_price_feed"),
        wbnb_token: get_contract("bnb_usd_price_feed"),
        doge_token: get_contract("doge_usd_price_feed"),
    }

    add_allowed_tokens(biven_farm, dict_of_allowed_tokens, account)
    if front_end_update:
        update_front_end()
    return biven_farm, biven_token


def add_allowed_tokens(biven_farm, dict_of_allowed_tokens, account):
    for token in dict_of_allowed_tokens:
        add_tx = biven_farm.addAllowedTokens(token.address, {"from": account})
        add_tx.wait(1)
        set_tx = biven_farm.setPriceFeedContract(
            token.address, dict_of_allowed_tokens[token], {"from": account}
        )
        set_tx.wait(1)
    return biven_farm


def update_front_end():
    # Send a builde folder
    copy_folders_to_front_end("./build/", "../front_end/src/chain-info")

    # sending the front end our config in json format
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open("../front_end/src/brownie-config.json", "w") as brownie_config_json:
            json.dump(config_dict, brownie_config_json)
    print("Front end updated")


def copy_folders_to_front_end(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def main():
    deploy_biven_farm_and_biven_token(front_end_update=True)
