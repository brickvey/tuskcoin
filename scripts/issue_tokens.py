from scripts.helpful_scripts import get_account, get_contract


def issue_tokens():
    """You can call this function once you have deployed your TokenFarm contract to a live network
    and have users that have staked tokens.

    Note that it relies on get_contract, so be mindful to correctly configure your Token Farm contract
    into brownie-config.yaml as well as the contract_to_mock dict as described in the get_contract docstring
    Run this function with this command: `brownie run scripts/issue_tokens.py --network kovan`
        This function will:
            - Print your account address and deployed TokenFarm contract address to confirm that you're using the right ones
            - Call issueTokens on your deployed TokenFarm contract to issue the DAPP token reward to your users
    """
    account = get_account()
    print(f"Issue Tokens called by: {account}")
    biven_farm = get_contract("BivenFarm")
    print(f"BivenFarm contract called to issue tokens: {biven_farm}")
    tx = biven_farm.issueTokens({"from": account})
    tx.wait(1)


def main():
    issue_tokens()
