from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    get_contract,
    INITIAL_PRICE_FEED_VALUE,
    DECIMALS,
)
from brownie import network, exceptions
import pytest
from scripts.deploy import deploy_biven_farm_and_biven_token, KEPT_BALANCE


def test_set_price_feed_contract():
    # Arrange
    if network.show_active not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip
        print("Only for local testing")
    account = get_account()
    non_owner = get_account(index=1)
    biven_farm, biven_token = deploy_biven_farm_and_biven_token()
    # Act
    price_feed_address = get_contract("bnb_usd_price_feed")
    biven_farm.setPriceFeedContract(
        biven_token.address, price_feed_address, {"from": account}
    )
    # Assert
    assert biven_farm.tokenPriceFeedMapping(biven_token.address) == price_feed_address
    with pytest.raises(exceptions.VirtualMachineError):
        biven_farm.setPriceFeedContract(
            biven_token.address, price_feed_address, {"from": non_owner}
        )


def test_stake_tokens(amount_staked):
    # Arrange
    if network.show_active not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip
        print("Only for local testing")
    account = get_account()
    biven_farm, biven_token = deploy_biven_farm_and_biven_token()
    # Act
    biven_token.approve(biven_farm.address, amount_staked, {"from": account})
    biven_farm.stakeTokens(amount_staked, biven_token.address, {"from": account})
    # Assert
    assert (
        biven_farm.stakingBalance(biven_token.address, account.address) == amount_staked
    )
    assert biven_farm.uniqueTokensStaked(account.address) == 1
    assert biven_farm.stakers(0) == account.address
    return biven_farm, biven_token


def test_issues_tokens(amount_staked):
    # Arrange
    if network.show_active not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip
        print("Only for local testing")
    account = get_account()
    biven_farm, biven_token = test_stake_tokens(amount_staked)
    starting_balance = biven_token.balanceOf(account.address)
    # Act
    biven_farm.issueTokens({"from": account})
    # Arrange
    assert (
        biven_token.balanceOf(account.address)
        == starting_balance + INITIAL_PRICE_FEED_VALUE
    )


def test_get_user_total_value_with_different_tokens(amount_staked, random_erc20):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip
        print("Only for local testing!")
    account = get_account()
    biven_farm, biven_token = test_stake_tokens(amount_staked)
    # Act
    biven_farm.addAllowedTokens(random_erc20.address, {"from": account})
    biven_farm.setPriceFeedContract(
        random_erc20.address, get_contract("bnb_usd_price_feed"), {"from": account}
    )
    random_erc20_stake_amount = amount_staked * 2
    random_erc20.approve(
        biven_farm.address, random_erc20_stake_amount, {"from": account}
    )
    biven_farm.stakeTokens(
        random_erc20_stake_amount, random_erc20.address, {"from": account}
    )
    # Assert
    total_value = biven_farm.getUserTotalValue(account.address)
    assert total_value == INITIAL_PRICE_FEED_VALUE * 3


def test_get_token_value():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip
        print("Only for local testing!")
    biven_farm, biven_token = deploy_biven_farm_and_biven_token()
    # Act / Assert
    assert biven_farm.getTokenValue(biven_token.address) == (
        INITIAL_PRICE_FEED_VALUE,
        DECIMALS,
    )


def test_unstake_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip
        print("Only for local testing!")
    account = get_account()
    biven_farm, biven_token = test_stake_tokens(amount_staked)
    # Act
    biven_farm.unstakeTokens(biven_token.address, {"from": account})
    assert biven_token.balanceOf(account.address) == KEPT_BALANCE
    assert biven_farm.stakingBalance(biven_token.address, account.address) == 0
    assert biven_farm.uniqueTokensStaked(account.address) == 0


def test_add_allowed_tokens():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip
        print("Only for local testing!")
    account = get_account()
    non_owner = get_account(index=1)
    biven_farm, biven_token = deploy_biven_farm_and_biven_token()
    # Act
    biven_farm.addAllowedTokens(biven_token.address, {"from": account})
    # Assert
    assert biven_farm.allowedTokens(0) == biven_token.address
    with pytest.raises(exceptions.VirtualMachineError):
        biven_farm.addAllowedTokens(biven_token.address, {"from": non_owner})
