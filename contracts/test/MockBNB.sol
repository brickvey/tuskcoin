pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockBNB is ERC20 {
    constructor() public ERC20("Mock BNB", "BNB") {}
}