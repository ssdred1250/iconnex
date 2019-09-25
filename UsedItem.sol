pragma solidity ^0.5.0;

contract ShoppingMall {

    address payable owner = msg.sender;
    uint FEE = 1 finney;

    uint itemIdCount = 0;
    
    enum State { ForSale, Sold, Shipped, Received }
    
    struct Item {
      string name;
      uint price;
      State state;
      address payable seller;
      address buyer;
    }

    mapping(uint => Item) items;
    
    event itemEvent(
        uint itemId,
        string name,
        uint price,
        State state,
        address seller,
        address buyer
    );
    
    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }
    
    modifier checkState(uint _id, State _state) {
        require(items[_id].state == _state);
        _;
    }
   
    modifier checkCaller(address _caller) {
        require(msg.sender == _caller);
        _;
    }
    
    modifier checkValue(uint _value) {
        require(msg.value >= _value);
        _;
    }
    
    function addItem(string memory _name, uint _price) public payable checkValue(FEE) returns(uint) {
        
        Item memory newItem;
        newItem.name = _name;
        newItem.price = _price;
        newItem.state = State.ForSale;
        newItem.seller = msg.sender;
        newItem.buyer = address(0);
        uint newItemId = itemIdCount;
        items[itemIdCount] = newItem; 
        itemIdCount++;
        
        uint paymentChange = msg.value - FEE;
        if (paymentChange > 0) {
            address(msg.sender).transfer(paymentChange);
        }
    
        emit itemEvent(
            newItemId,
            items[newItemId].name,
            items[newItemId].price,
            items[newItemId].state,
            items[newItemId].seller,
            items[newItemId].buyer
        );

        return newItemId;
    }
    
    function buyItem(uint _id) public payable checkState(_id, State.ForSale) checkValue(items[_id].price) {
        
        items[_id].buyer = msg.sender;
        items[_id].state = State.Sold;
        items[_id].seller.transfer(items[_id].price);
       
        uint paymentChange = msg.value - items[_id].price;
        if (paymentChange > 0) {
            address(msg.sender).transfer(paymentChange);
        }

        emit itemEvent(
          _id,
          items[_id].name,
          items[_id].price,
          items[_id].state,
          items[_id].seller,
          items[_id].buyer
        );
    }
    
    function shipItem(uint _id) public checkState(_id, State.Sold) checkCaller(items[_id].seller) {
        items[_id].state = State.Shipped;
        emit itemEvent(
            _id,
            items[_id].name,
            items[_id].price,
            items[_id].state,
            items[_id].seller,
            items[_id].buyer
        );
    }
    
    function receiveItem(uint _id) public checkState(_id, State.Shipped) checkCaller(items[_id].buyer) {
        items[_id].state = State.Received;
        emit itemEvent(
            _id,
            items[_id].name,
            items[_id].price,
            items[_id].state,
            items[_id].seller,
            items[_id].buyer
        );
    }
    
    function getItem(uint _id) public view returns(string memory, uint, State, address, address) {
        return (items[_id].name, items[_id].price, items[_id].state, items[_id].seller, items[_id].buyer);
    }
    
    function withdrawFunds() public onlyOwner {
        require(address(this).balance > 0);
        owner.transfer(address(this).balance);
    }
}