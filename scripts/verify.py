from brownie import BivenToken


def main():
    token = BivenToken.at("0xDf77F46003b4fE1DFE676F7960895f32A797DdF6")
    BivenToken.publish_source(token)
