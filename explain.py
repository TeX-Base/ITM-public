import pickle
from pprint import pprint, pformat
import pandas
import tabulate
import json
# Specify the path to your pickle file
file_path = "components/probe_dumper/tmp/MetricsEval.MD1-Urban.pkl"

# Open the pickle file in read mode
with open(file_path, "rb") as file:
    # Load the contents of the pickle file
    data = pickle.load(file)

# read the data/keds_weights.json and get the top ten values for moraldesert
with open("data/keds_weights.json") as file:
    contents = json.loads(file.read())
    # get the values of the "kdma_specific_weights": "moraldesert"
    weights = contents["kdma_specific_weights"]
    # get the top ten values for moraldesert
    moral_desert_weights = weights["moraldesert"]
    top_moral_desert_weights = sorted(moral_desert_weights.items(), key=lambda x: x[1], reverse=True)[:10]


minDecision = data.explanation.minDecision #
minDistance = data.explanation.minDistance # not sure why this doesn't match the data.explanation.topDecisions more closely
new_cases = data.explanation.new_cases
#choice_justifications = minDecision.justifications
scenario_description = data.scenario_description
top_decisions = data.explanation.topDecisions

print("\n---Scenario Description---")
print(scenario_description)

print("---Example Decision---")
example_decision = new_cases[6]
print("Treatment: ", example_decision["treatment"])
print("Directness of causality: ", example_decision["directness_of_causality"])
print("Moral Desert: ", example_decision["moraldesert"])
print("Moral Desert Neighbors:", example_decision["moraldesert_neighbor1"], example_decision["moraldesert_neighbor2"],example_decision["moraldesert_neighbor3"], example_decision["moraldesert_neighbor4"])

# convert the example decision to a pandas dataframe
example_decision_df =  pandas.DataFrame(example_decision, index=[0])


print("\n---Nearest cases from case base---")
for top_decision in top_decisions:
    print("Case No. " + str(top_decision[1]["index"]) + " " +top_decision[1]["action"])

# select the first decision from the top decisions as an example
example_neighbor = top_decisions[0][1]
example_neighbor_df = pandas.DataFrame(example_neighbor, index=[0])
print("\n---Example Neighbor---")
print("Case No. " + str(example_neighbor["index"]) + " " + example_neighbor["action"])
print()
input("Press Enter to continue...")
# compare two pandas dataframes and find the columns they have in common
common_columns = example_decision_df.columns.intersection(example_neighbor_df.columns)

# top 10 weights for moraldesert
print("\nTop 10 weights for moraldesert:")
print(tabulate.tabulate(top_moral_desert_weights, headers=["Attribute", "Weight"], tablefmt="fancy_grid"))
input("Press Enter to continue...")

# find all of the columns in common columns that also have corresponding values in top_moral_desert_weights
top_columns = [column for column in common_columns if column in dict(top_moral_desert_weights)]
        
# find the columns in top_columns for both example_decision and example_neighbor and print as a table
print("\n---Attributes with the same values and top weights for moraldesert (example | neighbor):")
for column in top_columns:
    if example_decision[column] == example_neighbor[column]:
        # print the column name, the decision value, and the neighbor value as a table
        print(column + ": ", example_decision[column], " | ",  example_neighbor[column])
print()
input("Press Enter to continue...")

# attributes with different values and top weights for moraldesert
print("\n---Attributes with different values and top weights for moraldesert (example | neighbor):")
for column in top_columns:
    if example_decision[column] != example_neighbor[column]:
        # print the column name, the decision value, and the neighbor value as a table       
        print(column + ": ", example_decision[column], " | ",  example_neighbor[column])
print()
input("Press Enter to continue...")

# all attributes with the same values
print("\n--All attributes with the same values (example | neighbor):")
for column in common_columns:
    if example_decision[column] == example_neighbor[column]:
        # print the column name, the decision value, and the neighbor value as a table       
        print(column + ": ", example_decision[column], " | ",  example_neighbor[column])
print()
input("Press Enter to continue...")

# if any of the common columns are different, print them
print("\n--All attributes with different values (example | neighbor):")
for column in common_columns:
    if example_decision[column] != example_neighbor[column]:
        # print the column name, the decision value, and the neighbor value as a table       
        print(column + ": ", example_decision[column], " | ",  example_neighbor[column])

