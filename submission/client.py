import argparse
import json
import multiprocessing
from time import sleep
from termcolor import colored
from customer import Customer  # Ensure it's imported with uppercase 'C'

# Start customer gRPC client processes
def serveCustomer(customer_instance):
    customer_instance.createStub()
    customer_instance.executeEvents()

    output = customer_instance.output()

    with open('output.json', 'r') as output_file:
        try:
            data = json.load(output_file)
        except json.JSONDecodeError:
            data = []
    with open('output.json', 'w') as output_file:
        print(output)
        data.append(output)
        json.dump(data, output_file)  # Write as JSON format

def createCustomerProcesses(processes):
    customers = []
    customerProcesses = []

    # Instantiate Customer objects from the input list
    for process in processes:  # Now 'processes' is a list of customer and branch objects
        if process["type"] == "customer":  # Check if the type is customer
            customer_instance = Customer(process["id"], process["events"])  # Ensure Customer class name is correct
            customers.append(customer_instance)  # Append instance to the list

    # Spawn Customer processes
    for customer_instance in customers:
        customer_process = multiprocessing.Process(target=serveCustomer, args=(customer_instance,))
        customerProcesses.append(customer_process)
        customer_process.start()
        sleep(2)

    # Wait for Customer processes to complete
    for customerProcess in customerProcesses:
        customerProcess.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    args = parser.parse_args()

    try:
        # Load JSON file from 'input_file' arg
        input_data = json.load(open(args.input_file))

        # print(input_data)  # Debug: Print the loaded JSON

        # Initialize output file
        open("output.json", "w").close()  # Create or clear the output.json file

        createCustomerProcesses(input_data)  # Pass the list directly

    except FileNotFoundError:
        print(colored(f"Could not find input file '{args.input_file}'", "red"))
    except json.decoder.JSONDecodeError:
        print(colored("Error decoding JSON file", "red"))
