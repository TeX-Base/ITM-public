import pickle
from pprint import pprint, pformat
import pandas
import tabulate

# Specify the path to your pickle file
file_path = "components/probe_dumper/tmp/MetricsEval.MD1-Urban.pkl"

# Open the pickle file in read mode
with open(file_path, "rb") as file:
    # Load the contents of the pickle file
    data = pickle.load(file)

minDecision = data.explanation.minDecision #
minDistance = data.explanation.minDistance # not sure why this doesn't match the data.explanation.topDecisions more closely
new_cases = data.explanation.new_cases
#choice_justifications = minDecision.justifications
scenario_description = data.scenario_description
top_decisions = data.explanation.topDecisions


print("Scenario Description:")
print(scenario_description)

print("Example Decision:")
example_decision = new_cases[6]

example_decision_df =  pandas.DataFrame(example_decision, index=[0])
print("Treatment", example_decision["treatment"])
print("Moral Desert Neighbors:", example_decision["moraldesert_neighbor1"], example_decision["moraldesert_neighbor2"],example_decision["moraldesert_neighbor3"], example_decision["moraldesert_neighbor4"])



print("\nNearest cases from case base:")
for top_decision in top_decisions:
    print("Case No. " + str(top_decision[1]["index"]) + " " +top_decision[1]["action"])

# select the first decision from the top decisions as an example
example_neighbor = top_decisions[0][1]
example_neighbor_df = pandas.DataFrame(example_neighbor, index=[0])
print("\nExample Neighbor:")
print("Case No. " + str(example_neighbor["index"]) + " " + example_neighbor["action"])

# compare two pandas dataframes and find the columns they have in common
common_columns = example_decision_df.columns.intersection(example_neighbor_df.columns)

# if any of the common columns are different, print them
print("\nAttributes with different values (example | neighbor):")
for column in common_columns:
    if example_decision[column] != example_neighbor[column]:
        # print the column name, the decision value, and the neighbor value as a table       
        print(column + ": ", example_decision[column], " | ",  example_neighbor[column])

