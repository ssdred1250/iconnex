from iconservice import *

TAG = 'UsedItem'

class UsedItem(IconScoreBase):

    _FEE = "fee"
    _ITEM_ID_COUNT = "_item_id_count"
    _ITEM_ID = "item_id"
    _NAME_KEY = "name_key"
    _PRICE_KEY = "price_key"
    _STATE_KEY = "state_key"
    _SELLER_KEY = "seller_key"
    _BUYER_KEY = "buyer_key"


    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._fee = VarDB(self._FEE, db, int)
        self._item_id_count = VarDB(self._ITEM_ID_COUNT, db, int)
        self._name_key = DictDB(self._NAME_KEY, db, str)
        self._price_key = DictDB(self._PRICE_KEY, db, int)
        self._state_key = DictDB(self._STATE_KEY, db, bool)
        self._seller_key = DictDB(self._SELLER_KEY, db, Address)
        self._buyer_key = DictDB(self._BUYER_KEY, db, Address)

    def on_install(self) -> None:
        super().on_install()
        self._fee.set(1000000000000000000)
        self._item_id_count.set(0)

    def on_update(self) -> None:
        super().on_update()
    
    @property
    def _item_id(self):
        return ArrayDB(self._ITEM_ID, self.db, int)

    @eventlog
    def eventItemEvent(self, _newItemId: int, _name: str, _price: int, _state: bool, _seller: Address, _buyer: Address):
        pass

    @payable
    @external
    def addItem(self, _name: str, _price: int):
        if self.msg.value < self._fee.get():
            revert("Not Enough Money")
        
        newItemId = self._item_id_count.get()

        self._name_key[newItemId] = _name
        self._price_key[newItemId] = _price
        self._state_key[newItemId] = True
        self._seller_key[newItemId] = self.msg.sender
        # self._buyer_key[newItemId] = Address(0)
        self._item_id.put(newItemId)

        self._item_id_count.set(self._item_id_count.get() + 1)

        paymentChange = self.msg.value - self._fee.get()

        # if (paymentChange > 0):
        #     self.icx.transfer(self.msg.sender, paymentChange)
        
        self.eventItemEvent(newItemId, self._name_key[newItemId], self._price_key[newItemId], self._state_key[newItemId], self._seller_key[newItemId], self._buyer_key[newItemId])

    @external
    @payable
    def buyItem(self, _id: int):
        if self._state_key[_id] == False:
            revert("Sold")

        if self.msg.value < self._price_key[_id]:
            revert("Not Enough Money")

        self._buyer_key[_id] = self.msg.sender
        self._state_key[_id] = False

        paymentChange = self.msg.value - self._price_key[_id]

        # if (paymentChange > 0):
        #     self.icx.transfer(self.msg.sender, paymentChange)

        self.icx.transfer(self._seller_key[_id], self._price_key[_id])

        self.eventItemEvent(_id, self._name_key[_id], self._price_key[_id], self._state_key[_id], self._seller_key[_id], self._buyer_key[_id])

    @external(readonly=True)
    def getItem(self, _id: int) -> str:
        return 'name: ' + str(self._name_key[_id]) + ' price: ' + str(self._price_key[_id]) + ' state: ' + str(self._state_key[_id]) + ' seller: ' + str(self._seller_key[_id]) + ' buyer: ' + str(self._buyer_key[_id])

    @external(readonly=True)
    def getId(self) -> int:
        return self._item_id.get(self._item_id_count.get() - 1)

    @external(readonly=True)
    def getPrice(self, _id: int) -> int:
        return self._price_key[_id]

    @external(readonly=True)
    def getList(self) -> dict:
        itemList = [
                    {"id": id,
                    "name": self._name_key[id], 
                    "price": self._price_key[id], 
                    "state": self._state_key[id], 
                    "seller": self._seller_key[id], 
                    "buyer": self._buyer_key[id]} for id in self._item_id
                    ]
        return itemList


