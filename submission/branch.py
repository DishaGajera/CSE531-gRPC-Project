import grpc
import banks_pb2_grpc
from banks_pb2 import MsgRequest, MsgResponse

class Branch(banks_pb2_grpc.branchServicer):

    def __init__(self, id, balance, branches):
        # unique ID of the Branch
        self.id = id
        # replica of the Branch's balance
        self.balance = balance
        # the list of process IDs of the branches
        self.branches = branches
        # the list of Client stubs to communicate with the branches
        self.stubList = list()
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # iterate the processID of the branches

        # TODO: students are expected to store the processID of the branches
    def createStubs(self):
        for branchId in self.branches:
            if branchId != self.id:
                port = str(50000 + branchId)
                channel = grpc.insecure_channel("localhost:" + port)
                self.stubList.append(banks_pb2_grpc.branchStub(channel))

    # TODO: students are expected to process requests from both Client and Branch
    def MsgDelivery(self, request, context):
        return self.ProcessMsg(request, True)

    # Incoming MsgRequest from Branch propagation
    def MsgPropagation(self, request, context):
        return self.ProcessMsg(request, False)

    # Handle received Msg, generate and return a MsgResponse
    def ProcessMsg(self, request, propagate):
        result = "success"
        if request.interface == "deposit" or request.interface == "withdraw":
            if request.money < 0:
                result = "fail"
            elif request.interface == "deposit":
                self.balance += request.money
                if propagate == True:
                    self.Propagate_Deposit(request)
            elif request.interface == "withdraw":
                if self.balance >= request.money:
                    self.balance -= request.money
                    if propagate == True:
                        self.Propagate_Withdraw(request)
                else:
                    result = "fail"
            else:
                result = "fail"

            # Create msg to be appended to self.recvMsg list
            msg = {"interface": request.interface, "result": result}
            return MsgResponse(interface=request.interface, result=result)
        else:
            msg = {"interface": request.interface, "balance": self.balance}
            return MsgResponse(interface=request.interface, balance=self.balance)

        # self.recvMsg.append(msg)

    # Propagate Customer withdraw to other Branches
    def Propagate_Withdraw(self, request):
        for stub in self.stubList:
            stub.MsgPropagation(MsgRequest(id=request.id, interface="withdraw", money=request.money))

    # Propagate Customer deposit to other Branches
    def Propagate_Deposit(self, request):
        for stub in self.stubList:
            stub.MsgPropagation(MsgRequest(id=request.id, interface="deposit", money=request.money))