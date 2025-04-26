ABI = [
    {
        "inputs": [
        {
            "internalType": "address[]",
            "name": "users",
            "type": "address[]"
        },
        {
            "internalType": "address[]",
            "name": "tokens",
            "type": "address[]"
        },
        {
            "internalType": "uint256[]",
            "name": "amounts",
            "type": "uint256[]"
        },
        {
            "internalType": "bytes32[][]",
            "name": "proofs",
            "type": "bytes32[][]"
        }
    ],
    "name": "claim",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
    }
]

TokenABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    }
]