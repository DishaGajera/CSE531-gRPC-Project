import grpc
from banks_pb2 import MsgRequest
import banks_pb2_grpc
from time import sleep

class Customer:
    def __init__(self, id, events):
        # unique ID of the Customer
        self.id = id
        # events from the input
        self.events = events
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # pointer for the stub
        self.stub = None

    # Create the Customer stub
    def createStub(self):
        port = str(50000 + self.id)
        channel = grpc.insecure_channel("localhost:" + port)
        self.stub = banks_pb2_grpc.branchStub(channel)

    # Send events to the Bank
    def executeEvents(self):
        for event in self.events:
            if event["interface"] == "deposit" or event["interface"] == "withdraw":
                money = event.get("money")  # Using get to avoid KeyError
                # Send request to Branch server
                response = self.stub.MsgDelivery(
                    MsgRequest(id=event["id"], interface=event["interface"], money=money)
                )
                # Create msg to be appended to self.recvMsg list
                msg = {"interface": response.interface, "result": response.result}
                self.recvMsg.append(msg)
            else:
                response = self.stub.MsgDelivery(
                    MsgRequest(id=event["id"], interface=event["interface"])
                )
                msg = {"interface": response.interface, "balance": response.balance}
                self.recvMsg.append(msg)

    # Generate output msg
    def output(self):
        return {"id": self.id, "recv": self.recvMsg}
