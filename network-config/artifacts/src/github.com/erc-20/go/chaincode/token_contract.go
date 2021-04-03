package chaincode

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"strconv"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// Define key names for options
const totalSupplyKey = "totalSupply"

// Define objectType names for prefix
const allowancePrefix = "allowance"

// SmartContract provides functions for transferring tokens between accounts
type SmartContract struct {
	contractapi.Contract
}

// event provides an organized struct for emitting events
type event struct {
	From  string `json:"from"`
	To    string `json:"to"`
	Value int    `json:"value"`
}

type spentToken struct {
	Key   string `json:"key"`
}

// Mint creates new tokens and adds them to minter's account balance
// This function triggers a Transfer event
func (s *SmartContract) Mint(ctx contractapi.TransactionContextInterface, amount int) error {

	// Check minter authorization - this sample assumes Org1 is the central banker with privilege to mint new tokens
	clientMSPID, err := ctx.GetClientIdentity().GetMSPID()
	if err != nil {
		return fmt.Errorf("failed to get MSPID: %v", err)
	}
	if clientMSPID != "MSB1" {
		return fmt.Errorf("client is not authorized to mint new tokens")
	}

	// Get ID of submitting client identity
	minter, err := ctx.GetClientIdentity().GetID()
	if err != nil {
		return fmt.Errorf("failed to get client id: %v", err)
	}

	if amount <= 0 {
		return fmt.Errorf("mint amount must be a positive integer")
	}

	currentBalanceBytes, err := ctx.GetStub().GetState(minter)
	if err != nil {
		return fmt.Errorf("failed to read minter account %s from world state: %v", minter, err)
	}

	var currentBalance int

	// If minter current balance doesn't yet exist, we'll create it with a current balance of 0
	if currentBalanceBytes == nil {
		currentBalance = 0
	} else {
		currentBalance, _ = strconv.Atoi(string(currentBalanceBytes)) // Error handling not needed since Itoa() was used when setting the account balance, guaranteeing it was an integer.
	}

	updatedBalance := currentBalance + amount

	err = ctx.GetStub().PutState(minter, []byte(strconv.Itoa(updatedBalance)))
	if err != nil {
		return err
	}

	// Update the totalSupply
	totalSupplyBytes, err := ctx.GetStub().GetState(totalSupplyKey)
	if err != nil {
		return fmt.Errorf("failed to retrieve total token supply: %v", err)
	}

	var totalSupply int

	// If no tokens have been minted, initialize the totalSupply
	if totalSupplyBytes == nil {
		totalSupply = 0
	} else {
		totalSupply, _ = strconv.Atoi(string(totalSupplyBytes)) // Error handling not needed since Itoa() was used when setting the totalSupply, guaranteeing it was an integer.
	}

	// Add the mint amount to the total supply and update the state
	totalSupply += amount
	err = ctx.GetStub().PutState(totalSupplyKey, []byte(strconv.Itoa(totalSupply)))
	if err != nil {
		return err
	}

	// Emit the Transfer event
	transferEvent := event{"0x0", minter, amount}
	transferEventJSON, err := json.Marshal(transferEvent)
	if err != nil {
		return fmt.Errorf("failed to obtain JSON encoding: %v", err)
	}
	err = ctx.GetStub().SetEvent("Transfer", transferEventJSON)
	if err != nil {
		return fmt.Errorf("failed to set event: %v", err)
	}

	log.Printf("minter account %s balance updated from %d to %d", minter, currentBalance, updatedBalance)

	return nil
}

// Burn redeems tokens the minter's account balance
// This function triggers a Transfer event
func (s *SmartContract) Burn(ctx contractapi.TransactionContextInterface, amount int) error {

	// Check minter authorization - this sample assumes Org1 is the central banker with privilege to burn new tokens
	clientMSPID, err := ctx.GetClientIdentity().GetMSPID()
	if err != nil {
		return fmt.Errorf("failed to get MSPID: %v", err)
	}
	if clientMSPID != "Org1MSP" {
		return fmt.Errorf("client is not authorized to mint new tokens")
	}

	// Get ID of submitting client identity
	minter, err := ctx.GetClientIdentity().GetID()
	if err != nil {
		return fmt.Errorf("failed to get client id: %v", err)
	}

	if amount <= 0 {
		return errors.New("burn amount must be a positive integer")
	}

	currentBalanceBytes, err := ctx.GetStub().GetState(minter)
	if err != nil {
		return fmt.Errorf("failed to read minter account %s from world state: %v", minter, err)
	}

	var currentBalance int

	// Check if minter current balance exists
	if currentBalanceBytes == nil {
		return errors.New("The balance does not exist")
	}

	currentBalance, _ = strconv.Atoi(string(currentBalanceBytes)) // Error handling not needed since Itoa() was used when setting the account balance, guaranteeing it was an integer.

	updatedBalance := currentBalance - amount

	err = ctx.GetStub().PutState(minter, []byte(strconv.Itoa(updatedBalance)))
	if err != nil {
		return err
	}

	// Update the totalSupply
	totalSupplyBytes, err := ctx.GetStub().GetState(totalSupplyKey)
	if err != nil {
		return fmt.Errorf("failed to retrieve total token supply: %v", err)
	}

	// If no tokens have been minted, throw error
	if totalSupplyBytes == nil {
		return errors.New("totalSupply does not exist")
	}

	totalSupply, _ := strconv.Atoi(string(totalSupplyBytes)) // Error handling not needed since Itoa() was used when setting the totalSupply, guaranteeing it was an integer.

	// Subtract the burn amount to the total supply and update the state
	totalSupply -= amount
	err = ctx.GetStub().PutState(totalSupplyKey, []byte(strconv.Itoa(totalSupply)))
	if err != nil {
		return err
	}

	// Emit the Transfer event
	transferEvent := event{minter, "0x0", amount}
	transferEventJSON, err := json.Marshal(transferEvent)
	if err != nil {
		return fmt.Errorf("failed to obtain JSON encoding: %v", err)
	}
	err = ctx.GetStub().SetEvent("Transfer", transferEventJSON)
	if err != nil {
		return fmt.Errorf("failed to set event: %v", err)
	}

	log.Printf("minter account %s balance updated from %d to %d", minter, currentBalance, updatedBalance)

	return nil
}

// Transfer transfers tokens from client account to recipient account
// recipient account must be a valid clientID as returned by the ClientID() function
// This function triggers a Transfer event
func (s *SmartContract) Transfer(ctx contractapi.TransactionContextInterface, recipient string, amount int) error {

	// Get ID of submitting client identity
	clientID, err := ctx.GetClientIdentity().GetID()
	if err != nil {
		return fmt.Errorf("failed to get client id: %v", err)
	}

	err = transferHelper(ctx, clientID, recipient, amount)
	if err != nil {
		return fmt.Errorf("failed to transfer: %v", err)
	}

	// Emit the Transfer event
	transferEvent := event{clientID, recipient, amount}
	transferEventJSON, err := json.Marshal(transferEvent)
	if err != nil {
		return fmt.Errorf("failed to obtain JSON encoding: %v", err)
	}
	err = ctx.GetStub().SetEvent("Transfer", transferEventJSON)
	if err != nil {
		return fmt.Errorf("failed to set event: %v", err)
	}

	return nil
}


func (s *SmartContract) AddSpentToken(ctx contractapi.TransactionContextInterface, key string) error {
	token := spentToken{
		Key:   key,
	}

	tokenAsBytes, _ := json.Marshal(token)
	err := ctx.GetStub().PutState("DoubleSpend"+ key, tokenAsBytes)
	if err != nil {
		return fmt.Errorf("Failed to put to world state. %s", err.Error())
	}
	return nil
}

func (s *SmartContract) FindDoubleSpend(ctx contractapi.TransactionContextInterface, key string) (bool, error) {
	tokenAsBytes, err := ctx.GetStub().GetState(key)

	if err != nil {
		return false, fmt.Errorf("Failed to read from world state. %s", err.Error())
	}

	if tokenAsBytes == nil {
		return false, nil
	}

	return true, nil
}


// TotalSupply returns the total token supply
func (s *SmartContract) TotalSupply(ctx contractapi.TransactionContextInterface) (int, error) {

	// Retrieve total supply of tokens from state of smart contract
	totalSupplyBytes, err := ctx.GetStub().GetState(totalSupplyKey)
	if err != nil {
		return 0, fmt.Errorf("failed to retrieve total token supply: %v", err)
	}

	var totalSupply int

	// If no tokens have been minted, return 0
	if totalSupplyBytes == nil {
		totalSupply = 0
	} else {
		totalSupply, _ = strconv.Atoi(string(totalSupplyBytes)) // Error handling not needed since Itoa() was used when setting the totalSupply, guaranteeing it was an integer.
	}

	log.Printf("TotalSupply: %d tokens", totalSupply)

	return totalSupply, nil
}

// Helper Functions
// transferHelper is a helper function that transfers tokens from the "from" address to the "to" address
// Dependant functions include Transfer and TransferFrom
func transferHelper(ctx contractapi.TransactionContextInterface, from string, to string, value int) error {

	if from == to {
		return fmt.Errorf("cannot transfer to and from same client account")
	}

	if value < 0 { // transfer of 0 is allowed in ERC-20, so just validate against negative amounts
		return fmt.Errorf("transfer amount cannot be negative")
	}

	fromCurrentBalanceBytes, err := ctx.GetStub().GetState(from)
	if err != nil {
		return fmt.Errorf("failed to read client account %s from world state: %v", from, err)
	}

	if fromCurrentBalanceBytes == nil {
		return fmt.Errorf("client account %s has no balance", from)
	}

	fromCurrentBalance, _ := strconv.Atoi(string(fromCurrentBalanceBytes)) // Error handling not needed since Itoa() was used when setting the account balance, guaranteeing it was an integer.

	if fromCurrentBalance < value {
		return fmt.Errorf("client account %s has insufficient funds", from)
	}

	toCurrentBalanceBytes, err := ctx.GetStub().GetState(to)
	if err != nil {
		return fmt.Errorf("failed to read recipient account %s from world state: %v", to, err)
	}

	var toCurrentBalance int
	// If recipient current balance doesn't yet exist, we'll create it with a current balance of 0
	if toCurrentBalanceBytes == nil {
		toCurrentBalance = 0
	} else {
		toCurrentBalance, _ = strconv.Atoi(string(toCurrentBalanceBytes)) // Error handling not needed since Itoa() was used when setting the account balance, guaranteeing it was an integer.
	}

	fromUpdatedBalance := fromCurrentBalance - value
	toUpdatedBalance := toCurrentBalance + value

	err = ctx.GetStub().PutState(from, []byte(strconv.Itoa(fromUpdatedBalance)))
	if err != nil {
		return err
	}

	err = ctx.GetStub().PutState(to, []byte(strconv.Itoa(toUpdatedBalance)))
	if err != nil {
		return err
	}

	log.Printf("client %s balance updated from %d to %d", from, fromCurrentBalance, fromUpdatedBalance)
	log.Printf("recipient %s balance updated from %d to %d", to, toCurrentBalance, toUpdatedBalance)

	return nil
}
