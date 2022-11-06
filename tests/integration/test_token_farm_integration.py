from brownie import network
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    get_contract,
)
from scripts.deploy import deploy_biven_farm_and_biven_token
import pytest


def test_stake_and_issue_correct_amounts(amount_staked):
    # Arrange
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip
        print("Only for integration testing!")
    biven_farm, biven_token = deploy_biven_farm_and_biven_token()
    account = get_account()
    biven_token.approve(biven_farm.address, amount_staked, {"from": account})
    biven_farm.stakeTokens(amount_staked, biven_token.address, {"from": account})
    starting_balance = biven_token.balanceOf(account.address)
    price_feed_contract = get_contract("doge_usd_price_feed")
    (_, price, _, _, _) = price_feed_contract.latestRoundData()
    # Stake 1 token
    # 1 Token = $2000
    # We should be issued, 2000 tokens
    amount_token_to_issue = (
        price / 10 ** price_feed_contract.decimals()
    ) * amount_staked
    # Act
    issue_tx = biven_farm.issueTokens({"from": account})
    issue_tx.wait(1)
    # Assert
    assert (
        biven_token.balanceOf(account.address)
        == amount_token_to_issue + starting_balance
    )
