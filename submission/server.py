import argparse
import json
import multiprocessing
import grpc
from concurrent import futures
from time import sleep
from termcolor import colored

import banks_pb2_grpc
from branch import Branch


# Start branch gRPC server process
def serveBranch(branch):
    print("Starting to create stubs...")
    branch.createStubs()
    print("Finished creating stubs.")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    banks_pb2_grpc.add_branchServicer_to_server(branch, server)
    port = str(50000 + branch.id)
    server.add_insecure_port("[::]:" + port)
    server.start()
    server.wait_for_termination()


def createBranchProcesses(processes):
    # List of Branch objects
    branches = []
    # List of Branch IDs
    branchIds = []
    # List of Branch processes
    branchProcesses = []

    # Instantiate Branch objects
    for process in processes:
        if process["type"] == "branch":
            branch = Branch(process["id"], process["balance"], branchIds)
            branches.append(branch)
            branchIds.append(branch.id)
    print('Branches', branches)

    # Spawn Branch processes
    for branch in branches:
        branch_process = multiprocessing.Process(target=serveBranch, args=(branch,))
        branchProcesses.append(branch_process)
        branch_process.start()

    # Allow branch processes to start
    sleep(5)
    print("Server started successfully.")
    return branchProcesses


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    args = parser.parse_args()

    try:
        # Load JSON file from 'input_file' arg
        input = json.load(open(args.input_file))
        createBranchProcesses(input)

    except FileNotFoundError:
        print(colored(f"Could not find input file '{args.input_file}'", "red"))
    except json.decoder.JSONDecodeError:
        print(colored("Error decoding JSON file", "red"))
